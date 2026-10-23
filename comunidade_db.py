"""Comunidade autenticada: tabelas e políticas já criadas no Supabase."""
import re
from auth import cliente as obter_cliente, usuario_atual as obter_usuario_id

AVATARES = ["🎓", "👨‍💻", "👩‍💻", "🧠", "📚", "🚀"]


def ler_todos(consulta):
    resultado = []
    inicio = 0
    while True:
        pagina = consulta.range(inicio, inicio + 499).execute().data
        resultado.extend(pagina)
        if len(pagina) < 500:
            return resultado
        inicio += 500


def carregar_perfil():
    dados = (obter_cliente().table("comunidade_perfis").select("*")
             .eq("usuario_id", obter_usuario_id()).execute().data)
    return dados[0] if dados else None


def salvar_perfil(nome, usuario, bio, curso, avatar, ranking):
    nome = nome.strip()
    usuario = usuario.strip().lstrip("@").lower()
    bio, curso = bio.strip(), curso.strip()
    if not 3 <= len(nome) <= 60:
        raise ValueError("Informe um nome com 3 a 60 caracteres.")
    if not re.fullmatch(r"[a-z0-9_]{3,25}", usuario):
        raise ValueError("O usuário deve ter 3 a 25 caracteres: letras sem acento, números ou sublinhado.")
    if len(bio) > 180 or len(curso) > 80:
        raise ValueError("A bio ou o curso ultrapassou o limite.")
    if avatar not in AVATARES:
        raise ValueError("Escolha um avatar válido.")
    (obter_cliente().table("comunidade_perfis").upsert({
        "usuario_id": obter_usuario_id(), "nome": nome, "usuario": usuario,
        "bio": bio, "curso": curso, "avatar": avatar,
        "participar_ranking": bool(ranking),
    }, on_conflict="usuario_id").execute())


def carregar_comunidade():
    banco, usuario_id = obter_cliente(), obter_usuario_id()
    perfis = ler_todos(banco.table("comunidade_perfis").select("*").order("usuario_id"))
    grupos = ler_todos(banco.table("comunidade_grupos").select("*").order("nome"))
    membros = ler_todos(banco.table("comunidade_membros").select("*")
                       .order("usuario_id").order("grupo"))
    posts = (banco.table("comunidade_posts").select("*").order("criado_em", desc=True)
             .order("id").limit(50).execute().data)
    comentarios, curtidas = [], []
    if posts:
        ids = [post["id"] for post in posts]
        comentarios = ler_todos(banco.table("comunidade_comentarios").select("*")
                                .in_("post_id", ids).order("criado_em").order("id"))
        curtidas = ler_todos(banco.table("comunidade_curtidas").select("*")
                            .in_("post_id", ids).order("post_id").order("usuario_id"))
    for grupo in grupos:
        participantes = [m["usuario_id"] for m in membros if m["grupo"] == grupo["nome"]]
        grupo["membros"] = len(participantes)
        grupo["participando"] = usuario_id in participantes
    for post in posts:
        post["comentarios"] = [c for c in comentarios if c["post_id"] == post["id"]]
        post["curtidas"] = [c["usuario_id"] for c in curtidas if c["post_id"] == post["id"]]
    return {"perfis": {p["usuario_id"]: p for p in perfis}, "grupos": grupos, "posts": posts}


def criar_post(texto, grupo=None):
    texto = texto.strip()
    if not 1 <= len(texto) <= 600:
        raise ValueError("Escreva uma publicação com até 600 caracteres.")
    (obter_cliente().table("comunidade_posts").insert({
        "usuario_id": obter_usuario_id(), "texto": texto, "grupo": grupo,
    }).execute())


def definir_curtida(post_id, curtir):
    banco, usuario_id = obter_cliente(), obter_usuario_id()
    if curtir:
        (banco.table("comunidade_curtidas").upsert({
            "usuario_id": usuario_id, "post_id": post_id,
        }, on_conflict="usuario_id,post_id", ignore_duplicates=True).execute())
    else:
        (banco.table("comunidade_curtidas").delete()
         .eq("usuario_id", usuario_id).eq("post_id", post_id).execute())


def adicionar_comentario(post_id, texto):
    texto = texto.strip()
    if not 1 <= len(texto) <= 300:
        raise ValueError("Escreva um comentário com até 300 caracteres.")
    (obter_cliente().table("comunidade_comentarios").insert({
        "usuario_id": obter_usuario_id(), "post_id": post_id, "texto": texto,
    }).execute())


def definir_participacao(grupo, participar):
    banco, usuario_id = obter_cliente(), obter_usuario_id()
    if participar:
        (banco.table("comunidade_membros").upsert({
            "usuario_id": usuario_id, "grupo": grupo,
        }, on_conflict="usuario_id,grupo", ignore_duplicates=True).execute())
    else:
        (banco.table("comunidade_membros").delete()
         .eq("usuario_id", usuario_id).eq("grupo", grupo).execute())


def carregar_ranking():
    return obter_cliente().rpc("comunidade_ranking_semanal").execute().data


AREAS_GRUPOS = [
    "Tecnologia", "Saúde", "Direito", "Educação", "Engenharias",
    "Ciências Humanas", "Negócios", "Idiomas", "Artes", "Concursos",
]


def normalizar_busca(texto):
    import unicodedata
    texto = unicodedata.normalize("NFKD", texto)
    return " ".join("".join(c for c in texto if not unicodedata.combining(c)).casefold().split())


def grupos_semelhantes(nome, grupos):
    from difflib import SequenceMatcher
    alvo = normalizar_busca(nome)
    if len(alvo) < 3:
        return []
    return [g for g in grupos if (
        alvo in normalizar_busca(g["nome"])
        or normalizar_busca(g["nome"]) in alvo
        or SequenceMatcher(None, alvo, normalizar_busca(g["nome"])).ratio() >= 0.72
    )][:5]


def filtrar_grupos(grupos, busca="", area=None):
    termo = normalizar_busca(busca)
    return [g for g in grupos if (
        (area is None or g.get("area", "Tecnologia") == area)
        and (not termo or termo in normalizar_busca(
            f"{g['nome']} {g['descricao']} {g.get('area', 'Tecnologia')}"
        ))
    )]


def salvar_grupo(nome, descricao, area, nome_original=None):
    nome, descricao, area = " ".join(nome.split()), descricao.strip(), " ".join(area.split())
    if not 3 <= len(nome) <= 80:
        raise ValueError("O nome do grupo deve ter 3 a 80 caracteres.")
    if not 3 <= len(descricao) <= 500:
        raise ValueError("A descrição deve ter 3 a 500 caracteres.")
    if not 2 <= len(area) <= 60:
        raise ValueError("Informe uma área com 2 a 60 caracteres.")
    banco, usuario_id = obter_cliente(), obter_usuario_id()
    dados = {"nome": nome, "descricao": descricao, "area": area}
    try:
        if nome_original is None:
            # O gatilho do banco inclui o criador como membro atomicamente.
            resposta = banco.table("comunidade_grupos").insert({
                **dados, "criador_id": usuario_id,
            }).execute()
        else:
            resposta = (banco.table("comunidade_grupos").update(dados)
                        .eq("nome", nome_original).eq("criador_id", usuario_id).execute())
    except Exception as erro:
        if str(getattr(erro, "code", "")) == "23505":
            raise ValueError("Já existe um grupo com esse nome. Busque o grupo existente ou escolha outro nome.") from erro
        raise
    if not resposta.data:
        raise ValueError("O grupo não foi encontrado ou você não tem permissão para editá-lo. Atualize a comunidade.")
