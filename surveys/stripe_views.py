import stripe
import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .models import Userapp, Workplace
from .stripe_plans import PLANS

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


# ─────────────────────────────────────────────────────────────
# 1. LISTA DE PLANES (pública — para mostrar en la landing)
# ─────────────────────────────────────────────────────────────
class StripePlansView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        from django.shortcuts import render
        from .stripe_plans import PLANS
        userapp = request.user.userapp
        plan_key = getattr(userapp, 'stripe_plan_key', '')
        plan_activo = PLANS.get(plan_key, {}).get('name', '') if plan_key else ''
        return render(request, 'stripe_planes.html', {
            'planes': PLANS,
            'plan_activo': plan_activo,
            'workplaces': Workplace.objects.filter(user=request.user),
        })

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
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=f"{request.user.first_name} {request.user.last_name}",
                    metadata={'user_id': request.user.id}
                )
                userapp.stripe_customer_id = customer.id
                userapp.save()

            base_url = request.build_absolute_uri('/').rstrip('/')
            session = stripe.billing_portal.Session.create(
                customer=userapp.stripe_customer_id,
                return_url=f"{base_url}/edit_profile/",
            )
            return redirect(session.url)

        except Userapp.DoesNotExist:
            return redirect('/login/')
        except stripe.error.StripeError as e:
            logger.error(f"Portal error: {e}")
            return redirect('edit_profile')


# ─────────────────────────────────────────────────────────────
# 4. PÁGINAS DE RETORNO DESPUÉS DEL PAGO
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
