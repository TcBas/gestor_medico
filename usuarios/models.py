from django.db import models
from django.contrib.auth.models import User

CARRERAS = [
    ('medicina', 'Medicina'),
    ('enfermeria', 'Enfermería'),
    ('odontologia', 'Odontología'),
    ('psicologia', 'Psicología'),
    ('estadistica', 'Ing.Estadistica e Informatica'),
]

TIPOS = [
    ('doctor', 'Doctor'),
    ('estudiante', 'Estudiante'),
]

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    nombres = models.CharField(max_length=150)
    apellido_paterno = models.CharField(max_length=150)
    apellido_materno = models.CharField(max_length=150, blank=True, null=True)
    dni = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    
    # Solo para estudiantes
    codigo_matricula = models.CharField(max_length=50, blank=True, null=True)
    carrera = models.CharField(max_length=100, choices=CARRERAS, blank=True, null=True)
    
    # Solo para doctores (por ahora dejamos estos vacíos)
    colegiatura = models.CharField(max_length=50, blank=True, null=True)
    especialidad_medica = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.tipo}'


class Cita(models.Model):
    estudiante = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='citas_estudiante',
        limit_choices_to={'tipo': 'estudiante'}
    )
    doctor = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='citas_doctor',
        limit_choices_to={'tipo': 'doctor'}
    )
    fecha = models.DateTimeField()
    estado = models.CharField(max_length=50)
    motivo = models.TextField()

    def __str__(self):
        estudiante_nombre = f"{self.estudiante.nombres} {self.estudiante.apellido_paterno} {self.estudiante.apellido_materno or ''}"
        doctor_nombre = f"{self.doctor.nombres} {self.doctor.apellido_paterno} {self.doctor.apellido_materno or ''}"
        return f"Cita de {estudiante_nombre.strip()} con {doctor_nombre.strip()} - {self.fecha}"
