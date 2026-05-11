from rest_framework import serializers
from .models import *
# from django.core.management import call_command


class UserappSerializer(serializers.ModelSerializer):
	image_url = serializers.SerializerMethodField('get_image_url')
	def get_image_url(self, obj):
		return '%s%s' % ("/media/", obj.image)
	class Meta:
		model = Userapp
		# fields = ('inspection' , 'requirements')

		fields = '__all__'
class WorkplaceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Workplace
		fields = '__all__'
class EmployeeSerializer(serializers.ModelSerializer):

	class Meta:
		model = Employee
		fields = '__all__'
class RiskSurveyASerializer(serializers.ModelSerializer):

	class Meta:
		model = RiskSurveyA
		fields = '__all__'
class RiskSurveyBSerializer(serializers.ModelSerializer):

	class Meta:
		model = RiskSurveyB
		fields = '__all__'
class TraumaSurveySerializer(serializers.ModelSerializer):

	class Meta:
		model = TraumaSurvey
		fields = '__all__'
class CardSerializer(serializers.ModelSerializer):

	class Meta:
		model = PaymentCard
		fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):

	class Meta:
		model = Product
		fields = '__all__'
class PaymentSerializer(serializers.ModelSerializer):

	class Meta:
		model = Payment
		fields = '__all__'
class ResultFilesSerializer(serializers.ModelSerializer):

	class Meta:
		model = ResultFiles
		fields = '__all__'