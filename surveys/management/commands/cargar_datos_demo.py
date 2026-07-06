from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from surveys.models import Workplace, Employee, RiskSurveyA, RiskSurveyB, Candidate, WorkEnvironmentSurvey, PortafolioEvidencias
import random, string


def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


EMPLEADOS_DEMO = [
    {"name": "Ana García López", "gender": 2, "age": 3, "civil_state": 0, "study_level": 5,
     "ocupation": "Contadora", "department": "Administración", "charge_type": 2,
     "contract_type": 0, "employee_type": 0, "shift_type": 0, "shift_rotation": 1, "time_in_charge": 3, "exp": 5},
    {"name": "Carlos Martínez Ruiz", "gender": 1, "age": 4, "civil_state": 2, "study_level": 3,
     "ocupation": "Operador", "department": "Producción", "charge_type": 0,
     "contract_type": 0, "employee_type": 0, "shift_type": 1, "shift_rotation": 0, "time_in_charge": 2, "exp": 3},
    {"name": "María Rodríguez Torres", "gender": 2, "age": 2, "civil_state": 2, "study_level": 4,
     "ocupation": "Supervisora", "department": "Producción", "charge_type": 1,
     "contract_type": 0, "employee_type": 0, "shift_type": 0, "shift_rotation": 0, "time_in_charge": 4, "exp": 6},
    {"name": "Roberto Hernández Silva", "gender": 1, "age": 5, "civil_state": 0, "study_level": 2,
     "ocupation": "Almacenista", "department": "Logística", "charge_type": 0,
     "contract_type": 0, "employee_type": 0, "shift_type": 0, "shift_rotation": 1, "time_in_charge": 1, "exp": 2},
    {"name": "Laura Sánchez Jiménez", "gender": 2, "age": 3, "civil_state": 4, "study_level": 5,
     "ocupation": "Coordinadora RH", "department": "Recursos Humanos", "charge_type": 1,
     "contract_type": 0, "employee_type": 0, "shift_type": 0, "shift_rotation": 0, "time_in_charge": 3, "exp": 4},
    {"name": "Jorge Pérez Mendoza", "gender": 1, "age": 6, "civil_state": 0, "study_level": 5,
     "ocupation": "Gerente", "department": "Dirección", "charge_type": 3,
     "contract_type": 0, "employee_type": 0, "shift_type": 0, "shift_rotation": 0, "time_in_charge": 5, "exp": 10},
]

SURVEY_A_BAJO = {
    "r2_p1": 4, "r2_p2": 4, "r2_p3": 4, "r2_p4": 4, "r2_p5": 4, "r2_p6": 3, "r2_p7": 2, "r2_p8": 3,
    "r2_p9": 2, "r2_p10": 3, "r2_p11": 3, "r2_p12": 4, "r2_p13": 4, "r2_p14": 3, "r2_p15": 4,
    "r2_p16": 4, "r2_p17": 3, "r2_p18": 0, "r2_p19": 1, "r2_p20": 0, "r2_p21": 0, "r2_p22": 1,
    "r2_p23": 0, "r2_p24": 0, "r2_p25": 0, "r2_p26": 0, "r2_p27": 0, "r2_p28": 0, "r2_p29": 0,
    "r2_p30": 0, "r2_p31": 0, "r2_p32": 0, "r2_p33": 0, "r2_p34": 4, "r2_p35": 4, "r2_p36": 4,
    "r2_p37": 4, "r2_p38": 4, "r2_p39": 4, "r2_p40": 4, "r2_p_a": 1, "r2_p41": None, "r2_p42": None,
    "r2_p43": None, "r2_p_b": 1, "r2_p44": None, "r2_p45": None, "r2_p46": None,
}

SURVEY_A_MEDIO = {
    "r2_p1": 2, "r2_p2": 2, "r2_p3": 3, "r2_p4": 2, "r2_p5": 2, "r2_p6": 1, "r2_p7": 1, "r2_p8": 2,
    "r2_p9": 1, "r2_p10": 1, "r2_p11": 2, "r2_p12": 2, "r2_p13": 2, "r2_p14": 1, "r2_p15": 2,
    "r2_p16": 2, "r2_p17": 2, "r2_p18": 1, "r2_p19": 2, "r2_p20": 1, "r2_p21": 2, "r2_p22": 2,
    "r2_p23": 2, "r2_p24": 2, "r2_p25": 2, "r2_p26": 2, "r2_p27": 2, "r2_p28": 2, "r2_p29": 2,
    "r2_p30": 2, "r2_p31": 2, "r2_p32": 2, "r2_p33": 2, "r2_p34": 2, "r2_p35": 3, "r2_p36": 3,
    "r2_p37": 3, "r2_p38": 3, "r2_p39": 3, "r2_p40": 3, "r2_p_a": 1, "r2_p41": None, "r2_p42": None,
    "r2_p43": None, "r2_p_b": 1, "r2_p44": None, "r2_p45": None, "r2_p46": None,
}

