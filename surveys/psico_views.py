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

        
        class TestResultView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, session_id):
        from django.shortcuts import render
        session = get_object_or_404(
            TestSession,
            id=session_id,
            candidate__user=request.user,
            status='completada'
        )
        result = get_object_or_404(TestResult, session=session)
        scores = result.scores
        tipo = session.instrumento.tipo

        ctx = {
            'session': session,
            'candidate': session.candidate,
            'instrumento': session.instrumento,
            'scores': scores,
            'tipo': tipo,
            'name': request.user.userapp.name,
        }

        # Interpretación DISC
        if tipo == 'disc':
            total = sum(scores.values()) or 1
            pct = {k: max(0, round((v / 28) * 100)) for k, v in scores.items()}
            dominante = max(scores, key=scores.get)
            segundo = sorted(scores, key=scores.get, reverse=True)[1]

            perfiles = {
                'D': {'nombre': 'Dominante', 'color': '#ea5455', 'desc': 'Orientado a resultados, directo y decidido. Toma iniciativa y enfrenta desafíos con determinación.', 'fortalezas': ['Toma decisiones rápidas', 'Alta orientación a resultados', 'Liderazgo natural en situaciones de presión'], 'desarrollo': ['Puede ser percibido como impaciente', 'Necesita desarrollar escucha activa'], 'puestos': 'Dirección, gerencia, ventas, proyectos'},
                'I': {'nombre': 'Influyente', 'color': '#ff9f43', 'desc': 'Comunicativo, entusiasta y orientado a las personas. Motiva a otros con facilidad.', 'fortalezas': ['Excelente comunicación interpersonal', 'Genera entusiasmo en el equipo', 'Facilidad para construir relaciones'], 'desarrollo': ['Puede descuidar los detalles', 'Necesita estructura para mantener el enfoque'], 'puestos': 'Ventas, relaciones públicas, servicio al cliente, capacitación'},
                'S': {'nombre': 'Estable', 'color': '#28c76f', 'desc': 'Paciente, confiable y orientado al equipo. Brinda estabilidad y consistencia.', 'fortalezas': ['Alta confiabilidad y constancia', 'Excelente trabajo en equipo', 'Manejo efectivo de situaciones de presión'], 'desarrollo': ['Puede resistirse a cambios rápidos', 'Necesita apoyo para tomar decisiones bajo incertidumbre'], 'puestos': 'Administración, soporte, recursos humanos, atención al cliente'},
                'C': {'nombre': 'Cumplidor', 'color': '#7367f0', 'desc': 'Analítico, preciso y orientado a la calidad. Sigue procesos y estándares con rigor.', 'fortalezas': ['Alta precisión y atención al detalle', 'Pensamiento analítico', 'Respeto por procesos y normas'], 'desarrollo': ['Puede ser perfeccionista en exceso', 'Necesita trabajar la comunicación asertiva'], 'puestos': 'Finanzas, calidad, tecnología, auditoría, investigación'},
            }

            ctx['pct'] = pct
            ctx['dominante'] = dominante
            ctx['segundo'] = segundo
            ctx['perfil_dominante'] = perfiles[dominante]
            ctx['perfil_segundo'] = perfiles[segundo]
            ctx['perfiles'] = perfiles
            ctx['perfil_nombre'] = f"Perfil {dominante}-{segundo}: {perfiles[dominante]['nombre']} con tendencia {perfiles[segundo]['nombre']}"

        # Interpretación Moss
        elif tipo == 'moss':
            total = scores.get('total', 0)
            max_score = 90
            pct = round((total / max_score) * 100)
            if pct >= 80:
                nivel = 'Muy alto'
                color = '#28c76f'
                apto = True
                interpretacion = 'Excelentes habilidades de supervisión. Perfil altamente recomendado para puestos de liderazgo y gestión de equipos.'
            elif pct >= 60:
                nivel = 'Alto'
                color = '#7367f0'
                apto = True
                interpretacion = 'Buenas habilidades de supervisión. Recomendado para puestos de liderazgo con desarrollo continuo.'
            elif pct >= 40:
                nivel = 'Medio'
                color = '#ff9f43'
                apto = False
                interpretacion = 'Habilidades de supervisión en desarrollo. Se recomienda para puestos operativos con potencial de crecimiento.'
            else:
                nivel = 'Bajo'
                color = '#ea5455'
                apto = False
                interpretacion = 'Habilidades de supervisión limitadas. Se recomienda para puestos sin responsabilidad de gestión de personas.'
            ctx['total'] = total
            ctx['pct'] = pct
            ctx['nivel'] = nivel
            ctx['color'] = color
            ctx['apto'] = apto
            ctx['interpretacion'] = interpretacion

        # Interpretación Raven
        elif tipo == 'raven':
            correctas = scores.get('correctas', 0)
            total = scores.get('total', 60)
            pct = scores.get('porcentaje', 0)
            if pct >= 85:
                nivel = 'Muy Superior'
                color = '#28c76f'
                desc = 'Capacidad intelectual sobresaliente. Aprende con rapidez y resuelve problemas complejos.'
            elif pct >= 70:
                nivel = 'Superior'
                color = '#7367f0'
                desc = 'Capacidad intelectual por encima del promedio. Buen potencial de aprendizaje.'
            elif pct >= 50:
                nivel = 'Normal'
                color = '#ff9f43'
                desc = 'Capacidad intelectual dentro del promedio esperado para el puesto.'
            elif pct >= 30:
                nivel = 'Inferior al promedio'
                color = '#ea5455'
                desc = 'Capacidad intelectual por debajo del promedio. Se recomienda evaluar para puestos operativos.'
            else:
                nivel = 'Inferior'
                color = '#ea5455'
                desc = 'Capacidad intelectual limitada para puestos que requieren razonamiento complejo.'
            ctx['correctas'] = correctas
            ctx['total_items'] = total
            ctx['pct'] = pct
            ctx['nivel'] = nivel
            ctx['color'] = color
            ctx['desc'] = desc

        # Interpretación Zavic
        elif tipo == 'zavic':
            total_pts = sum(scores.values()) or 1
            pct = {k: round((v / total_pts) * 100) for k, v in scores.items()}
            alerta_corrupcion = scores.get('C', 0) > scores.get('M', 0)
            escalas = {
                'M': {'nombre': 'Moral', 'color': '#28c76f', 'desc': 'Actúa guiado por principios éticos personales'},
                'L': {'nombre': 'Legal', 'color': '#7367f0', 'desc': 'Respeta normas y reglamentos establecidos'},
                'I': {'nombre': 'Indiferente', 'color': '#ff9f43', 'desc': 'Tendencia a no involucrarse ante situaciones'},
                'C': {'nombre': 'Corrupción', 'color': '#ea5455', 'desc': 'Tendencia a actuar en beneficio propio indebidamente'},
            }
            ctx['pct'] = pct
            ctx['escalas'] = escalas
            ctx['alerta_corrupcion'] = alerta_corrupcion

        return render(request, 'psico_resultado.html', ctx)