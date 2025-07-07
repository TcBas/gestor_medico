from django import forms
from django.contrib.auth.models import User
from .models import Perfil

class RegistroEstudianteForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  # ✅ Aquí el calendario

    class Meta:
        model = Perfil
        fields = [
            'nombres', 'apellido_paterno', 'apellido_materno', 'dni', 'telefono',
            'direccion', 'fecha_nacimiento', 'codigo_matricula', 'carrera'
        ]

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )
        perfil = super().save(commit=False)
        perfil.user = user
        perfil.tipo = 'estudiante'
        if commit:
            perfil.save()
        return perfil
