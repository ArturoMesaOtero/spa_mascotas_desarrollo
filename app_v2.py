import time
import streamlit as st
from components.camera import camera_component
from components.video_player import video_player
from utils.image_processor import ImageProcessor
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import json
import requests


def guardar_bytes_imagen(imagen, id_unica, analisis_dict, nombre1, telefono1, codigo_postal1, apellidos1, email1,
                         nombre_mascota1):
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
        sql = "INSERT INTO spa_historico (foto, id_unica, comentario_ia, nombre,telefono,codigo_postal,apellidos,email,nombre_mascota) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (
            img_byte_arr, id_unica, comentario_ia, nombre1, telefono1, codigo_postal1, apellidos1, email1,
            nombre_mascota1))
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


def conexion_crm(id_unica, nombre1, telefono1, codigo_postal1, apellidos1, email1, nombre_mascota1):
    try:
        # URL del endpoint para agregar un contacto
        url = 'https://rest.gohighlevel.com/v1/contacts/'

        # Datos del nuevo contacto
        data = {
            "firstName": nombre1,
            "lastName": apellidos1,
            "email": email1,
            "phone": telefono1,
            "postalCode": codigo_postal1,
            "customField": [
                {
                    "id": "AP16mGzffYjOMExDQZMl",
                    "value": id_unica
                },
                {
                    "id": "mHThIoyLd9QaNhG1MAIr",
                    "value": nombre_mascota1
                },
                {"id": "4IsJt3mv0Zp8QTEM0Gmu", "value": "app"}
            ]
        }

        # Encabezados de la solicitud, incluyendo la clave API
        headers = {
            'Authorization': st.secrets["crm"]["Authorization_key"],
            'Content-Type': 'application/json'
        }

        # Enviar la solicitud POST
        response = requests.post(url, json=data, headers=headers)

        # Verificar la respuesta
        if response.status_code == 200:
            print('Contacto agregado exitosamente.')
        else:
            print(f'Error al agregar el contacto: {response.status_code}')
        return True
    except Error as e:
        print(f"Error: {e}")
        return False

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
if 'modal_confirmed' not in st.session_state:
    st.session_state.modal_confirmed = False

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
        /* Estilos para el modal */
    .custom-modal {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .modal-time {
        font-size: 24px;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        padding: 10px;
        margin: 10px 0;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Título con estilo
col_logo, col_title = st.columns([1, 4])  # Ajusta las proporciones según necesites

with col_logo:
    st.image("imagenes/spa_logo_1.jpg", width=100)  # Ajusta el nombre del archivo y el ancho según tu logo

with col_title:
    st.markdown("""
        <h1 style='color: #FF4B4B; margin: 0; padding-top: 10px;'>
            📸 Análisis de Imágenes con IA
        </h1>
    """, unsafe_allow_html=True)

# Contenedor principal
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.analysis_complete:
            captured_image = camera_component()
            if captured_image is not None:
                st.session_state.image = captured_image
                st.session_state.analysis_complete = True
                st.rerun()

    # Mostrar imagen capturada
    if st.session_state.image is not None:
        with col2:
            st.image(st.session_state.image, caption="Foto capturada", use_container_width=True)

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

                # Añadir un espaciado después del video
                st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)

                with col1:
                    # Carga la primera imagen
                    st.video("videos/video_promo.mp4")

                with col2:
                    # Carga la segunda imagen
                    st.image("imagenes/spa_img_4.jpg",
                             use_container_width=True)

                # Después de las imágenes y el espaciado
                st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

                # Generamos el current_time pero no lo mostramos
                if st.session_state.current_time is None:
                    st.session_state.current_time = datetime.now().strftime("%d%H%M%S")

                # Estilo común para botones y enlaces
                st.markdown("""
                    <style>
                    .streamlit-button {
                        width: 100%;
                        background-color: #FFFFFF;
                        color: rgb(38, 39, 48);
                        padding: 0.6rem 0.6rem;
                        position: relative;
                        text-align: center;
                        text-decoration: none;
                        vertical-align: middle;
                        cursor: pointer;
                        user-select: none;
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        font-weight: normal;
                        margin: 0.5rem 0;
                        display: inline-block;
                        box-shadow: rgba(0, 0, 0, 0.08) 0px 1px 3px;
                        transition: color 0.2s ease 0s, background-color 0.2s ease 0s, border-color 0.2s ease 0s, box-shadow 0.2s ease 0s;
                        font-size: 1rem;
                        line-height: 1.6;
                    }
                    .streamlit-button:hover {
                        border-color: rgb(255, 75, 75);
                        color: rgb(255, 75, 75);
                        text-decoration: none;
                    }
                    </style>
                    <a href="https://paradisefunnel.com/inicio-page" target="_blank" class="streamlit-button">
                        📝 Ir a Paradise Funnel
                    </a>
                """, unsafe_allow_html=True)

                # Añadimos un pequeño espacio
                st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

                # Formulario popup
                with st.form(key='contact_form'):
                    st.markdown("""
                        <style>
                        .stForm {
                            background-color: white;
                            padding: 20px;
                            border-radius: 10px;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                            margin: 10px 0;
                        }

                        .stTextInput > label, .stTextArea > label {
                            color: #E94ECF !important;
                            font-weight: 500;
                        }

                        .required {
                            color: #E94ECF !important;
                        }

                        .stTextInput > div > div > input,
                        .stTextArea > div > div > textarea {
                            border: 1px solid #ddd !important;
                            border-radius: 5px;
                            padding: 10px;
                            min-height: 40px;
                        }

                        .checkbox-container {
                            display: flex;
                            align-items: start;
                            gap: 10px;
                            margin: 20px 0;
                        }

                        .stButton > button {
                            width: 100%;
                            background-color: #E94ECF !important;
                            color: white;
                            font-weight: 500;
                            padding: 10px 20px;
                            border-radius: 5px;
                            border: none;
                            cursor: pointer;
                            margin-top: 20px;
                        }

                        /* Estilo para el logo */
                        .logo-container {
                            text-align: center;
                            margin-bottom: 20px;
                        }
                        </style>
                    """, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)

                    with col1:
                        nombre = st.text_input("NOMBRE *")
                        telefono = st.text_input("TELÉFONO *")
                        codigo_postal = st.text_input("CODIGO POSTAL *")

                    with col2:
                        apellidos = st.text_input("APELLIDOS *")
                        email = st.text_input("EMAIL *")
                        nombre_mascota = st.text_input("NOMBRE MASCOTA *")

                    acepto = st.checkbox(
                        "Acepto que mis datos personales sean recopilados y utilizados conforme a la normativa vigente de protección de datos.",
                        value=True  # Esto hará que el checkbox esté marcado por defecto
                    )

                    # Creamos dos columnas para los botones
                    col_submit, col_google = st.columns(2)

                    with col_submit:
                        submitted = st.form_submit_button("ENVIAR")
                        if submitted and acepto:
                            st.session_state.show_confirmation = True

                    with col_google:
                        st.markdown("""
                            <style>
                            .streamlit-button {
                                width: 100%;
                                background-color: #FFFFFF;
                                color: rgb(38, 39, 48);
                                padding: 0.6rem 0.6rem;
                                position: relative;
                                text-align: center;
                                text-decoration: none;
                                vertical-align: middle;
                                cursor: pointer;
                                user-select: none;
                                border: 1px solid rgba(49, 51, 63, 0.2);
                                border-radius: 0.5rem;
                                font-weight: normal;
                                margin: 0.5rem 0;
                                display: inline-block;
                                box-shadow: rgba(0, 0, 0, 0.08) 0px 1px 3px;
                                transition: color 0.2s ease 0s, background-color 0.2s ease 0s, border-color 0.2s ease 0s, box-shadow 0.2s ease 0s;
                                font-size: 1rem;
                                line-height: 1.6;
                            }
                            .streamlit-button:hover {
                                border-color: rgb(255, 75, 75);
                                color: rgb(255, 75, 75);
                                text-decoration: none;
                            }
                            </style>
                            <a href="https://paradisefunnel.com/inicio-page" target="_blank" class="streamlit-button">
                                📝 Condiciones del sorteo
                            </a>
                        """, unsafe_allow_html=True)

                # Añadimos un pequeño espacio
                st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

                # Botón de guardar debajo del enlace
                if 'show_confirmation' not in st.session_state:
                    st.session_state.show_confirmation = False

                # El resto del código para el modal de confirmación se mantiene igual
                if st.session_state.show_confirmation:
                    with st.spinner("Guardando imagen..."):
                        if guardar_bytes_imagen(st.session_state.image, st.session_state.current_time,
                                                analysis, nombre, telefono, codigo_postal, apellidos, email,
                                                nombre_mascota) and conexion_crm(st.session_state.current_time,
                                                                                 nombre, telefono, codigo_postal,
                                                                                 apellidos, email,
                                                                                 nombre_mascota):
                            st.success("✅ Imagen guardada correctamente")
                            time.sleep(1)
                            st.session_state.image = None
                            st.session_state.analysis_complete = False
                            st.session_state.current_time = None
                            st.session_state.show_confirmation = False
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar la imagen")
                            st.session_state.show_confirmation = False
