from django import forms
from django.contrib.auth.models import User
from .models import Perfil

class RegistroEstudianteForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirmar Contraseña')  # NUEVO CAMPO
    email = forms.EmailField()
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  # ✅ Calendario

    class Meta:
        model = Perfil
        fields = [
            'nombres', 'apellido_paterno', 'apellido_materno', 'dni', 'telefono',
            'direccion', 'fecha_nacimiento', 'codigo_matricula', 'carrera'
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")  # Validación

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