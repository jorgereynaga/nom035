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