from django.core.management.base import BaseCommand
from surveys.models import PsychoInstrument, PsychoItem


class Command(BaseCommand):
        help = 'Carga el instrumento Competencias Laborales a la base de datos'

        def handle(self, *args, **kwargs):
                instrumento, created = PsychoInstrument.objects.get_or_create(
                        tipo='competencias',
                        defaults={
                                'nombre': 'Competencias Laborales',
                                'descripcion': 'Evaluación de competencias laborales generales en 8 dimensiones.',
                                'tiempo_limite': 20,
                                'instrucciones': 'A continuación encontrarás 40 afirmaciones sobre tu forma de trabajar. Indica que tan de acuerdo estas con cada una, del 1 (Totalmente en desacuerdo) al 5 (Totalmente de acuerdo).',
                                'activo': True,
                        }
                )

                if not created:
                        if instrumento.items.exists():
                                self.stdout.write(self.style.WARNING('El instrumento Competencias Laborales ya esta cargado, omitiendo.'))
                                return

                reactivos = [
{
"numero": 1,
"descripcion": "Explico mis ideas de forma clara para que otras personas comprendan lo que necesito comunicar.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación"
}
]
},
{
"numero": 2,
"descripcion": "Escucho con atención las instrucciones antes de iniciar una actividad de trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación"
}
]
},
{
"numero": 3,
"descripcion": "Confirmo la información importante para asegurar que entendí correctamente una tarea.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación"
}
]
},
{
"numero": 4,
"descripcion": "Comparto información útil con las personas que la necesitan para realizar su trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación"
}
]
},
{
"numero": 5,
"descripcion": "Presento avances, dudas o problemas de trabajo de manera ordenada y oportuna.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación"
}
]
},
{
"numero": 6,
"descripcion": "Colaboro con otras personas para cumplir objetivos comunes del área o proyecto.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Trabajo en equipo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Trabajo en equipo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Trabajo en equipo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Trabajo en equipo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Trabajo en equipo"
}
]
},
{
"numero": 7,
"descripcion": "Cumplo con la parte que me corresponde cuando trabajo con un equipo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Trabajo en equipo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Trabajo en equipo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Trabajo en equipo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Trabajo en equipo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Trabajo en equipo"
}
]
},
{
"numero": 8,
"descripcion": "Apoyo a mis compañeras y compañeros cuando necesitan resolver una tarea relacionada con el trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Trabajo en equipo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Trabajo en equipo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Trabajo en equipo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Trabajo en equipo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Trabajo en equipo"
}
]
},
{
"numero": 9,
"descripcion": "Respeto los acuerdos definidos por el equipo para organizar el trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Trabajo en equipo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Trabajo en equipo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Trabajo en equipo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Trabajo en equipo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Trabajo en equipo"
}
]
},
{
"numero": 10,
"descripcion": "Participo en actividades de equipo aportando información, ideas o apoyo cuando se requiere.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Trabajo en equipo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Trabajo en equipo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Trabajo en equipo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Trabajo en equipo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Trabajo en equipo"
}
]
},
{
"numero": 11,
"descripcion": "Entrego mis actividades dentro de los tiempos acordados.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Responsabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Responsabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Responsabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Responsabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Responsabilidad"
}
]
},
{
"numero": 12,
"descripcion": "Doy seguimiento a mis pendientes hasta dejarlos concluidos o reportados.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Responsabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Responsabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Responsabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Responsabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Responsabilidad"
}
]
},
{
"numero": 13,
"descripcion": "Aviso con oportunidad cuando una actividad puede retrasarse o requiere apoyo adicional.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Responsabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Responsabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Responsabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Responsabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Responsabilidad"
}
]
},
{
"numero": 14,
"descripcion": "Uso de forma adecuada los recursos, herramientas e información que se me asignan.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Responsabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Responsabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Responsabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Responsabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Responsabilidad"
}
]
},
{
"numero": 15,
"descripcion": "Cumplo los procedimientos establecidos para realizar mis actividades de trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Responsabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Responsabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Responsabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Responsabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Responsabilidad"
}
]
},
{
"numero": 16,
"descripcion": "Ordeno mis actividades antes de iniciar una jornada, proyecto o tarea importante.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Organización y planeación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Organización y planeación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Organización y planeación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Organización y planeación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Organización y planeación"
}
]
},
{
"numero": 17,
"descripcion": "Priorizo las tareas de acuerdo con su importancia, urgencia o impacto en el resultado.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Organización y planeación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Organización y planeación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Organización y planeación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Organización y planeación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Organización y planeación"
}
]
},
{
"numero": 18,
"descripcion": "Registro pendientes, acuerdos o fechas clave para darles seguimiento.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Organización y planeación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Organización y planeación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Organización y planeación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Organización y planeación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Organización y planeación"
}
]
},
{
"numero": 19,
"descripcion": "Distribuyo mi tiempo para avanzar en mis actividades sin dejar pendientes importantes al final.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Organización y planeación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Organización y planeación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Organización y planeación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Organización y planeación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Organización y planeación"
}
]
},
{
"numero": 20,
"descripcion": "Mantengo ordenada la información que necesito para realizar y comprobar mi trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Organización y planeación"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Organización y planeación"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Organización y planeación"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Organización y planeación"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Organización y planeación"
}
]
},
{
"numero": 21,
"descripcion": "Reviso la información disponible antes de proponer una solución a un problema de trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas"
}
]
},
{
"numero": 22,
"descripcion": "Identifico las causas principales de un problema antes de decidir qué acción tomar.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas"
}
]
},
{
"numero": 23,
"descripcion": "Propongo alternativas cuando una actividad no puede resolverse de la forma habitual.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas"
}
]
},
{
"numero": 24,
"descripcion": "Solicito apoyo o autorización cuando un problema rebasa mi función o nivel de decisión.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas"
}
]
},
{
"numero": 25,
"descripcion": "Documento o comunico las acciones tomadas para resolver un problema relevante de trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas"
}
]
},
{
"numero": 26,
"descripcion": "Ajusto mis actividades cuando cambian las prioridades del trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Adaptabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Adaptabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Adaptabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Adaptabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Adaptabilidad"
}
]
},
{
"numero": 27,
"descripcion": "Sigo las nuevas instrucciones cuando se actualiza un proceso o forma de trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Adaptabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Adaptabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Adaptabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Adaptabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Adaptabilidad"
}
]
},
{
"numero": 28,
"descripcion": "Reorganizo mis pendientes cuando surge una actividad urgente o imprevista.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Adaptabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Adaptabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Adaptabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Adaptabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Adaptabilidad"
}
]
},
{
"numero": 29,
"descripcion": "Realizo mis actividades con diferentes personas, áreas o estilos de trabajo cuando la operación lo requiere.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Adaptabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Adaptabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Adaptabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Adaptabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Adaptabilidad"
}
]
},
{
"numero": 30,
"descripcion": "Aplico cambios en mi forma de trabajar cuando se requiere mejorar un resultado o cumplir una indicación.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Adaptabilidad"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Adaptabilidad"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Adaptabilidad"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Adaptabilidad"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Adaptabilidad"
}
]
},
{
"numero": 31,
"descripcion": "Trabajo con enfoque en cumplir los objetivos asignados a mi puesto o proyecto.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a resultados"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a resultados"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a resultados"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a resultados"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a resultados"
}
]
},
{
"numero": 32,
"descripcion": "Reviso mis avances para identificar si estoy cumpliendo con lo esperado.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a resultados"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a resultados"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a resultados"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a resultados"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a resultados"
}
]
},
{
"numero": 33,
"descripcion": "Busco que mis entregables cumplan con la calidad solicitada.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a resultados"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a resultados"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a resultados"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a resultados"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a resultados"
}
]
},
{
"numero": 34,
"descripcion": "Ajusto mis actividades cuando detecto que el resultado no corresponde con lo esperado.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a resultados"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a resultados"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a resultados"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a resultados"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a resultados"
}
]
},
{
"numero": 35,
"descripcion": "Propongo mejoras concretas para lograr mejores resultados en mi trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a resultados"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a resultados"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a resultados"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a resultados"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a resultados"
}
]
},
{
"numero": 36,
"descripcion": "Identifico conocimientos o habilidades que necesito fortalecer para realizar mejor mi trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Aprendizaje y mejora continua"
}
]
},
{
"numero": 37,
"descripcion": "Aplico en mis actividades la retroalimentación que recibo sobre mi desempeño.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Aprendizaje y mejora continua"
}
]
},
{
"numero": 38,
"descripcion": "Participo en capacitaciones o actividades de aprendizaje relacionadas con mi trabajo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Aprendizaje y mejora continua"
}
]
},
{
"numero": 39,
"descripcion": "Uso lo aprendido para mejorar la forma en que realizo mis actividades.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Aprendizaje y mejora continua"
}
]
},
{
"numero": 40,
"descripcion": "Solicito orientación o capacitación cuando necesito mejorar una actividad específica de mi puesto.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Aprendizaje y mejora continua"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Aprendizaje y mejora continua"
}
]
}
]

                for r in reactivos:
                        PsychoItem.objects.create(
                                instrumento=instrumento,
                                numero=r['numero'],
                                tipo='multiple',
                                texto=r['descripcion'],
                                opciones=r['opciones'],
                        )

                self.stdout.write(self.style.SUCCESS(f'Competencias Laborales cargado: {len(reactivos)} reactivos creados.'))