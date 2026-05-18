import uuid
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Candidate, TestSession, PsychoInstrument, TestResponse, TestResult, PsychoItem
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


class CandidateListView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request):
        candidates = Candidate.objects.filter(user=request.user).order_by('-record_create')
        instrumentos = PsychoInstrument.objects.filter(activo=True)
        ctx = {
            'candidates': candidates,
            'instrumentos': instrumentos,
            'name': request.user.userapp.name,
        }
        return render(request, 'psico_candidatos.html', ctx)


class CandidateCreateView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def post(self, request):
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        puesto = request.POST.get('puesto', '').strip()
        tipo = request.POST.get('tipo', 'externo')
        notas = request.POST.get('notas', '').strip()

        if not nombre:
            return JsonResponse({'error': 'El nombre es requerido'}, status=400)

        candidate = Candidate.objects.create(
            user=request.user,
            nombre=nombre,
            email=email,
            puesto=puesto,
            tipo=tipo,
            notas=notas,
        )
        return JsonResponse({
            'id': candidate.id,
            'nombre': candidate.nombre,
            'puesto': candidate.puesto,
            'tipo': candidate.get_tipo_display(),
            'status': 'ok'
        })


class CandidateDetailView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id, user=request.user)
        sessions = candidate.sessions.select_related('instrumento').order_by('-record_create')
        instrumentos = PsychoInstrument.objects.filter(activo=True)
        ctx = {
            'candidate': candidate,
            'sessions': sessions,
            'instrumentos': instrumentos,
            'name': request.user.userapp.name,
        }
        return render(request, 'psico_candidato_detalle.html', ctx)


class AssignTestView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def post(self, request, candidate_id):
        candidate = get_object_or_404(Candidate, id=candidate_id, user=request.user)
        instrumento_id = request.POST.get('instrumento_id')

        if not instrumento_id:
            return JsonResponse({'error': 'Instrumento requerido'}, status=400)

        instrumento = get_object_or_404(PsychoInstrument, id=instrumento_id, activo=True)

        token = uuid.uuid4().hex
        expira_en = timezone.now() + timedelta(days=7)

        session = TestSession.objects.create(
            candidate=candidate,
            instrumento=instrumento,
            token=token,
            expira_en=expira_en,
        )

        test_url = request.build_absolute_uri(f'/psico/test/{token}/')

        return JsonResponse({
            'status': 'ok',
            'session_id': session.id,
            'token': token,
            'test_url': test_url,
            'instrumento': instrumento.nombre,
            'expira_en': expira_en.strftime('%d/%m/%Y'),
        })


class TestSessionView(View):
    """Vista pública — el candidato responde sin login"""

    def get(self, request, token):
        session = get_object_or_404(TestSession, token=token)

        if session.status == 'expirada':
            return render(request, 'psico_test_expirado.html')

        if session.status == 'completada':
            return render(request, 'psico_test_completado.html')

        if timezone.now() > session.expira_en:
            session.status = 'expirada'
            session.save()
            return render(request, 'psico_test_expirado.html')

        if session.status == 'pendiente':
            session.status = 'en_proceso'
            session.fecha_inicio = timezone.now()
            session.save()

        items = session.instrumento.items.order_by('numero')
        ctx = {
            'session': session,
            'items': items,
            'candidate': session.candidate,
            'instrumento': session.instrumento,
        }
        return render(request, 'psico_test.html', ctx)

@method_decorator(csrf_exempt, name='dispatch')
class TestCompleteView(View):
    """Recibe las respuestas del candidato"""

    def post(self, request, token):
        session = get_object_or_404(TestSession, token=token)

        if session.status not in ['pendiente', 'en_proceso']:
            return JsonResponse({'error': 'Sesión no válida'}, status=400)

        try:
            data = json.loads(request.body)
            respuestas = data.get('respuestas', [])
        except Exception:
            return JsonResponse({'error': 'Datos inválidos'}, status=400)

        for r in respuestas:
            item_id = r.get('item_id')
            respuesta = r.get('respuesta')
            try:
                item = PsychoItem.objects.get(id=item_id, instrumento=session.instrumento)
                TestResponse.objects.update_or_create(
                    session=session,
                    item=item,
                    defaults={'respuesta': respuesta}
                )
            except PsychoItem.DoesNotExist:
                continue

        session.status = 'completada'
        session.fecha_completado = timezone.now()
        session.save()

        # Calcular scores básicos
        scores = self._calcular_scores(session)
        TestResult.objects.update_or_create(
            session=session,
            defaults={'scores': scores}
        )

        return JsonResponse({'status': 'ok', 'redirect': f'/psico/test/{token}/'})

    def _calcular_scores(self, session):
        tipo = session.instrumento.tipo
        responses = session.responses.select_related('item').all()

        if tipo == 'disc':
            scores = {'D': 0, 'I': 0, 'S': 0, 'C': 0}
            for r in responses:
                respuesta = r.respuesta
                mas = respuesta.get('mas')
                menos = respuesta.get('menos')
                opciones = r.item.opciones
                for op in opciones:
                    if op.get('dimension') == mas:
                        scores[mas] = scores.get(mas, 0) + 1
                    if op.get('dimension') == menos:
                        scores[menos] = scores.get(menos, 0) - 1
            return scores

        elif tipo == 'moss':
            total = 0
            for r in responses:
                respuesta = r.respuesta
                puntos = respuesta.get('puntos', 0)
                total += puntos
            return {'total': total}

        elif tipo == 'raven':
            correctas = 0
            total = responses.count()
            for r in responses:
                respuesta = r.respuesta
                if respuesta.get('seleccion') == r.item.respuesta_correcta:
                    correctas += 1
            return {
                'correctas': correctas,
                'total': total,
                'porcentaje': round((correctas / total * 100) if total > 0 else 0)
            }

        elif tipo == 'zavic':
            scores = {'M': 0, 'L': 0, 'I': 0, 'C': 0}
            for r in responses:
                distribucion = r.respuesta.get('distribucion', {})
                for escala, puntos in distribucion.items():
                    scores[escala] = scores.get(escala, 0) + puntos
            return scores

        return {}