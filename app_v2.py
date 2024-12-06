import time

import streamlit as st
from components.camera import camera_component
from components.video_player import video_player
from utils.image_processor import ImageProcessor
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import webbrowser
import json


def guardar_bytes_imagen(imagen, id_unica, analisis_dict):
    try:
        # Convertir la imagen PIL a bytes
        from io import BytesIO

        # Crear un buffer de bytes
        img_byte_arr = BytesIO()
        # Guardar la imagen en el buffer en formato JPEG
        imagen.save(img_byte_arr, format='JPEG')
        # Obtener los bytes
        img_byte_arr = img_byte_arr.getvalue()

        # Convertir el diccionario de análisis a JSON string
        comentario_ia = json.dumps(analisis_dict) if analisis_dict else '{}'

        conexion = mysql.connector.connect(
            host=st.secrets["mysql"]["MYSQL_HOST"],
            database=st.secrets["mysql"]["MYSQL_DATABASE"],
            user=st.secrets["mysql"]["MYSQL_USER"],
            password=st.secrets["mysql"]["MYSQL_PASSWORD"]
        )

        cursor = conexion.cursor()
        sql = "INSERT INTO spa_historico (foto, id_unica, comentario_ia) VALUES (%s, %s, %s)"
        cursor.execute(sql, (img_byte_arr, id_unica, comentario_ia))
        conexion.commit()

        print(f"Imagen guardada con éxito. ID: {cursor.lastrowid}")
        return True

    except Error as e:
        print(f"Error: {e}")
        return False

    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()


# Configuración de la página
st.set_page_config(
    page_title="Análisis de Imágenes",
    page_icon="📸",
    layout="wide"
)

# Inicialización del estado
if 'image_processor' not in st.session_state:
    st.session_state.image_processor = ImageProcessor()
if 'image' not in st.session_state:
    st.session_state.image = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'current_time' not in st.session_state:
    st.session_state.current_time = None

# Estilos globales
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .analysis-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Título con estilo
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; margin-bottom: 2rem;'>
        📸 Análisis de Imágenes con IA
    </h1>
""", unsafe_allow_html=True)

# Contenedor principal
with st.container():
    # Sección de la cámara
    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.analysis_complete:
            captured_image = camera_component()
            if captured_image is not None:
                st.session_state.image = captured_image
                st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
                if st.button("🔍 Analizar Imagen"):
                    st.session_state.analysis_complete = True
                    st.rerun()

    # Mostrar imagen capturada
    if st.session_state.image is not None:
        with col2:
            zoom_level = st.slider("Nivel de Zoom", 0.5, 2.0, 1.0, 0.1)
            width = int(st.session_state.image.size[0] * zoom_level)
            st.image(st.session_state.image, caption="Foto capturada", width=width)

    # Análisis y resultados
    if st.session_state.analysis_complete:
        with st.spinner('Analizando la imagen con IA...'):
            analysis = st.session_state.image_processor.analyze_image(st.session_state.image)

            if analysis:
                st.markdown("### 🤖 Análisis de la IA")
                st.markdown(f"""
                    <div class="analysis-container">
                        {analysis}
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("### 🎥 Video Informativo")
                video_player(analysis)

                if st.session_state.current_time is None:
                    st.session_state.current_time = datetime.now().strftime("%d%H%M%S")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(
                        f'<div class="equal-elements timestamp">{st.session_state.current_time}</div>',
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        '<a href="https://paradisefunnel.com/inicio-page" target="_blank" class="equal-elements google-btn">📝 Ir a Paradise Funnel</a>',
                        unsafe_allow_html=True
                    )

                with col3:
                    if st.button("🔄 Guardar"):
                        with st.spinner("Guardando imagen..."):
                            if guardar_bytes_imagen(st.session_state.image, st.session_state.current_time, analysis):
                                st.success("✅ Imagen guardada correctamente")
                                time.sleep(1)  # Dar tiempo para ver el mensaje
                                st.session_state.image = None
                                st.session_state.analysis_complete = False
                                st.session_state.current_time = None
                                st.rerun()
                            else:
                                st.error("❌ Error al guardar la imagen")
