import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from core.data_loader import load_master, load_areas
from core.perfil_textual import generar_perfil_textual
from core.semantic_matcher import recomendar_areas

# CONFIG STREAMLIT

st.set_page_config(
    page_title="Recomendacion de Area Academica",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 Recomendacion de Areas Academicas")
st.caption("Basado en perfil academico, contexto social y observaciones")

# CARGA DE DATOS

df = load_master()
areas = load_areas()

areas["texto_area"] = (
    areas["nombre_area"].astype(str) + ". " +
    areas["descripcion"].astype(str)
)

# SELECCIoN ESTUDIANTE

st.subheader("🎓 Selecciona un estudiante")

names = (
    df["nombre_estudiante"]
    .dropna()
    .astype(str)
    .sort_values()
    .unique()
)

sel = st.selectbox("Estudiante", names)
row = df[df["nombre_estudiante"] == sel].iloc[0]

# MeTRICAS

c1, c2, c3 = st.columns(3)

c1.metric("Nota promedio", f"{row['nota_promedio']:.1f}")
c2.metric("Asistencia", f"{row['asistencia']:.1f}%")
c3.metric("Contexto social (CS)", f"{row['CS']:.2f}")

# PERFIL TEXTUAL

st.subheader("🧠 Perfil integral del estudiante")

perfil_texto = generar_perfil_textual(row)
st.write(perfil_texto)

# RECOMENDACION DE AREAS

st.subheader("🎯 Areas academicas recomendadas")

ranking = recomendar_areas(perfil_texto, areas)

top = ranking.head(3)

for _, r in top.iterrows():
    st.success(f"**{r['nombre_area']}** — Afinidad {r['afinidad']:.1%}")
    st.caption(r["descripcion"])

# TABLA COMPLETA

st.write("### 📊 Afinidad por area academica")

tabla = ranking[["nombre_area", "afinidad"]].copy()

st.dataframe(
    tabla.style.format({"afinidad": "{:.2%}"}),
    use_container_width=True
)

# GRAFICO RADIAL

st.write("### 🧭 Distribucion de afinidad")

labels = tabla["nombre_area"].tolist()
values = tabla["afinidad"].tolist()

angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
values_c = values + values[:1]
angles_c = np.concatenate([angles, [angles[0]]])

fig = plt.figure(figsize=(2.6, 2.6))
ax = fig.add_subplot(111, polar=True)

ax.plot(angles_c, values_c, linewidth=1.2)
ax.fill(angles_c, values_c, alpha=0.25)

ax.set_xticks(angles)
ax.set_xticklabels(labels, fontsize=7)

ax.set_yticklabels([])
ax.set_ylim(0, 1)
ax.grid(alpha=0.3)
ax.spines["polar"].set_visible(False)

st.pyplot(fig)

# OBSERVACIONES

st.subheader("📝 Observaciones registradas")

if isinstance(row["observaciones"], str) and len(row["observaciones"]) > 0:
    with st.expander("Ver observaciones"):
        for obs in row["observaciones"].split("|"):
            st.write("• " + obs.strip())
else:
    st.info("Este estudiante no tiene observaciones registradas.")

# FOOTER

st.markdown("---")
st.caption(
    "Sistema basado en perfiles explicables + matching semantico (TF-IDF). "
    "No clasifica estudiantes, orienta decisiones."
)
