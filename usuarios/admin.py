from django.contrib import admin
from .models import Perfil, Cita

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'tipo', 'dni', 'telefono')
    list_filter = ('tipo',)
    search_fields = ('nombres', 'apellido_paterno', 'apellido_materno', 'dni')

    # Función para mostrar nombre completo
    def nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellido_paterno} {obj.apellido_materno or ''}".strip()
    nombre_completo.short_description = 'Nombre Completo'

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'doctor', 'fecha', 'estado')
    list_filter = ('estado',)
    search_fields = ('motivo',)
