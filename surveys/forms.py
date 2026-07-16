# -*- coding: utf8 -*-

from django import forms
from django.core.exceptions import ValidationError
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
    _cls = {'class': 'form-control'}
    responsable_nombre = forms.CharField(label='Nombre del responsable NOM-035', max_length=200, widget=forms.TextInput(attrs=_cls))
    responsable_puesto = forms.CharField(label='Puesto del responsable', max_length=150, widget=forms.TextInput(attrs=_cls))
    representante_legal_nombre = forms.CharField(label='Nombre del representante legal', max_length=200, widget=forms.TextInput(attrs=_cls))
    representante_legal_cargo = forms.CharField(label='Cargo del representante legal', max_length=150, widget=forms.TextInput(attrs=_cls))
    canal_quejas = forms.CharField(label='Canal de quejas', max_length=200, widget=forms.TextInput(attrs=_cls))
    responsable_quejas = forms.CharField(label='Responsable de atención de quejas', max_length=200, widget=forms.TextInput(attrs=_cls))
    correo_quejas = forms.EmailField(label='Correo de quejas', widget=forms.EmailInput(attrs=_cls))
    tiempo_respuesta_quejas = forms.CharField(label='Tiempo estimado de respuesta', max_length=100, widget=forms.TextInput(attrs=_cls))
    periodicidad_revision = forms.CharField(label='Periodicidad de revisión', max_length=50, initial='Anual', widget=forms.TextInput(attrs=_cls))


class EvidenciaFaseCForm(forms.Form):
    _cls = {'class': 'form-control'}
    archivo = forms.FileField(label='Archivo', widget=forms.ClearableFileInput(attrs=_cls))
    notas = forms.CharField(label='Notas', required=False, widget=forms.Textarea(attrs=_cls))
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no debe superar 10 MB.')
            ext = archivo.name.split('.')[-1].lower()
            if ext not in ('pdf', 'jpg', 'jpeg', 'png'):
                raise forms.ValidationError('Solo se permiten archivos PDF, JPG o PNG.')
            from surveys.models import validar_contenido_archivo
            try:
                validar_contenido_archivo(archivo, ['pdf', 'jpg', 'jpeg', 'png'])
            except ValidationError as e:
                raise forms.ValidationError(str(e))
        return archivo
