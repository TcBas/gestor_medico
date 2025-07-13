# Usa una imagen oficial de Python
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libmariadb-dev && \
    rm -rf /var/lib/apt/lists/*

# Copia los requirements e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el proyecto
COPY . .

# Puerto que expone el contenedor
EXPOSE 80

# Comando para ejecutar la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]