SURVEY_A_ALTO = {
    "r2_p1": 0, "r2_p2": 0, "r2_p3": 1, "r2_p4": 0, "r2_p5": 0, "r2_p6": 0, "r2_p7": 0, "r2_p8": 0,
    "r2_p9": 0, "r2_p10": 0, "r2_p11": 0, "r2_p12": 0, "r2_p13": 0, "r2_p14": 0, "r2_p15": 0,
    "r2_p16": 0, "r2_p17": 0, "r2_p18": 4, "r2_p19": 4, "r2_p20": 4, "r2_p21": 4, "r2_p22": 4,
    "r2_p23": 4, "r2_p24": 4, "r2_p25": 4, "r2_p26": 4, "r2_p27": 4, "r2_p28": 4, "r2_p29": 4,
    "r2_p30": 4, "r2_p31": 4, "r2_p32": 4, "r2_p33": 4, "r2_p34": 0, "r2_p35": 0, "r2_p36": 0,
    "r2_p37": 0, "r2_p38": 0, "r2_p39": 0, "r2_p40": 0, "r2_p_a": 1, "r2_p41": None, "r2_p42": None,
    "r2_p43": None, "r2_p_b": 1, "r2_p44": None, "r2_p45": None, "r2_p46": None,
}

PERFILES_A = [SURVEY_A_BAJO, SURVEY_A_BAJO, SURVEY_A_MEDIO, SURVEY_A_MEDIO, SURVEY_A_ALTO, SURVEY_A_BAJO]

SURVEY_B_BAJO = {
    "r3_p1": 0, "r3_p2": 4, "r3_p3": 4, "r3_p4": 0, "r3_p5": 4, "r3_p6": 4, "r3_p7": 4, "r3_p8": 3,
    "r3_p9": 2, "r3_p10": 3, "r3_p11": 3, "r3_p12": 2, "r3_p13": 3, "r3_p14": 3, "r3_p15": 4,
    "r3_p16": 4, "r3_p17": 4, "r3_p18": 4, "r3_p19": 4, "r3_p20": 4, "r3_p21": 3, "r3_p22": 4,
    "r3_p23": 0, "r3_p24": 1, "r3_p25": 0, "r3_p26": 0, "r3_p27": 0, "r3_p28": 1, "r3_p29": 4,
    "r3_p30": 0, "r3_p31": 0, "r3_p32": 0, "r3_p33": 0, "r3_p34": 0, "r3_p35": 0, "r3_p36": 0,
    "r3_p37": 0, "r3_p38": 0, "r3_p39": 0, "r3_p40": 0, "r3_p41": 0, "r3_p42": 0, "r3_p43": 0,
    "r3_p44": 0, "r3_p45": 0, "r3_p46": 0, "r3_p47": 0, "r3_p48": 0, "r3_p49": 0, "r3_p50": 0,
    "r3_p51": 0, "r3_p52": 0, "r3_p53": 0, "r3_p54": 4, "r3_p55": 0, "r3_p56": 0, "r3_p57": 0,
    "r3_p58": 4, "r3_p59": 4, "r3_p60": 4, "r3_p61": 4, "r3_p62": 4, "r3_p63": 4, "r3_p64": 4,
    "r3_a": 1, "r3_p65": None, "r3_p66": None, "r3_p67": None, "r3_p68": None,
    "r3_b": 1, "r3_p69": None, "r3_p70": None, "r3_p71": None, "r3_p72": None,
}

SURVEY_B_MEDIO = {
    "r3_p1": 2, "r3_p2": 2, "r3_p3": 2, "r3_p4": 2, "r3_p5": 2, "r3_p6": 2, "r3_p7": 2, "r3_p8": 2,
    "r3_p9": 2, "r3_p10": 2, "r3_p11": 2, "r3_p12": 2, "r3_p13": 2, "r3_p14": 2, "r3_p15": 2,
    "r3_p16": 2, "r3_p17": 2, "r3_p18": 2, "r3_p19": 2, "r3_p20": 2, "r3_p21": 2, "r3_p22": 2,
    "r3_p23": 2, "r3_p24": 2, "r3_p25": 2, "r3_p26": 2, "r3_p27": 2, "r3_p28": 2, "r3_p29": 2,
    "r3_p30": 2, "r3_p31": 2, "r3_p32": 2, "r3_p33": 2, "r3_p34": 2, "r3_p35": 2, "r3_p36": 2,
    "r3_p37": 2, "r3_p38": 2, "r3_p39": 2, "r3_p40": 2, "r3_p41": 2, "r3_p42": 2, "r3_p43": 2,
    "r3_p44": 2, "r3_p45": 2, "r3_p46": 2, "r3_p47": 2, "r3_p48": 2, "r3_p49": 2, "r3_p50": 2,
    "r3_p51": 2, "r3_p52": 2, "r3_p53": 2, "r3_p54": 2, "r3_p55": 2, "r3_p56": 2, "r3_p57": 2,
    "r3_p58": 2, "r3_p59": 3, "r3_p60": 3, "r3_p61": 3, "r3_p62": 3, "r3_p63": 3, "r3_p64": 3,
    "r3_a": 1, "r3_p65": None, "r3_p66": None, "r3_p67": None, "r3_p68": None,
    "r3_b": 1, "r3_p69": None, "r3_p70": None, "r3_p71": None, "r3_p72": None,
}

