from django.contrib import admin
from .models import*
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.unregister(User)
class UserInline(admin.StackedInline):
    model = Userapp
    can_delete = False
    fields = (
        'name', 'phone', 'client_id', 'validated_email',
        'workplaces_available', 'workplaces_availableB', 'workplaces_availableC',
        'stripe_customer_id', 'stripe_subscription_id',
        'stripe_plan_key', 'psico_plan_key', 'psico_evaluaciones_disponibles',
        'nom035_creditos', 'nom035_demo', 'psico_demo',
        'image',
    )

UserAdmin.list_display += ('nombre','telefono','fecha_creacion',)
class UserAdmin(UserAdmin):
	# resource_class = ResourceUser
	inlines = (UserInline,)
	# list_filter = ('userapp__is_subscribed',)
	search_fields = ['username','userapp__name']
	fileds=("username","email","is_staff","nombre","telefono")
	ordering = ['-date_joined']
	def nombre(self, obj):
		return obj.userapp.name
	def telefono(self, obj):
		return obj.userapp.phone
	def fecha_creacion(self, obj):
		return obj.userapp.record_create
admin.site.register(User, UserAdmin)



class EmployeeAdmin(admin.ModelAdmin):
	search_fields = ['id','name','workplace__name']
	list_filter = ('workplace__user__userapp__name',)
	list_display = ('id','workplace_name','name','gender_d','ocupation','time_in_charge_d','department')
	ordering = ['-id']
	raw_id_fields = ('workplace',)
	def workplace_name(self, obj):
		return obj.workplace.name
	def gender_d(self, obj):
		return obj.get_gender_display()
	def time_in_charge_d(self, obj):
		return obj.get_time_in_charge_display()
admin.site.register(Employee,EmployeeAdmin)


admin.site.register(Workplace)
admin.site.register(RiskSurveyA)
admin.site.register(RiskSurveyB)
admin.site.register(TraumaSurvey)
admin.site.register(PaymentCard)
admin.site.register(Product)
admin.site.register(Payment)
admin.site.register(PurchasedProducts)
admin.site.register(ResultFiles)
admin.site.register(Candidate)

admin.site.register(WorkEnvironmentSurvey)

class PartnerAdmin(admin.ModelAdmin):
	list_display = ('name', 'code', 'active', 'user', 'record_create')
	search_fields = ['name', 'code', 'contact_email']
	list_filter = ('active',)
class PartnerCommissionAdmin(admin.ModelAdmin):
	list_display = ('partner', 'referred_userapp', 'plan_key', 'monto_plan', 'monto_comision', 'estado', 'fecha_pago', 'record_create')
	list_filter = ('estado', 'partner')
	search_fields = ['partner__name', 'partner__code', 'referred_userapp__name']
	actions = ['marcar_pagada']
	def marcar_pagada(self, request, queryset):
		from django.utils import timezone
		queryset.filter(estado='pendiente').update(estado='pagada', fecha_pago=timezone.now().date())
	marcar_pagada.short_description = 'Marcar como pagada (hoy)'
admin.site.register(Partner, PartnerAdmin)
admin.site.register(PartnerCommission, PartnerCommissionAdmin)
