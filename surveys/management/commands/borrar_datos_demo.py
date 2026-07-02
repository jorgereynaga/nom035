from django.core.management.base import BaseCommand
from surveys.models import Workplace, Employee, RiskSurveyA, RiskSurveyB, Candidate, WorkEnvironmentSurvey
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Borra datos demo de un usuario'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        user_id = options['user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuario {user_id} no encontrado'))
            return

        # Borrar workplaces demo y todo lo relacionado
        workplaces_demo = Workplace.objects.filter(user=user, es_demo=True)
        for wp in workplaces_demo:
            WorkEnvironmentSurvey.objects.filter(workplace=wp, es_demo=True).delete()
            employees_demo = Employee.objects.filter(workplace=wp, es_demo=True)
            for emp in employees_demo:
                RiskSurveyA.objects.filter(employee=emp, es_demo=True).delete()
                RiskSurveyB.objects.filter(employee=emp).delete()
            employees_demo.delete()
        workplaces_demo.delete()

        # Borrar candidatos demo
        Candidate.objects.filter(user=user, es_demo=True).delete()

        self.stdout.write(self.style.SUCCESS(f'Datos demo eliminados para usuario {user.username}'))
