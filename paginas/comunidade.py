"""Perfis, publicações, grupos e ranking vinculados à conta autenticada."""
import html
import logging
import streamlit as st
from auth import usuario_atual as obter_usuario_id
from comunidade_db import (
    AVATARES, carregar_perfil, salvar_perfil, carregar_comunidade,
    criar_post, definir_curtida, adicionar_comentario,
    definir_participacao, carregar_ranking, salvar_grupo,
    AREAS_GRUPOS, filtrar_grupos, grupos_semelhantes,
)
from operations import formatar_tempo, formatar_data_social

logger = logging.getLogger(__name__)


def executar(acao, mensagem):
    try:
        acao()
    except ValueError as erro:
        st.error(str(erro))
    except Exception:
        logger.exception("Falha ao atualizar a comunidade")
        st.error("Não foi possível concluir. Confira a conexão e as permissões do Supabase. Ao salvar um perfil, confira também se o nome de usuário já está em uso.")
    else:
        st.session_state["comunidade_mensagem"] = mensagem
        st.rerun()


def formulario_perfil(perfil=None):
    perfil = perfil or {}
    st.caption("Nome, usuário, avatar, curso e bio serão visíveis aos participantes autenticados da comunidade. Seu e-mail de login não será exibido aqui.")
    with st.form("perfil_comunidade"):
        c1, c2 = st.columns([1, 3])
        with c1:
            atual = perfil.get("avatar", "🎓")
            avatar = st.selectbox("Avatar", AVATARES, index=AVATARES.index(atual) if atual in AVATARES else 0)
        with c2:
            nome = st.text_input("Nome de exibição", value=perfil.get("nome", ""), max_chars=60)
            usuario = st.text_input("Usuário", value=perfil.get("usuario", ""), max_chars=25,
                                    help="Letras sem acento, números ou sublinhado. Deve ser único.")
        curso = st.text_input("Curso ou área", value=perfil.get("curso", ""), max_chars=80)
        bio = st.text_area("Bio", value=perfil.get("bio", ""), max_chars=180)
        ranking = st.checkbox("Quero aparecer no ranking com meu tempo total e meus dias de estudo desta semana.",
                              value=perfil.get("participar_ranking", False))
        salvar = st.form_submit_button("Salvar perfil", type="primary")
    if salvar:
        executar(lambda: salvar_perfil(nome, usuario, bio, curso, avatar, ranking), "Perfil salvo!")


st.markdown('<span class="badge-pill">Comunidade</span>', unsafe_allow_html=True)
st.markdown("## 🌎 Estude junto. Evolua junto.")
st.caption("Compartilhe avanços, participe de grupos e acompanhe outros estudantes.")
if mensagem := st.session_state.pop("comunidade_mensagem", None):
    st.success(mensagem)
try:
    usuario_id = obter_usuario_id()
    perfil = carregar_perfil()
except Exception:
    logger.exception("Falha ao carregar perfil da comunidade")
    st.error("Não foi possível carregar seu perfil. Confira a conexão e se o SQL da comunidade foi executado por completo.")
    st.stop()
if perfil is None:
    st.subheader("Complete seu perfil")
    st.write("Você já tem uma conta. Escolha como aparecer na comunidade.")
    formulario_perfil()
    st.stop()
if st.button("Atualizar comunidade"):
    st.rerun()
try:
    dados = carregar_comunidade()
except Exception:
    logger.exception("Falha ao carregar comunidade")
    st.error("Não foi possível carregar a comunidade. Confira a conexão, as tabelas e suas permissões no Supabase.")
    st.stop()
perfis = dados["perfis"]


def identificar(autor_id):
    p = perfis.get(autor_id, {})
    return f"{p.get('avatar', '🎓')} {p.get('nome', 'Estudante')} (@{p.get('usuario', 'estudante')})"


