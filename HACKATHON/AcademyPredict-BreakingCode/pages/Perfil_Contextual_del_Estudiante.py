
import streamlit as st
import pandas as pd
import os
from core.form_utils import calcular_riesgo_desde_form

st.set_page_config(page_title="Formulario Contexto", page_icon="🎓", layout="wide")

st.markdown("""
<style>
h1 {color: #1e3a5f;}
h2 {color: #2c5282; border-bottom: 2px solid #4299e1; padding-bottom: 10px;}
h3 {color: #3182ce;}
</style>
""", unsafe_allow_html=True)

st.title("🎓 Formulario de Contexto Estudiantil")
st.markdown("### Evaluacion de factores de riesgo y apoyo")
st.markdown("---")

if st.button("🔄 Nueva evaluacion"):
    st.rerun()
    
@st.cache_data
def cargar_estudiantes():
    ruta = os.path.join("datasets", "estudiantes.csv")
    if not os.path.exists(ruta):
        return pd.DataFrame(columns=["id_estudiante", "nombre_estudiante", "edad", "genero", "semestre_actual", "estado_academico"])
    return pd.read_csv(ruta)

df_estudiantes = cargar_estudiantes()

st.subheader("🔍 Seleccionar estudiante")
if not df_estudiantes.empty:
    opciones = ["Ninguno"] + [f"{row.id_estudiante} - {row.nombre_estudiante}" for _, row in df_estudiantes.iterrows()]
    seleccion = st.selectbox("Estudiante", opciones)

    estudiante_seleccionado = None
    if seleccion != "Ninguno":
        id_sel = int(seleccion.split(" - ")[0])
        estudiante_seleccionado = df_estudiantes[df_estudiantes.id_estudiante == id_sel].iloc[0]
else:
    estudiante_seleccionado = None

