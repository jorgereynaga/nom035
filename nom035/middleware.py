from django.core.mail import EmailMultiAlternatives

def send_mail(to_emails, ctx, template='email-template.html', subject='Tu registro a nuestra plataforma IHES 035 está completo', text_content='Gracias por tu registro con nosotros.'):
    from_email = 'IHES <n035.ihes@gmail.com>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_emails)
    return msg.send()

class ExceptionLoggingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        try:
            import traceback
            tb = traceback.format_exc()
            send_mail(["erick.fcm.0@gmail.com"], ctx={}, template='error-template.html', subject='Error en IHES 035', text_content=tb)
        except Exception:
            pass