feed, grupos, ranking, meu_perfil = st.tabs(["📰 Feed", "👥 Grupos", "🏆 Ranking", "👤 Meu perfil"])
with feed:
    st.caption("Publicações são visíveis a todos os participantes autenticados. Os grupos organizam os assuntos.")
    coluna_feed, lateral = st.columns([2.1, 1], gap="large")
    with lateral:
        with st.container(border=True):
            st.text(identificar(usuario_id))
            st.text(perfil.get("curso", ""))
            st.text(perfil.get("bio", ""))
            st.caption("Seus grupos")
            meus_grupos = [g for g in dados["grupos"] if g["participando"]]
            for g in meus_grupos:
                st.text(g["nome"])
            if not meus_grupos:
                st.caption("Entre em um grupo na aba Grupos.")
    with coluna_feed:
        opcoes = [None] + [g["nome"] for g in meus_grupos]
        with st.form("novo_post"):
            texto = st.text_area("O que você estudou hoje?", max_chars=600)
            grupo = st.selectbox("Publicar em", opcoes, format_func=lambda item: item or "Geral")
            publicar = st.form_submit_button("Publicar", type="primary")
        if publicar:
            executar(lambda: criar_post(texto, grupo), "Publicação criada!")
        st.caption("Exibindo as 50 publicações mais recentes.")
        if not dados["posts"]:
            st.info("Ainda não há publicações. Compartilhe seu primeiro avanço!")
        for post in dados["posts"]:
            with st.container(border=True):
                st.text(identificar(post["usuario_id"]))
                st.caption(f"{formatar_data_social(post['criado_em'])} · {post['grupo'] or 'Geral'}")
                # Escape de conteúdo enviado pelos participantes antes do HTML.
                texto_seguro = html.escape(post["texto"]).replace("\n", "<br>")
                st.markdown(f'<div class="post-text">{texto_seguro}</div>', unsafe_allow_html=True)
                curtiu = usuario_id in post["curtidas"]
                if st.button(f"{'💜' if curtiu else '🤍'} {len(post['curtidas'])}", key=f"curtida_{post['id']}"):
                    executar(lambda post=post, curtiu=curtiu: definir_curtida(post["id"], not curtiu), "Curtida atualizada.")
                with st.expander(f"Comentários ({len(post['comentarios'])})"):
                    for comentario in post["comentarios"]:
                        st.text(identificar(comentario["usuario_id"]))
                        st.text(comentario["texto"])
                        st.divider()
                    with st.form(f"comentario_{post['id']}"):
                        texto_comentario = st.text_input("Seu comentário", max_chars=300)
                        enviar = st.form_submit_button("Comentar")
                    if enviar:
                        executar(lambda post=post, texto=texto_comentario: adicionar_comentario(post["id"], texto), "Comentário enviado!")
