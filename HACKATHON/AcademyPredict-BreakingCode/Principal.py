import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns 

# configuracion streamlit
st.set_page_config(page_title="Dashboard Academico", layout="wide")

# carga de datos
@st.cache_data
def cargar_datos():
    folder = "datasets"
    est  = pd.read_csv(os.path.join(folder, "estudiantes.csv"))
    rend = pd.read_csv(os.path.join(folder, "rendimiento.csv"))
    obs  = pd.read_csv(os.path.join(folder, "observaciones.csv"))

    # nota y asistencia
    periodos = ["P1", "P2", "P3", "P4"]
    rend["nota"] = rend["CF"].fillna(rend[periodos].mean(axis=1))
    stats = rend.groupby("id_estudiante").agg(
        nota_promedio=("nota", "mean"),
        asistencia=("asistencia", "mean")
        
    ).reset_index()

    # cantidad de observaciones
    obs_count = obs["id_estudiante"].value_counts().reset_index()
    obs_count.columns = ["id_estudiante", "n_observaciones"]

    df = est.merge(stats, on="id_estudiante", how="left")\
            .merge(obs_count, on="id_estudiante", how="left")
    df["n_observaciones"] = df["n_observaciones"].fillna(0)
    df["asistencia"]= df['asistencia']/100 # dividimos esta columnas para poder aplicarles el formato de porcentaje
    df["Periodos"] = np.tile(["P1", "P2", "P3", "P4"], len(df) // 4 + 1)[:len(df)]
    return df

df = cargar_datos()

# KPIs
st.title("📊 Dashboard Academico")

col1, col2, col3, col4 = st.columns(4)
col1.metric("📚 Total Estudiantes", len(df))
col2.metric("📈 Promedio General", f"{df['nota_promedio'].mean():.1f}")
col3.metric("✅ Asistencia Porcentual (%)", f"{(df['asistencia'].mean()):.1%}")
col4.metric("📝 Observaciones Totales", df["n_observaciones"].sum())

# graficos generalizados de estudiantes
col1, col2 = st.columns(2)

with col1:
   
    plt.style.use("ggplot") # le agregamos un estilo a los graficos
    st.subheader("📊 Distribucion de notas")
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.barplot(data=df, y= "nota_promedio", x= "Periodos", color= "skyblue", alpha= 0.9, ax= ax, errorbar= None)
    ax.set_xlabel("Nota promedio")
    ax.set_ylabel("Estudiantes")
    st.pyplot(fig)

with col2:
    st.subheader("📈 Asistencia vs Nota")
    fig, ax = plt.subplots(figsize=(4, 4))
    sns.scatterplot(x= 'asistencia', y= 'nota_promedio', hue= "genero", color= ['teal', 'blue'], ax= ax, data= df)
    ax.set_xlabel("Asistencia (%)")
    ax.set_ylabel("Nota promedio")
    st.pyplot(fig)

# tabla resumen
st.subheader("📋 Resumen Por Estudiante")
st.dataframe(df[["id_estudiante", "nombre_estudiante", "nota_promedio", "asistencia", "n_observaciones"]]
             .style.format({"nota_promedio": "{:.1f}", "asistencia": "{:.0%}"})) # le elimine el signo de % que provocaba el cambio

# selector individual
st.subheader("🔍 Detalle Individual")
sel = st.selectbox("Seleccione Estudiante", sorted(df["nombre_estudiante"].dropna().astype(str).unique()))
row = df[df["nombre_estudiante"] == sel].iloc[0]
st.write(f"**Nota:** {row['nota_promedio']:.1f} | **Asistencia:** {(row['asistencia']):.1%} | **Observaciones:** {int(row['n_observaciones'])}")

st.markdown("---")
st.caption("📊 Dashboard Academico | Dataset 2025")