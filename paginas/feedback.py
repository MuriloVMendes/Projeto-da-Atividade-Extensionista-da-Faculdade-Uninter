"""Página pública de avaliação do StudyTrack."""

import html

import streamlit as st

from operations import (
    calcular_resumo_feedback,
    carregar_feedbacks,
    feedback_online_ativo,
    formatar_data_feedback,
    registrar_feedback,
)


st.markdown('<span class="badge-pill">Feedback</span>', unsafe_allow_html=True)
st.markdown("## 💬 Avalie o StudyTrack")
st.markdown(
    '<p class="subtitle">Conte como foi sua experiência. As respostas autorizadas '
    "ficam públicas para demonstrar os resultados da aplicação do projeto.</p>",
    unsafe_allow_html=True,
)

if st.session_state.pop("feedback_enviado", False):
    st.success("Obrigado! Seu feedback foi salvo e publicado.")

if not feedback_online_ativo():
    st.warning(
        "Modo de teste local: os feedbacks estão salvos somente neste computador. "
        "Configure o banco online antes de aplicar o projeto com os participantes."
    )

try:
    feedbacks = carregar_feedbacks()
except RuntimeError as erro:
    st.error(str(erro))
    feedbacks = []

resumo = calcular_resumo_feedback(feedbacks)

st.write("")
metrica1, metrica2, metrica3 = st.columns(3)
metrica1.metric("Média geral", f"{resumo['media']:.1f} de 5")
metrica2.metric("Participantes", resumo["total"])
metrica3.metric("Avaliações positivas", f"{resumo['positivos']:.0f}%")

st.write("")
coluna_formulario, coluna_avaliacoes = st.columns([1, 1.35], gap="large")

with coluna_formulario:
    with st.container(border=True):
        st.markdown("### Deixe sua opinião")
        st.caption("Avalie somente depois de utilizar as funcionalidades do StudyTrack.")

        with st.form("formulario_feedback", clear_on_submit=True):
            anonimo = st.checkbox("Publicar como participante anônimo")
            nome = st.text_input(
                "Seu nome",
                max_chars=60,
                placeholder="Ex.: Ana Souza",
                help="Não precisa preencher se escolher a avaliação anônima.",
            )
            avaliacao = st.radio(
                "Nota de 0 a 5 estrelas *",
                options=[ 1, 2, 3, 4, 5],
                index=None,
                horizontal=True,
                format_func=lambda nota: "0" if nota == 0 else "⭐" * nota,
            )
            comentario = st.text_area(
                "Comentário *",
                max_chars=500,
                height=150,
                placeholder=(
                    "O StudyTrack ajudou na organização dos seus estudos? "
                    "O que você gostou e o que poderia melhorar?"
                ),
            )
            autorizou = st.checkbox(
                "Autorizo a publicação desta avaliação na página do projeto. *"
            )
            enviar = st.form_submit_button(
                "Enviar feedback",
                type="primary",
                use_container_width=True,
            )

            if enviar:
                if avaliacao is None:
                    st.error("Selecione uma nota de 1 a 5 estrelas.")
                else:
                    try:
                        registrar_feedback(
                            nome,
                            anonimo,
                            avaliacao,
                            comentario,
                            autorizou,
                        )
                        st.session_state["feedback_enviado"] = True
                        st.rerun()
                    except (ValueError, RuntimeError) as erro:
                        st.error(str(erro))

    st.info(
        "O formulário não solicita e-mail, telefone ou outros dados pessoais. "
        "Quem preferir pode publicar a opinião de forma anônima."
    )

with coluna_avaliacoes:
    st.markdown("### Opinião dos participantes")

    if not feedbacks:
        st.info("Ainda não há feedbacks publicados.")
    else:
        with st.expander("Ver distribuição das notas"):
            for nota in range(5, -1, -1):
                quantidade = resumo["distribuicao"].get(nota, 0)
                percentual = quantidade / resumo["total"]
                rotulo = "0 estrelas" if nota == 0 else "⭐" * nota
                st.write(f"{rotulo} — {quantidade} avaliação(ões)")
                st.progress(percentual)

        for item in feedbacks:
            nota = max(0, min(5, int(item.get("avaliacao", 0))))
            estrelas = "Sem estrelas" if nota == 0 else "⭐" * nota
            nome = html.escape(str(item.get("nome", "Participante anônimo")))
            comentario = html.escape(str(item.get("comentario", "")))
            data = formatar_data_feedback(item.get("criado_em"))

            with st.container(border=True):
                st.markdown(
                    f'<div class="feedback-stars">{estrelas}</div>'
                    f'<div class="feedback-comment">“{comentario}”</div>'
                    f'<div class="feedback-author">— {nome} · {data}</div>',
                    unsafe_allow_html=True,
                )

st.divider()
st.caption(
    "Resultados enviados por participantes que utilizaram o protótipo StudyTrack."
)
