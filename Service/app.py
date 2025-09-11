# LIBRERÍAS

import streamlit as st 
import json
import pandas as pd 
from api_backend import model_service
from datetime import datetime, timedelta
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ruta absoluta al directorio /Service


# CARGA DEL HISTORIAL DE RECLAMOS DESDE JSON

historial_file = os.path.join(BASE_DIR, ".", "historial.json")
historial_file = os.path.abspath(historial_file)
if os.path.exists(historial_file) and os.path.getsize(historial_file) > 0:
    try:
        with open(historial_file, "r", encoding="utf-8") as f:
            historial_data = json.load(f)
            st.session_state.historial_ids = list(historial_data.keys())
            for ident, datos in historial_data.items():
                st.session_state[f"analisis_{ident}"] = datos
    except Exception:
        st.session_state.historial_ids = []
else:
    st.session_state.historial_ids = []


# CONFIGURACIÓN

# Carga de la configuración de Streamlit desde el archivo config.toml que está en .streamlit
config_path = os.path.join(BASE_DIR, "..", ".streamlit", "config.toml")
config_path = os.path.abspath(config_path)

# Configuración general de la app
icono_path = os.path.abspath(os.path.join(BASE_DIR, "..", "Assets", "ai_coche.png"))
st.set_page_config(
    page_title="CarClaim AI",
    page_icon=icono_path, 
    layout="wide"
)

# Inicializar modo
if "modo_actual" not in st.session_state:
    st.session_state.modo_actual = "formulario"

