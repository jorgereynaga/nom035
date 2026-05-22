from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from datetime import timedelta

def validate_file_extension(value):
	ext = value.name.split('.')
	valid_extensions = ['jpg','png']
	if not ext[len(ext)-1] in valid_extensions:
		raise ValidationError(f'Solo se admiten archivos JPG y PNG! la extension de tu archivo es {ext}')
	if value.size>2621440:
		raise ValidationError(u'Archivo muy pesado. Limite de 2.5Mb')

def user_directory_path(instance, filename):
	return 'logos/{0}/{1}'.format(instance.user.id, filename)
def result_directory_path(instance, filename):
	return 'results/{0}/{1}/{2}'.format(instance.workplace.id,instance.evaluation,filename)
class Userapp(models.Model):
	#empresa
	user=models.OneToOneField(User,related_name="userapp",on_delete=models.CASCADE)
	name=models.CharField(u'Nombre, Denominación, Razón social', max_length=150)
	phone=models.CharField(u'Teléfono', max_length=12)
	client_id=models.CharField(u'Cliente conekta', max_length=30, blank=True, null=True)
	validated_email=models.BooleanField(u'Correo Validado',default=False)
	workplaces_available=models.IntegerField(u'Centros pagados A', default=0)
	workplaces_availableB=models.IntegerField(u'Centros pagados B', default=0)
	workplaces_availableC=models.IntegerField(u'Centros pagados C', default=0)
	workplaces_availableC = models.IntegerField(u'Centros pagados C', default=0)

	# Stripe
	stripe_customer_id = models.CharField(u'Stripe Customer ID', max_length=100, blank=True, null=True)
	stripe_subscription_id = models.CharField(u'Stripe Subscription ID', max_length=100, blank=True, null=True)
	stripe_plan_key = models.CharField(u'Plan activo', max_length=100, blank=True, default='')
	psico_evaluaciones_disponibles = models.IntegerField(u'Evaluaciones psicométricas disponibles', default=0)
	#cus_2fkJPFjQKABcmiZWz
	#email
	#username=correo
	record_create=models.DateTimeField(auto_now_add=True)
	record_update=models.DateTimeField(auto_now=True)
	image=models.FileField(u'Logo de la empresa', upload_to=user_directory_path,validators=[validate_file_extension], blank=True, null=True)


class Workplace(models.Model):
	user=models.ForeignKey(User,related_name="workplaces",on_delete=models.CASCADE)
	name=models.CharField(u'Nombre, Denominación, Razón social', max_length=150)
	main_activity=models.CharField(u'Actividad principal', max_length=300)
	objective=models.CharField(u'Objetivo de la empresa', max_length=300)
	other_activities=models.CharField(u'Principales actividades', max_length=300)
	address=models.CharField(u'Domicilio', max_length=300)
	address_locality=models.CharField(u'Localidad', max_length=300)
	address_state= models.CharField(u'Estado', max_length=300)
	address_postal_code= models.CharField(u'Código postal', max_length=300)
	# employee=models.ForeignKey(Employee,verbose_name='Empleado', on_delete=models.PROTECT)
	# choices=((0,'1 a 15 empleados'),(2,'16 a 50 empleados'),(3,'Más de 50 empleados'))
	evaluation=models.IntegerField('Número de evaluación',default=1)
	paid=models.BooleanField('evaluación pagada')
	employee_num = models.IntegerField(u'Cantidad de empleados')
	access_code = models.CharField(u'Codigo de acceso',max_length=255,unique=True)
	record_create=models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return f"{self.name}"
	def survey_type(self):
		if self.employee_num>0 and self.employee_num<=15:
			return 1
		elif self.employee_num>15 and self.employee_num<=50:
			return 2
		elif self.employee_num>50:
			return 3
		else:
			return 0

class ResultFiles(models.Model):
	workplace=models.ForeignKey(Workplace,related_name="result_files",verbose_name='Centro de trabajo', on_delete=models.PROTECT)
	evaluation=models.IntegerField('Número de evaluación')
	image=models.FileField(u'Archivo', upload_to=result_directory_path, blank=True, null=True)
	record_create = models.DateTimeField(u"Fecha de creación",auto_now_add=True)
	result_type=models.IntegerField(u'Tipo de resultado',choices=enumerate(["Informe de resultados ejecutivo","Informe de resultados detallado",
		"Resultados del Instrumento para Identificar los Factores de Riesgo Psicosocial","Gantt de Actividades",
		"Lista de Verificación de Evidencias de la NOM35","Propuesta de Política de Prevención de Riesgos Psicosociales"]))
	def __str__(self):
		return f"{self.workplace.name}"
class Result(models.Model):
	workplace=models.ForeignKey(Workplace,related_name="results",verbose_name='Centro de trabajo', on_delete=models.PROTECT)
	nom035method= models.CharField(u'Método utilizado para aplicar la norma 035', max_length=300)
	recomendations= models.CharField(u'Recomendaciones', max_length=300)
	actions= models.CharField(u'Accciones de intervención', max_length=300)
	conclusion= models.CharField(u'Conclusiones', max_length=300)
	record_create = models.DateTimeField(u"Fecha de creación",auto_now_add=True)
	evaluation=models.IntegerField('Número de evaluación')

	def __str__(self):
		return f"{self.workplace.name}"
	def expiration_date(self):
		present=self.record_create
		future=self.record_create-timedelta(days=7)
		date=future-present
		return (date.days,future)

