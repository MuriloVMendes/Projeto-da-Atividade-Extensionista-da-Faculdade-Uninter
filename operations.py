import json
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import uuid4
from auth import (
    cliente as obter_cliente,
    usuario_atual as obter_usuario_id,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FEEDBACKS_FILE = DATA_DIR / "feedbacks.json"


def carregar_json(caminho):
    """Carrega um arquivo JSON e retorna seus dados."""
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    except json.JSONDecodeError:
        raise ValueError(f"O arquivo JSON é inválido: {caminho}")


def salvar_json(caminho, dados):
    """Salva dados em JSON garantindo que a pasta exista."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


def carregar_metas():
    resposta = (
        obter_cliente()
        .table("disciplinas")
        .select("id, nome, meta_horas")
        .eq("usuario_id", obter_usuario_id())
        .order("nome")
        .execute()
    )

    return resposta.data


def carregar_sessoes():
    disciplinas = {
        item["id"]: item["nome"]
        for item in carregar_metas()
    }

    resposta = (
        obter_cliente()
        .table("sessoes")
        .select("id, disciplina_id, duracao_minutos, criado_em")
        .eq("usuario_id", obter_usuario_id())
        .order("criado_em", desc=True)
        .execute()
    )

    sessoes = resposta.data

    for sessao in sessoes:
        sessao["disciplina"] = disciplinas.get(
            sessao["disciplina_id"],
            "Disciplina removida",
        )

    return sessoes


def registrar_sessao(disciplina, duracao):
    duracao = int(duracao)

    if not 1 <= duracao <= 1440:
        raise ValueError("Informe uma duração entre 1 e 1440 minutos.")

    # Aceita o ID usado pelo novo painel e o nome usado pelo Pomodoro atual.
    encontrada = next(
        (
            item
            for item in carregar_metas()
            if item["id"] == disciplina or item["nome"] == disciplina
        ),
        None,
    )

    if encontrada is None:
        raise ValueError("Cadastre ou selecione uma disciplina válida.")

    (
        obter_cliente()
        .table("sessoes")
        .insert({
            "usuario_id": obter_usuario_id(),
            "disciplina_id": encontrada["id"],
            "duracao_minutos": duracao,
        })
        .execute()
    )


def salvar_disciplina(nome, meta_horas, disciplina_id=None):
    nome = nome.strip()
    meta_horas = float(meta_horas)

    if not nome or len(nome) > 100:
        raise ValueError("Informe um nome com até 100 caracteres.")

    if meta_horas <= 0:
        raise ValueError("A meta deve ser maior que zero.")

    dados = {
        "nome": nome,
        "meta_horas": meta_horas,
    }

    usuario_id = obter_usuario_id()
    tabela = obter_cliente().table("disciplinas")

    if disciplina_id:
        (
            tabela
            .update(dados)
            .eq("id", disciplina_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
    else:
        (
            tabela
            .insert({
                **dados,
                "usuario_id": usuario_id,
            })
            .execute()
        )


def excluir_sessao(sessao_id):
    (
        obter_cliente()
        .table("sessoes")
        .delete()
        .eq("id", sessao_id)
        .eq("usuario_id", obter_usuario_id())
        .execute()
    )


def calcular_tempo_por_disciplina(sessoes):
    """Calcula o tempo acumulado, em minutos, por disciplina."""
    tempos = {}
    for sessao in sessoes:
        disciplina = sessao["disciplina"]
        duracao = sessao["duracao_minutos"]
        tempos[disciplina] = tempos.get(disciplina, 0) + duracao
    return tempos


def calcular_progresso(tempo_estudado, meta_horas):
    """Calcula o percentual de cumprimento da meta, limitado à barra de 100%."""
    if meta_horas <= 0:
        return 0.0
    meta_minutos = meta_horas * 60
    progresso = (tempo_estudado / meta_minutos) * 100
    return min(progresso, 100.0)


def formatar_tempo(minutos):
    """Converte minutos para uma apresentação em horas e minutos."""
    minutos = int(minutos)
    horas = minutos // 60
    minutos_restantes = minutos % 60
    if horas and minutos_restantes:
        return f"{horas}h {minutos_restantes}min"
    if horas:
        return f"{horas}h"
    return f"{minutos_restantes}min"


def gerar_sugestao(progresso):
    if progresso >= 100:
        return "Meta atingida! Continue mantendo uma rotina consistente."
    if progresso >= 75:
        return "Você está perto da meta. Mantenha a frequência de estudos."
    if progresso >= 50:
        return "Bom progresso. Tente manter sessões regulares para alcançar a meta."
    if progresso > 0:
        return "Continue estudando e procure aumentar gradualmente a frequência das sessões."
    return "Ainda não há sessões registradas. Comece registrando seu primeiro estudo."


# ---------------- Datas da comunidade ----------------

def formatar_data_social(valor):
    """Formata timestamps do feed sem depender de bibliotecas extras."""
    try:
        dt = datetime.fromisoformat(valor)
        agora = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        delta = agora - dt
        segundos = max(0, int(delta.total_seconds()))
        if segundos < 60:
            return "agora"
        if segundos < 3600:
            return f"há {segundos // 60} min"
        if segundos < 86400:
            return f"há {segundos // 3600} h"
        if segundos < 172800:
            return "ontem"
        return dt.strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return "recentemente"


# ---------------- Feedback ----------------

def _configuracao_supabase():
    """Lê as credenciais do banco sem armazená-las no código do projeto."""
    try:
        import streamlit as st

        configuracao = st.secrets["supabase"]
        url = str(configuracao["url"]).rstrip("/")
        chave = str(configuracao["key"])
        if url and chave:
            return url, chave
    except (FileNotFoundError, KeyError, ModuleNotFoundError, TypeError):
        pass
    return None


def feedback_online_ativo():
    """Indica se os feedbacks estão ligados ao armazenamento permanente."""
    return _configuracao_supabase() is not None


def _requisicao_feedback(metodo, parametros="", dados=None):
    configuracao = _configuracao_supabase()
    if not configuracao:
        raise RuntimeError("O banco de feedback ainda não foi configurado.")

    url_base, chave = configuracao
    endereco = f"{url_base}/rest/v1/feedbacks"
    if parametros:
        endereco = f"{endereco}?{parametros}"

    corpo = None
    if dados is not None:
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")

    requisicao = Request(
        endereco,
        data=corpo,
        method=metodo,
        headers={
            "apikey": chave,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Prefer": "return=representation",
        },
    )

    try:
        with urlopen(requisicao, timeout=12) as resposta:
            conteudo = resposta.read().decode("utf-8")
            return json.loads(conteudo) if conteudo else []
    except HTTPError as erro:
        detalhe = erro.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            "O banco recusou a operação. Confira a tabela e as permissões. "
            f"Detalhe: {detalhe[:180]}"
        ) from erro
    except URLError as erro:
        raise RuntimeError(
            "Não foi possível acessar o banco de feedback. Verifique sua conexão."
        ) from erro


def _carregar_feedbacks_locais():
    if not FEEDBACKS_FILE.exists():
        return []
    return carregar_json(FEEDBACKS_FILE).get("feedbacks", [])


def carregar_feedbacks():
    """Carrega os feedbacks públicos do banco ou do arquivo de teste local."""
    if feedback_online_ativo():
        parametros = urlencode({
            "select": "id,nome,anonimo,avaliacao,comentario,criado_em",
            "autorizou_publicacao": "eq.true",
            "order": "criado_em.desc",
        })
        return _requisicao_feedback("GET", parametros)

    return sorted(
        _carregar_feedbacks_locais(),
        key=lambda item: item.get("criado_em", ""),
        reverse=True,
    )


def registrar_feedback(nome, anonimo, avaliacao, comentario, autorizou_publicacao):
    """Valida e salva uma avaliação de zero a cinco estrelas."""
    nome = nome.strip()
    comentario = comentario.strip()
    avaliacao = int(avaliacao)

    if not anonimo and len(nome) < 3:
        raise ValueError("Informe seu nome ou escolha publicar como anônimo.")
    if avaliacao < 0 or avaliacao > 5:
        raise ValueError("Selecione uma nota de 0 a 5 estrelas.")
    if len(comentario) < 10:
        raise ValueError("Escreva um comentário com pelo menos 10 caracteres.")
    if len(comentario) > 500:
        raise ValueError("O comentário pode ter no máximo 500 caracteres.")
    if not autorizou_publicacao:
        raise ValueError("É necessário autorizar a publicação da avaliação.")

    registro = {
        "nome": "Participante anônimo" if anonimo else nome,
        "anonimo": bool(anonimo),
        "avaliacao": avaliacao,
        "comentario": comentario,
        "autorizou_publicacao": True,
    }

    if feedback_online_ativo():
        return _requisicao_feedback("POST", dados=registro)

    registro.update({
        "id": uuid4().hex[:12],
        "criado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
    })
    feedbacks = _carregar_feedbacks_locais()
    feedbacks.append(registro)
    salvar_json(FEEDBACKS_FILE, {"feedbacks": feedbacks})
    return registro


def calcular_resumo_feedback(feedbacks):
    """Calcula os indicadores públicos da avaliação do StudyTrack."""
    total = len(feedbacks)
    if total == 0:
        return {
            "total": 0,
            "media": 0.0,
            "positivos": 0.0,
            "distribuicao": {nota: 0 for nota in range(6)},
        }

    notas = [int(item["avaliacao"]) for item in feedbacks]
    positivos = sum(1 for nota in notas if nota >= 4)
    return {
        "total": total,
        "media": sum(notas) / total,
        "positivos": (positivos / total) * 100,
        "distribuicao": {nota: notas.count(nota) for nota in range(6)},
    }


def formatar_data_feedback(valor):
    try:
        data = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
        return data.strftime("%d/%m/%Y às %H:%M")
    except (TypeError, ValueError):
        return "Data não informada"
