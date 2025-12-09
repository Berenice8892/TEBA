from django import forms
from django.forms import ModelForm
from .models import Alumno

class AlumnoForm(ModelForm):
    class Meta:
        model = Alumno
        fields = "__all__"
        
class AvatarForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['avatar']