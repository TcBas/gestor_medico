from django.shortcuts import render, redirect
from .forms import RegistroEstudianteForm
from django.contrib import messages
from usuarios import views  # ✅ Cambia 'usuarios' por el nombre real de tu app.
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Perfil
from django.contrib.auth import logout
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)  # Agrega esto arriba de tu views.py

def registro_estudiante(request):
    if request.method == 'POST':
        form = RegistroEstudianteForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # Creamos o actualizamos perfil automáticamente
            perfil, creado = Perfil.objects.get_or_create(user=usuario)
            perfil.tipo = 'estudiante'  # Aquí defines que es ESTUDIANTE
            perfil.save()
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroEstudianteForm()
    return render(request, 'registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                perfil = Perfil.objects.get(user=user)
                tipo_usuario = perfil.tipo.strip().lower()
                
                # Comparación más robusta
                if 'doctor' in tipo_usuario:  # Por si acaso hay espacios o prefijos/sufijos
                    return redirect('vista_doctor')
                elif 'estudiante' in tipo_usuario:
                    return redirect('vista_estudiante')
                else:
                    messages.error(request, f'Tipo de usuario no reconocido: "{tipo_usuario}"')
                    return redirect('login')
            except Perfil.DoesNotExist:
                messages.error(request, 'Perfil no encontrado.')
                return redirect('login')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('login')
    return render(request, 'login.html')



def vista_estudiante(request):
    return render(request, 'vista_estudiante.html')

def vista_doctor(request):
    return render(request, 'vista_doctor.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige al login después de cerrar sesión