with grupos:
    st.subheader("Encontre sua turma")
    st.caption("Grupos de qualquer área de estudo. Todos são visíveis aos participantes da comunidade.")
    with st.expander("➕ Criar grupo"):
        nome_novo = st.text_input("Nome do novo grupo", max_chars=80, key="grupo_novo_nome",
                                 placeholder="Ex.: Anatomia — grupo de estudos")
        semelhantes = grupos_semelhantes(nome_novo, dados["grupos"])
        if semelhantes:
            st.info("Antes de criar, confira estes grupos com nomes semelhantes:")
            for existente in semelhantes:
                st.text(f"{existente['nome']} · {existente.get('area', 'Tecnologia')}")
        st.caption("Após criar, você será o primeiro membro e poderá editar o grupo.")
        with st.form("criar_grupo"):
            area_nova = st.selectbox("Área de estudo", AREAS_GRUPOS + ["Outra área"], key="grupo_novo_area")
            area_personalizada = st.text_input("Se escolheu Outra área, informe qual", max_chars=60,
                                               key="grupo_novo_area_livre")
            descricao_nova = st.text_area("Descrição do novo grupo", max_chars=500,
                                         placeholder="Explique o assunto e para quem é o grupo.")
            criar = st.form_submit_button("Criar grupo", type="primary")
        if criar:
            area_final = area_personalizada if area_nova == "Outra área" else area_nova
            executar(lambda: salvar_grupo(nome_novo, descricao_nova, area_final),
                     "Grupo criado! Você já participa dele.")

    meus_grupos_criados = [g for g in dados["grupos"] if g.get("criador_id") == usuario_id]
    if meus_grupos_criados:
        with st.expander("✏️ Editar meus grupos"):
            por_nome = {g["nome"]: g for g in meus_grupos_criados}
            original = st.selectbox("Grupo para editar", list(por_nome), key="grupo_editar_escolha")
            atual = por_nome[original]
            with st.form(f"editar_grupo_{original}"):
                nome_editado = st.text_input("Nome do grupo", value=atual["nome"], max_chars=80)
                descricao_editada = st.text_area("Descrição", value=atual["descricao"], max_chars=500)
                area_editada = st.text_input("Área de estudo", value=atual.get("area", "Tecnologia"), max_chars=60)
                salvar = st.form_submit_button("Salvar grupo")
            if salvar:
                executar(lambda: salvar_grupo(nome_editado, descricao_editada, area_editada, original),
                         "Grupo atualizado! Participantes e publicações foram preservados.")

    c_busca, c_area = st.columns([2, 1])
    with c_busca:
        busca = st.text_input("Buscar grupos", placeholder="Nome, assunto ou descrição", key="grupo_busca")
    with c_area:
        areas = sorted({g.get("area", "Tecnologia") for g in dados["grupos"]})
        filtro_area = st.selectbox("Filtrar por área", [None] + areas,
                                   format_func=lambda valor: valor or "Todas as áreas")
    encontrados = filtrar_grupos(dados["grupos"], busca, filtro_area)
    st.caption(f"{len(encontrados)} grupo(s) encontrado(s)")
    if not encontrados:
        st.info("Nenhum grupo encontrado. Ajuste a busca ou crie um novo grupo.")
    colunas = st.columns(2)
    for i, grupo in enumerate(encontrados):
        with colunas[i % 2]:
            with st.container(border=True):
                st.text(grupo["nome"])
                st.caption(grupo.get("area", "Tecnologia"))
                st.text(grupo["descricao"])
                criador_id = grupo.get("criador_id")
                st.caption(f"Criado por: {identificar(criador_id) if criador_id else 'StudyTrack — grupo inicial'}")
                st.caption(f"{grupo['membros']} membro(s)")
                participando = grupo["participando"]
                if st.button("Sair do grupo" if participando else "Participar", key=f"grupo_{grupo['nome']}"):
                    executar(lambda grupo=grupo, participando=participando: definir_participacao(grupo["nome"], not participando), "Participação atualizada.")
with ranking:
    st.subheader("🏆 Ranking semanal")
    st.caption("Da segunda-feira até agora, no horário de Brasília. Ordenado por dias com estudo e depois por minutos. Dias com estudo não significam dias consecutivos.")
    st.info("A participação é opcional. Ative ou desative a exibição dos seus totais em Meu perfil.")
    try:
        pessoas = carregar_ranking()
    except Exception:
        logger.exception("Falha ao carregar ranking")
        st.error("Não foi possível carregar o ranking. Confira a função comunidade_ranking_semanal no Supabase.")
    else:
        if not pessoas:
            st.info("Ainda não há participantes no ranking.")
        for posicao, pessoa in enumerate(pessoas, 1):
            voce = " · você" if pessoa["usuario_id"] == usuario_id else ""
            medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(posicao, str(posicao))
            st.text(f"{medalha} {pessoa['avatar']} {pessoa['nome']}{voce}")
            st.caption(f"{pessoa['dias']} dia(s) com estudo · {formatar_tempo(pessoa['minutos'])}")
with meu_perfil:
    st.subheader("Seu perfil na comunidade")
    formulario_perfil(perfil)
st.divider()
st.caption("StudyTrack Community — progresso compartilhado, apoio e constância.")
