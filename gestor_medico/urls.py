from django.contrib import admin
from django.urls import path
from .views import index  # Importa la vista index principal
from usuarios import views  # Importa tus vistas personalizadas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),  # Página principal

    # ✅ Login con tu vista personalizada que redirige según tipo de usuario
    path('login/', views.login_view, name='login'),

    # ✅ Registro de usuario (dejamos solo esta)
    path('registro/', views.registro_estudiante, name='registro'),

    # ✅ Vistas según rol
    path('vista_estudiante/', views.vista_estudiante, name='vista_estudiante'),
    path('vista_doctor/', views.vista_doctor, name='vista_doctor'),

    # ✅ Cierre de sesión
    path('logout/', views.logout_view, name='logout'),
]
