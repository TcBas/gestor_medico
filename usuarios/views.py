from django.shortcuts import render, redirect
from .forms import RegistroEstudianteForm
from django.contrib import messages
from usuarios import views  # ✅ Cambia 'usuarios' por el nombre real de tu app.


def registro_estudiante(request):
    if request.method == 'POST':
        form = RegistroEstudianteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroEstudianteForm()
    return render(request, 'registro.html', {'form': form})