SURVEY_B_ALTO = {
    "r3_p1": 4, "r3_p2": 0, "r3_p3": 0, "r3_p4": 4, "r3_p5": 0, "r3_p6": 0, "r3_p7": 0, "r3_p8": 0,
    "r3_p9": 0, "r3_p10": 0, "r3_p11": 0, "r3_p12": 0, "r3_p13": 0, "r3_p14": 0, "r3_p15": 0,
    "r3_p16": 0, "r3_p17": 0, "r3_p18": 0, "r3_p19": 0, "r3_p20": 0, "r3_p21": 0, "r3_p22": 0,
    "r3_p23": 4, "r3_p24": 4, "r3_p25": 4, "r3_p26": 4, "r3_p27": 4, "r3_p28": 4, "r3_p29": 0,
    "r3_p30": 4, "r3_p31": 4, "r3_p32": 4, "r3_p33": 4, "r3_p34": 4, "r3_p35": 4, "r3_p36": 4,
    "r3_p37": 4, "r3_p38": 4, "r3_p39": 4, "r3_p40": 4, "r3_p41": 4, "r3_p42": 4, "r3_p43": 4,
    "r3_p44": 4, "r3_p45": 4, "r3_p46": 4, "r3_p47": 4, "r3_p48": 4, "r3_p49": 4, "r3_p50": 4,
    "r3_p51": 4, "r3_p52": 4, "r3_p53": 4, "r3_p54": 0, "r3_p55": 4, "r3_p56": 4, "r3_p57": 4,
    "r3_p58": 0, "r3_p59": 0, "r3_p60": 0, "r3_p61": 0, "r3_p62": 0, "r3_p63": 0, "r3_p64": 0,
    "r3_a": 1, "r3_p65": None, "r3_p66": None, "r3_p67": None, "r3_p68": None,
    "r3_b": 1, "r3_p69": None, "r3_p70": None, "r3_p71": None, "r3_p72": None,
}

PERFILES_B = [SURVEY_B_BAJO, SURVEY_B_BAJO, SURVEY_B_MEDIO, SURVEY_B_MEDIO, SURVEY_B_ALTO, SURVEY_B_BAJO]


