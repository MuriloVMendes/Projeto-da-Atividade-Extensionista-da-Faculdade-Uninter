"""Informações acadêmicas e limitações do projeto."""

import streamlit as st


st.markdown('<span class="badge-pill">Sobre</span>', unsafe_allow_html=True)
st.markdown("## Sobre o StudyTrack")
st.markdown(
    '<p class="subtitle">Projeto desenvolvido para a Atividade Extensionista – '
    "Tecnologia Aplicada à Inclusão Digital.</p>",
    unsafe_allow_html=True,
)

st.markdown("### Objetivo")
st.write(
    "O StudyTrack busca apoiar estudantes que têm dificuldade para organizar a rotina "
    "de estudos ou acompanhar o próprio progresso. A aplicação reúne essas tarefas em "
    "uma interface web simples, que pode ser aberta pelo navegador."
)

st.markdown("### Como a tecnologia é aplicada")
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("#### 📚 Organização")
        st.write("Registro das sessões e visualização das metas acadêmicas.")
    with st.container(border=True):
        st.markdown("#### 🌐 Acesso pelo navegador")
        st.write("Após a publicação, o participante não precisa instalar o Python.")
with col2:
    with st.container(border=True):
        st.markdown("#### 📈 Acompanhamento")
        st.write("Indicadores simples ajudam o estudante a entender sua evolução.")
    with st.container(border=True):
        st.markdown("#### 🤝 Participação")
        st.write("A comunidade permite compartilhar experiências e incentivar colegas.")

st.markdown("### Limitações desta versão")
st.warning(
    "Este é um protótipo acadêmico com login e dados salvos no Supabase. "
    "As metas e sessões são individuais; o conteúdo da comunidade é visível aos "
    "participantes autenticados. O ranking semanal é opcional. O feed exibe as "
    "50 publicações mais recentes e requer atualização para mostrar novas interações."
)

st.divider()
st.caption("Projeto acadêmico — Atividade Extensionista.")
