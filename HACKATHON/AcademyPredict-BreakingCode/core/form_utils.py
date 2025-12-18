# core/form_utils.py

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def norm_slider(valor, min_v=1, max_v=5):
    """Normaliza sliders 1–5 a 0–1"""
    return (valor - min_v) / (max_v - min_v)


def calcular_riesgo_desde_form(d: dict) -> float:
    """
    Calcula F (contexto) ∈ [0,1]
    usando pesos por bloque y promedios reales
    """

    # ---------- BLOQUES NORMALIZADOS ----------
    familia = clamp01(d.get("familia_normalizado", 0))

    educ = clamp01(d.get("educacion_normalizado", 0))
    laboral = clamp01(d.get("laboral_normalizado", 0))
    recursos = clamp01(d.get("recursos_normalizado", 0))

    salud = (
        norm_slider(d.get("salud_general", 3)) * 0.6 +
        clamp01(d.get("salud_acceso_normalizado", 0)) * 0.4
    )

    habitos = (
        norm_slider(d.get("horas_estudio", 2), 0, 8) * 0.35 +
        clamp01(d.get("actividades_normalizado", 0)) * 0.35 +
        norm_slider(d.get("asistencia_escuela", 4)) * 0.30
    )

    animo = (
        clamp01(d.get("animo_normalizado", 0)) * 0.5 +
        norm_slider(d.get("motivacion_estudio", 3)) * 0.5
    )

    contexto_social = (
        norm_slider(d.get("apoyo_familiar", 3)) * 0.35 +
        norm_slider(d.get("integracion_companeros", 3)) * 0.35 +
        (1 - clamp01(d.get("violencia_normalizado", 0))) * 0.30
    )

    extras = (
        clamp01(d.get("transporte_normalizado", 0)) * 0.33 +
        clamp01(d.get("servicios_normalizado", 0)) * 0.34 +
        clamp01(d.get("cultura_normalizado", 0)) * 0.33
    )

    # ---------- PESOS GLOBALES ----------
    PESOS = {
        "familia": 0.15,
        "educ": 0.10,
        "laboral": 0.10,
        "recursos": 0.10,
        "salud": 0.10,
        "habitos": 0.15,
        "animo": 0.15,
        "social": 0.10,
        "extra": 0.05
    }

    F = (
        familia * PESOS["familia"] +
        educ * PESOS["educ"] +
        laboral * PESOS["laboral"] +
        recursos * PESOS["recursos"] +
        salud * PESOS["salud"] +
        habitos * PESOS["habitos"] +
        animo * PESOS["animo"] +
        contexto_social * PESOS["social"] +
        extras * PESOS["extra"]
    )

    return round(clamp01(F), 4)