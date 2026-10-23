"""Autenticação: um cliente Supabase exclusivo por sessão do navegador."""
import streamlit as st
from supabase import create_client


def cliente():
    if 'supabase_cliente' not in st.session_state:
        config = st.secrets['supabase']
        st.session_state.supabase_cliente = create_client(config['url'], config['key'])
    return st.session_state.supabase_cliente


def usuario_atual():
    sessao = cliente().auth.get_session()
    if not sessao:
        raise ValueError('Entre na sua conta para continuar.')
    return sessao.user.id


def exigir_login():
    try:
        sb = cliente()
        sessao = sb.auth.get_session()
    except Exception:
        st.error('Não foi possível iniciar a conexão. Confira .streamlit/secrets.toml e sua conexão.')
        st.stop()

    if sessao:
        st.sidebar.caption(f'Conta: {sessao.user.email}')
        if st.sidebar.button('Sair da conta'):
            try:
                sb.auth.sign_out()
            except Exception:
                st.sidebar.error('Não foi possível sair. Tente novamente.')
                st.stop()
            st.session_state.clear()
            st.rerun()
        return

    st.title('📚 StudyTrack')
    st.write('Entre na sua conta para acompanhar seus estudos.')
    entrar, cadastrar = st.tabs(['Entrar', 'Criar conta'])
    with entrar:
        with st.form('login'):
            email = st.text_input('E-mail', key='login_email')
            senha = st.text_input('Senha', type='password', key='login_senha')
            enviar = st.form_submit_button('Entrar', type='primary')
        if enviar:
            try:
                resposta = sb.auth.sign_in_with_password({'email': email.strip(), 'password': senha})
                if not resposta.session:
                    raise ValueError('Sem sessão')
            except Exception:
                st.error('Não foi possível entrar. Confira e-mail, senha, confirmação do e-mail e conexão.')
            else:
                st.rerun()
    with cadastrar:
        with st.form('cadastro'):
            email = st.text_input('E-mail', key='cadastro_email')
            senha = st.text_input('Senha (mínimo de 8 caracteres)', type='password', key='cadastro_senha')
            confirmar = st.text_input('Confirme a senha', type='password')
            enviar = st.form_submit_button('Criar conta')
        if enviar:
            if not email.strip() or len(senha) < 8:
                st.error('Informe o e-mail e uma senha com pelo menos 8 caracteres.')
            elif senha != confirmar:
                st.error('As senhas não conferem.')
            else:
                try:
                    resposta = sb.auth.sign_up({'email': email.strip(), 'password': senha})
                except Exception:
                    st.error('Não foi possível concluir o cadastro. Confira os dados e tente novamente mais tarde.')
                else:
                    if resposta.session:
                        st.rerun()
                    st.success('Se o cadastro estiver disponível, você receberá um e-mail de confirmação. Confirme e volte à aba Entrar.')
    st.stop()
