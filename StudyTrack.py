"""Ponto de entrada e navegação do StudyTrack."""

import streamlit as st

from style import aplicar_estilo, sidebar_brand


st.set_page_config(page_title="StudyTrack", page_icon="📚", layout="wide")

aplicar_estilo()
sidebar_brand()

from auth import exigir_login
exigir_login()

# A página inicial usa a raiz do site; as demais recebem caminhos únicos.
paginas = [
    st.Page(
        "paginas/inicio.py",
        title="Início",
        icon="🏠",
        default=True,
    ),
    st.Page(
        "paginas/painel.py",
        title="Painel de Progresso",
        icon="📊",
        url_path="progresso",
    ),
    st.Page(
        "paginas/comunidade.py",
        title="Comunidade",
        icon="🌎",
        url_path="comunidade",
    ),
    st.Page(
        "paginas/pomodoro.py",
        title="Pomodoro",
        icon="🍅",
        url_path="pomodoro",
    ),

    st.Page(
            "paginas/feedback.py",
            title="Feedback",
            icon="💬",
            url_path="feedback",
    ),
    st.Page(
        "paginas/sobre.py",
        title="Sobre",
        icon="ℹ️",
        url_path="sobre",
    ),

]

navegacao = st.navigation(paginas)
navegacao.run()
