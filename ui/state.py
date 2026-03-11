import streamlit as st
import tempfile
import os

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def save_uploaded_file(uploaded_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name

def cleanup_file(path: str):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