# Carga del schema
ruta_schema = os.path.join(os.path.dirname(__file__), '..', 'Artifacts', 'io_schema.json')
ruta_schema = os.path.abspath(ruta_schema)  
with open(ruta_schema, 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Estilos globales
st.markdown("""
    <style>
    /* Color del texto en los inputs normales */
    input, textarea {
        color: white !important;
    }
    /* Placeholder blanco */
    ::placeholder {
        color: white !important;
        opacity: 1 !important;
    }
    /* Selectbox (más específico para BaseWeb) */
    .stSelectbox div[data-baseweb="select"] > div {
        color: white !important;
    }
    .stSelectbox div[data-baseweb="select"] div[role="option"] {
        color: black !important;  /* Puedes dejar blanco si fondo oscuro */
    }
    /* También sliders */
    .stSlider > div[data-baseweb="slider"] > div {
        color: white !important;
    }
    /* Cambiar el estilo del label del text_input en la sidebar */
    section[data-testid="stSidebar"] div[data-testid="stTextInputLabel"] {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #2b3f51 !important;
    }
    /* ajustar el placeholder si quieres */
    section[data-testid="stSidebar"] input[type="password"]::placeholder {
        color: gray !important;
        font-size: 16px !important;
    }
    /* Input de clave API: texto negro siempre */
    section[data-testid="stSidebar"] input[type="password"],
    section[data-testid="stSidebar"] input[type="text"] {
        color: #2b3f51 !important;
        background-color: white !important;
    }
        /* Cambiar color del botón de historial en el sidebar */
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #2b3f51 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 6px 12px !important;
        font-weight: bold !important;
    }
    /* Opcional: cambiar color al pasar el ratón */
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: #3C556B !important;
        color: #ffffff !important;
    }        
    </style>
""", unsafe_allow_html=True)


# ENCABEZADO UI

col1, col2, col3 = st.columns([3, 2, 1], gap="large")

with col1:
    st.markdown("<h1 style='color: #2b3f51;font-size:60px;'>CarClaim AI</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:16px;'>Bienvenido/a a CarClaim AI, una herramienta diseñada para ayudarte a evaluar el <b>riesgo de fraude en reclamos de seguros de vehículos</b> de forma rápida, objetiva y precisa.</p>",
        unsafe_allow_html=True
    )
    with st.expander("🛈 ¿Cómo funciona esta herramienta?"):
        st.markdown(""" 
            <div style='font-size:15px; padding-bottom: 12px;'>
                    1. Introduce los datos del reclamo en el formulario.<br>
                    2. El Agente IA generará automáticamente un <b>score de fraude</b>, un <b>nivel de riesgo</b> y una serie de <b>recomendaciones prácticas</b>.<br>
                    3. Si introduces una clave de API válida, obtendrás una <b>explicación detallada generada por el asistente IA</b>.<br>
                    4. Utiliza esta información para <b>aprobar, investigar o escalar</b> el reclamo de forma informada.
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style="position: relative; background-color: #2b3f51;
                    padding: 18px 16px; border-radius: 12px;
                    margin-top: 35px; font-size: 14px;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
                    color: white; line-height: 1.5; max-width: 100%;
                    font-size:15px;">
            <b>¡Hola! Soy tu Agente IA.</b> Estoy aquí para acompañarte en el análisis de reclamos de vehículos, identificando riesgos de fraude y ofreciéndote explicaciones útiles y recomendaciones prácticas.
            <div style="
                content: '';
                position: absolute;
                right: -16px;
                top: 35%;
                width: 0;
                height: 0;
                border-top: 10px solid transparent;
                border-bottom: 10px solid transparent;
                border-left: 16px solid #2b3f51;
            "></div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.image(icono_path, width=170)

# Línea divisoria + espacio vertical
st.markdown("""
    <hr style='margin-top: 40px; margin-bottom: 40px; border: none; height: 2px; background-color: #cccccc;' />
""", unsafe_allow_html=True)


# BARRA LATERAL

st.sidebar.title("⚙️ Configuración")
api_key = st.sidebar.text_input("🔐 Ingresa la clave API", type="password")
if api_key:
    st.sidebar.success("API key guardada")

# Función para borrar historial
def borrar_historial():
    st.session_state.historial_ids = []
    st.session_state.modo_actual = "formulario"
    if "ultimo_analisis" in st.session_state:
        del st.session_state["ultimo_analisis"]
    with open(historial_file, "w", encoding="utf-8") as f:
        json.dump({}, f)

st.sidebar.title("📄 Historial de reclamaciones")

if "historial_ids" in st.session_state and st.session_state.historial_ids:

    # Obtener fechas mínimas y máximas del historial
    fechas = [datetime.strptime(ident[-14:], "%Y%m%d%H%M%S") for ident in st.session_state.historial_ids]
    fecha_min = min(fechas).date()
    fecha_max = max(fechas).date()

    # Selector de rango de fechas (ajustado para soportar selección de una sola fecha)
    rango_fechas = st.sidebar.date_input("📅 Buscar por rango de fechas", [fecha_min, fecha_max])
    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        fecha_inicio, fecha_fin = rango_fechas
    else:
        fecha_inicio = fecha_fin = rango_fechas if isinstance(rango_fechas, datetime) else datetime.today().date()

    # Campo de búsqueda
    busqueda = st.sidebar.text_input("🔍 Buscar por nombre", "")

    # Botones de análisis filtrados
    hay_identificadores = False
    for ident in reversed(st.session_state.historial_ids):
        fecha_ident = datetime.strptime(ident[-14:], "%Y%m%d%H%M%S").date()
        if fecha_inicio <= fecha_ident <= fecha_fin and (busqueda.lower() in ident.lower()):
            hay_identificadores = True
            if st.sidebar.button(ident, key=f"btn_{ident}"):
                st.session_state.ultimo_analisis = ident
                st.session_state.modo_actual = "analisis"
                st.rerun()

    # Botón de borrar historial
    st.sidebar.button("🗑️ Borrar historial", disabled=not hay_identificadores, on_click=borrar_historial)

else:
    st.sidebar.warning("Aún no hay análisis registrados")


# MODO FORMULARIO

orden_campos = [
        "FECHA DE LA RECLAMACION",
        "FECHA DEL ACCIDENTE",
        "FECHA EN LA QUE SE EMITIO LA POLIZA",
        "MARCA DEL VEHICULO",
        "TIPO DE VEHICULO",
        "ANTIGUEDAD DEL VEHICULO",
        "PRECIO DEL VEHICULO",
        "FRANQUICIA DE LA POLIZA",
        "TIPO DE POLIZA",
        "GENERO DEL ASEGURADO",
        "EDAD DEL ASEGURADO",
        "ESTADO CIVIL DEL ASEGURADO",
        "NUMERO DE RECLAMACIONES PASADAS",
        "CUANTO TIEMPO DESPUES SE MUDO EL ASEGURADOR TRAS EL ACCIDENTE",
        "TIPO DE AGENTE QUE GESTIONO LA POLIZA",
        "ZONA DONDE OCURRIO EL ACCIDENTE",
        "CULPABLE DEL ACCIDENTE",
        "NUMERO DE COCHES INVOLUCRADOS EN EL ACCIDENTE",
        "INFORME POLICIAL DEL ACCIDENTE",
        "TESTIGOS DEL ACCIDENTE",
        "NUMERO DE DOCUMENTOS RELACIONADOS CON EL ACCIDENTE"
    ]

etiquetas_campos = {
        "FECHA DE LA RECLAMACION": "FECHA DE LA RECLAMACIÓN",
        "FECHA DEL ACCIDENTE": "FECHA DEL ACCIDENTE",
        "FECHA EN LA QUE SE EMITIO LA POLIZA": "FECHA EN LA QUE SE EMITIÓ LA POLIZA",
        "MARCA DEL VEHICULO": "MARCA DEL VEHÍCULO",
        "TIPO DE VEHICULO": "TIPO DE VEHÍCULO",
        "ANTIGUEDAD DEL VEHICULO": "ANTIGÜEDAD DEL VEHÍCULO (en años)",
        "PRECIO DEL VEHICULO": "PRECIO DEL VEHÍCULO",
        "FRANQUICIA DE LA POLIZA": "FRANQUICIA DE LA PÓLIZA",
        "TIPO DE POLIZA": "TIPO DE PÓLIZA",
        "GENERO DEL ASEGURADO": "GÉNERO DEL ASEGURADO",
        "EDAD DEL ASEGURADO": "EDAD DEL ASEGURADO",
        "ESTADO CIVIL DEL ASEGURADO": "ESTADO CIVIL DEL ASEGURADO",
        "NUMERO DE RECLAMACIONES PASADAS": "NÚMERO DE RECLAMACIONES PASADAS",
        "CUANTO TIEMPO DESPUES SE MUDO EL ASEGURADOR TRAS EL ACCIDENTE": "¿CUÁNTO TIEMPO DESPUÉS SE MUDÓ EL ASEGURADOR TRAS EL ACCIDENTE? (en años)",
        "TIPO DE AGENTE QUE GESTIONO LA POLIZA": "TIPO DE AGENTE QUE GESTIONÓ LA PÓLIZA",
        "ZONA DONDE OCURRIO EL ACCIDENTE": "ZONA DONDE OCURRIÓ EL ACCIDENTE",
        "CULPABLE DEL ACCIDENTE": "CULPABLE DEL ACCIDENTE",
        "NUMERO DE COCHES INVOLUCRADOS EN EL ACCIDENTE": "NÚMERO DE COCHES INVOLUCRADOS EN EL ACCIDENTE",
        "INFORME POLICIAL DEL ACCIDENTE": "INFORME POLICIAL DEL ACCIDENTE",
        "TESTIGOS DEL ACCIDENTE": "TESTIGOS DEL ACCIDENTE",
        "NUMERO DE DOCUMENTOS RELACIONADOS CON EL ACCIDENTE": "NÚMERO DE DOCUMENTOS RELACIONADOS CON EL ACCIDENTE"
    }
if st.session_state.modo_actual == "formulario":
    entrada = {}
    errores = []
    fecha_accidente_dt = None
    fecha_emision_dt = None
    fecha_reclamacion_dt = datetime.today()
    entrada["FECHA DE LA RECLAMACION"] = datetime.today().strftime("%d/%m/%Y")

    nombre_reclamador = st.text_input("PRIMERO, INGRESA EL NOMBRE DEL RECLAMADOR")
    identificador_unico = f"{nombre_reclamador}_{datetime.now().strftime('%Y%m%d%H%M%S')}" if nombre_reclamador else None

    with st.form(key="formulario_reclamo"):
        orden_campos_filtrado = [campo for campo in orden_campos if campo != "FECHA DE LA RECLAMACION"]

        for i in range(0, len(orden_campos_filtrado), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j >= len(orden_campos_filtrado):
                    break
                campo = orden_campos_filtrado[i + j]
                info = schema[campo]
                if info.get("derived"):
                    continue
                tipo = info["type"]
                label = etiquetas_campos.get(campo, campo)
                with cols[j]:
                    if tipo == "date":
                        fecha = st.date_input(label, format="DD/MM/YYYY")
                        entrada[campo] = fecha.strftime("%d/%m/%Y")
                        if campo == "FECHA DEL ACCIDENTE":
                            fecha_accidente_dt = fecha
                        elif campo == "FECHA EN LA QUE SE EMITIO LA POLIZA":
                            fecha_emision_dt = fecha
                    elif tipo == "categorical":
                        opciones = list(info["options"].keys())
                        if campo in [
                            "GENERO DEL ASEGURADO",
                            "TIPO DE AGENTE QUE GESTIONO LA POLIZA",
                            "ZONA DONDE OCURRIO EL ACCIDENTE",
                            "CULPABLE DEL ACCIDENTE",
                            "INFORME POLICIAL DEL ACCIDENTE",
                            "TESTIGOS DEL ACCIDENTE"
                        ]:
                            entrada[campo] = st.radio(label, opciones, horizontal=True, key=f"{campo}_radio")
                        else:
                            seleccion = st.selectbox(label, ["Selecciona una opción"] + opciones)
                            entrada[campo] = seleccion    
                    elif tipo == "numeric":
                        if campo == "EDAD DEL ASEGURADO":
                            entrada[campo] = st.number_input(label, min_value=16, max_value=110, step=1)
                        elif campo == "PRECIO DEL VEHICULO":
                            entrada[campo] = st.slider(label, min_value=500, max_value=100000, step=500)
                        else:
                            entrada[campo] = st.number_input(label, min_value=0, step=1)

        entrada["FECHA DE LA RECLAMACION"] = datetime.today().strftime("%d/%m/%Y")
        fecha_reclamacion_dt = datetime.today().date()
        submit = st.form_submit_button("🔍︎   Analizar reclamo")
        if submit:
            if not identificador_unico or f"analisis_{identificador_unico}" in st.session_state:
                st.stop()

            if fecha_accidente_dt and fecha_accidente_dt > fecha_reclamacion_dt:
                errores.append("La **FECHA DEL ACCIDENTE** no puede ser posterior a la **FECHA DE LA RECLAMACIÓN**.")
            if fecha_emision_dt:
                if fecha_accidente_dt and fecha_emision_dt > fecha_accidente_dt:
                    errores.append("La **FECHA DE EMISIÓN DE LA PÓLIZA** no puede ser posterior a la **FECHA DEL ACCIDENTE**.")
                if fecha_emision_dt > fecha_reclamacion_dt:
                    errores.append("La **FECHA DE EMISIÓN DE LA PÓLIZA** no puede ser posterior a la **FECHA DE LA RECLAMACIÓN**.")

            for campo in orden_campos:
                info = schema[campo]
                if info.get("derived") or info["type"] != "categorical":
                    continue
                if entrada[campo] == "Selecciona una opción":
                    label = etiquetas_campos.get(campo, campo)
                    errores.append(f"Debe seleccionar una opción válida para **{label}**.")

            if errores:
                for err in errores:
                    st.error(f"❌ {err}")
            else:
                df = pd.DataFrame([entrada])
                try:
                    resultado = model_service(df)
                    if "historial_ids" not in st.session_state:
                        st.session_state.historial_ids = []

                    # Crear análisis sin explicación IA de momento
                    st.session_state[f"analisis_{identificador_unico}"] = {
                        "entrada": entrada,
                        "resultado": resultado,
                        "explicacion_ia": None  # ← inicializa aquí
                    }
                    st.session_state.historial_ids.append(identificador_unico)
                    st.session_state.ultimo_analisis = identificador_unico
                    st.session_state.modo_actual = "analisis"

                    # Guardar historial actualizado, aunque aún no tenga explicación IA
                    historial_data = {
                        ident: st.session_state[f"analisis_{ident}"]
                        for ident in st.session_state.historial_ids
                    }
                    with open(historial_file, "w", encoding="utf-8") as f:
                        json.dump(historial_data, f, ensure_ascii=False, indent=2)

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error al procesar el reclamo: {e}")


# MODO ANÁLISIS

if st.session_state.modo_actual == "analisis" and "ultimo_analisis" in st.session_state:
    data = st.session_state[f"analisis_{st.session_state.ultimo_analisis}"]
    entrada = data["entrada"]
    resultado = data["resultado"]
    explicacion_guardada = data.get("explicacion_ia", None)

    st.subheader("📝 Resumen de la reclamación")

    campos_visibles = [c for c in orden_campos if c != "FECHA DE LA RECLAMACION" and c in entrada]
    for i in range(0, len(campos_visibles), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(campos_visibles):
                campo = campos_visibles[i + j]
                etiqueta = etiquetas_campos.get(campo, campo)
                with cols[j]:
                    st.markdown(f"**{etiqueta}:** {entrada[campo]}")

    st.subheader("📊 Resultado del análisis")
    st.metric("Score de fraude", resultado["score"])
    st.metric("Nivel de riesgo", resultado["riesgo"].upper())

    st.markdown("### 📋 Recomendaciones")
    for rec in resultado["recomendaciones"]:
        st.markdown(f"- {rec}")

    # Mostrar explicación guardada si existe
    if explicacion_guardada:
        st.markdown("### 💡 Explicación del Modelo (IA)")
        st.info(explicacion_guardada)

    # Generar explicación si hay API y aún no hay explicación
    elif api_key:
        try:
            from api_backend import generar_explicacion_llm
            explicacion_ia = generar_explicacion_llm(resultado, entrada, api_key)

            if explicacion_ia.startswith("❌ Error al generar explicación IA: Error code: 401"):
                st.error("❌ API no válida. Verifica que la clave sea correcta.")
            elif "Error" in explicacion_ia or "⚠️" in explicacion_ia:
                st.warning(explicacion_ia)
            else:
                st.markdown("### 💡 Explicación del Modelo (IA)")
                st.info(explicacion_ia)
                # Guardar explicación en el análisis y archivo
                st.session_state[f"analisis_{st.session_state.ultimo_analisis}"]["explicacion_ia"] = explicacion_ia

        except Exception as e:
            st.warning(f"❌ No se pudo generar la explicación IA: {e}")

    # Guardar el historial completo actualizado
    historial_data = {
        ident: st.session_state[f"analisis_{ident}"]
        for ident in st.session_state.historial_ids
    }
    with open(historial_file, "w", encoding="utf-8") as f:
        json.dump(historial_data, f, ensure_ascii=False, indent=2)

    # Botón para volver
    st.markdown("---")
    if st.button("🡰 Volver al formulario"):
        st.session_state.modo_actual = "formulario"
        st.rerun()
