from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import streamlit as st

from operations import (
    carregar_metas,
    carregar_sessoes,
    salvar_disciplina,
    registrar_sessao,
    excluir_sessao,
    calcular_tempo_por_disciplina,
    calcular_progresso,
    formatar_tempo,
    gerar_sugestao,
)


def formatar_data_registro(valor):
    """Exibe datas do banco no horário de Brasília."""
    try:
        data = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)
        return data.astimezone(ZoneInfo("America/Sao_Paulo")).strftime(
            "%d/%m/%Y às %H:%M"
        )
    except (TypeError, ValueError):
        return "Data não informada"


def concluir(mensagem):
    st.session_state["painel_mensagem"] = mensagem
    st.rerun()


st.title("📊 Painel de Progresso")

mensagem = st.session_state.pop("painel_mensagem", None)

if mensagem:
    st.success(mensagem)

try:
    disciplinas = carregar_metas()
    sessoes = carregar_sessoes()
except Exception:
    st.error(
        "Não foi possível carregar seus estudos. "
        "Confira a conexão e as permissões das tabelas no Supabase."
    )
    st.stop()


with st.expander(
    "Cadastrar disciplina e meta",
    expanded=not disciplinas,
):
    with st.form("nova_disciplina"):
        nome = st.text_input("Nome da disciplina", max_chars=100)

        meta = st.number_input(
            "Meta total de estudo (horas)",
            min_value=0.5,
            value=10.0,
            step=0.5,
        )

        cadastrar = st.form_submit_button("Cadastrar disciplina")

    if cadastrar:
        try:
            salvar_disciplina(nome, meta)
        except ValueError as erro:
            st.error(str(erro))
        except Exception:
            st.error(
                "Não foi possível cadastrar. Confira a conexão "
                "e se você já possui uma disciplina com esse nome."
            )
        else:
            concluir("Disciplina cadastrada!")


if not disciplinas:
    st.info("Cadastre sua primeira disciplina acima para começar.")
    st.stop()


por_id = {
    item["id"]: item
    for item in disciplinas
}


with st.expander("Editar disciplina e meta"):
    editar_id = st.selectbox(
        "Escolha a disciplina",
        options=list(por_id),
        format_func=lambda item: por_id[item]["nome"],
        key="disciplina_editar",
    )

    atual = por_id[editar_id]

    with st.form(f"editar_disciplina_{editar_id}"):
        novo_nome = st.text_input(
            "Nome",
            value=atual["nome"],
            max_chars=100,
        )

        nova_meta = st.number_input(
            "Meta total (horas)",
            min_value=0.5,
            value=float(atual["meta_horas"]),
            step=0.5,
        )

        salvar = st.form_submit_button("Salvar alterações")

    if salvar:
        try:
            salvar_disciplina(novo_nome, nova_meta, editar_id)
        except ValueError as erro:
            st.error(str(erro))
        except Exception:
            st.error(
                "Não foi possível salvar. Confira a conexão "
                "e se o nome já está sendo usado."
            )
        else:
            concluir("Disciplina atualizada!")


st.subheader("Registrar sessão")

with st.form("registrar_sessao"):
    disciplina_id = st.selectbox(
        "Disciplina",
        options=list(por_id),
        format_func=lambda item: por_id[item]["nome"],
    )

    duracao = st.number_input(
        "Duração (minutos)",
        min_value=1,
        max_value=1440,
        value=60,
    )

    registrar = st.form_submit_button(
        "Registrar estudo",
        type="primary",
    )

if registrar:
    try:
        registrar_sessao(disciplina_id, duracao)
    except ValueError as erro:
        st.error(str(erro))
    except Exception:
        st.error("Não foi possível registrar. Confira sua conexão.")
    else:
        concluir("Sessão registrada!")


st.subheader("Seu progresso")

tempos = calcular_tempo_por_disciplina(sessoes)

col1, col2 = st.columns(2)

col1.metric(
    "Tempo total estudado",
    formatar_tempo(sum(tempos.values())),
)

col2.metric("Sessões registradas", len(sessoes))

for item in disciplinas:
    estudado = tempos.get(item["nome"], 0)

    progresso = calcular_progresso(
        estudado,
        float(item["meta_horas"]),
    )

    with st.container(border=True):
        st.subheader(item["nome"])
        st.progress(progresso / 100)

        st.caption(
            f"{progresso:.1f}% · "
            f"Estudado: {formatar_tempo(estudado)} · "
            f"Meta: {item['meta_horas']}h"
        )

        st.caption(gerar_sugestao(progresso))


st.subheader("Histórico")
st.caption("Datas e horários de Brasília.")

if not sessoes:
    st.info("Você ainda não registrou sessões.")
else:
    st.dataframe(
        [
            {
                "Disciplina": item["disciplina"],
                "Minutos": item["duracao_minutos"],
                "Data e hora": formatar_data_registro(item["criado_em"]),
            }
            for item in sessoes
        ],
        hide_index=True,
        use_container_width=True,
    )

    registros = {
        item["id"]: item
        for item in sessoes
    }

    with st.expander("Excluir uma sessão incorreta"):
        sessao_id = st.selectbox(
            "Escolha o registro",
            options=list(registros),
            format_func=lambda item: (
                f"{registros[item]['disciplina']} · "
                f"{registros[item]['duracao_minutos']} minutos · "
                f"{formatar_data_registro(registros[item]['criado_em'])}"
            ),
        )

        confirmar = st.checkbox("Confirmo a exclusão desta sessão")

        if st.button("Excluir sessão", disabled=not confirmar):
            try:
                excluir_sessao(sessao_id)
            except Exception:
                st.error("Não foi possível excluir. Confira sua conexão.")
            else:
                concluir("Sessão excluída!")