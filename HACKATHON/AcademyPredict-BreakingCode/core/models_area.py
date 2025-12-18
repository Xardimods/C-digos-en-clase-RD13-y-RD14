from core.nlp import (
    limpiar_texto,
    quitar_acentos,
    score_keywords
)
from core.config import (
    PALABRAS_CIENCIA,
    PALABRAS_NUMERO,
    PALABRAS_SOCIAL,
    MODIFICADORES,
    RIESGO_EXPR
)


def calc_scores(obs_list):
    if not isinstance(obs_list, list):
        return 0, 0, 0

    texto = limpiar_texto(" ".join(obs_list))
    texto = limpiar_texto(texto)
    texto = quitar_acentos(texto)

    sc = score_keywords(texto, PALABRAS_CIENCIA, MODIFICADORES)
    sn = score_keywords(texto, PALABRAS_NUMERO, MODIFICADORES)
    ss = score_keywords(texto, PALABRAS_SOCIAL, MODIFICADORES)

    riesgo = score_keywords(texto, RIESGO_EXPR)

    sc -= riesgo * 0.2
    sn -= riesgo * 0.2
    ss -= riesgo * 0.2

    return max(0, sc), max(0, sn), max(0, ss)