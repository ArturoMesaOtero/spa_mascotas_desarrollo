import streamlit as st
from PIL import Image


def camera_component():
    st.markdown("""
        <style>
        .stCamera > button {
            background-color: #FF4B4B;
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stCamera > button:hover {
            background-color: #FF3333;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .loading-spinner {
            text-align: center;
            padding: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    img_file_buffer = st.camera_input("📸 Toma una foto", key="camera")
    if img_file_buffer is not None:
        return Image.open(img_file_buffer)
    return None
