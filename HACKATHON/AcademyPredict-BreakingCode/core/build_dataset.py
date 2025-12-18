# core/build_dataset.py

import os
import pandas as pd
import numpy as np

from core.data_loader import load_base_data
from core.nlp import (
    puntaje_ambiente,
    limpiar_texto,
    quitar_acentos,
    score_keywords
)
from core.config import (
    PALABRAS_CIENCIA,
    PALABRAS_NUMERO,
    PALABRAS_SOCIAL,
    MODIFICADORES
)
from core.models_riesgo import calcular_riesgo

# Paths

BASE_PATH = "datasets"
RAW_PATH = f"{BASE_PATH}"
PROC_PATH = f"{BASE_PATH}/processed"
MASTER_PATH = f"{BASE_PATH}/master"

os.makedirs(PROC_PATH, exist_ok=True)
os.makedirs(MASTER_PATH, exist_ok=True)

# Helpers

def calc_scores(obs_list):
    if not isinstance(obs_list, list):
        return 0, 0, 0

    texto = limpiar_texto(" ".join(obs_list))
    texto = quitar_acentos(texto)

    sc = score_keywords(texto, PALABRAS_CIENCIA, MODIFICADORES)
    sn = score_keywords(texto, PALABRAS_NUMERO, MODIFICADORES)
    ss = score_keywords(texto, PALABRAS_SOCIAL, MODIFICADORES)

    return max(0, sc), max(0, sn), max(0, ss)

# Builder principal

def build_master_dataset(
    anio_academico="2025-2026",
    semestre=1,
    modelo_nlp=None
):
    data = load_base_data()

    est = data["est"]
    rend = data["rend"]
    obs = data["obs"]

    #  CONTEXTO SOCIAL (opcional) 
    try:
        cs = pd.read_csv(f"{RAW_PATH}/contexto_formulario.csv")
        
    except FileNotFoundError:
        cs = pd.DataFrame(columns=["id_estudiante", "CS"])

    # RENDIMIENTO 
    rend = rend[
        (rend["año_academico"] == anio_academico) &
        (rend["semestre"] == semestre)
    ]

    periodos = ["P1", "P2", "P3", "P4"]
    rend["nota"] = rend["CF"].fillna(rend[periodos].mean(axis=1))

    rend_agg = (
        rend.groupby("id_estudiante")
        .agg(
            nota_promedio=("nota", "mean"),
            asistencia=("asistencia", "mean"),
            var_nota=("nota", "std") # desviacion estandar como varianza
        )
        .reset_index()
    )

    rend_agg["var_nota"] = rend_agg["var_nota"].fillna(0)
    rend_agg.to_csv(f"{PROC_PATH}/rendimiento_agg.csv", index=False)

    # OBSERVACIONES 
    obs_agg = (
        obs.groupby("id_estudiante")["observacion"]
        .apply(list)
        .reset_index()
    )

    obs_agg["F"] = obs_agg["observacion"].apply(
        lambda x: puntaje_ambiente(" ".join(x), modelo_nlp)
        if isinstance(x, list) else 0.5
    )

    obs_agg["var_F"] = obs_agg["observacion"].apply( # variablidad del contexto, ambiente segun las observaciones
        lambda x: np.std([
            puntaje_ambiente(o, modelo_nlp) for o in x
        ]) if isinstance(x, list) and len(x) > 1 else 0
    )

    obs_agg["num_obs"] = obs_agg["observacion"].apply(len)
    obs_agg[["score_ciencia", "score_num", "score_social"]] = (
        obs_agg["observacion"]
        .apply(lambda x: pd.Series(calc_scores(x)))
    )

    obs_agg["observaciones"] = obs_agg["observacion"].apply(
        lambda x: " | ".join(x)
    )

    obs_agg.drop(columns=["observacion"], inplace=True)
    obs_agg.to_csv(f"{PROC_PATH}/observaciones_agg.csv", index=False)

    # CONTEXTO SOCIAL 
    if "CS_fuente" not in cs.columns:
        cs["CS_fuente"] = "formulario"

    cs.to_csv(f"{PROC_PATH}/contexto_formulario.csv", index=False)

    cs["CS"] = pd.to_numeric(cs["CS"], errors="coerce")
    cs["CS"] = cs["CS"].clip(0, 1)

    # MASTER MERGE 
    df = (
        est
        .merge(rend_agg, on="id_estudiante", how="left")
        .merge(obs_agg, on="id_estudiante", how="left")
        .merge(cs, on="id_estudiante", how="left")
    )

    df["CS"] = df["CS"].fillna(0.5)

    # RIESGO 
    df[["Rd", "F"]] = df.apply(
        lambda r: pd.Series(calcular_riesgo(r, modelo_nlp)),
        axis=1
    )

    # SAVE MASTER 
    fname = f"df_master_{anio_academico}_{semestre}.csv"
    path = f"{MASTER_PATH}/{fname}"
    df.to_csv(path, index=False)

    return path
