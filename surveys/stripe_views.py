import stripe
import json
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Userapp
from .stripe_plans import PLANS, PRICE_ID_TO_PLAN

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


# ─────────────────────────────────────────────────────────────
# 1. LISTA DE PLANES (pública — para mostrar en la landing)
# ─────────────────────────────────────────────────────────────
class StripePlansView(View):
    def get(self, request):
        return JsonResponse({'plans': PLANS})


# ─────────────────────────────────────────────────────────────
# 2. CREAR SESIÓN DE CHECKOUT (el usuario elige un plan)
# ─────────────────────────────────────────────────────────────
class StripeCheckoutView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request):
        try:
            data = json.loads(request.body)
            plan_key = data.get('plan_key')

            if plan_key not in PLANS:
                return JsonResponse({'error': 'Plan no válido'}, status=400)

            plan = PLANS[plan_key]
            user = request.user
            userapp = Userapp.objects.get(user=user)

            # Obtener o crear cliente en Stripe
            if userapp.stripe_customer_id:
                customer_id = userapp.stripe_customer_id
            else:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}",
                    metadata={'user_id': user.id}
                )
                customer_id = customer.id
                userapp.stripe_customer_id = customer_id
                userapp.save()

            # Configurar modo según tipo de plan
            if plan['periodo'] == 'unico':
                mode = 'payment'
            else:
                mode = 'subscription'

            base_url = request.build_absolute_uri('/').rstrip('/')

            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': plan['price_id'],
                    'quantity': 1,
                }],
                mode=mode,
                success_url=f"{base_url}/payments/success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{base_url}/payments/cancel/",
                metadata={
                    'user_id': user.id,
                    'plan_key': plan_key,
                }
            )

            return JsonResponse({'checkout_url': session.url})

        except Userapp.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Error en checkout: {e}")
            return JsonResponse({'error': 'Error interno'}, status=500)


# ─────────────────────────────────────────────────────────────
# 3. PORTAL DEL CLIENTE (gestiona su suscripción sin tu ayuda)
# ─────────────────────────────────────────────────────────────
class StripePortalView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        try:
            userapp = Userapp.objects.get(user=request.user)

            if not userapp.stripe_customer_id:
                return redirect('/payments/')

            base_url = request.build_absolute_uri('/').rstrip('/')
            session = stripe.billing_portal.Session.create(
                customer=userapp.stripe_customer_id,
                return_url=f"{base_url}/payments/",
            )
            return redirect(session.url)

        except Userapp.DoesNotExist:
            return redirect('/login/')
        except stripe.error.StripeError as e:
            logger.error(f"Portal error: {e}")
            return redirect('/payments/')


