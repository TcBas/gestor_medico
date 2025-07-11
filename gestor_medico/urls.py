from django.contrib import admin
from django.urls import path
from .views import index  # Importa la vista index principal
from usuarios import views  # Importa tus vistas personalizadas
from django.contrib.auth import views as auth_views

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
    path('perfil_estudiante/', views.perfil_estudiante, name='perfil_estudiante'),
    path('editar_perfil_estudiante/', views.editar_perfil_estudiante, name='editar_perfil_estudiante'),
    path('perfil_doctor/', views.perfil_doctor, name='perfil_doctor'),

    # ✅ Cierre de sesión
    path('logout/', views.logout_view, name='logout'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