class Command(BaseCommand):
    help = 'Carga datos demo para nuevos usuarios'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **kwargs):
        user_id = kwargs['user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuario {user_id} no encontrado'))
            return

        if user.workplaces.filter(es_demo=True).exists():
            self.stdout.write(self.style.WARNING('Ya tiene datos demo'))
            return

        wp = Workplace.objects.create(
            user=user,
            name='Empresa Demo S.A. de C.V.',
            main_activity='Manufactura y distribución de productos',
            objective='Producción y comercialización de bienes',
            other_activities='Distribución, logística y servicio al cliente',
            address='Av. Industria 123, Col. Centro',
            address_locality='Guadalajara',
            address_state='Jalisco',
            address_postal_code='44100',
            employee_num=6,
            paid=False,
            evaluation=2,
            access_code=gen_code(),
            es_demo=True,
        )
        self.stdout.write(f'Workplace demo creado: {wp.name}')
        PortafolioEvidencias.objects.create(
            workplace=wp,
            periodo_evaluacion='2026',
            responsable_nombre='Ana García López',
            responsable_puesto='Coordinadora de Recursos Humanos',
            representante_legal_nombre='Roberto Hernández Castillo',
            representante_legal_cargo='Director General',
            canal_quejas='Buzón físico en recepción y correo electrónico',
            responsable_quejas='Ana García López',
            correo_quejas='rh@empresademo.com',
            tiempo_respuesta_quejas='5 días hábiles',
            periodicidad_revision='Anual',
        )
        self.stdout.write('Portafolio de Evidencias demo creado')

        for i, emp_data in enumerate(EMPLEADOS_DEMO):
            emp = Employee.objects.create(
                workplace=wp,
                name=emp_data['name'],
                gender=emp_data['gender'],
                age=emp_data['age'],
                civil_state=emp_data['civil_state'],
                study_level=emp_data['study_level'],
                ocupation=emp_data['ocupation'],
                department=emp_data['department'],
                charge_type=emp_data['charge_type'],
                contract_type=emp_data.get('contract_type', 0),
                employee_type=emp_data.get('employee_type', 0),
                shift_type=emp_data.get('shift_type', 0),
                shift_rotation=emp_data.get('shift_rotation', 1),
                time_in_charge=emp_data['time_in_charge'],
                exp=emp_data['exp'],
                es_demo=True,
            )
            RiskSurveyA.objects.create(employee=emp, evaluation=1, es_demo=True, **PERFILES_A[i])
            RiskSurveyB.objects.create(employee=emp, evaluation=1, **PERFILES_B[i])
            self.stdout.write(f'  Empleado demo: {emp.name}')

        candidatos_demo = [
            {'nombre': 'Pedro Alvarado Vega', 'email': 'pedro.demo@ejemplo.com', 'puesto': 'Gerente de Ventas'},
            {'nombre': 'Sofia Ramirez Cruz', 'email': 'sofia.demo@ejemplo.com', 'puesto': 'Analista Financiero'},
        ]
        for cand_data in candidatos_demo:
            cand = Candidate.objects.create(
                user=user,
                nombre=cand_data['nombre'],
                email=cand_data['email'],
                puesto=cand_data['puesto'],
                tipo='externo',
                es_demo=True,
            )
            self.stdout.write(f'  Candidato demo: {cand.nombre}')


        # Datos demo clima laboral
        departamentos = ['Administracion', 'Produccion', 'Direccion', 'Logistica', 'Recursos Humanos']
        import random
        perfiles_clima = [
            [4,4,5,4,5, 4,3,4,3,4, 5,4,4,5,4, 3,3,4,4,5, 4,5,4,4,4, 4,4,5,4,4, 3,4,4,5,4, 5,4,4,5,5],
            [3,3,3,2,4, 3,2,3,2,3, 3,3,3,3,3, 2,2,3,3,3, 3,3,3,3,3, 2,2,3,2,2, 2,3,2,3,3, 3,3,3,3,3],
            [5,5,4,5,5, 5,4,5,4,5, 4,5,5,4,5, 4,4,5,5,5, 5,4,5,5,5, 4,5,4,5,4, 4,5,5,4,5, 5,5,5,4,5],
            [2,2,2,1,3, 2,2,2,1,2, 2,2,2,2,2, 1,1,2,2,2, 2,2,2,2,2, 1,1,2,1,1, 1,2,1,2,2, 2,2,2,2,2],
            [4,3,4,4,4, 3,3,4,3,3, 4,4,3,4,4, 3,3,4,3,4, 4,3,4,4,3, 3,3,4,3,3, 3,3,3,4,3, 4,4,3,4,4],
            [5,4,5,5,5, 4,4,5,4,4, 5,4,5,4,5, 4,4,5,4,5, 5,4,5,5,4, 4,4,5,4,4, 4,4,4,5,4, 5,5,4,5,5],
            [3,2,3,3,3, 2,2,3,2,2, 3,3,2,3,3, 2,2,3,2,3, 3,2,3,3,2, 2,2,3,2,2, 2,2,2,3,2, 3,3,2,3,3],
            [4,4,4,3,4, 4,3,4,3,3, 4,4,4,4,4, 3,3,4,3,4, 4,4,4,4,3, 3,3,4,3,3, 3,4,3,4,3, 4,4,3,4,4],
        ]
        depts_asignados = ['Administracion','Produccion','Produccion','Logistica','Recursos Humanos','Direccion','Administracion','Produccion']
        for idx, perfil in enumerate(perfiles_clima):
            data = {'workplace': wp, 'department': depts_asignados[idx], 'es_demo': True}
            for i, val in enumerate(perfil, 1):
                data[f'cl_p{i}'] = val
            WorkEnvironmentSurvey.objects.create(**data)
        self.stdout.write('  Datos demo clima laboral cargados')

        # Asignar evaluaciones psicometricas demo
        from surveys.models import PsychoInstrument, TestSession
        import uuid
        from django.utils import timezone
        from datetime import timedelta
        candidatos = list(Candidate.objects.filter(user=user, es_demo=True))
        instrumentos = list(PsychoInstrument.objects.filter(activo=True)[:2])
        for i, cand in enumerate(candidatos):
            if i < len(instrumentos):
                instrumento = instrumentos[i]
                token = uuid.uuid4().hex
                expira_en = timezone.now() + timedelta(days=365)
                TestSession.objects.create(
                    candidate=cand,
                    instrumento=instrumento,
                    token=token,
                    expira_en=expira_en,
                )
                self.stdout.write(f'  Sesion psicometrica demo: {cand.nombre} -> {instrumento.nombre}')
        self.stdout.write(self.style.SUCCESS('Datos demo cargados correctamente'))