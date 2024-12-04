import streamlit as st
from components.camera import camera_component
from components.video_player import video_player
from components.form import show_form_popup
from utils.image_processor import ImageProcessor
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import webbrowser


def guardar_bytes_imagen(imagen, id_unica):
    try:
        # Convertir la imagen PIL a bytes
        from io import BytesIO

        # Crear un buffer de bytes
        img_byte_arr = BytesIO()
        # Guardar la imagen en el buffer en formato JPEG
        imagen.save(img_byte_arr, format='JPEG')
        # Obtener los bytes
        img_byte_arr = img_byte_arr.getvalue()

        conexion = mysql.connector.connect(
            host=st.secrets["mysql"]["MYSQL_HOST"],
            database=st.secrets["mysql"]["MYSQL_DATABASE"],
            user=st.secrets["mysql"]["MYSQL_USER"],
            password=st.secrets["mysql"]["MYSQL_PASSWORD"]
        )

        cursor = conexion.cursor()
        sql = "INSERT INTO spa_historico (foto, id_unica) VALUES (%s, %s)"
        cursor.execute(sql, (img_byte_arr, id_unica))
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

# Inicializar el procesador de imágenes
if 'image_processor' not in st.session_state:
    st.session_state.image_processor = ImageProcessor()

# Título con estilo
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; margin-bottom: 2rem;'>
        📸 Análisis de Imágenes con IA
    </h1>
""", unsafe_allow_html=True)

# Contenedor principal
with st.container():
    # Sección de la cámara
    col1, col2 = st.columns([2, 1])

    with col1:
        image = camera_component()

    if image is not None:
        with col2:
            st.image(image, caption="Foto capturada", use_column_width=True)

        # Análisis de la imagen con OpenAI
        with st.spinner('Analizando la imagen con IA...'):
            analysis = st.session_state.image_processor.analyze_image(image)

            if analysis:
                st.markdown("### 🤖 Análisis de la IA")
                st.markdown(f"""
                    <div class="analysis-container">
                        {analysis}
                    </div>
                """, unsafe_allow_html=True)

                # Reproducción de video basado en la raza
                st.markdown("### 🎥 Video Informativo")
                video_player(analysis)  # Pasamos el diccionario completo

                # Botón para mostrar el formulario
                col_btn, col_time = st.columns([1, 1])

                with col_btn:
                    def handle_button_click():
                        # Solo guardar la imagen
                        guardar_bytes_imagen(image, current_time)
                        st.success("✅ Imagen guardada correctamente")


                    # Crear un contenedor para el botón y el enlace
                    st.markdown("""
                        <style>
                        .button-container {
                            display: flex;
                            gap: 10px;
                            align-items: center;
                        }
                        .custom-link {
                            display: inline-block;
                            padding: 8px 16px;
                            background-color: #FF4B4B;
                            color: white;
                            text-decoration: none;
                            border-radius: 5px;
                            transition: all 0.3s ease;
                        }
                        .custom-link:hover {
                            background-color: #FF3333;
                            color: white;
                            text-decoration: none;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    # Botón para guardar y enlace para redirigir
                    st.markdown("""
                        <div class="button-container">
                            <a href="https://paradisefunnel.com/inicio-page" target="_blank" class="custom-link">
                                📝 Ir a Paradise Funnel
                            </a>
                        </div>
                    """, unsafe_allow_html=True)

                    # Botón para solo guardar
                    if st.button("💾 Guardar Imagen", key="save_button", on_click=handle_button_click):
                        pass

                with col_time:
                    # Crear timestamp actual
                    current_time = datetime.now().strftime("%d%H%M%S")

                    # Estilo y contenido del timestamp
                    st.markdown("""
                        <style>
                        .timestamp-box {
                            background-color: #f0f2f6;
                            padding: 10px 20px;
                            border-radius: 5px;
                            font-family: monospace;
                            font-size: 1.2em;
                            color: #0f1116;
                            text-align: center;
                            border: 1px solid #ddd;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            margin: 0.5rem 0;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    st.markdown(
                        f'<div class="timestamp-box">{current_time}</div>',
                        unsafe_allow_html=True
                    )