class Employee(models.Model):
	"""Formulario de empleados"""
	workplace=models.ForeignKey(Workplace,related_name="employees",verbose_name='Centro de trabajo', on_delete=models.PROTECT)
	name=models.CharField(u'Nombre y Apellidos', max_length=150)
	gender= models.IntegerField(u'Sexo',choices=((1,'Hombre'),(2,'Mujer')))
	choices_age=((0,'15-19'),(1,'20-24'),(2,'25-29'),(3,'30-34'),(4,'35-39'),(5,'40-44'),
		(6,'45-49'),(7,'50-54'),(8,'55-59'),(9,'60-64'),(10,'65-69'),(11,'70 o más'))
	age=models.IntegerField(u'Edad en años',choices=choices_age)
	choices=((0,'Casado'),(1,'Divorciado'),(2,'Soltero'),(3,'Viudo'),(4,'Unión Libre'))
	civil_state=models.IntegerField(u'Estado civil',choices=choices)
	choices_level=((0,'Sin formación'),(1,'Primaria'),(2,'Secundaria'),(3,'Preparatoria o Bachillerato'),
		(4,'Técnico superior'),(5,'Licenciatura'),(6,'Maestría'),(7,'Doctorado'))
	study_level=models.IntegerField(u'Nivel de estudios',choices=choices_level)
	ocupation= models.CharField(u'Ocupación, Profesión o Puesto', max_length=50)
	department= models.CharField(u'Departamento, Sección o Área', max_length=50)
	choices_level=((0,'Operativo'),(1,'Supervisor'),(2,'Profesional o Técnico'),(3,'Gerente'))
	charge_type= models.IntegerField(u'Tipo de puesto',choices=choices_level)
	choices_contract=((0,'Por obra o proyecto'),(1,'Por tiempo determinado (Temporal)'),(2,'Por tiempo indeterminado'),(3,'Por Honorarios'))
	contract_type= models.IntegerField(u'Tipo de contratación',choices=choices_contract)
	choices_employee_type=((0,'Sindicalizado'),(1,'Confianza'),(2,'Ninguno'))
	employee_type= models.IntegerField(u'Tipo de personal',choices=choices_employee_type)
	choices_shift_type=((0,'Fijo Nocturno (Entre las 20:00 y 06:00 horas)'),(1,'Fijo Diurno (Entre las 06:00 y 20:00 horas)'),
		(2,'Fijo Mixto (Combinación del nocturno y diurno)'))
	shift_type= models.IntegerField(u'Tipo de jornada de trabajo',choices=choices_shift_type)
	shift_rotation= models.IntegerField(u'Realiza rotación de turnos',choices=((0,'Sí'),(1,'No')))
	#Experiencia (Años) como titulo
	choices_time_in_charge=((0,'Menos de 6 meses'),(1,'Entre 6 meses y un año'),(2,'Entre 1 a 4 años'),(3,'Entre 5 a 9 años'),
		(4,'Entre 10 a 14 años'),(5,'Entre 15 a 19 años'),(6,'Entre 20 a 24 años'),(7,'Entre 25 años o Más'))
	time_in_charge= models.IntegerField(u'Tiempo en el puesto actual',choices=choices_time_in_charge)
	choices_exp=((0,'Menos de 6 meses'),(1,'Entre 6 meses y un año'),(2,'Entre 1 a 4 años'),(3,'Entre 5 a 9 años'),
		(4,'Entre 10 a 14 años'),(5,'Entre 15 a 19 años'),(6,'Entre 20 a 24 años'),(7,'Entre 25 años o Más'))
	exp= models.IntegerField(u'Tiempo de experiencia laboral',choices=choices_exp)
	record_create = models.DateTimeField(auto_now_add=True)
	record_update = models.DateTimeField(auto_now=True)
	def __str__(self):
		return f"{self.name}"
	def get_status(self, text="default",evaluation=None):
		status=f"danger'>No contestada"
		status_txt=f"No contestada"
		if evaluation==None:
			evaluation=self.workplace.evaluation
		if hasattr(self,'survey3'):
			if self.survey3.filter(evaluation=evaluation).exists():
				status="warning'>Incompleta"
				status_txt="Incompleta"
		if hasattr(self,'surveyA'):
			if self.surveyA.filter(evaluation=evaluation).exists():
				status="success'>Contestada"
				status_txt="Contestada"
		if hasattr(self,'surveyB'):
			if self.surveyB.filter(evaluation=evaluation).exists():
				status="success'>Contestada"
				status_txt="Contestada"
		if text=="default":
			return status
		else:
			return status_txt
	def get_code(self):
		code=f"{self.id}0|0{hex(int(self.record_create.timestamp()))[2:]}"
		return code
	class Meta:
		verbose_name='Datos del Empleado'
		verbose_name_plural='Datos del Empleado'

class RiskSurveyA(models.Model):
	"""Identificacion de analisis de los factores de riesgo psicosocial"""
	employee=models.ForeignKey(Employee,related_name='surveyA', verbose_name='Empleado', on_delete=models.PROTECT)
	choices=((0,'Siempre'),(1,'Casi siempre'),(2,'Algunas veces'),(3,'Casi nunca'),(4,'Nunca'))
	not_choices=((4,'Siempre'),(3,'Casi siempre'),(2,'Algunas veces'),(1,'Casi nunca'),(0,'Nunca'))
	r2_p1= models.IntegerField(u'Mi trabajo me exige hacer mucho esfuerzo físico',choices=not_choices)
	r2_p2= models.IntegerField(u'Me preocupa sufrir un accidente en mi trabajo',choices=not_choices)
	r2_p3= models.IntegerField(u'Considero que las actividades que realizo son peligrosas',choices=not_choices)
	r2_p4= models.IntegerField(u'Por la cantidad de trabajo que tengo debo quedarme tiempo adicional a mi turno',choices=not_choices)
	r2_p5= models.IntegerField(u'Por la cantidad de trabajo que tengo debo trabajar sin parar',choices=not_choices)
	r2_p6= models.IntegerField(u'Considero que es necesario mantener un ritmo de trabajo acelerado',choices=not_choices)
	r2_p7= models.IntegerField(u'Mi trabajo exige que esté muy concentrado',choices=not_choices)
	r2_p8= models.IntegerField(u'Mi trabajo requiere que memorice mucha información',choices=not_choices)
	r2_p9= models.IntegerField(u'Mi trabajo exige que atienda varios asuntos al mismo tiempo',choices=not_choices)
	r2_p10= models.IntegerField(u'En mi trabajo soy responsable de cosas de mucho valor',choices=not_choices)
	r2_p11= models.IntegerField(u'Respondo ante mi jefe por los resultados de toda mi área de trabajo',choices=not_choices)
	r2_p12= models.IntegerField(u'En mi trabajo me dan órdenes contradictorias',choices=not_choices)
	r2_p13= models.IntegerField(u'Considero que en mi trabajo me piden hacer cosas innecesarias',choices=not_choices)
	r2_p14= models.IntegerField(u'Trabajo horas extras más de tres veces a la semana',choices=not_choices)
	r2_p15= models.IntegerField(u'Mi trabajo me exige laborar en días de descanso, festivos o fines de semana',choices=not_choices)
	r2_p16= models.IntegerField(u'Considero que el tiempo en el trabajo es mucho y perjudica mis actividades familiares o personales',choices=not_choices)
	r2_p17= models.IntegerField(u'Pienso en las actividades familiares o personales cuando estoy en mi trabajo',choices=not_choices)
	r2_p18= models.IntegerField(u'Mi trabajo permite que desarrolle nuevas habilidades',choices=choices)
	r2_p19= models.IntegerField(u'En mi trabajo puedo aspirar a un mejor puesto',choices=choices)
	r2_p20= models.IntegerField(u'Durante mi jornada de trabajo puedo tomar pausas cuando las necesito',choices=choices)
	r2_p21= models.IntegerField(u'Puedo decidir la velocidad a la que realizo mis actividades en mi trabajo',choices=choices)
	r2_p22= models.IntegerField(u'Puedo cambiar el orden de las actividades que realizo en mi trabajo',choices=choices)
	r2_p23= models.IntegerField(u'Me informan con claridad cuáles son mis funciones',choices=choices)
	r2_p24= models.IntegerField(u'Me explican claramente los resultados que debo obtener en mi trabajo',choices=choices)
	r2_p25= models.IntegerField(u'Me informan con quién puedo resolver problemas o asuntos de trabajo',choices=choices)
	r2_p26= models.IntegerField(u'Me permiten asistir a capacitaciones relacionadas con mi trabajo',choices=choices)
	r2_p27= models.IntegerField(u'Recibo capacitación útil para hacer mi trabajo',choices=choices)
	r2_p28= models.IntegerField(u'Mi jefe tiene en cuenta mis puntos de vista y opiniones',choices=choices)
	r2_p29= models.IntegerField(u'Mi jefe ayuda a solucionar los problemas que se presentan en el trabajo',choices=choices)
	r2_p30= models.IntegerField(u'Puedo confiar en mis compañeros de trabajo',choices=choices)
	r2_p31= models.IntegerField(u'Cuando tenemos que realizar trabajo de equipo los compañeros colaboran',choices=choices)
	r2_p32= models.IntegerField(u'Mis compañeros de trabajo me ayudan cuando tengo dificultades',choices=choices)
	r2_p33= models.IntegerField(u'En mi trabajo puedo expresarme libremente sin interrupciones',choices=choices)
	r2_p34= models.IntegerField(u'Recibo críticas constantes a mi persona y/o trabajo',choices=not_choices)
	r2_p35= models.IntegerField(u'Recibo burlas, calumnias, difamaciones, humillaciones o ridiculizaciones',choices=not_choices)
	r2_p36= models.IntegerField(u'Se ignora mi presencia o se me excluye de las reuniones de trabajo y en la toma de decisiones',choices=not_choices)
	r2_p37= models.IntegerField(u'Se manipulan las situaciones de trabajo para hacerme parecer un mal trabajador',choices=not_choices)
	r2_p38= models.IntegerField(u'Se ignoran mis éxitos laborales y se atribuyen a otros trabajadores',choices=not_choices)
	r2_p39= models.IntegerField(u'Me bloquean o impiden las oportunidades que tengo para obtener ascenso o mejora en mi trabajo',choices=not_choices)
	r2_p40= models.IntegerField(u'He presenciado actos de violencia en mi centro de trabajo',choices=not_choices)
	r2_p_a= models.IntegerField(u'En mi trabajo debo brindar servicio a clientes o usuarios:',choices=((0,'Sí'),(1,'No')))
	r2_p41= models.IntegerField(u'Atiendo clientes o usuarios muy enojados',choices=not_choices, blank=True, null=True)
	r2_p42= models.IntegerField(u'Mi trabajo me exige atender personas muy necesitadas de ayuda o enfermas',choices=not_choices, blank=True, null=True)
	r2_p43= models.IntegerField(u'Para hacer mi trabajo debo demostrar sentimientos distintos a los míos',choices=not_choices, blank=True, null=True)
	r2_p_b= models.IntegerField(u'Soy jefe de otros trabajadores:',choices=((0,'Sí'),(1,'No')))
	r2_p44= models.IntegerField(u'Comunican tarde los asuntos de trabajo',choices=not_choices, blank=True, null=True)
	r2_p45= models.IntegerField(u'Dificultan el logro de los resultados del trabajo',choices=not_choices, blank=True, null=True)
	r2_p46= models.IntegerField(u'Ignoran las sugerencias para mejorar su trabajo',choices=not_choices, blank=True, null=True)
	record_create = models.DateTimeField(auto_now_add=True)
	evaluation=models.IntegerField('Número de evaluación')
	def __str__(self):
		return f"{self.employee.name}"
	class Meta:
		verbose_name='Identificacion de analisis de los factores de riesgo psicosocial'
		verbose_name_plural='Identificacion de analisis de los factores de riesgo psicosocial'

