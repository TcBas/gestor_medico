from django.db import models
from django.contrib.auth.models import User

CARRERAS = [
    ('medicina', 'Medicina Humana'),
    ('enfermeria', 'Enfermería'),
    ('odontologia', 'Odontología'),
    ('psicologia', 'Psicología'),
    ('estadistica', 'Ingeniería Estadística e Informática'),
    ('civil', 'Ingeniería Civil'),
    ('sistemas', 'Ingeniería de Sistemas'),
    ('electronica', 'Ingeniería Electrónica'),
    ('agronomia', 'Ingeniería Agronómica'),
    ('ambiental', 'Ingeniería Ambiental'),
    ('derecho', 'Derecho'),
    ('contabilidad', 'Contabilidad'),
    ('administracion', 'Administración'),
    ('economia', 'Economía'),
    ('educacion_inicial', 'Educación Inicial'),
    ('educacion_primaria', 'Educación Primaria'),
    ('educacion_secundaria', 'Educación Secundaria'),
    ('biologia', 'Biología'),
    ('matematica', 'Matemática'),
    ('fisica', 'Física'),
    ('quimica', 'Química'),
    ('arquitectura', 'Arquitectura'),
    ('zootecnia', 'Zootecnia'),
    ('veterinaria', 'Medicina Veterinaria'),
]

TIPOS = [
    ('doctor', 'Doctor'),
    ('estudiante', 'Estudiante'),
]

#Estados de Citas
ESTADOS = [
    ('Pendiente', 'Pendiente'),
    ('Aceptada', 'Aceptada'),
    ('Rechazada', 'Rechazada'),
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
    fecha = models.DateField()  # Solo fecha, sin hora
    orden = models.PositiveSmallIntegerField()  # Número de orden (1-10)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='Pendiente')
    motivo = models.TextField()

    def __str__(self):
        estudiante_nombre = f"{self.estudiante.nombres} {self.estudiante.apellido_paterno} {self.estudiante.apellido_materno or ''}"
        doctor_nombre = f"{self.doctor.nombres} {self.doctor.apellido_paterno} {self.doctor.apellido_materno or ''}"
        return f"Cita de {estudiante_nombre.strip()} con {doctor_nombre.strip()} - {self.fecha} (Orden {self.orden})"

class AnalisisMedico(models.Model):
    paciente = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='analisis_medico', limit_choices_to={'tipo': 'estudiante'})
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    altura = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    tipo_sangre = models.CharField(max_length=10, blank=True, null=True)
    sexo = models.CharField(max_length=10, blank=True, null=True)
    alergias = models.CharField(max_length=255, blank=True, null=True)
    enfermedades_cronicas = models.TextField(blank=True, null=True)
    medicamentos_actuales = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Análisis Médico de {self.paciente.nombres} {self.paciente.apellido_paterno}"