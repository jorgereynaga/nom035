"""nom035 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path,include
from surveys.views import *
from surveys.stripe_views import (
    StripePlansView, StripeCheckoutView, StripePortalView,
    StripeWebhookView, PaymentSuccessView, PaymentCancelView
)

from surveys.psico_views import (
    CandidateListView, CandidateCreateView, CandidateDetailView,
    AssignTestView, TestSessionView, TestCompleteView, TestResultView,
    GenerarPerfilNarrativoView, ReporteUnificadoView,
)


from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views
#from django.contrib.staticfiles.views import serve
urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-token-create/', TokenCreation.as_view()),
    path('api/users/', UserappList.as_view()),
    path('api/workplace/', WorkplaceList.as_view()),
    path('api/result_files/', ResultFilesList.as_view()),
    path('api/employee/', EmployeeList.as_view()),
    path('app/access/', SurveyView.as_view()),
    path('api/validate/', ValidateCodeList.as_view()),
    path('api/products/', ProductList.as_view()),
    path('api/payments/', PaymentList.as_view()),
    path('api/addCard/', AddCardList.as_view()),
    path('api/create_pdf/', PDFCreate.as_view()),
    path('api/end_evaluation/', EndEvaluation.as_view()),
    path('api/save_chart/', SaveCharts.as_view()),
    #bot
    path('bot/99b2d8fA40Pcb35040300Pd1b45b5152913434373fb570d665/', BotView.as_view()),

    path('ihes_admin/', admin.site.urls),
    path('terms_and_conditions/', TACView.as_view(), name="tyc"),
    path('main', Index.as_view(), name="index"),
    path('login/', LoginView.as_view(), name="login"),
    path('email_verification/<str:code>/<str:iv>', EmailVerification.as_view()),
    path('email_verification', EmailVerification.as_view(), name='email_verification'),
    path('password_recover/<str:code>/<str:iv>', PasswordRecover.as_view()),
    path('password_recover', PasswordRecover.as_view(), name='password_recover'),
    path('edit_profile/', EditProfileView.as_view(), name="edit_profile"),
    path('logout/', LoginView.as_view(), name='logout'),
    path('newuser/', NewUserView.as_view(), name='newuser'),
    path('workplaces/', WorkplaceView.as_view(), name='workplaces'),
    path('workplaces/<int:workplace_id>/', WorkplaceDetailView.as_view(), name='single_workplace'),
    path('workplaces/<int:workplace_id>/<int:evaluation>/', WorkplaceDetailView.as_view(), name='single_workplace2'),
    path('workplace_result/<int:workplace_id>/', WorkplaceResultView.as_view(), name='workplace_result'),
    path('workplace_result/<int:workplace_id>/<int:evaluation>/', WorkplaceResultView.as_view(), name='workplace_result2'),
    path('workplaceform/', WorkplaceFormView.as_view(), name='workplaceform'),
    path('employeeform/', EmployeeFormView.as_view()),
    path('employeeform/get_departments', get_departments, name='get_departments'),
    path('employeeform/<int:workplace_id>/', EmployeeFormView.as_view(), name='employeeform'),
    path('employees_dt/<int:workplace_id>/<int:t>/', employees_dt, name='employees_dt'),
    path('employees_dt/<int:workplace_id>/<int:t>/<int:evaluation>/', employees_dt, name='employees_dt2'),
    # path('survey/<str:workplace_uuid>/', SurveyView.as_view(), name='survey'),
    path('get_questions/', get_questions, name='get_questions'),
    path('get_chart_data/', get_chart_data, name='get_chart_data'),
    path('get_results/', get_results, name='get_results'),
    path('add_evidence/', add_evidence, name='add_evidence'),
    path('get_workplaces/', get_workplaces, name='get_workplaces'),
    path('contact/', contact, name='contact'),
    path('save_answers/', SaveAnswers.as_view(), name='save_answers'),
    path('payments/', PaymentView.as_view(), name='payments'),
    path('TestView/', TestView.as_view(), name='TestView'),
    path('evidence/', EvidenceView.as_view(), name='evidence'),
    path('files/tmp/<int:user_id>/<str:file_name>', download_file),
    path('files/charts/<int:workplace_id>/<str:evaluation>/<str:file_name>', download_file2),
    #re_path(r'^(?:663egpo6oxo1uuwg7y2hcttf3hqcga.html)?$', serve, kwargs={'path': '/663egpo6oxo1uuwg7y2hcttf3hqcga.html'}),

    # Urls Web Page
    # path('', WebIndex.as_view(), name="webindex"),
    path('psico/reporte/<int:candidate_id>/', ReporteUnificadoView.as_view(), name='reporte_candidato'),

    # Stripe
    path('stripe/planes/', StripePlansView.as_view(), name='stripe_planes'),
    path('stripe/checkout/', StripeCheckoutView.as_view(), name='stripe_checkout'),
    path('stripe/portal/', StripePortalView.as_view(), name='stripe_portal'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('payments/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payments/cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
    # Psicometría
    path('psico/candidatos/', CandidateListView.as_view(), name='candidatos'),
    path('psico/candidatos/nuevo/', CandidateCreateView.as_view(), name='candidato_nuevo'),
    path('psico/candidatos/<int:candidate_id>/', CandidateDetailView.as_view(), name='candidato_detalle'),
    path('psico/asignar/<int:candidate_id>/', AssignTestView.as_view(), name='asignar_test'),
    path('psico/test/<str:token>/', TestSessionView.as_view(), name='test_session'),
    path('psico/test/<str:token>/completar/', TestCompleteView.as_view(), name='test_completar'),
    path('psico/resultado/<int:session_id>/', TestResultView.as_view(), name='test_resultado'),
    path('psico/perfil-narrativo/<int:session_id>/', GenerarPerfilNarrativoView.as_view(), name='perfil_narrativo'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from surveys.views import stripe_webhook
from surveys.views import LandingView

urlpatterns += [
    path('stripe/webhook/', stripe_webhook),
]

