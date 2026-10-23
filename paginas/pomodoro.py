"""Temporizador Pomodoro integrado ao progresso do estudante."""

import time

import streamlit as st

from operations import carregar_metas, registrar_sessao


st.markdown('<span class="badge-pill">Pomodoro</span>', unsafe_allow_html=True)
st.markdown("## 🍅 Temporizador Pomodoro")
st.markdown(
    '<p class="subtitle">'
    "Divida o estudo em períodos de foco e descanso."
    "</p>",
    unsafe_allow_html=True,
)

try:
    disciplinas = carregar_metas()
    nomes_disciplinas = {item["id"]: item["nome"] for item in disciplinas}
    if not nomes_disciplinas:
        st.info("Cadastre uma disciplina no Painel de Progresso antes de usar o Pomodoro.")
        st.stop()
except Exception as erro:
    st.error("Não foi possível carregar as disciplinas. Confira sua conexão.")
    st.stop()


# Valores iniciais do temporizador
if "pomodoro_total" not in st.session_state:
    st.session_state.pomodoro_total = 0

if "pomodoro_rodando" not in st.session_state:
    st.session_state.pomodoro_rodando = False

if "pomodoro_fim" not in st.session_state:
    st.session_state.pomodoro_fim = None

if "pomodoro_restante" not in st.session_state:
    st.session_state.pomodoro_restante = 25 * 60

if "pomodoro_fase" not in st.session_state:
    st.session_state.pomodoro_fase = "Foco"

if "pomodoro_ciclos" not in st.session_state:
    st.session_state.pomodoro_ciclos = 0

if "pomodoro_config" not in st.session_state:
    st.session_state.pomodoro_config = (25, 5)


st.markdown("### Configuração")

bloqueado = st.session_state.pomodoro_rodando

col1, col2, col3 = st.columns(3)

with col1:
    disciplina = st.selectbox(
        "Disciplina",
        list(nomes_disciplinas),
        format_func=lambda item: nomes_disciplinas[item],
        disabled=bloqueado,
    )

with col2:
    foco_minutos = st.number_input(
        "Tempo de foco",
        min_value=1,
        max_value=120,
        value=25,
        step=5,
        disabled=bloqueado,
    )

with col3:
    pausa_minutos = st.number_input(
        "Tempo de descanso",
        min_value=1,
        max_value=30,
        value=5,
        step=1,
        disabled=bloqueado,
    )


# Atualiza o temporizador quando a configuração for alterada
configuracao_atual = (foco_minutos, pausa_minutos)

if (
    configuracao_atual != st.session_state.pomodoro_config
    and not st.session_state.pomodoro_rodando
):
    st.session_state.pomodoro_config = configuracao_atual
    st.session_state.pomodoro_fim = None

    if st.session_state.pomodoro_fase == "Foco":
        st.session_state.pomodoro_restante = foco_minutos * 60
    else:
        st.session_state.pomodoro_restante = pausa_minutos * 60


@st.fragment(run_every="1s")
def exibir_temporizador():
    restante = st.session_state.pomodoro_restante

    if st.session_state.pomodoro_rodando:
        restante = max(
            0,
            int(st.session_state.pomodoro_fim - time.time()),
        )

        st.session_state.pomodoro_restante = restante

        if restante <= 0:
            if st.session_state.pomodoro_fase == "Foco":
                try:
                    registrar_sessao(st.session_state.pomodoro_disciplina, foco_minutos)
                except Exception:
                    st.error("Não foi possível salvar o ciclo concluído. Reconecte e tente novamente; não reinicie nem saia desta página até salvar.")
                    return
                st.session_state.pomodoro_total += foco_minutos

                st.session_state.pomodoro_ciclos += 1
                st.session_state.pomodoro_fase = "Descanso"
                st.session_state.pomodoro_restante = pausa_minutos * 60

                st.toast(
                    "Período de foco concluído e registrado!",
                    icon="✅",
                )
            else:
                st.session_state.pomodoro_fase = "Foco"
                st.session_state.pomodoro_restante = foco_minutos * 60

                st.toast(
                    "Descanso concluído. Vamos voltar aos estudos!",
                    icon="📚",
                )

            st.session_state.pomodoro_rodando = False
            st.session_state.pomodoro_fim = None
            st.rerun()

    minutos = restante // 60
    segundos = restante % 60

    fase = st.session_state.pomodoro_fase

    if fase == "Foco":
        total_segundos = foco_minutos * 60
        icone = "📚"
    else:
        total_segundos = pausa_minutos * 60
        icone = "☕"

    tempo_decorrido = total_segundos - restante
    progresso = tempo_decorrido / total_segundos
    progresso = max(0.0, min(progresso, 1.0))

    st.write("")

    with st.container(border=True):
        st.markdown(
    (
        '<div style="text-align:center; padding:20px 0;">'
        f'<div style="font-size:1.1rem; font-weight:700;">'
        f'{icone} {fase}'
        '</div>'
        '<div style="'
        'font-size:4rem;'
        'font-weight:800;'
        'color:#4F46E5;'
        'line-height:1.2;'
        'margin:15px 0;'
        '">'
        f'{minutos:02d}:{segundos:02d}'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

        st.progress(progresso)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "▶️ Iniciar",
                use_container_width=True,
                disabled=st.session_state.pomodoro_rodando,
            ):
                if ("pomodoro_disciplina" not in st.session_state
                    or st.session_state.pomodoro_restante == foco_minutos * 60):
                    st.session_state.pomodoro_disciplina = disciplina
                st.session_state.pomodoro_fim = (
                    time.time() + st.session_state.pomodoro_restante
                )

                st.session_state.pomodoro_rodando = True
                st.rerun()

        with col2:
            if st.button(
                "⏸️ Pausar",
                use_container_width=True,
                disabled=not st.session_state.pomodoro_rodando,
            ):
                st.session_state.pomodoro_restante = max(
                    0,
                    int(st.session_state.pomodoro_fim - time.time()),
                )

                st.session_state.pomodoro_rodando = False
                st.session_state.pomodoro_fim = None
                st.rerun()

        with col3:
            if st.button(
                "🔄 Reiniciar",
                use_container_width=True,
            ):
                st.session_state.pomodoro_rodando = False
                st.session_state.pomodoro_fim = None

                if st.session_state.pomodoro_fase == "Foco":
                    st.session_state.pomodoro_restante = foco_minutos * 60
                else:
                    st.session_state.pomodoro_restante = pausa_minutos * 60

                st.rerun()

    st.write("")

    col1, col2 = st.columns(2)

    col1.metric(
        "Ciclos concluídos",
        st.session_state.pomodoro_ciclos,
    )

    col2.metric(
        "Tempo registrado",
        f"{st.session_state.pomodoro_total} min",
    )


exibir_temporizador()

st.info(
    "Quando um período de foco terminar, o tempo será registrado "
    "automaticamente no Painel de Progresso."
)

st.divider()
st.caption("StudyTrack — foco, organização e constância.")