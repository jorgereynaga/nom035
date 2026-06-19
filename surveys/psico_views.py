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
        from surveys.models import Workplace
        if not Workplace.objects.filter(user=request.user).exists():
            return JsonResponse({'error': 'Debes registrar un centro de trabajo antes de agregar candidatos.'}, status=400)
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
        userapp = getattr(request.user, "userapp", None)
        if userapp and not getattr(userapp, "psico_plan_key", ""):
            from django.http import HttpResponse
            return HttpResponse('<h2 style="font-family:sans-serif;text-align:center;margin-top:80px">&#128274; Reporte no disponible en modo demo.<br><a href="/stripe/planes/" style="color:#2563eb">Adquiere un plan para ver tus reportes</a></h2>', status=403)
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

        userapp = request.user.userapp
        disponibles = getattr(userapp, 'psico_evaluaciones_disponibles', 0)
        demo = getattr(userapp, 'psico_demo', 0)
        if disponibles <= 0 and demo <= 0:
            return JsonResponse({'error': 'Sin creditos psicometricos disponibles. Contrata un plan.'}, status=403)
        usar_demo = disponibles <= 0 and demo > 0

        token = uuid.uuid4().hex
        expira_en = timezone.now() + timedelta(days=7)

        session = TestSession.objects.create(
            candidate=candidate,
            instrumento=instrumento,
            token=token,
            expira_en=expira_en,
        )
        if usar_demo:
            userapp.psico_demo = demo - 1
        else:
            userapp.psico_evaluaciones_disponibles = disponibles - 1
        userapp.save()

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
        if tipo == 'disc':
            pct = {k: max(0, round((v / 28) * 100)) for k, v in scores.items()}
            dominante = max(scores, key=scores.get)
            segundo = sorted(scores, key=scores.get, reverse=True)[1]
            perfiles = {
                'D': {'nombre': 'Dominante', 'color': '#ea5455', 'desc': 'Orientado a resultados, directo y decidido.', 'fortalezas': ['Toma decisiones rapidas', 'Alta orientacion a resultados', 'Liderazgo natural'], 'desarrollo': ['Puede ser impaciente', 'Necesita escucha activa'], 'puestos': 'Direccion, gerencia, ventas, proyectos'},
                'I': {'nombre': 'Influyente', 'color': '#ff9f43', 'desc': 'Comunicativo, entusiasta y orientado a las personas.', 'fortalezas': ['Excelente comunicacion', 'Genera entusiasmo', 'Construye relaciones'], 'desarrollo': ['Puede descuidar detalles', 'Necesita estructura'], 'puestos': 'Ventas, relaciones publicas, capacitacion'},
                'S': {'nombre': 'Estable', 'color': '#28c76f', 'desc': 'Paciente, confiable y orientado al equipo.', 'fortalezas': ['Alta confiabilidad', 'Trabajo en equipo', 'Manejo de presion'], 'desarrollo': ['Puede resistir cambios', 'Necesita apoyo para decidir'], 'puestos': 'Administracion, soporte, recursos humanos'},
                'C': {'nombre': 'Cumplidor', 'color': '#7367f0', 'desc': 'Analitico, preciso y orientado a la calidad.', 'fortalezas': ['Alta precision', 'Pensamiento analitico', 'Respeto por procesos'], 'desarrollo': ['Puede ser perfeccionista', 'Necesita comunicacion asertiva'], 'puestos': 'Finanzas, calidad, tecnologia, auditoria'},
            }
            ctx['pct'] = pct
            ctx['dominante'] = dominante
            ctx['segundo'] = segundo
            ctx['perfil_dominante'] = perfiles[dominante]
            ctx['perfil_segundo'] = perfiles[segundo]
            ctx['perfiles'] = perfiles
            ctx['perfil_nombre'] = f"Perfil {dominante}-{segundo}: {perfiles[dominante]['nombre']} con tendencia {perfiles[segundo]['nombre']}"
        elif tipo == 'moss':
            total = scores.get('total', 0)
            pct = round((total / 90) * 100)
            if pct >= 80:
                nivel, color, apto, interpretacion = 'Muy alto', '#28c76f', True, 'Excelentes habilidades de supervision. Altamente recomendado para liderazgo.'
            elif pct >= 60:
                nivel, color, apto, interpretacion = 'Alto', '#7367f0', True, 'Buenas habilidades de supervision. Recomendado con desarrollo continuo.'
            elif pct >= 40:
                nivel, color, apto, interpretacion = 'Medio', '#ff9f43', False, 'Habilidades en desarrollo. Recomendado para puestos operativos.'
            else:
                nivel, color, apto, interpretacion = 'Bajo', '#ea5455', False, 'Habilidades limitadas. No recomendado para gestion de personas.'
            ctx['total'] = total
            ctx['pct'] = pct
            ctx['nivel'] = nivel
            ctx['color'] = color
            ctx['apto'] = apto
            ctx['interpretacion'] = interpretacion
        elif tipo == 'raven':
            correctas = scores.get('correctas', 0)
            total = scores.get('total', 60)
            pct = scores.get('porcentaje', 0)
            if pct >= 85:
                nivel, color, desc = 'Muy Superior', '#28c76f', 'Capacidad intelectual sobresaliente.'
            elif pct >= 70:
                nivel, color, desc = 'Superior', '#7367f0', 'Capacidad por encima del promedio.'
            elif pct >= 50:
                nivel, color, desc = 'Normal', '#ff9f43', 'Capacidad dentro del promedio esperado.'
            else:
                nivel, color, desc = 'Inferior', '#ea5455', 'Capacidad limitada para puestos de alta complejidad.'
            ctx['correctas'] = correctas
            ctx['total_items'] = total
            ctx['pct'] = pct
            ctx['nivel'] = nivel
            ctx['color'] = color
            ctx['desc'] = desc
        elif tipo == 'zavic':
            total_pts = sum(scores.values()) or 1
            pct = {k: round((v / total_pts) * 100) for k, v in scores.items()}
            alerta_corrupcion = scores.get('C', 0) > scores.get('M', 0)
            escalas = {
                'M': {'nombre': 'Moral', 'color': '#28c76f'},
                'L': {'nombre': 'Legal', 'color': '#7367f0'},
                'I': {'nombre': 'Indiferente', 'color': '#ff9f43'},
                'C': {'nombre': 'Corrupcion', 'color': '#ea5455'},
            }
            ctx['pct'] = pct
            ctx['escalas'] = escalas
            ctx['alerta_corrupcion'] = alerta_corrupcion
        return render(request, 'psico_resultado.html', ctx)


