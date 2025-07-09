from django.shortcuts import render, redirect
from .forms import RegistroEstudianteForm
from django.contrib import messages
from usuarios import views  # ✅ Cambia 'usuarios' por el nombre real de tu app.
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Perfil, Cita
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
import logging
from datetime import timedelta, datetime

logger = logging.getLogger(__name__)  # Agrega esto arriba de tu views.py

def registro_estudiante(request):
    if request.method == 'POST':
        form = RegistroEstudianteForm(request.POST)
        if form.is_valid():
            perfil = form.save()  # YA guarda perfil y user
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroEstudianteForm()
    return render(request, 'registro.html', {'form': form})


def login_view(request):
    if 'registro' in request.GET and request.GET['registro'] == 'exitoso':
        messages.success(request, 'Registro exitoso. Por favor, inicie sesión.')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                perfil = Perfil.objects.get(user=user)
                tipo_usuario = perfil.tipo.strip().lower()
                
                if tipo_usuario == 'doctor':
                    return redirect('vista_doctor')
                elif tipo_usuario == 'estudiante':
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
    doctores = Perfil.objects.filter(tipo='doctor')
    estudiante = Perfil.objects.get(user=request.user)
    hoy = timezone.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6, hours=23, minutes=59, seconds=59)
    proxima_fecha = fin_semana + timedelta(seconds=1)  # Desde la próxima semana

    citas_esta_semana = Cita.objects.filter(
        estudiante=estudiante,
        fecha__range=(inicio_semana, fin_semana)
    )

    if request.method == 'POST':
        if citas_esta_semana.exists():
            messages.error(request, "Solo puedes agendar una cita por semana.")
        else:
            doctor_id = request.POST.get('doctor')
            fecha = request.POST.get('fecha')
            motivo = request.POST.get('motivo')

            if doctor_id and fecha and motivo:
                doctor = Perfil.objects.get(id=doctor_id)
                Cita.objects.create(
                    estudiante=estudiante,
                    doctor=doctor,
                    fecha=fecha,
                    motivo=motivo,
                    estado='Pendiente'
                )
                messages.success(request, "Cita agendada con éxito.")
                return redirect('vista_estudiante')
            else:
                messages.error(request, "Por favor, completa todos los campos.")

    citas = Cita.objects.filter(estudiante=estudiante).order_by('-fecha')

    return render(request, 'vista_estudiante.html', {
        'doctores': doctores,
        'citas': citas,
        'citas_esta_semana': citas_esta_semana.first(),
        'proxima_fecha': proxima_fecha,
    })

def vista_doctor(request):
    perfil = Perfil.objects.get(user=request.user)

    # Filtrar solo citas aceptadas del doctor actual
    citas_aceptadas = Cita.objects.filter(
        doctor=perfil,
        estado='Aceptada'
    ).order_by('fecha')

    return render(request, 'vista_doctor.html', {
        'citas_aceptadas': citas_aceptadas,
    })

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige al login después de cerrar sesión