# ─────────────────────────────────────────────────────────────
# 4. WEBHOOK DE STRIPE (activa/desactiva acceso automáticamente)
# ─────────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        event_type = event['type']
        data = event['data']['object']

        logger.info(f"Stripe webhook: {event_type}")

        if event_type == 'checkout.session.completed':
            self._handle_checkout_completed(data)

        elif event_type == 'invoice.paid':
            self._handle_invoice_paid(data)

        elif event_type == 'invoice.payment_failed':
            self._handle_payment_failed(data)

        elif event_type in ['customer.subscription.deleted',
                            'customer.subscription.updated']:
            self._handle_subscription_change(data)

        return HttpResponse(status=200)

    def _handle_checkout_completed(self, session):
        try:
            user_id = session['metadata'].get('user_id')
            plan_key = session['metadata'].get('plan_key')

            if not user_id or not plan_key:
                return

            userapp = Userapp.objects.get(user_id=user_id)
            plan = PLANS.get(plan_key)

            if not plan:
                return

            # Activar acceso según módulo
            self._activate_plan(userapp, plan, plan_key)

            # Guardar subscription_id si es recurrente
            if session.get('subscription'):
                userapp.stripe_subscription_id = session['subscription']

            userapp.stripe_plan_key = plan_key
            userapp.save()

            logger.info(f"Plan activado: user={user_id}, plan={plan_key}")

        except Userapp.DoesNotExist:
            logger.error(f"Userapp no encontrado: user_id={user_id}")
        except Exception as e:
            logger.error(f"Error en checkout_completed: {e}")

    def _handle_invoice_paid(self, invoice):
        try:
            customer_id = invoice.get('customer')
            userapp = Userapp.objects.get(stripe_customer_id=customer_id)
            plan_key = userapp.stripe_plan_key

            if plan_key and plan_key in PLANS:
                plan = PLANS[plan_key]
                self._activate_plan(userapp, plan, plan_key)
                userapp.save()
                logger.info(f"Renovación pagada: customer={customer_id}")

        except Userapp.DoesNotExist:
            logger.error(f"Userapp no encontrado: customer={customer_id}")
        except Exception as e:
            logger.error(f"Error en invoice_paid: {e}")

    def _handle_payment_failed(self, invoice):
        try:
            customer_id = invoice.get('customer')
            userapp = Userapp.objects.get(stripe_customer_id=customer_id)
            # Opcional: enviar email de aviso pero no desactivar aún
            logger.warning(f"Pago fallido: customer={customer_id}")
        except Exception as e:
            logger.error(f"Error en payment_failed: {e}")

    def _handle_subscription_change(self, subscription):
        try:
            customer_id = subscription.get('customer')
            status = subscription.get('status')
            userapp = Userapp.objects.get(stripe_customer_id=customer_id)

            if status in ['canceled', 'unpaid', 'past_due']:
                # Desactivar acceso
                userapp.workplaces_available = 0
                userapp.workplaces_availableB = 0
                userapp.workplaces_availableC = 0
                userapp.psico_evaluaciones_disponibles = 0
                userapp.stripe_plan_key = ''
                userapp.save()
                logger.info(f"Acceso desactivado: customer={customer_id}, status={status}")

        except Userapp.DoesNotExist:
            logger.error(f"Userapp no encontrado: customer={customer_id}")
        except Exception as e:
            logger.error(f"Error en subscription_change: {e}")

    def _activate_plan(self, userapp, plan, plan_key):
        modulo = plan['modulo']
        empleados_max = plan['empleados_max']
        evaluaciones = plan['evaluaciones_mes']

        if modulo == 'nom035':
            # Asignar créditos de centros de trabajo según tamaño
            if empleados_max <= 15:
                userapp.workplaces_available = userapp.workplaces_available + 1
            elif empleados_max <= 50:
                userapp.workplaces_availableB = userapp.workplaces_availableB + 1
            else:
                userapp.workplaces_availableC = userapp.workplaces_availableC + 1

        elif modulo == 'psicometria':
            if evaluaciones == -1:
                # Ilimitado
                userapp.psico_evaluaciones_disponibles = 99999
            else:
                userapp.psico_evaluaciones_disponibles = (
                    userapp.psico_evaluaciones_disponibles + evaluaciones
                )

        elif modulo == 'suite':
            # Activa NOM-035 PyME + psicometría
            if empleados_max <= 50:
                userapp.workplaces_availableB = userapp.workplaces_availableB + 1
            else:
                userapp.workplaces_availableC = userapp.workplaces_availableC + 1

            if evaluaciones == -1:
                userapp.psico_evaluaciones_disponibles = 99999
            else:
                userapp.psico_evaluaciones_disponibles = (
                    userapp.psico_evaluaciones_disponibles + evaluaciones
                )


# ─────────────────────────────────────────────────────────────
# 5. PÁGINAS DE RETORNO DESPUÉS DEL PAGO
# ─────────────────────────────────────────────────────────────
class PaymentSuccessView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        from django.shortcuts import render
        session_id = request.GET.get('session_id')
        return render(request, 'payment_success.html', {'session_id': session_id})


class PaymentCancelView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        from django.shortcuts import render
        return render(request, 'payment_cancel.html')