class TraumaSurvey(models.Model):
	"""Identificacion de trabajadores sujetos a traumas severos"""
	employee=models.ForeignKey(Employee,related_name='survey3', verbose_name='Empleado', on_delete=models.PROTECT)
	# choices=((0,'Siempre'),(1,'Casi siempre'),(2,'Algunas veces'),(3,'Casi nunca'),(4,'Nunca'))
	r1_p1= models.IntegerField(u"""¿Ha presenciado o sufrido alguna vez, durante o con motivo del trabajo un acontecimiento como los siguientes?: 
		Accidente que tenga como consecuencia la muerte, la pérdida de un miembro o una lesión grave, Asaltos, 
		Actos violentos que derivaron en lesiones graves, Secuestro, Amenazas,
		Cualquier otro que ponga en riesgo su vida o salud, y/o la de otras personas""",choices=((0,'Sí'),(1,'No')))
	r1_p2= models.IntegerField(u'¿Ha tenido recuerdos recurrentes sobre el acontecimiento que le provocan malestares?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p3= models.IntegerField(u'¿Ha tenido sueños de carácter recurrente sobre el acontecimiento, que le producen malestar?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p4= models.IntegerField(u'¿Se ha esforzado por evitar todo tipo de sentimientos, conversaciones o situaciones que le puedan recordar el acontecimiento?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p5= models.IntegerField(u'¿Se ha esforzado por evitar todo tipo de actividades, lugares o personas que motivan recuerdos del acontecimiento?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p6= models.IntegerField(u'¿Ha tenido dificultad para recordar alguna parte importante del evento?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p7= models.IntegerField(u'¿Ha disminuido su interés en sus actividades cotidianas?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p8= models.IntegerField(u'¿Se ha sentido usted alejado o distante de los demás?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p9= models.IntegerField(u'¿Ha notado que tiene dificultad para expresar sus sentimientos?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p10= models.IntegerField(u'¿Ha tenido la impresión de que su vida se va a acortar, que va a morir antes que otras personas o que tiene un futuro limitado?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p11= models.IntegerField(u'¿Ha tenido usted dificultades para dormir?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p12= models.IntegerField(u'¿Ha estado particularmente irritable o le han dado arranques de coraje?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p13= models.IntegerField(u'¿Ha tenido dificultad para concentrarse?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p14= models.IntegerField(u'¿Ha estado nervioso o constantemente en alerta?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	r1_p15= models.IntegerField(u'¿Se ha sobresaltado fácilmente por cualquier cosa?',choices=((0,'Sí'),(1,'No')),blank=True,null=True)
	record_create = models.DateTimeField(auto_now_add=True)
	evaluation=models.IntegerField('Número de evaluación')
	def __str__(self):
		return f"{self.employee.name}"
	class Meta:
		verbose_name='Acontecimientos traumáticos severos'
		verbose_name_plural='Acontecimientos traumáticos severos'
class RiskSurveyB(models.Model):
	"""Identificacion de analisis de los factores de riesgo psicosocial"""
	employee=models.ForeignKey(Employee,related_name='surveyB', verbose_name='Empleado', on_delete=models.PROTECT)
	choices=((0,'Siempre'),(1,'Casi siempre'),(2,'Algunas veces'),(3,'Casi nunca'),(4,'Nunca'))
	not_choices=((4,'Siempre'),(3,'Casi siempre'),(2,'Algunas veces'),(1,'Casi nunca'),(0,'Nunca'))
	r3_p1= models.IntegerField(u'El espacio donde trabajo me permite realizar mis actividades de manera segura e higiénica',choices=choices)
	r3_p2= models.IntegerField(u'Mi trabajo me exige hacer mucho esfuerzo físico',choices=not_choices)
	r3_p3= models.IntegerField(u'Me preocupa sufrir un accidente en mi trabajo',choices=not_choices)
	r3_p4= models.IntegerField(u'Considero que en mi trabajo se aplican las normas de seguridad y salud en el trabajo',choices=choices)
	r3_p5= models.IntegerField(u'Considero que las actividades que realizo son peligrosas',choices=not_choices)
	r3_p6= models.IntegerField(u'Por la cantidad de trabajo que tengo debo quedarme tiempo adicional a mi turno',choices=not_choices)
	r3_p7= models.IntegerField(u'Por la cantidad de trabajo que tengo debo trabajar sin parar',choices=not_choices)
	r3_p8= models.IntegerField(u'Considero que es necesario mantener un ritmo de trabajo acelerado',choices=not_choices)
	r3_p9= models.IntegerField(u'Mi trabajo exige que esté muy concentrado',choices=not_choices)
	r3_p10= models.IntegerField(u'Mi trabajo requiere que memorice mucha información',choices=not_choices)
	r3_p11= models.IntegerField(u'En mi trabajo tengo que tomar decisiones difíciles muy rápido',choices=not_choices)
	r3_p12= models.IntegerField(u'Mi trabajo exige que atienda varios asuntos al mismo tiempo',choices=not_choices)
	r3_p13= models.IntegerField(u'En mi trabajo soy responsable de cosas de mucho valor',choices=not_choices)
	r3_p14= models.IntegerField(u'Respondo ante mi jefe por los resultados de toda mi área de trabajo',choices=not_choices)
	r3_p15= models.IntegerField(u'En mi trabajo me dan órdenes contradictorias',choices=not_choices)
	r3_p16= models.IntegerField(u'Considero que en mi trabajo me piden hacer cosas innecesarias',choices=not_choices)
	r3_p17= models.IntegerField(u'Trabajo horas extras más de tres veces a la semana',choices=not_choices)
	r3_p18= models.IntegerField(u'Mi trabajo me exige laborar en días de descanso, festivos o fines de semana',choices=not_choices)
	r3_p19= models.IntegerField(u'Considero que el tiempo en el trabajo es mucho y perjudica mis actividades familiares o personales',choices=not_choices)
	r3_p20= models.IntegerField(u'Debo atender asuntos de trabajo cuando estoy en casa',choices=not_choices)
	r3_p21= models.IntegerField(u'Pienso en las actividades familiares o personales cuando estoy en mi trabajo',choices=not_choices)
	r3_p22= models.IntegerField(u'Pienso que mis responsabilidades familiares afectan mi trabajo',choices=not_choices)
	r3_p23= models.IntegerField(u'Mi trabajo permite que desarrolle nuevas habilidades',choices=choices)
	r3_p24= models.IntegerField(u'En mi trabajo puedo aspirar a un mejor puesto',choices=choices)
	r3_p25= models.IntegerField(u'Durante mi jornada de trabajo puedo tomar pausas cuando las necesito',choices=choices)
	r3_p26= models.IntegerField(u'Puedo decidir cuánto trabajo realizo durante la jornada laboral',choices=choices)
	r3_p27= models.IntegerField(u'Puedo decidir la velocidad a la que realizo mis actividades en mi trabajo',choices=choices)
	r3_p28= models.IntegerField(u'Puedo cambiar el orden de las actividades que realizo en mi trabajo',choices=choices)
	r3_p29= models.IntegerField(u'Los cambios que se presentan en mi trabajo dificultan mi labor',choices=not_choices)
	r3_p30= models.IntegerField(u'Cuando se presentan cambios en mi trabajo se tienen en cuenta mis ideas o aportaciones',choices=choices)
	r3_p31= models.IntegerField(u'Me informan con claridad cuáles son mis funciones',choices=choices)
	r3_p32= models.IntegerField(u'Me explican claramente los resultados que debo obtener en mi trabajo',choices=choices)
	r3_p33= models.IntegerField(u'Me explican claramente los objetivos de mi trabajo',choices=choices)
	r3_p34= models.IntegerField(u'Me informan con quién puedo resolver problemas o asuntos de trabajo',choices=choices)
	r3_p35= models.IntegerField(u'Me permiten asistir a capacitaciones relacionadas con mi trabajo',choices=choices)
	r3_p36= models.IntegerField(u'Recibo capacitación útil para hacer mi trabajo',choices=choices)
	r3_p37= models.IntegerField(u'Mi jefe ayuda a organizar mejor el trabajo',choices=choices)
	r3_p38= models.IntegerField(u'Mi jefe tiene en cuenta mis puntos de vista y opiniones',choices=choices)
	r3_p39= models.IntegerField(u'Mi jefe me comunica a tiempo la información relacionada con el trabajo',choices=choices)
	r3_p40= models.IntegerField(u'La orientación que me da mi jefe me ayuda a realizar mejor mi trabajo',choices=choices)
	r3_p41= models.IntegerField(u'Mi jefe ayuda a solucionar los problemas que se presentan en el trabajo',choices=choices)
	r3_p42= models.IntegerField(u'Puedo confiar en mis compañeros de trabajo',choices=choices)
	r3_p43= models.IntegerField(u'Entre compañeros solucionamos los problemas de trabajo de forma respetuosa',choices=choices)
	r3_p44= models.IntegerField(u'En mi trabajo me hacen sentir parte del grupo',choices=choices)
	r3_p45= models.IntegerField(u'Cuando tenemos que realizar trabajo de equipo los compañeros colaboran',choices=choices)
	r3_p46= models.IntegerField(u'Mis compañeros de trabajo me ayudan cuando tengo dificultades',choices=choices)
	r3_p47= models.IntegerField(u'Me informan sobre lo que hago bien en mi trabajo',choices=choices)
	r3_p48= models.IntegerField(u'La forma como evalúan mi trabajo en mi centro de trabajo me ayuda a mejorar mi desempeño',choices=choices)
	r3_p49= models.IntegerField(u'En mi centro de trabajo me pagan a tiempo mi salario',choices=choices)
	r3_p50= models.IntegerField(u'El pago que recibo es el que merezco por el trabajo que realizo',choices=choices)
	r3_p51= models.IntegerField(u'Si obtengo los resultados esperados en mi trabajo me recompensan o reconocen',choices=choices)
	r3_p52= models.IntegerField(u'Las personas que hacen bien el trabajo pueden crecer laboralmente',choices=choices)
	r3_p53= models.IntegerField(u'Considero que mi trabajo es estable',choices=choices)
	r3_p54= models.IntegerField(u'En mi trabajo existe continua rotación de personal',choices=not_choices)
	r3_p55= models.IntegerField(u'Siento orgullo de laborar en este centro de trabajo',choices=choices)
	r3_p56= models.IntegerField(u'Me siento comprometido con mi trabajo',choices=choices)
	r3_p57= models.IntegerField(u'En mi trabajo puedo expresarme libremente sin interrupciones',choices=choices)
	r3_p58= models.IntegerField(u'Recibo críticas constantes a mi persona y/o trabajo',choices=not_choices)
	r3_p59= models.IntegerField(u'Recibo burlas, calumnias, difamaciones, humillaciones o ridiculizaciones',choices=not_choices)
	r3_p60= models.IntegerField(u'Se ignora mi presencia o se me excluye de las reuniones de trabajo y en la toma de decisiones',choices=not_choices)
	r3_p61= models.IntegerField(u'Se manipulan las situaciones de trabajo para hacerme parecer un mal trabajador',choices=not_choices)
	r3_p62= models.IntegerField(u'Se ignoran mis éxitos laborales y se atribuyen a otros trabajadores',choices=not_choices)
	r3_p63= models.IntegerField(u'Me bloquean o impiden las oportunidades que tengo para obtener ascenso o mejora en mi trabajo',choices=not_choices)
	r3_p64= models.IntegerField(u'He presenciado actos de violencia en mi centro de trabajo',choices=not_choices)
	r3_a=models.IntegerField(u'En mi trabajo debo brindar servicio a clientes o usuarios:',choices=((0,'Sí'),(1,'No')))
	r3_p65= models.IntegerField(u'Atiendo clientes o usuarios muy enojados',choices=not_choices, blank=True, null=True)
	r3_p66= models.IntegerField(u'Mi trabajo me exige atender personas muy necesitadas de ayuda o enfermas',choices=not_choices, blank=True, null=True)
	r3_p67= models.IntegerField(u'Para hacer mi trabajo debo demostrar sentimientos distintos a los míos',choices=not_choices, blank=True, null=True)
	r3_p68= models.IntegerField(u'Mi trabajo me exige atender situaciones de violencia',choices=not_choices, blank=True, null=True)
	r3_b= models.IntegerField(u'Soy jefe de otros trabajadores:',choices=((0,'Sí'),(1,'No')))
	r3_p69= models.IntegerField(u'Comunican tarde los asuntos de trabajo',choices=not_choices, blank=True, null=True)
	r3_p70= models.IntegerField(u'Dificultan el logro de los resultados del trabajo',choices=not_choices, blank=True, null=True)
	r3_p71= models.IntegerField(u'Cooperan poco cuando se necesita',choices=not_choices, blank=True, null=True)
	r3_p72= models.IntegerField(u'Ignoran las sugerencias para mejorar su trabajo',choices=not_choices, blank=True, null=True)
	record_create = models.DateTimeField(auto_now_add=True)
	evaluation=models.IntegerField('Número de evaluación')
	def __str__(self):
		return f"{self.employee.name}"
	class Meta:
		verbose_name='Identificacion de analisis de los factores de riesgo psicosocial'
		verbose_name_plural='Identificacion de analisis de los factores de riesgo psicosocial'
	# def cal_dominios(self):
	# 	[{"Condiciones en el ambiente de trabajo":self.r3_p1+self.r3_p3},
	# 	]
		
	# def cal_categoria(self):
	# 	[{"Accidente de trabajo":self.r3_p1+self.r3_p2+self.r3_p3+self.r3_p4+self.r3_p5},
	# 	]
	# def cal_final(self):
	# 	final=self.r3_p1+self.r3_p2+self.r3_p3+self.r3_p4+self.r3_p5


class Product(models.Model):
	name=models.CharField(u'Nombre', max_length=55)
	description=models.CharField(u'Descripción', max_length=255)
	price=models.PositiveIntegerField(u'Precio', default=0)
	choices=((0,'1 a 15 empleados'),(1,'16 a 50 empleados'),(2,'Más de 50 empleados'))
	category = models.IntegerField(u'Categoría por cantidad de empleados',choices=choices)
	def __str__(self):
		return "{}-{}".format(self.id, self.name)

	class Meta:
		verbose_name=u'Producto'
		verbose_name_plural=u'Productos'
		ordering = ['-pk']


class Payment(models.Model):
	user=models.ForeignKey(User,related_name='user_payments',on_delete=models.PROTECT)
	payment_id = models.CharField('Id de pago',max_length=64)
	is_paid = models.CharField('Referencia',max_length=128,blank=True,null=True)
	payer_email = models.EmailField('Email del que paga',blank=True)

	record_create = models.DateTimeField(u"Fecha de creación",auto_now_add=True)
	record_update = models.DateTimeField(auto_now=True)
	def __str__(self):
		return "{}-{}, {}".format(self.id, self.user.userapp.name, self.payment_id)

	class Meta:
		verbose_name=u'Pago'
		verbose_name_plural=u'Pagos'
		ordering = ['-pk']

class PaymentCard(models.Model):
	user=models.ForeignKey(User,related_name='user_cards',on_delete=models.PROTECT)
	last4=models.CharField('Últimos 4 dígitos',max_length=4)
	exp_month=models.IntegerField('Mes de expiración')
	exp_year=models.IntegerField('Año de expiración')
	brand=models.CharField('Marca',max_length=30)
	name=models.CharField('Nombre',max_length=50)
	card_token=models.CharField('Token de tarjeta',max_length=50)

	record_create = models.DateTimeField(u"Fecha de creación",auto_now_add=True)
	record_update = models.DateTimeField(auto_now=True)
	def __str__(self):
		return "{}-{}, {}".format(self.id, self.user.userapp.name, self.last4)

	class Meta:
		verbose_name=u'Tarjetas'
		verbose_name_plural=u'Tarjetas'
		ordering = ['-pk']

class PurchasedProducts(models.Model):
	product=models.ForeignKey(Product,related_name='payments',on_delete=models.PROTECT,null=True,blank=True)
	workplace=models.ForeignKey(Workplace,related_name="workplace_payments",verbose_name='Centro de trabajo', on_delete=models.PROTECT)
	payment=models.ForeignKey(Payment,related_name='purchased_products',on_delete=models.PROTECT,null=True,blank=True)
	payment_method=models.ForeignKey(PaymentCard,related_name='method_purchases',on_delete=models.PROTECT,null=True,blank=True)
	quantity=models.PositiveIntegerField(u'Cantidad')
	def __str__(self):
		return "{}-{} {}".format(self.payment.user.userapp.name,self.payment.is_paid or 'sin pago', self.product.name)

	class Meta:
		verbose_name=u'Producto comparado'
		verbose_name_plural=u'Productos comparados'
		ordering = ['-pk']

# ============================================================
# MÓDULO DE PSICOMETRÍA
# ============================================================

class PsychoInstrument(models.Model):
	"""Catálogo de instrumentos psicométricos"""
	TIPOS = (
		('disc', 'DISC'),
		('zavic', 'Valores e Intereses (Zavic)'),
		('raven', 'Razonamiento (Raven)'),
		('moss', 'Supervisión (Moss)'),
	)
	nombre = models.CharField(u'Nombre', max_length=100)
	tipo = models.CharField(u'Tipo', max_length=20, choices=TIPOS)
	descripcion = models.TextField(u'Descripción', blank=True)
	activo = models.BooleanField(u'Activo', default=True)
	tiempo_limite = models.IntegerField(u'Tiempo límite (minutos)', default=30)
	instrucciones = models.TextField(u'Instrucciones para el evaluado', blank=True)
	record_create = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name = 'Instrumento Psicométrico'
		verbose_name_plural = 'Instrumentos Psicométricos'


class PsychoItem(models.Model):
	"""Reactivos/preguntas de cada instrumento"""
	TIPOS_ITEM = (
		('disc_group', 'Grupo DISC (más/menos)'),
		('distribute', 'Distribución de puntos'),
		('multiple', 'Opción múltiple'),
	)
	instrumento = models.ForeignKey(
		PsychoInstrument, related_name='items',
		on_delete=models.CASCADE
	)
	numero = models.IntegerField(u'Número de reactivo')
	tipo = models.CharField(u'Tipo de reactivo', max_length=20, choices=TIPOS_ITEM)
	texto = models.TextField(u'Texto del reactivo', blank=True)
	dificultad = models.CharField(
		u'Dificultad', max_length=10,
		choices=(('facil','Fácil'),('medio','Medio'),('dificil','Difícil')),
		blank=True
	)
	opciones = models.JSONField(u'Opciones (JSON)', default=list)
	respuesta_correcta = models.CharField(u'Respuesta correcta', max_length=10, blank=True)
	record_create = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.instrumento.nombre} — Item {self.numero}"

	class Meta:
		verbose_name = 'Reactivo'
		verbose_name_plural = 'Reactivos'
		ordering = ['instrumento', 'numero']


class Candidate(models.Model):
	"""Candidato externo o empleado en proceso de evaluación psicométrica"""
	TIPOS = (
		('externo', 'Candidato externo'),
		('empleado', 'Empleado actual'),
	)
	user = models.ForeignKey(
		User, related_name='candidates',
		on_delete=models.CASCADE,
		verbose_name='Empresa RH'
	)
	nombre = models.CharField(u'Nombre completo', max_length=150)
	email = models.EmailField(u'Correo electrónico', blank=True)
	puesto = models.CharField(u'Puesto al que aplica', max_length=100, blank=True)
	tipo = models.CharField(u'Tipo', max_length=20, choices=TIPOS, default='externo')
	employee = models.ForeignKey(
		Employee, related_name='psico_sessions',
		on_delete=models.SET_NULL,
		null=True, blank=True,
		verbose_name='Empleado relacionado'
	)
	notas = models.TextField(u'Notas', blank=True)
	record_create = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nombre} — {self.puesto or 'sin puesto'}"

	class Meta:
		verbose_name = 'Candidato'
		verbose_name_plural = 'Candidatos'
		ordering = ['-record_create']


class TestSession(models.Model):
	"""Sesión de evaluación psicométrica"""
	STATUS = (
		('pendiente', 'Pendiente'),
		('en_proceso', 'En proceso'),
		('completada', 'Completada'),
		('expirada', 'Expirada'),
	)
	candidate = models.ForeignKey(
		Candidate, related_name='sessions',
		on_delete=models.CASCADE
	)
	instrumento = models.ForeignKey(
		PsychoInstrument, related_name='sessions',
		on_delete=models.PROTECT
	)
	token = models.CharField(u'Token único', max_length=64, unique=True)
	status = models.CharField(u'Estado', max_length=20, choices=STATUS, default='pendiente')
	fecha_envio = models.DateTimeField(u'Fecha de envío', auto_now_add=True)
	fecha_inicio = models.DateTimeField(u'Fecha de inicio', null=True, blank=True)
	fecha_completado = models.DateTimeField(u'Fecha de completado', null=True, blank=True)
	expira_en = models.DateTimeField(u'Expira en', null=True, blank=True)
	record_create = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.candidate.nombre} — {self.instrumento.nombre} ({self.status})"

	class Meta:
		verbose_name = 'Sesión de Evaluación'
		verbose_name_plural = 'Sesiones de Evaluación'
		ordering = ['-record_create']


class TestResponse(models.Model):
	"""Respuestas del candidato a cada reactivo"""
	session = models.ForeignKey(
		TestSession, related_name='responses',
		on_delete=models.CASCADE
	)
	item = models.ForeignKey(
		PsychoItem, related_name='responses',
		on_delete=models.PROTECT
	)
	respuesta = models.JSONField(u'Respuesta (JSON)', default=dict)
	record_create = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Sesión {self.session.id} — Item {self.item.numero}"

	class Meta:
		verbose_name = 'Respuesta'
		verbose_name_plural = 'Respuestas'
		ordering = ['session', 'item']


class TestResult(models.Model):
	"""Resultado calculado de una sesión completada"""
	session = models.OneToOneField(
		TestSession, related_name='result',
		on_delete=models.CASCADE
	)
	scores = models.JSONField(u'Puntuaciones (JSON)', default=dict)
	interpretacion = models.TextField(u'Interpretación', blank=True)
	perfil_narrativo = models.TextField(u'Perfil narrativo (IA)', blank=True)
	record_create = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Resultado — {self.session.candidate.nombre}"

	class Meta:
		verbose_name = 'Resultado'
		verbose_name_plural = 'Resultados'

# class MessengerUsers(models.Model):
# 	first_name=models.CharField('Nombre',max_length=70)
# 	last_name=models.CharField('Apellidos',max_length=70)
# 	phone=models.CharField('Teléfono',max_length=12)
# 	email=models.CharField('Correo electrónico',max_length=70)
# 	def __str__(self):
# 		return "{} {}".format(self.first_name,self.last_name)

# 	class Meta:
# 		verbose_name=u'usuarios de messenger'
# 		verbose_name_plural=u'usuarios de messenger'
# 		ordering = ['-pk']
# ---------------------------------------
# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
# 	url=f"https://amjb.org.mx/change-password/?request_id={reset_password_token.key}"
# 	context = {
# 		'current_user': reset_password_token.user,
# 		'username': reset_password_token.user.username,
# 		'email': reset_password_token.user.email,
# 		'reset_password_url':url,
# 		"date_today":process_date(datetime.now()),
# 		"subject":"Reestablecimiento de contraseña",
# 	}
# 	htmly=get_template('mailer_password.html')
# 	html_content=htmly.render(context)
# 	email_plaintext_message = f"""Buenos días, Hemos recibido una solicitud de reestablecimiento de contraseña del correo {reset_password_token.user.email}. 
# 	Para reestablecerla, haz clic en el siguiente enlace {url}, Si tu no solicitaste este cambio por favor reportalo al correo convencion@amjb.org.mx."""
# 	from_email=u'Asociación Mexicana de Jefes de Bomberos <mailer@amjb.org.mx>'
# 	msg = EmailMultiAlternatives("Reinicio de contraseña para la Convención Nacional de Bomberos Zapopan 2019",email_plaintext_message,
# 	   from_email,[reset_password_token.user.email])
# 	msg.attach_alternative(html_content, "text/html")
# 	msg.send()
# from __future__ import unicode_literals



# class ConektaWebhook(generics.GenericAPIView):
# 	def post(self, request, *args, **kwargs):
# 		obj=request.data['data']
# 		if obj is not None:
# 			obj=request.data['data']['object']
# 			if 'payment_method' in obj:
# 				method=obj['payment_method']['type']
# 				if method=='oxxo' or method=='spei':
# 					if obj['status']=='paid':
# 						orders=Payment.objects.filter(payment_id=obj['order_id'])
# 						from_email=u'Asociación Mexicana de Jefes de Bomberos <mailer@amjb.org.mx>'
# 						text_content=u'.'
# 						htmly=get_template('mailer.html')
# 						saved=False
# 						user=orders.last().user.userapp if orders.last() else None
# 						subject=u'Tus eventos para la Convención Nacional de jefes de bomberos Zapopan 2019'
# 						for order in orders:
# 							if order.is_paid:
# 								order.is_paid=None
# 								order.save()
# 								saved=True
# 							if order.product is not None:
# 								if order.product.idproduct==1:
# 									user=order.user.userapp
# 									user.is_subscribed=True
# 									user.save()
# 									subject=u'Admisión a la Convención Nacional de jefes de bomberos Zapopan 2019'
# 						if saved and user:
# 							to=user.user.email
# 							products_list=[]
# 							_sum=0.0
# 							for item in orders:
# 								if item.event is not None:
# 									_sum=_sum+item.event.price
# 									products_list.append({"name":item.event.name,"desc":item.event.description,"quantity":1,"amount":item.event.price,"amount_total":item.event.price*1})
# 								else:
# 									_sum=_sum+item.product.price
# 									products_list.append({"name":item.product.name,"desc":item.product.description,"quantity":1,"amount":item.product.price,"amount_total":item.product.price*1})
# 							ctx={"date_today":process_date(datetime.now()),
# 								"subject":subject,
# 								"user_name":user.user.get_full_name(),
# 								"user_state":user.state,
# 								"user_city":user.city,
# 								"user_phone":user.phone,
# 								"user_mail":to,
# 								"payment_amount":_sum,
# 								"refer":"Pagado",
# 								"payment_method":method,
# 								"payment_id":obj['order_id'],
# 								"companion_code":user.get_companion_code() if not user.companion else 'No aplica',
# 								"products":products_list,
# 								"sub":(_sum-(_sum*0.16)-(_sum*0.04)),
# 								"card_charges":_sum*0.04,
# 								"iva":_sum*0.16,
# 								"subtotal":_sum}
# 							html_content=htmly.render(ctx)
# 							msg=EmailMultiAlternatives(subject, text_content, from_email, [to])
# 							# msg2=EmailMultiAlternatives(subject, text_content, from_email, ["erick.fcm.0@gmail.com"])
# 							msg.attach_alternative(html_content, "text/html")
# 							# msg2.attach_alternative(html_content, "text/html")
# 							msg.send()
# 							# msg2.send()
# 							call_command('notif', f'Correo enviado a {user}  {to}')
# 							print(f'Correo enviado a {user}  {to}')

# 		return Response("Success")

# from django.contrib.auth.models import User
# from django.db import models
# from datetime import date
# from io import StringIO
# from PIL import Image

# # Create your models here.
# class Grade(models.Model):
# 	key=models.AutoField(u'Clave',primary_key=True)
# 	name=models.CharField(u'Nombre', max_length=255)   
# 	#(1,'Táctico'),(2,'Operativo'),(3,'Estratégico')
# 	level=models.PositiveIntegerField(u'Nivel',default=0) 
# 	def __str__(self):
# 		return "%s %s" % (self.key, self.name)

# 	class Meta:
# 		verbose_name=u'Grado'
# 		verbose_name_plural=u'Grados'

# class Userapp(models.Model):
# 	iduser=models.AutoField('iduser',primary_key=True)
# 	user = models.OneToOneField(User,related_name='userapp', on_delete=models.CASCADE)
# 	birth_date=models.DateField(u'Fecha de Nacimiento')
# 	alergies=models.CharField(u'Alergias',max_length=50,blank=True)
# 	city=models.CharField(u'Ciudad',max_length=50)
# 	state=models.CharField(u'Estado',max_length=30)
# 	dependency=models.CharField(u'Dependencia',max_length=150)
# 	gender=models.IntegerField(u'Género',choices=((1,'Masculino'),(2,'Femenino'),))
# 	grade = models.ForeignKey(Grade, related_name='userapp',on_delete=models.PROTECT)
# 	insurance_num=models.CharField(u'Número de seguro',max_length=50,blank=True)
# 	insurance_dep=models.CharField(u'Nombre de asegurador',max_length=50,blank=True)
# 	companion=models.BooleanField(u'Es acompañante?',default=False)
# 	companion_of=models.ForeignKey('self',related_name="companions",verbose_name=u'Código de acompañante',null=True,blank=True,on_delete=models.SET_NULL)
# 	partner=models.BooleanField(u'Es socio?',default=False)
# 	phone=models.CharField(u'Teléfono',max_length=15)
# 	disability=models.CharField(u'Discapacidades',max_length=50, blank=True)
# 	is_subscribed=models.BooleanField(u"Suscrito",default=False)
# 	# email=models.CharField(u'Correo Eléctrico',max_length=35)

# 	record_create = models.DateTimeField(auto_now_add=True)
# 	record_update = models.DateTimeField(auto_now=True)
# 	def get_companion_code(self):
# 		if self.companion==False:
# 			return "{}-{}{}{}".format(self.iduser,self.user.first_name[0:1],self.user.last_name[0:1],self.birth_date.strftime('%Y%d%m'))
# 		else:
# 			return None
# 	def get_user_age(self):
# 		today = date.today()
# 		age=today.year-self.birth_date.year-((today.month, today.day)<(self.birth_date.month, self.birth_date.day))
# 		return age
# 	def get_processed_date(self):
# 		return self.birth_date.strftime('%d/%m/%Y')

# 	def __str__(self):
# 		return "{}-{}".format(self.iduser, self.user.get_full_name())

# 	class Meta:
# 		verbose_name=u'Usuario'
# 		verbose_name_plural=u'Usuarios'
# 		ordering = ['-pk']
# def valid_num(value):
# 	if value>5:
# 		ValidationError("La categoría debe ser de 1 a 5.")
# class Place(models.Model):
# 	idplace=models.AutoField(u'Clave',primary_key=True)
# 	name=models.CharField(u'Nombre', max_length=55)
# 	description=models.CharField(u'Descripción', max_length=255)
# 	place_type=models.IntegerField(u'Tipo de lugar',choices=((1,'Sede'),(2,'Hotel'))) 
# 	latlong=models.CharField(u'Ubicación', max_length=55)
# 	price=models.CharField(u'Precio', max_length=55) 
# 	category=models.PositiveIntegerField(u"Categoría",validators=[valid_num])
# 	contact=models.CharField(u'Contacto', max_length=100)
# 	reservation_code=models.CharField(u'Código de reservación', max_length=60)
# 	def get_lat(self):
# 		return "{}".format(self.latlong.split(',')[1])
# 	def get_long(self):
# 		return "{}".format(self.latlong.split(',')[0])
	 
# 	def __str__(self):
# 		return "{}-{} {}".format(self.idplace, self.name, self.get_place_type_display())

# 	class Meta:
# 		verbose_name=u'Lugar'
# 		verbose_name_plural=u'Lugares'

# class Event(models.Model):
# 	idevent=models.AutoField('idevent',primary_key=True)
# 	gauging=models.PositiveIntegerField(u'Aforo') 
# 	name=models.CharField(u'Nombre', max_length=50)
# 	description=models.TextField(u'Descripción', max_length=700)
# 	coordinator=models.TextField(u'Coordinador y staff', max_length=500)
# 	requirements=models.TextField(u'Requerimientos', max_length=500)
# 	lodging=models.TextField(u'Hospedaje y alimentos', max_length=500)
# 	contact=models.CharField(u'contacto', max_length=200)
# 	start_date = models.DateField(u'Fecha de inicio')
# 	start_time = models.TimeField(u'Hora de inicio')
# 	end_date = models.DateField(u'Fecha de termino')
# 	end_time = models.TimeField(u'Hora de término')
# 	place=models.ForeignKey(Place,related_name='events',on_delete=models.PROTECT)
# 	event_type=models.IntegerField(u'Tipo de evento',choices=((1,'Curso'),(2,'Taller'),(3,'Conferencia'),(4,'Evento General'),(5,'Recorridos'),)) 
# 	grade_type=models.IntegerField(u'Tipo por grado',choices=((0,'General'),(1,'Táctico'),(2,'Operativo'),(3,'Estratégico'))) 
# 	speaker=models.CharField(u'Presentador', max_length=75)
# 	price=models.PositiveIntegerField(u'Precio', default=0)

# 	def get_processed_date_start(self):
# 		return "{} {}".format(self.start_date.strftime('%d/%m/%Y'),self.start_time.strftime('%H:%M'))
# 	def get_processed_date_end(self):
# 		return "{} {}".format(self.end_date.strftime('%d/%m/%Y'),self.end_time.strftime('%H:%M'))
	
# 	def __str__(self):
# 		return "{}-{}".format(self.idevent, self.name)

# 	class Meta:
# 		verbose_name=u'Evento'
# 		verbose_name_plural=u'Eventos'
# 		ordering = ['-pk']

# class Product(models.Model):
# 	idproduct=models.AutoField('idproduct',primary_key=True)
# 	name=models.CharField(u'Nombre', max_length=50)
# 	description=models.CharField(u'Descripción', max_length=255)
# 	price=models.PositiveIntegerField(u'Precio', default=0)
		
# 	def __str__(self):
# 		return "{}-{}".format(self.idproduct, self.name)

# 	class Meta:
# 		verbose_name=u'Producto'
# 		verbose_name_plural=u'Productos'
# 		ordering = ['-pk']

# class Payment(models.Model):
# 	idpayment=models.AutoField('idpayment',primary_key=True)
# 	event=models.ForeignKey(Event,related_name='event_payments',on_delete=models.PROTECT,null=True,blank=True)
# 	product=models.ForeignKey(Product,related_name='product_payments',on_delete=models.PROTECT,null=True,blank=True)
# 	user=models.ForeignKey(User,related_name='user_payments',on_delete=models.PROTECT)
# 	 # Identificador de paypal para este pago
# 	payment_id = models.CharField('Id de pago',max_length=64)
# 	is_paid = models.CharField('Referencia',max_length=128,blank=True,null=True)

# 	# Id unico asignado por paypal a cada usuario
# 	payer_id = models.CharField('Id del que paga',max_length=128, blank=True)

# 	# Dirección de email del cliente proporcionada por paypal.
# 	payer_email = models.EmailField('Email del que paga',blank=True)

# 	record_create = models.DateTimeField(u"Fecha de creación",auto_now_add=True)
# 	record_update = models.DateTimeField(auto_now=True)
# 	def __str__(self):
# 		if self.event is not None:
# 			return "{}-{}, {}".format(self.idpayment, self.user.get_full_name(), self.event)
# 		else:
# 			return "{}-{}, {}".format(self.idpayment, self.user.get_full_name(), self.product)

# 	class Meta:
# 		verbose_name=u'Pago'
# 		verbose_name_plural=u'Pagos'
# 		ordering = ['-pk']
# def upath(instance, filename):	
# 	extension=filename.split('.')
# 	fileext=extension[len(extension)-1]
# 	path = 'sponsors/{0}.{1}'.format(instance.name,fileext)
# 	return  path

# def validate_file_extension(value):
# 	import os	 
# 	from django.conf import settings 
# 	from django.core.exceptions import ValidationError   
# 	ext = os.path.splitext(value.name)[1]
# 	valid_extensions = ['.jpg','.png']
# 	if not ext in valid_extensions:
# 		raise ValidationError(u'Solo se admiten archivos JPG y PNG!')
# 	if value.size > 2621440:
# 		raise ValidationError(u'Archivo muy pesado. Limite de 2.5Mb')

# class Sponsor(models.Model):
# 	idsponsor=models.AutoField('idsponsor',primary_key=True)
# 	name=models.CharField(u'Nombre', max_length=50)
# 	description=models.CharField(u'Descripción', max_length=255)
# 	phone=models.CharField(u'Teléfono',max_length=15,blank=True)
# 	email = models.EmailField('Email',blank=True)
# 	webpage = models.URLField('Página web',blank=True)
# 	image = models.FileField(u'Imagen del patrocinador',upload_to=upath, validators=[validate_file_extension],null=True)

# 	record_create = models.DateTimeField(u"Fecha de creación",auto_now_add=True)
# 	record_update = models.DateTimeField(auto_now=True)
# 	def __str__(self):
# 		return "{}-{}".format(self.idsponsor, self.name)

# 	def save(self, *args, **kwargs):
# 		# try:
# 		# 	if self.image is not None:
# 		# 		image_field = self.image
# 		# 		image_file = StringIO.StringIO(image_field.read())
# 		# 		image = Image.open(image_file)
# 		# 		w,h = image.size
# 		# 		image = image.resize((w/2, h/2), Image.ANTIALIAS)
# 		# 		image_file = StringIO.StringIO()
# 		# 		image.save(image_file, 'JPEG', quality=90)
# 		# 		image_field.file = image_file
# 		# except:
# 		# 	pass
# 		super(Sponsor, self).save(*args, **kwargs)
# 	class Meta:
# 		verbose_name=u'Patrocinador'
# 		verbose_name_plural=u'Patrocinadores'
# 		ordering = ['-pk']


# class UserEvent(models.Model):
# 	id_user_event=models.AutoField('id_user_event',primary_key=True)
# 	event=models.ForeignKey(Event, related_name='user_event',on_delete=models.PROTECT)
# 	user=models.ForeignKey(User, related_name='events',on_delete=models.PROTECT)
# 	interested=models.BooleanField(u'Interesado', default=False)
# 	in_cart=models.BooleanField(u'En el carrito', default=False)
# 	paid=models.ForeignKey(Payment, related_name='paid_events',on_delete=models.PROTECT,null=True)
# 	# paid=models.BooleanField(u'Pagado', default=False)
# 	attendance=models.PositiveIntegerField(u'Asistencia', default=0)

# 	record_create = models.DateTimeField(u"Fecha de creación",auto_now_add=True)
# 	record_update = models.DateTimeField(auto_now=True)
# 	def attended_all_days(self):
# 		attended_days=self.attendance
# 		delta=self.event.end_date - self.event.start_date
# 		if attended_days>=delta.days:
# 			return True
# 		else:
# 			return False
# 	def __str__(self):
# 		return "{}-{} {}".format(self.id_user_event,self.user.get_full_name(),self.event)

# 	class Meta:
# 		verbose_name=u'Agenda de conferencias'
# 		verbose_name_plural=u'Agenda de conferencias'
# 		ordering = ['-pk']
class CreditWallet(models.Model):
    workplace = models.OneToOneField(Workplace, on_delete=models.CASCADE)

    nom035_total = models.IntegerField(default=0)
    nom035_used = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def nom035_available(self):
        return self.nom035_total - self.nom035_used

    def __str__(self):
        return f"{self.workplace.name} - NOM035: {self.nom035_available()}"