from celery import shared_task
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
import logging,os
p_= logging.getLogger(__name__)

@shared_task
def pdf_reports_task(user,template,ctx):
	p_.error(ctx)
	html_string=render_to_string(f'pdf/{template}.html', ctx)
	# import logging
	# logger = logging.getLogger('weasyprint')
	# logger.addHandler(logging.FileHandler('/tesalia/log/weasyprint.log'))
	# print(user)
	html=HTML(string=html_string)
	if not os.path.exists(f"{settings.BASE_DIR}/files/tmp/{user}"):
		os.mkdir(f"{settings.BASE_DIR}/files/tmp/{user}")
	html.write_pdf(target=f'{settings.BASE_DIR}/files/tmp/{user}/{template}.pdf',stylesheets=[
		settings.BASE_DIR + '/static/app-assets/css/bootstrap.css',
		# settings.BASE_DIR + '/static/app-assets/css/bootstrap-grid.css',
		# settings.BASE_DIR + '/static/app-assets/css/bootstrap-reboot.css',
	]);