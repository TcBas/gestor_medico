from django.conf import settings
from google import genai


# =========================
# CONFIGURACIÓN GEMINI (SDK NUEVO)
# =========================
client = genai.Client(api_key=settings.GEMINI_API_KEY)


# =========================
# ASISTENTE MÉDICO
# =========================
def asistente_medico(paciente, analisis):
    """
    Genera un resumen clínico usando Gemini (SDK nuevo).
    Seguro contra None y errores.
    """

    if analisis is None:
        return "⚠️ No hay datos médicos registrados para este paciente."

    # Valores seguros
    peso = analisis.peso or "No registrado"
    altura = analisis.altura or "No registrada"
    sexo = analisis.sexo or "No especificado"
    tipo_sangre = analisis.tipo_sangre or "No especificado"
    alergias = analisis.alergias or "Ninguna"
    enfermedades = analisis.enfermedades_cronicas or "Ninguna"
    medicamentos = analisis.medicamentos_actuales or "Ninguno"
    observaciones = analisis.observaciones or "Sin observaciones"
    diagnostico = analisis.diagnostico or "No registrado"

    prompt = f"""
Eres un asistente médico profesional.

Paciente:
Nombre: {paciente.nombres} {paciente.apellido_paterno}
Sexo: {sexo}

Datos clínicos:
- Peso: {peso}
- Altura: {altura}
- Tipo de sangre: {tipo_sangre}
- Alergias: {alergias}
- Enfermedades crónicas: {enfermedades}
- Medicamentos actuales: {medicamentos}
- Observaciones: {observaciones}
- Diagnóstico previo: {diagnostico}

Genera un resumen clínico profesional, claro y conciso.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        return response.text.strip()

    except Exception as e:
        return f"❌ Error al generar resumen con IA: {str(e)}"
