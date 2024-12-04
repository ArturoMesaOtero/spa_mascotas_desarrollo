import streamlit as st
import os
from utils.helpers import get_valid_video_path, video_exists


def video_player(analysis_dict):
    st.markdown("""
        <style>
        .video-container {
            margin: 20px 0;
            padding: 10px;
            border-radius: 10px;
            background-color: #f8f9fa;
        }
        .video-message {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            font-size: 0.9em;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="video-container">', unsafe_allow_html=True)

        raza = analysis_dict.get('raza_escogida')
        video_path = get_valid_video_path(raza)

        if video_path == "./videos/default.mp4":
            st.info("ℹ️ Mostrando video informativo general sobre mascotas.")
        else:
            st.success(f"🎥 Reproduciendo video específico para la raza {raza}")

        if video_exists(video_path):
            st.video(video_path)
        else:
            st.error("❌ Lo sentimos, el video no está disponible en este momento.")

        st.markdown('</div>', unsafe_allow_html=True)