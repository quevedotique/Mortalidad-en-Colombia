"""
Módulo de integración con Google Antigravity (Gemini API).
Provee: generación de hipótesis epidemiológicas, predicción de tendencias,
traducción CIE-10 y clustering de riesgo municipal.
"""

import os
import json
import re
import google.generativeai as genai

_API_KEY = os.getenv("GEMINI_API_KEY", "")
_MODEL_CANDIDATES = [
    "gemini-1.5-flash-002",
    "gemini-1.5-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro"
]


def _configure_genai() -> bool:
    if not _API_KEY:
        return False
    genai.configure(api_key=_API_KEY)
    return True


def _generate_text(prompt: str) -> str:
    if not _configure_genai():
        raise RuntimeError("La variable de entorno GEMINI_API_KEY no está configurada.")

    last_error = None
    for model_name in _MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(prompt)
            return resp.text
        except Exception as e:
            last_error = e
            message = str(e)
            if re.search(r"404|not found|ModelService\.ListModels|list_models|not supported|quota exceeded|429|free_tier", message, re.I):
                continue
            raise

    raise RuntimeError(
        f"No se pudo conectar con ningún modelo Gemini válido. "
        f"Intentados: {', '.join(_MODEL_CANDIDATES)}. Último error: {last_error}"
    )


def generar_hipotesis(resumen: dict) -> str:
    prompt = f"""Eres un epidemiólogo experto en salud pública colombiana.
Analiza estos datos de mortalidad del año 2019 y redacta un párrafo de diagnóstico con hallazgos clave y recomendaciones de política pública.
Usa un tono técnico pero comprensible. Máximo 200 palabras. Responde en español.

Datos del segmento:
- Departamento: {resumen.get('departamento', 'Colombia')}
- Sexo: {resumen.get('sexo', 'Todos')}
- Grupo de edad: {resumen.get('edad', 'Todos')}
- Total de muertes: {resumen.get('total_muertes', 0):,}
- Media nacional de referencia: {resumen.get('media_nacional', 0):,.0f}
- % de causas externas (homicidios/accidentes): {resumen.get('pct_externas', 0):.1f}%
- Top 3 causas: {json.dumps(resumen.get('top_causas', []), ensure_ascii=False)}
"""
    try:
        return _generate_text(prompt)
    except Exception as e:
        return f"Error al consultar la IA: {e}"


def predecir_tendencia_mensual(datos_mes: list[dict]) -> str:
    prompt = f"""Eres un bioestadístico. Analiza la siguiente serie mensual de muertes en Colombia 2019.
Identifica patrones de estacionalidad, meses con picos anómalos y posibles causas contextuales (clima, festividades, epidemias estacionales en Colombia).
Máximo 150 palabras. Responde en español.

Serie mensual: {json.dumps(datos_mes, ensure_ascii=False)}
"""
    try:
        return _generate_text(prompt)
    except Exception as e:
        return f"Error al consultar la IA: {e}"


def traducir_cie10(codigo: str, descripcion_tecnica: str) -> str:
    prompt = f"""Traduce este código y descripción médica CIE-10 a un lenguaje simple que entienda cualquier ciudadano colombiano.
Máximo 10 palabras. Solo devuelve la traducción, sin explicaciones.

Código: {codigo}
Descripción técnica: {descripcion_tecnica}
"""
    try:
        return _generate_text(prompt).strip()
    except Exception:
        return descripcion_tecnica


def clasificar_riesgo_municipios(municipios_data: list[dict]) -> list[dict]:
    """
    municipios_data: lista de {'municipio': str, 'total_muertes': int, 'top_causa': str}
    Devuelve la misma lista con campo 'nivel_riesgo': 'Alto'|'Medio'|'Bajo'
    """
    def _fallback_cuartiles(data):
        totales = sorted([m['total_muertes'] for m in data])
        n = len(totales)
        q1 = totales[n // 3] if n > 3 else 0
        q2 = totales[2 * n // 3] if n > 3 else 0
        for m in data:
            if m['total_muertes'] >= q2:
                m['nivel_riesgo'] = 'Alto'
            elif m['total_muertes'] >= q1:
                m['nivel_riesgo'] = 'Medio'
            else:
                m['nivel_riesgo'] = 'Bajo'
        return data

    # ← FIX: antes hacía _generate_text("") que crashea con Gemini
    if not _configure_genai():
        return _fallback_cuartiles(municipios_data)

    sample = municipios_data[:50]
    prompt = f"""Clasifica estos municipios colombianos en niveles de riesgo de mortalidad: Alto, Medio o Bajo.
Devuelve SOLO un JSON array con los mismos objetos más el campo "nivel_riesgo".
No incluyas markdown, solo el JSON puro.

Municipios: {json.dumps(sample, ensure_ascii=False)}
"""
    try:
        text = _generate_text(prompt).strip()
        text = re.sub(r'^```[a-z]*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
        clasificados = json.loads(text)
        nombres_clasif = {m['municipio'] for m in clasificados}
        for m in municipios_data:
            if m['municipio'] not in nombres_clasif:
                m['nivel_riesgo'] = 'Medio'
                clasificados.append(m)
        return clasificados
    except Exception:
        return _fallback_cuartiles(municipios_data)