class GenerarPerfilNarrativoView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def post(self, request, session_id):
        import os
        import json
        import urllib.request
        session = get_object_or_404(
            TestSession,
            id=session_id,
            candidate__user=request.user,
            status='completada'
        )
        result = get_object_or_404(TestResult, session=session)
        scores = result.scores
        tipo = session.instrumento.tipo
        candidato = session.candidate.nombre
        puesto = session.candidate.puesto or 'no especificado'
        if tipo == 'disc':
            dominante = max(scores, key=scores.get)
            nombres = {'D': 'Dominancia', 'I': 'Influencia', 'S': 'Estabilidad', 'C': 'Cumplimiento'}
            detalle = ', '.join([f"{nombres[k]}: {v}" for k, v in scores.items()])
            prompt = f"Eres un psicologo organizacional experto en evaluaciones de personal para empresas mexicanas. Genera un perfil narrativo profesional para Recursos Humanos sobre el candidato {candidato} que aplica al puesto de {puesto}. Resultados DISC: {detalle}. Dimension dominante: {nombres[dominante]}. Escribe 3 parrafos: 1) Perfil general, 2) Fortalezas laborales, 3) Areas de desarrollo y recomendacion. Tono profesional, objetivo, tercera persona. Sin numeros ni porcentajes."
        elif tipo == 'moss':
            total = scores.get('total', 0)
            pct = round((total / 90) * 100)
            prompt = f"Eres un psicologo organizacional experto en evaluaciones de personal para empresas mexicanas. Genera un perfil narrativo profesional para Recursos Humanos sobre el candidato {candidato} que aplica al puesto de {puesto}. Test Moss: {pct}% de habilidades de supervision. Escribe 2 parrafos: 1) Nivel de liderazgo y supervision, 2) Recomendacion para puestos de gestion. Tono profesional, objetivo, tercera persona."
        elif tipo == 'raven':
            pct = scores.get('porcentaje', 0)
            prompt = f"Eres un psicologo organizacional experto en evaluaciones de personal para empresas mexicanas. Genera un perfil narrativo profesional para Recursos Humanos sobre el candidato {candidato} que aplica al puesto de {puesto}. Test Raven: percentil {pct}%. Escribe 2 parrafos: 1) Aptitud intelectual y aprendizaje, 2) Recomendacion segun el puesto. Tono profesional, objetivo, tercera persona."
        elif tipo == 'zavic':
            escalas = {'M': 'Moral', 'L': 'Legal', 'I': 'Indiferente', 'C': 'Corrupcion'}
            detalle = ', '.join([f"{escalas[k]}: {v}" for k, v in scores.items()])
            alerta = scores.get('C', 0) > scores.get('M', 0)
            alerta_txt = 'IMPORTANTE: El indice de Corrupcion supera al de Moral.' if alerta else ''
            prompt = f"Eres un psicologo organizacional experto en evaluaciones de personal para empresas mexicanas. Genera un perfil narrativo profesional para Recursos Humanos sobre el candidato {candidato} que aplica al puesto de {puesto}. Test Zavic: {detalle}. {alerta_txt} Escribe 2 parrafos: 1) Perfil de valores e integridad, 2) Compatibilidad con la cultura organizacional. Tono profesional, objetivo, tercera persona."
        else:
            return JsonResponse({'error': 'Instrumento no soportado'}, status=400)
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        payload = json.dumps({
            'model': 'claude-haiku-4-5-20251001',
            'max_tokens': 600,
            'messages': [{'role': 'user', 'content': prompt}]
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            },
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                texto = data["content"][0]["text"]
                result.perfil_narrativo = texto
                result.save()
                return JsonResponse({'perfil': texto})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ReporteUnificadoView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, candidate_id):
        userapp = getattr(request.user, "userapp", None)
        if userapp and not getattr(userapp, "psico_plan_key", ""):
            from django.http import HttpResponse
            return HttpResponse('<h2 style="font-family:sans-serif;text-align:center;margin-top:80px">&#128274; Reporte no disponible en modo demo.<br><a href="/stripe/planes/" style="color:#2563eb">Adquiere un plan para ver tus reportes</a></h2>', status=403)
        candidate = get_object_or_404(Candidate, id=candidate_id, user=request.user)
        sesiones = TestSession.objects.filter(
            candidate=candidate,
            status='completada'
        ).select_related('instrumento', 'result').order_by('fecha_completado')

        resultados = []
        for s in sesiones:
            try:
                result = s.result
                scores = result.scores
                tipo = s.instrumento.tipo
                perfil_narrativo = result.perfil_narrativo or ''
                data = {'session': s, 'instrumento': s.instrumento, 'scores': scores, 'tipo': tipo, 'perfil_narrativo': perfil_narrativo}
                if tipo == 'disc':
                    pct = {k: max(0, round((v / 28) * 100)) for k, v in scores.items()}
                    dominante = max(scores, key=scores.get)
                    segundo = sorted(scores, key=scores.get, reverse=True)[1]
                    perfiles = {
                        'D': {'nombre': 'Dominante', 'color': '#ea5455'},
                        'I': {'nombre': 'Influyente', 'color': '#ff9f43'},
                        'S': {'nombre': 'Estable', 'color': '#28c76f'},
                        'C': {'nombre': 'Cumplidor', 'color': '#7367f0'},
                    }
                    data['pct'] = pct
                    data['dominante'] = dominante
                    data['segundo'] = segundo
                    data['perfiles'] = perfiles
                    data['perfil_nombre'] = f"Perfil {dominante}-{segundo}: {perfiles[dominante]['nombre']} con tendencia {perfiles[segundo]['nombre']}"
                elif tipo == 'moss':
                    total = scores.get('total', 0)
                    pct = round((total / 90) * 100)
                    if pct >= 80:
                        nivel, color = 'Muy alto', '#28c76f'
                    elif pct >= 60:
                        nivel, color = 'Alto', '#7367f0'
                    elif pct >= 40:
                        nivel, color = 'Medio', '#ff9f43'
                    else:
                        nivel, color = 'Bajo', '#ea5455'
                    data['total'] = total
                    data['pct'] = pct
                    data['nivel'] = nivel
                    data['color'] = color
                elif tipo == 'raven':
                    pct = scores.get('porcentaje', 0)
                    if pct >= 85:
                        nivel, color = 'Muy Superior', '#28c76f'
                    elif pct >= 70:
                        nivel, color = 'Superior', '#7367f0'
                    elif pct >= 50:
                        nivel, color = 'Normal', '#ff9f43'
                    else:
                        nivel, color = 'Inferior', '#ea5455'
                    data['pct'] = pct
                    data['nivel'] = nivel
                    data['color'] = color
                elif tipo == 'zavic':
                    total_pts = sum(scores.values()) or 1
                    pct = {k: round((v / total_pts) * 100) for k, v in scores.items()}
                    escalas = {
                        'M': {'nombre': 'Moral', 'color': '#28c76f'},
                        'L': {'nombre': 'Legal', 'color': '#7367f0'},
                        'I': {'nombre': 'Indiferente', 'color': '#ff9f43'},
                        'C': {'nombre': 'Corrupcion', 'color': '#ea5455'},
                    }
                    data['pct'] = pct
                    data['escalas'] = escalas
                    data['alerta_corrupcion'] = scores.get('C', 0) > scores.get('M', 0)
                resultados.append(data)
            except Exception:
                pass

        ctx = {
            'candidate': candidate,
            'resultados': resultados,
            'name': request.user.userapp.name,
            'fecha': __import__('datetime').date.today(),
        }
        return render(request, 'psico_reporte.html', ctx)
