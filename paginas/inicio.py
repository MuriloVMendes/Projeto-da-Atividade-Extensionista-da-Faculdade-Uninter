"""Tela inicial do StudyTrack."""

import streamlit as st

from operations import (
    calcular_tempo_por_disciplina,
    carregar_metas,
    carregar_sessoes,
    formatar_tempo,
)


st.markdown('<span class="badge-pill">StudyTrack</span>', unsafe_allow_html=True)
st.markdown("## Organize seus estudos e acompanhe sua evolução")
st.markdown(
    '<p class="subtitle">Uma ferramenta simples para registrar sessões, acompanhar metas '
    "e trocar experiências com outros estudantes.</p>",
    unsafe_allow_html=True,
)

st.write("")

try:
    disciplinas = carregar_metas()
    sessoes = carregar_sessoes()
    tempos = calcular_tempo_por_disciplina(sessoes)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tempo total estudado", formatar_tempo(sum(tempos.values())))
    col2.metric("Sessões registradas", len(sessoes))
    col3.metric("Disciplinas cadastradas", len(disciplinas))
except Exception:
    st.info("Não foi possível carregar o resumo. Confira a conexão com o banco de dados.")

st.write("")
st.markdown("### Recursos disponíveis")

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("#### 📊 Painel de progresso")
        st.write("Registre o tempo de estudo e acompanhe as metas de cada disciplina.")
with col2:
    with st.container(border=True):
        st.markdown("#### 🌎 Comunidade")
        st.write("Compartilhe avanços, participe de grupos e incentive outros estudantes.")
with col3:
    with st.container(border=True):
        st.markdown("#### 💡 Apoio à rotina")
        st.write("Receba mensagens simples de acordo com o progresso registrado.")

st.write("")
st.info("Use o menu lateral para acessar as páginas do aplicativo.")
st.divider()
st.caption("StudyTrack — tecnologia aplicada ao apoio e à inclusão de estudantes no meio digital.")
