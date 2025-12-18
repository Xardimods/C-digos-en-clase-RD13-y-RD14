def generar_perfil_textual(row):
    partes = []

    partes.append(
        f"Estudiante de {row['edad']} años con nota promedio de {row['nota_promedio']:.1f} "
        f"y asistencia del {row['asistencia']:.1f}%."
    )

    if row["F"] >= 0.7:
        partes.append("Presenta un entorno emocional y escolar favorable.")
    elif row["F"] >= 0.4:
        partes.append("Presenta un entorno social mixto.")
    else:
        partes.append("Se identifica un entorno social vulnerable.")

    if row["score_ciencia"] > 0:
        partes.append("Muestra interés por ciencias y experimentacion.")
    if row["score_num"] > 0:
        partes.append("Posee afinidad por el razonamiento logico y numérico.")
    if row["score_social"] > 0:
        partes.append("Destaca en habilidades sociales y comunicacion.")

    if isinstance(row["observaciones"], str):
        partes.append("Observaciones relevantes: " + row["observaciones"])

    return " ".join(partes)
