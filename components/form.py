import streamlit as st


def show_form_popup():
    with st.form(key='my_form'):
        st.markdown("""
            <style>
            .stForm {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)

        st.text_input("Nombre")
        st.text_input("Email")
        st.text_area("Comentarios")

        submitted = st.form_submit_button("Guardar")
        if submitted:
            st.success("¡Datos guardados exitosamente!")