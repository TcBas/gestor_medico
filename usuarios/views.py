from django.shortcuts import render, redirect
from .forms import RegistroEstudianteForm, GestionCitaForm
from django.contrib import messages

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
                # Buscar el siguiente número de orden disponible (1-10) para ese doctor y fecha
                from datetime import datetime as dt
                fecha_date = dt.strptime(fecha, "%Y-%m-%d").date()
                citas_dia = Cita.objects.filter(doctor=doctor, fecha=fecha_date)
                ordenes_ocupados = set(citas_dia.values_list('orden', flat=True))
                orden_disponible = None
                for i in range(1, 11):
                    if i not in ordenes_ocupados:
                        orden_disponible = i
                        break
                if orden_disponible is None:
                    messages.error(request, "Ya no hay cupos disponibles para ese doctor en ese día. Máximo 10 pacientes por día.")
                else:
                    Cita.objects.create(
                        estudiante=estudiante,
                        doctor=doctor,
                        fecha=fecha_date,
                        orden=orden_disponible,
                        motivo=motivo,
                        estado='Pendiente'
                    )
                    messages.success(request, f"Cita agendada con éxito. Tu número de orden es {orden_disponible}.")
                    return redirect('vista_estudiante')
            else:
                messages.error(request, "Por favor, completa todos los campos.")

    citas = Cita.objects.filter(estudiante=estudiante).order_by('-fecha')

    # Simulación de análisis médico
    analisis = {
        'tipo_sangre': 'O+',
        'alergias': 'Ninguna',
        'peso': '70',
        'altura': '175',
        'observaciones': 'Sin observaciones'
    }

    # Simulación de diagnóstico en cada cita (si no existe el campo)
    for cita in citas:
        if not hasattr(cita, 'diagnostico'):
            cita.diagnostico = 'Diagnóstico no registrado'

    from .models import CARRERAS
    return render(request, 'vista_estudiante.html', {
        'doctores': doctores,
        'citas': citas,
        'citas_esta_semana': citas_esta_semana.first(),
        'proxima_fecha': proxima_fecha,
        'analisis': analisis,
        'perfil': estudiante,
        'carreras': CARRERAS,
    })

def vista_doctor(request):
    from .models import AnalisisMedico
    from collections import defaultdict
    perfil = Perfil.objects.get(user=request.user)

    # Obtener todos los pacientes que tienen citas aceptadas con este doctor
    citas_aceptadas = Cita.objects.filter(
        doctor=perfil,
        estado='Aceptada'
    ).order_by('fecha')
    pacientes_ids = list(citas_aceptadas.values_list('estudiante', flat=True).distinct())
    pacientes = Perfil.objects.filter(id__in=pacientes_ids)

    # Calcular fechas de la semana a mostrar (lunes a viernes)
    hoy = timezone.now()
    # Si hoy es sábado (5) o domingo (6), mostrar la semana siguiente
    if hoy.weekday() >= 5:
        inicio_semana = (hoy + timedelta(days=(7 - hoy.weekday()))).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        inicio_semana = hoy - timedelta(days=hoy.weekday())  # lunes de la semana actual
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(5)]  # lunes a viernes
    fin_semana = inicio_semana + timedelta(days=4, hours=23, minutes=59, seconds=59)

    # Citas de la semana actual (todas, no solo del paciente seleccionado)
    citas_semana = Cita.objects.filter(
        doctor=perfil,
        estado='Aceptada',
        fecha__range=(inicio_semana, fin_semana)
    )

    # Agrupar citas por día
    citas_por_dia = defaultdict(list)
    for cita in citas_semana:
        dia = cita.fecha
        citas_por_dia[dia].append(cita)
    # Crear lista de días con sus citas para la plantilla
    citas_por_dia_lista = []
    for dia in dias_semana:
        citas = citas_por_dia.get(dia.date() if hasattr(dia, 'date') else dia, [])
        citas_por_dia_lista.append({'dia': dia, 'citas': citas})

    # Selección de paciente
    paciente_id = request.GET.get('paciente')
    paciente_seleccionado = None
    citas_paciente = []
    analisis = None
    if paciente_id:
        try:
            paciente_id_int = int(paciente_id)
            paciente_seleccionado = pacientes.get(id=paciente_id_int)
            citas_paciente = Cita.objects.filter(doctor=perfil, estudiante=paciente_seleccionado).order_by('-fecha')

            # Guardar datos médicos si es POST
            if request.method == 'POST':
                peso = request.POST.get('peso')
                altura = request.POST.get('altura')
                tipo_sangre = request.POST.get('tipo_sangre')
                alergias = request.POST.get('alergias')
                observaciones = request.POST.get('observaciones')
                diagnostico = request.POST.get('diagnostico')
                analisis_obj, _ = AnalisisMedico.objects.get_or_create(paciente=paciente_seleccionado)
                analisis_obj.peso = peso or None
                analisis_obj.altura = altura or None
                analisis_obj.tipo_sangre = tipo_sangre or None
                analisis_obj.alergias = alergias or None
                analisis_obj.observaciones = observaciones or None
                analisis_obj.diagnostico = diagnostico or None
                analisis_obj.save()
                # Redirigir para mostrar los datos actualizados (POST/Redirect/GET)
                return redirect(f"{request.path}?paciente={paciente_seleccionado.id}")

            # Leer datos médicos reales
            try:
                analisis_obj = AnalisisMedico.objects.get(paciente=paciente_seleccionado)
                analisis = {
                    'peso': analisis_obj.peso,
                    'altura': analisis_obj.altura,
                    'tipo_sangre': analisis_obj.tipo_sangre,
                    'alergias': analisis_obj.alergias,
                    'observaciones': analisis_obj.observaciones,
                    'diagnostico': analisis_obj.diagnostico,
                }
            except AnalisisMedico.DoesNotExist:
                analisis = {
                    'peso': '',
                    'altura': '',
                    'tipo_sangre': '',
                    'alergias': '',
                    'observaciones': '',
                    'diagnostico': '',
                }
        except (Perfil.DoesNotExist, ValueError):
            paciente_seleccionado = None
            citas_paciente = []
            analisis = None

    return render(request, 'vista_doctor.html', {
        'pacientes': pacientes,
        'paciente_seleccionado': paciente_seleccionado,
        'citas_paciente': citas_paciente,
        'analisis': analisis,
        'citas_por_dia_lista': citas_por_dia_lista,
    })

def perfil_estudiante(request):
    perfil = Perfil.objects.get(user=request.user)
    return render(request, 'perfil_estudiante.html', {'perfil': perfil})

from .forms import EditarPerfilEstudianteForm

def editar_perfil_estudiante(request):
    perfil = Perfil.objects.get(user=request.user)
    if request.method == 'POST':
        form = EditarPerfilEstudianteForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos actualizados correctamente.')
            return redirect('vista_estudiante')
    else:
        form = EditarPerfilEstudianteForm(instance=perfil)
    return render(request, 'editar_perfil_estudiante.html', {'perfil': perfil, 'form': form})

def perfil_doctor(request):
    perfil = Perfil.objects.get(user=request.user)
    return render(request, 'perfil_doctor.html', {'perfil': perfil})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige al login después de cerrar sesión