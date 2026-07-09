from django.core.management.base import BaseCommand
from surveys.models import PsychoInstrument, PsychoItem


class Command(BaseCommand):
        help = 'Carga el instrumento Perfil Comercial y Servicio al Cliente a la base de datos'

        def handle(self, *args, **kwargs):
                instrumento, created = PsychoInstrument.objects.get_or_create(
                        tipo='comercial',
                        defaults={
                                'nombre': 'Perfil Comercial y Servicio al Cliente',
                                'descripcion': 'Evaluación de competencias comerciales y de atención al cliente en 8 dimensiones.',
                                'tiempo_limite': 20,
                                'instrucciones': 'A continuación encontrarás 40 afirmaciones sobre tu forma de trabajar con clientes. Indica que tan de acuerdo estas con cada una, del 1 (Totalmente en desacuerdo) al 5 (Totalmente de acuerdo).',
                                'activo': True,
                        }
                )

                if not created:
                        if instrumento.items.exists():
                                self.stdout.write(self.style.WARNING('El instrumento Perfil Comercial ya esta cargado, omitiendo.'))
                                return

                reactivos = [
{
"numero": 1,
"descripcion": "Pregunto al cliente qué necesita antes de ofrecer un producto o servicio.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación al cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación al cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación al cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación al cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación al cliente"
}
]
},
{
"numero": 2,
"descripcion": "Escucho la situación del cliente antes de proponer una solución.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación al cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación al cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación al cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación al cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación al cliente"
}
]
},
{
"numero": 3,
"descripcion": "Confirmo con el cliente que la opción propuesta responde a lo que necesita.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación al cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación al cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación al cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación al cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación al cliente"
}
]
},
{
"numero": 4,
"descripcion": "Registro información relevante del cliente para mejorar la atención o el seguimiento.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación al cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación al cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación al cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación al cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación al cliente"
}
]
},
{
"numero": 5,
"descripcion": "Procuro que el cliente tenga claridad sobre el producto, servicio o solución que recibe.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación al cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación al cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación al cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación al cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación al cliente"
}
]
},
{
"numero": 6,
"descripcion": "Explico productos o servicios con palabras claras y fáciles de entender.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación comercial"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación comercial"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación comercial"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación comercial"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación comercial"
}
]
},
{
"numero": 7,
"descripcion": "Presento los beneficios del producto o servicio de acuerdo con la necesidad del cliente.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación comercial"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación comercial"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación comercial"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación comercial"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación comercial"
}
]
},
{
"numero": 8,
"descripcion": "Verifico que el cliente entendió la información antes de avanzar al siguiente paso.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación comercial"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación comercial"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación comercial"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación comercial"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación comercial"
}
]
},
{
"numero": 9,
"descripcion": "Respondo las preguntas del cliente con información concreta y relacionada con su caso.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación comercial"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación comercial"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación comercial"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación comercial"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación comercial"
}
]
},
{
"numero": 10,
"descripcion": "Comunico condiciones, precios, tiempos o alcances sin omitir información importante.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Comunicación comercial"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Comunicación comercial"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Comunicación comercial"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Comunicación comercial"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Comunicación comercial"
}
]
},
{
"numero": 11,
"descripcion": "Relaciono las características del producto o servicio con una necesidad real del cliente.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Persuasión ética"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Persuasión ética"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Persuasión ética"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Persuasión ética"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Persuasión ética"
}
]
},
{
"numero": 12,
"descripcion": "Ofrezco alternativas cuando detecto que una opción no es la más adecuada para el cliente.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Persuasión ética"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Persuasión ética"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Persuasión ética"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Persuasión ética"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Persuasión ética"
}
]
},
{
"numero": 13,
"descripcion": "Explico ventajas y limitaciones del producto o servicio para apoyar una decisión informada.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Persuasión ética"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Persuasión ética"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Persuasión ética"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Persuasión ética"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Persuasión ética"
}
]
},
{
"numero": 14,
"descripcion": "Presento argumentos de venta basados en información verificable del producto o servicio.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Persuasión ética"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Persuasión ética"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Persuasión ética"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Persuasión ética"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Persuasión ética"
}
]
},
{
"numero": 15,
"descripcion": "Evito comprometer resultados, descuentos o beneficios que no están autorizados.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Persuasión ética"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Persuasión ética"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Persuasión ética"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Persuasión ética"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Persuasión ética"
}
]
},
{
"numero": 16,
"descripcion": "Escucho la objeción del cliente antes de responder o insistir en una propuesta.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Manejo de objeciones"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Manejo de objeciones"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Manejo de objeciones"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Manejo de objeciones"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Manejo de objeciones"
}
]
},
{
"numero": 17,
"descripcion": "Hago preguntas para entender la razón de la duda o resistencia del cliente.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Manejo de objeciones"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Manejo de objeciones"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Manejo de objeciones"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Manejo de objeciones"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Manejo de objeciones"
}
]
},
{
"numero": 18,
"descripcion": "Respondo las objeciones con información relacionada con la necesidad expresada por el cliente.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Manejo de objeciones"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Manejo de objeciones"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Manejo de objeciones"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Manejo de objeciones"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Manejo de objeciones"
}
]
},
{
"numero": 19,
"descripcion": "Propongo una alternativa cuando el cliente no acepta la primera opción presentada.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Manejo de objeciones"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Manejo de objeciones"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Manejo de objeciones"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Manejo de objeciones"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Manejo de objeciones"
}
]
},
{
"numero": 20,
"descripcion": "Mantengo una conversación ordenada cuando el cliente expresa dudas, quejas o desacuerdo.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Manejo de objeciones"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Manejo de objeciones"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Manejo de objeciones"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Manejo de objeciones"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Manejo de objeciones"
}
]
},
{
"numero": 21,
"descripcion": "Registro los acuerdos o pendientes que surgen durante la atención o proceso de venta.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Seguimiento y cierre"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Seguimiento y cierre"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Seguimiento y cierre"
}
]
},
{
"numero": 22,
"descripcion": "Doy seguimiento al cliente en la fecha o plazo acordado.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Seguimiento y cierre"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Seguimiento y cierre"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Seguimiento y cierre"
}
]
},
{
"numero": 23,
"descripcion": "Confirmo con el cliente los pasos siguientes después de una llamada, visita o conversación.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Seguimiento y cierre"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Seguimiento y cierre"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Seguimiento y cierre"
}
]
},
{
"numero": 24,
"descripcion": "Solicito la decisión del cliente cuando ya cuenta con la información necesaria para avanzar.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Seguimiento y cierre"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Seguimiento y cierre"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Seguimiento y cierre"
}
]
},
{
"numero": 25,
"descripcion": "Cierro la atención o venta dejando claros los acuerdos, condiciones y responsables.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Seguimiento y cierre"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Seguimiento y cierre"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Seguimiento y cierre"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Seguimiento y cierre"
}
]
},
{
"numero": 26,
"descripcion": "Continúo con el proceso de atención aunque el cliente no acepte la primera propuesta.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Tolerancia al rechazo"
}
]
},
{
"numero": 27,
"descripcion": "Mantengo el trato profesional cuando el cliente decide no comprar o no continuar.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Tolerancia al rechazo"
}
]
},
{
"numero": 28,
"descripcion": "Solicito retroalimentación útil cuando un cliente rechaza una propuesta o servicio.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Tolerancia al rechazo"
}
]
},
{
"numero": 29,
"descripcion": "Busco otro prospecto, alternativa o siguiente acción cuando una oportunidad no avanza.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Tolerancia al rechazo"
}
]
},
{
"numero": 30,
"descripcion": "Conservo el seguimiento de mis actividades comerciales después de recibir una negativa.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Tolerancia al rechazo"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Tolerancia al rechazo"
}
]
},
{
"numero": 31,
"descripcion": "Identifico el problema principal del cliente antes de canalizarlo o proponer una solución.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas del cliente"
}
]
},
{
"numero": 32,
"descripcion": "Informo al cliente los pasos que se seguirán para atender su solicitud o inconformidad.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas del cliente"
}
]
},
{
"numero": 33,
"descripcion": "Canalizo al cliente con el área o persona correspondiente cuando no puedo resolver el caso directamente.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas del cliente"
}
]
},
{
"numero": 34,
"descripcion": "Doy seguimiento a las solicitudes del cliente hasta contar con una respuesta o cierre.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas del cliente"
}
]
},
{
"numero": 35,
"descripcion": "Confirmo con el cliente si la respuesta recibida atendió su solicitud o problema.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Solución de problemas del cliente"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Solución de problemas del cliente"
}
]
},
{
"numero": 36,
"descripcion": "Reviso mis avances comerciales o de servicio para saber si estoy cumpliendo mis metas.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a metas comerciales"
}
]
},
{
"numero": 37,
"descripcion": "Organizo mis actividades para atender clientes y avanzar en mis objetivos comerciales.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a metas comerciales"
}
]
},
{
"numero": 38,
"descripcion": "Priorizo oportunidades o clientes de acuerdo con el avance, necesidad o impacto esperado.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a metas comerciales"
}
]
},
{
"numero": 39,
"descripcion": "Realizo acciones concretas para mejorar mis indicadores de venta, atención o seguimiento.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a metas comerciales"
}
]
},
{
"numero": 40,
"descripcion": "Mantengo actualizado el registro de mis actividades comerciales o de atención para medir resultados.",
"opciones": [
{
"texto": "Totalmente en desacuerdo",
"valor": 1,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "En desacuerdo",
"valor": 2,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Neutral",
"valor": 3,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "De acuerdo",
"valor": 4,
"dimension": "Orientación a metas comerciales"
},
{
"texto": "Totalmente de acuerdo",
"valor": 5,
"dimension": "Orientación a metas comerciales"
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

                self.stdout.write(self.style.SUCCESS(f'Perfil Comercial cargado: {len(reactivos)} reactivos creados.'))