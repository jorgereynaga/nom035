from django.core.management.base import BaseCommand
from surveys.models import Workplace, RiskSurveyA, RiskSurveyB, EvaluationHistory


class Command(BaseCommand):
    help = (
        'Detecta y repara centros de trabajo cuya evaluacion actual ya avanzo '
        '(wk.evaluation > 1) pero a alguna evaluacion anterior con respuestas '
        'reales le falta el registro de EvaluationHistory -- esto pasaba con '
        'cuentas demo creadas antes del fix a cargar_datos_demo.py, que salteaba '
        'el flujo normal de "Finalizar aplicacion".'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--aplicar', action='store_true',
            help='Aplica los cambios. Sin esta bandera solo se muestra un dry-run.',
        )

    def handle(self, *args, **kwargs):
        aplicar = kwargs['aplicar']
        detectados = 0
        for wk in Workplace.objects.filter(evaluation__gt=1):
            historial_nums = set(wk.evaluation_history.values_list('numero_evaluacion', flat=True))
            employee_ids = list(wk.employees.values_list('id', flat=True))
            for numero in range(1, wk.evaluation):
                if numero in historial_nums:
                    continue
                if wk.survey_type() != 3:
                    tiene_respuestas = RiskSurveyA.objects.filter(evaluation=numero, employee_id__in=employee_ids).exists()
                else:
                    tiene_respuestas = RiskSurveyB.objects.filter(evaluation=numero, employee_id__in=employee_ids).exists()
                if not tiene_respuestas:
                    continue
                detectados += 1
                etiqueta = '[APLICANDO]' if aplicar else '[DRY-RUN]'
                self.stdout.write(f'{etiqueta} {wk.name} (id={wk.id}) -- falta historial de evaluacion {numero}')
                if aplicar:
                    EvaluationHistory.objects.create(workplace=wk, numero_evaluacion=numero, guia=wk.survey_type())
        if detectados == 0:
            self.stdout.write(self.style.SUCCESS('No se encontro ningun centro con este problema.'))
        else:
            accion = 'Reparados' if aplicar else 'Detectados (corre con --aplicar para corregir)'
            self.stdout.write(self.style.SUCCESS(f'{accion}: {detectados}'))