with st.form("context_form"):
    st.header("1. 🔍 Estudiante seleccionado")
    if estudiante_seleccionado is not None:
        st.info(
            f"**ID:** {estudiante_seleccionado.id_estudiante}  \n"
            f"**Nombre:** {estudiante_seleccionado.nombre_estudiante}  \n"
            f"**Edad:** {estudiante_seleccionado.edad}  \n"
            f"**Grado:** 5° Secundaria"
        )
    else:
        st.warning("⚠️ No has seleccionado un estudiante. El formulario no se puede enviar.")

    # Contexto Familiar
    st.header("2. 👨‍👩‍👧‍👦 Contexto Familiar")
    conv = st.radio("¿Con quien vives principalmente?", ["Ambos padres", "Padre", "Madre", "Otro familiar/tutor", "Ninguno"], index=0, help="Selecciona la opcion principal")
    hermanos = st.number_input("¿Cuantos hermanos tienes?", 0, 15, 0)

    st.subheader("Nivel educativo de los padres/tutores")
    edu_cols = st.columns(2)
    edu_univ = edu_cols[0].checkbox("Universitario", key="edu_univ")
    edu_sec  = edu_cols[0].checkbox("Secundaria", key="edu_sec")
    edu_prim = edu_cols[1].checkbox("Primaria", key="edu_prim")
    edu_otro = edu_cols[1].checkbox("Otro nivel", key="edu_otro")

    st.subheader("Estado laboral de los padres/tutores")
    lab_cols = st.columns(2)
    lab_emp  = lab_cols[0].checkbox("Empleado", key="lab_emp")
    lab_ind  = lab_cols[0].checkbox("Independiente/Emprendedor", key="lab_ind")
    lab_otro = lab_cols[1].checkbox("Otro estado", key="lab_otro")
    lab_des  = lab_cols[1].checkbox("Desempleado", key="lab_des")

    st.subheader("Recursos educativos en casa")
    rec_cols = st.columns(2)
    rec_int = rec_cols[0].checkbox("🌐 Internet", key="rec_int")
    rec_pc  = rec_cols[0].checkbox("💻 Computadora", key="rec_pc")
    rec_lib = rec_cols[1].checkbox("📚 Libros", key="rec_lib")
    rec_tut = rec_cols[1].checkbox("👨‍🏫 Tutorias", key="rec_tut")

    # Seguridad y Entorno
    st.header("3. 🏘️ Seguridad y Entorno")
    seguridad = st.slider("Seguridad del barrio", 1, 5, 3, help="1=Muy inseguro, 5=Muy seguro")
    vio_cols = st.columns(2)
    vio_robos  = vio_cols[0].checkbox("🚨 Robos", key="vio_robos")
    vio_peleas = vio_cols[0].checkbox("👊 Peleas", key="vio_peleas")
    vio_drogas = vio_cols[1].checkbox("💊 Drogas", key="vio_drogas")
    vio_acoso  = vio_cols[1].checkbox("😰 Acoso", key="vio_acoso")
    ruido = st.slider("Ruido que afecta el estudio", 1, 5, 3, help="1=Ninguno, 5=Mucho")
    esp_cols = st.columns(2)
    esp_bib  = esp_cols[0].checkbox("📖 Biblioteca", key="esp_bib")
    esp_cent = esp_cols[0].checkbox("🏛️ Centro comunitario", key="esp_cent")
    esp_otro = esp_cols[1].checkbox("🏫 Otro espacio", key="esp_otro")

    # Salud y Bienestar
    st.header("4. 🏥 Salud y Bienestar")
    salud_general = st.slider("Estado general de salud", 1, 5, 3, help="1=Muy malo, 5=Excelente")
    sal_cols = st.columns(2)
    sal_seg  = sal_cols[0].checkbox("📋 Seguro medico", key="sal_seg")
    sal_hosp = sal_cols[0].checkbox("🏥 Hospital", key="sal_hosp")
    sal_clin = sal_cols[1].checkbox("🩺 Clinica", key="sal_clin")
    sal_no   = sal_cols[1].checkbox("❌ Ningún acceso", key="sal_no")

    cond_cols = st.columns(2)
    cond_vis  = cond_cols[0].checkbox("👁️ Visual", key="cond_vis")
    cond_aud  = cond_cols[0].checkbox("👂 Auditiva", key="cond_aud")
    cond_emo  = cond_cols[1].checkbox("💭 Emocional", key="cond_emo")
    cond_otra = cond_cols[1].checkbox("🔷 Otra condicion", key="cond_otra")

    # Comportamiento y Habitos
    st.header("5. 📖 Comportamiento y Habitos")
    horas = st.slider("Horas de estudio diarias", 0, 8, 2)
    act_cols = st.columns(2)
    act_dep  = act_cols[0].checkbox("⚽ Deportes", key="act_dep")
    act_arte = act_cols[0].checkbox("🎨 Arte", key="act_arte")
    act_ciencia = act_cols[1].checkbox("🔬 Ciencia", key="act_ciencia")
    act_vol  = act_cols[1].checkbox("🤝 Voluntariado", key="act_vol")

    disp_cols = st.columns(2)
    disp_pc  = disp_cols[0].checkbox("💻 Computadora", key="disp_pc")
    disp_tab = disp_cols[0].checkbox("📱 Tablet", key="disp_tab")
    disp_cel = disp_cols[1].checkbox("📲 Celular", key="disp_cel")
    disp_no  = disp_cols[1].checkbox("❌ Ningún dispositivo", key="disp_no")

    asistencia = st.slider("Asistencia escolar", 1, 5, 4, help="1=Muy baja, 5=Perfecta")

    # Contexto Emocional y Social
    st.header("6. 💚 Contexto Emocional y Social")
    apoyo_fam   = st.slider("Apoyo familiar", 1, 5, 3)
    integracion = st.slider("Integracion con compañeros", 1, 5, 3)
    bullying    = st.radio("¿Has enfrentado bullying o acoso?", ["No", "Si"], horizontal=True)

    animo_cols = st.columns(2)
    ani_alegre = animo_cols[0].checkbox("😊 Alegre", key="ani_alegre")
    ani_neutral= animo_cols[0].checkbox("😐 Neutral", key="ani_neutral")
    ani_triste = animo_cols[1].checkbox("😢 Triste", key="ani_triste")
    ani_ansioso= animo_cols[1].checkbox("😰 Ansioso", key="ani_ansioso")
    ani_otro   = st.checkbox("🔷 Otro", key="ani_otro")

    motivacion = st.slider("Motivacion por el estudio", 1, 5, 3)

    # Percepcion Academica
    st.header("7. 📚 Percepcion Academica")
    mat_cols = st.columns(3)
    mat_mat = mat_cols[0].checkbox("🔢 Matematicas", key="mat_mat")
    mat_cie = mat_cols[0].checkbox("🔬 Ciencias", key="mat_cie")
    mat_his = mat_cols[1].checkbox("📜 Historia", key="mat_his")
    mat_idi = mat_cols[1].checkbox("🌍 Idiomas", key="mat_idi")
    mat_art = mat_cols[2].checkbox("🎨 Arte", key="mat_art")
    mat_dep = mat_cols[2].checkbox("⚽ Deportes", key="mat_dep")

    area_cols = st.columns(2)
    area_log = area_cols[0].checkbox("🧮 Logico-matematico", key="area_log")
    area_cie = area_cols[0].checkbox("🔭 Cientifico", key="area_cie")
    area_soc = area_cols[1].checkbox("🤝 Social", key="area_soc")
    area_art = area_cols[1].checkbox("🎭 Artistico", key="area_art")
    area_dep = st.checkbox("🏃 Deportivo", key="area_dep")

    meta_cols = st.columns(2)
    meta_apro  = meta_cols[0].checkbox("✅ Aprobar todo", key="meta_apro")
    meta_mej   = meta_cols[0].checkbox("📈 Mejorar areas debiles", key="meta_mej")
    meta_part  = meta_cols[1].checkbox("🎯 Participar en proyectos", key="meta_part")
    meta_hab   = meta_cols[1].checkbox("💡 Desarrollar habilidades", key="meta_hab")

    largo_cols = st.columns(2)
    largo_univ = largo_cols[0].checkbox("🎓 Universidad", key="largo_univ")
    largo_carr = largo_cols[0].checkbox("💼 Carrera especifica", key="largo_carr")
    largo_beca = largo_cols[1].checkbox("🏅 Becas", key="largo_beca")
    largo_comp = largo_cols[1].checkbox("🛠️ Competencias", key="largo_comp")

    # Contexto Ampliado
    st.header("8. 📊 Contexto Ampliado (opcional)")
    trans_cols = st.columns(2)
    trans_pub = trans_cols[0].checkbox("🚌 Transporte público", key="trans_pub")
    trans_pri = trans_cols[0].checkbox("🚗 Transporte privado", key="trans_pri")
    trans_cam = trans_cols[1].checkbox("🚶 Camina", key="trans_cam")

    serv_cols = st.columns(2)
    serv_agua = serv_cols[0].checkbox("💧 Agua potable", key="serv_agua")
    serv_luz  = serv_cols[0].checkbox("💡 Electricidad", key="serv_luz")
    serv_san  = serv_cols[1].checkbox("🚽 Saneamiento", key="serv_san")
    serv_int  = serv_cols[1].checkbox("📶 Internet hogar", key="serv_int")

    cult_cols = st.columns(2)
    cult_bib = cult_cols[0].checkbox("📚 Biblioteca pública", key="cult_bib")
    cult_mus = cult_cols[0].checkbox("🏛️ Museo", key="cult_mus")
    cult_cin = cult_cols[1].checkbox("🎬 Cine", key="cult_cin")
    cult_par = cult_cols[1].checkbox("🌳 Parques", key="cult_par")

    consent = st.checkbox("Confirmo que la informacion es verdadera y autorizo su uso academico", key="consent")

    # SUBMIT 
    if st.form_submit_button("📝 Enviar Formulario", use_container_width=True, type="primary"):
        if estudiante_seleccionado is None:
            st.error("❌ Debes seleccionar un estudiante antes de enviar.")
            st.stop()
        if not consent:
            st.error("❌ Debes aceptar el consentimiento.")
            st.stop()

        # normalizaciones para form_utils
        familia_norm   = {"Ambos padres": 0.40, "Padre": 0.15, "Madre": 0.15, "Otro familiar/tutor": 0.20, "Ninguno": 0.10}[conv]

        # educacion
        educ_pesos_act = edu_univ*0.45 + edu_sec*0.30 + edu_prim*0.15 + edu_otro*0.10
        educ_vals = []
        if edu_univ: educ_vals.append(0.45)
        if edu_sec:  educ_vals.append(0.30)
        if edu_prim: educ_vals.append(0.15)
        if edu_otro: educ_vals.append(0.10)
        educ_norm = sum(educ_vals) / len(educ_vals) if educ_vals else 0

        # laboral
        lab_pesos_act  = lab_emp*0.40 + lab_ind*0.35 + lab_otro*0.15 + lab_des*0.10
        lab_vals = []
        if lab_emp:  lab_vals.append(0.40)
        if lab_ind:  lab_vals.append(0.35)
        if lab_otro: lab_vals.append(0.15)
        if lab_des:  lab_vals.append(0.10)
        laboral_norm = sum(lab_vals) / len(lab_vals) if lab_vals else 0

        # recursos
        rec_pesos_act  = rec_int*0.30 + rec_pc*0.25 + rec_lib*0.20 + rec_tut*0.15
        rec_vals = []
        if rec_int: rec_vals.append(0.30)
        if rec_pc:  rec_vals.append(0.25)
        if rec_lib: rec_vals.append(0.20)
        if rec_tut: rec_vals.append(0.15)
        recursos_norm = sum(rec_vals) / len(rec_vals) if rec_vals else 0

        # violencia (negativo)
        vio_pesos_act  = vio_robos*0.30 + vio_peleas*0.25 + vio_drogas*0.30 + vio_acoso*0.15
        vio_vals = []
        if vio_robos:  vio_vals.append(0.30)
        if vio_peleas: vio_vals.append(0.25)
        if vio_drogas: vio_vals.append(0.30)
        if vio_acoso:  vio_vals.append(0.15)

        violencia_raw = sum(vio_vals) / len(vio_vals) if vio_vals else 0
        violencia_norm = violencia_raw   # 0–1 (luego se invierte en form_utils)

        # salud acceso
        sal_pesos_act  = sal_seg*0.40 + sal_hosp*0.35 + sal_clin*0.25
        sal_vals = []
        if sal_seg: sal_vals.append(0.40)
        if sal_hosp: sal_vals.append(0.35)
        if sal_clin: sal_vals.append(0.25)
        salud_acc_norm = sum(sal_vals) / len(sal_vals) if sal_vals else 0

        # actividades
        act_pesos_act  = act_ciencia*0.25 + act_vol*0.25 + act_dep*0.20 + act_arte*0.20
        act_vals = []
        if act_ciencia: act_vals.append(0.25)
        if act_vol:     act_vals.append(0.25)
        if act_dep:     act_vals.append(0.20)
        if act_arte:    act_vals.append(0.20)

        act_norm = sum(act_vals) / len(act_vals) if act_vals else 0

        # dispositivos
        disp_pesos_act = disp_pc*0.45 + disp_tab*0.30 + disp_cel*0.15
        disp_vals = []
        if disp_pc:  disp_vals.append(0.45)
        if disp_tab: disp_vals.append(0.30)
        if disp_cel: disp_vals.append(0.15)

        disp_norm = sum(disp_vals) / len(disp_vals) if disp_vals else 0

        # animo
        ani_pesos_act  = ani_alegre*0.50 + ani_neutral*0.25 + ani_otro*0.15
        ani_vals = []
        if ani_alegre:  ani_vals.append(0.50)
        if ani_neutral: ani_vals.append(0.25)
        if ani_otro:    ani_vals.append(0.15)

        animo_norm = sum(ani_vals) / len(ani_vals) if ani_vals else 0

        # materias
        mat_pesos_act  = mat_mat*0.20 + mat_cie*0.20 + mat_idi*0.15 + mat_his*0.15 + mat_art*0.15 + mat_dep*0.15
        mat_vals = []
        if mat_mat: mat_vals.append(0.20)
        if mat_cie: mat_vals.append(0.20)
        if mat_idi: mat_vals.append(0.15)
        if mat_his: mat_vals.append(0.15)
        if mat_art: mat_vals.append(0.15)
        if mat_dep: mat_vals.append(0.15)

        mat_norm = sum(mat_vals) / len(mat_vals) if mat_vals else 0


        # areas
        area_pesos_act = area_log*0.25 + area_cie*0.25 + area_soc*0.20 + area_art*0.15 + area_dep*0.15
        area_vals = []
        if area_log: area_vals.append(0.25)
        if area_cie: area_vals.append(0.25)
        if area_soc: area_vals.append(0.20)
        if area_art: area_vals.append(0.15)
        if area_dep: area_vals.append(0.15)

        area_norm = sum(area_vals) / len(area_vals) if area_vals else 0


        # transporte
        trans_pesos_act= trans_pri*0.45 + trans_pub*0.35 + trans_cam*0.20
        trans_vals = []
        if trans_pri: trans_vals.append(0.45)
        if trans_pub: trans_vals.append(0.35)
        if trans_cam: trans_vals.append(0.20)

        trans_norm = sum(trans_vals) / len(trans_vals) if trans_vals else 0


        # servicios
        serv_pesos_act = serv_agua*0.30 + serv_luz*0.30 + serv_san*0.25 + serv_int*0.15
        serv_vals = []
        if serv_agua: serv_vals.append(0.30)
        if serv_luz:  serv_vals.append(0.30)
        if serv_san:  serv_vals.append(0.25)
        if serv_int:  serv_vals.append(0.15)

        serv_norm = sum(serv_vals) / len(serv_vals) if serv_vals else 0

        # cultura
        cult_pesos_act = cult_bib*0.30 + cult_mus*0.25 + cult_cin*0.15 + cult_par*0.20
        cult_vals = []
        if cult_bib: cult_vals.append(0.30)
        if cult_mus: cult_vals.append(0.25)
        if cult_cin: cult_vals.append(0.15)
        if cult_par: cult_vals.append(0.20)

        cult_norm = sum(cult_vals) / len(cult_vals) if cult_vals else 0


        # diccionario para form_utils
        form_dict = {
            "familia_normalizado": familia_norm,
            "educacion_normalizado": educ_norm,
            "laboral_normalizado": laboral_norm,
            "recursos_normalizado": recursos_norm,
            "salud_general": salud_general,
            "salud_acceso_normalizado": salud_acc_norm,
            "horas_estudio": horas,
            "actividades_normalizado": act_norm,
            "asistencia_escuela": asistencia,
            "dispositivos_normalizado": disp_norm,
            "apoyo_familiar": apoyo_fam,
            "integracion_companeros": integracion,
            "bullying": bullying,
            "animo_normalizado": animo_norm,
            "motivacion_estudio": motivacion,
            "violencia_normalizado": violencia_norm,
            "condiciones_normalizado": (cond_vis*0.25 + cond_aud*0.25 + cond_emo*0.35 + cond_otra*0.15),
            # secciones 8
            "transporte_normalizado": trans_norm,
            "servicios_normalizado": serv_norm,
            "cultura_normalizado": cult_norm,
        }

        F = calcular_riesgo_desde_form(form_dict)

        # guardamos csv
        light = {
            "id_estudiante": estudiante_seleccionado.id_estudiante,
            "CS": F,
        }
        csv_path = os.path.join("datasets", "contexto_formulario.csv")
        os.makedirs("datasets", exist_ok=True)
        csv_path = os.path.join("datasets", "contexto_formulario.csv")
        df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame(columns=["id_estudiante", "CS"])
        df = df[df["id_estudiante"] != estudiante_seleccionado.id_estudiante]
        df = pd.concat([df, pd.DataFrame([{"id_estudiante": estudiante_seleccionado.id_estudiante, "CS": F}])], ignore_index=True)
        df.to_csv(csv_path, index=False)

        st.success(f"✅ Score de contexto (CS) guardado: **{F:.2f}**")
        st.balloons()
        st.rerun()

# sidebar
st.sidebar.title("ℹ️ Informacion")
st.sidebar.info("Formulario de contexto para estimar ambiente (F).")
st.sidebar.title("📊 Estadisticas")
csv_stats = "datasets/contexto_formulario.csv"
if estudiante_seleccionado is not None:
    st.sidebar.subheader("👤 Estudiante seleccionado")
    st.sidebar.write(f"**ID:** {estudiante_seleccionado.id_estudiante}")
    st.sidebar.write(f"**Nombre:** {estudiante_seleccionado.nombre_estudiante}")
    st.sidebar.write(f"**Edad:** {estudiante_seleccionado.edad}")
    st.sidebar.write(f"**Genero:** {estudiante_seleccionado.genero}")
    st.sidebar.write(f"**Estado:** {estudiante_seleccionado.estado_academico}")

if os.path.exists(csv_stats):
    df_stats = pd.read_csv(csv_stats)
    st.sidebar.metric("Total de formularios", len(df_stats))
    st.sidebar.metric("F promedio", f"{df_stats['CS'].mean():.2f}")
else:
    st.sidebar.metric("Total de formularios", 0)