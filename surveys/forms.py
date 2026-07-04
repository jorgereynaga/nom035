# -*- coding: utf8 -*-

from django import forms
from surveys.models import ResultFiles
class LoginForm(forms.Form):
    username = forms.CharField(
                label="",
                widget=forms.TextInput(
                    attrs={
                        'placeholder': 'Nombre de usuario' ,
                        'autofocus': 'autofocus' ,
                        'class': 'input_login',
                    })
                )
    password = forms.CharField(
                label="",
                widget=forms.PasswordInput(
                    attrs={
                    'placeholder': 'Contraseña', 
                    'value': '',
                    'class': 'input_login',
                    })
                )

class ResultFilesForm(forms.ModelForm):
    class Meta:
        model = ResultFiles
        exclude = ('record_create','evaluation')
        fields = '__all__'
class PoliticaPrevencionForm(forms.Form):
    responsable_nombre = forms.CharField(label='Nombre del responsable NOM-035', max_length=200)
    responsable_puesto = forms.CharField(label='Puesto del responsable', max_length=150)
    representante_legal_nombre = forms.CharField(label='Nombre del representante legal', max_length=200)
    representante_legal_cargo = forms.CharField(label='Cargo del representante legal', max_length=150)
    canal_quejas = forms.CharField(label='Canal de quejas', max_length=200)
    responsable_quejas = forms.CharField(label='Responsable de atención de quejas', max_length=200)
    correo_quejas = forms.EmailField(label='Correo de quejas')
    tiempo_respuesta_quejas = forms.CharField(label='Tiempo estimado de respuesta', max_length=100)
    periodicidad_revision = forms.CharField(label='Periodicidad de revisión', max_length=50, initial='Anual')

class PoliticaPrevencionForm(forms.Form):
    responsable_nombre = forms.CharField(label='Nombre del responsable NOM-035', max_length=200)
    responsable_puesto = forms.CharField(label='Puesto del responsable', max_length=150)
    representante_legal_nombre = forms.CharField(label='Nombre del representante legal', max_length=200)
    representante_legal_cargo = forms.CharField(label='Cargo del representante legal', max_length=150)
    canal_quejas = forms.CharField(label='Canal de quejas', max_length=200)
    responsable_quejas = forms.CharField(label='Responsable de atención de quejas', max_length=200)
    correo_quejas = forms.EmailField(label='Correo de quejas')
    tiempo_respuesta_quejas = forms.CharField(label='Tiempo estimado de respuesta', max_length=100)
    periodicidad_revision = forms.CharField(label='Periodicidad de revisión', max_length=50, initial='Anual')
