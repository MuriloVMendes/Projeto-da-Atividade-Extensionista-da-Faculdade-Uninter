"""Estilo visual compartilhado entre todas as páginas do StudyTrack."""

import streamlit as st

PRIMARY = "#4F46E5"
PRIMARY_DARK = "#4338CA"
ACCENT = "#06B6D4"
BG = "#F6F7FB"
CARD_BG = "#FFFFFF"
TEXT = "#0F172A"
MUTED = "#64748B"


def aplicar_estilo():
    """Injeta o CSS global usado em todas as páginas do app."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
        .stApp {{ background: {BG}; }}
        #MainMenu, footer {{visibility: hidden;}}
        .block-container {{ max-width: 1240px; padding-top: 2rem; }}

        section[data-testid="stSidebar"] {{ background: {CARD_BG}; border-right: 1px solid #E7E9F5; }}
        .brand {{ display:flex; align-items:center; gap:10px; padding:6px 4px 18px; border-bottom:1px solid #EEF0FA; margin-bottom:14px; }}
        .brand-logo {{ width:34px; height:34px; border-radius:9px; background:linear-gradient(135deg,{PRIMARY},{ACCENT}); display:flex; align-items:center; justify-content:center; font-size:18px; }}
        .brand-name {{ font-weight:800; font-size:17px; color:{TEXT}; letter-spacing:-.3px; }}
        a[data-testid="stPageLink-NavLink"] {{ border-radius:10px !important; font-weight:600 !important; }}

        .stButton > button, .stFormSubmitButton > button {{
            background:linear-gradient(135deg,{PRIMARY},{PRIMARY_DARK}); color:white; border:none; border-radius:10px;
            padding:10px 22px; font-weight:700; transition:transform .15s ease, box-shadow .15s ease;
            box-shadow:0 6px 16px rgba(79,70,229,.20);
        }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{ transform:translateY(-1px); box-shadow:0 10px 22px rgba(79,70,229,.28); color:white; }}
        button[kind="secondary"] {{ background:white !important; color:{TEXT} !important; border:1px solid #E5E7EB !important; box-shadow:none !important; }}

        div[data-testid="stMetric"] {{ background:{CARD_BG}; border:1px solid #ECEEF7; border-radius:16px; padding:18px 20px; box-shadow:0 6px 20px rgba(15,23,42,.05); }}
        div[data-testid="stProgress"] > div > div {{ background:linear-gradient(90deg,{PRIMARY},{ACCENT}); }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius:16px !important; border:1px solid #ECEEF7 !important; box-shadow:0 6px 20px rgba(15,23,42,.05); background:#fff; }}
        h1,h2,h3 {{ color:{TEXT}; letter-spacing:-.4px; }}
        .subtitle {{ color:{MUTED}; font-size:1.02rem; }}
        .badge-pill {{ display:inline-block; background:#EEF0FE; color:{PRIMARY}; padding:6px 16px; border-radius:999px; font-weight:700; font-size:.85rem; margin-bottom:14px; }}

        .profile-card {{ background:linear-gradient(145deg,#ffffff,#f5f7ff); border:1px solid #e8eafb; border-radius:18px; padding:22px; margin-bottom:12px; }}
        .profile-avatar {{ width:58px; height:58px; border-radius:18px; background:#EEF0FE; display:flex; align-items:center; justify-content:center; font-size:30px; margin-bottom:12px; }}
        .profile-name {{ font-weight:800; color:{TEXT}; font-size:1.1rem; }}
        .profile-user {{ color:{MUTED}; font-size:.88rem; margin-bottom:8px; }}
        .profile-bio {{ color:#475569; font-size:.92rem; line-height:1.5; }}

        .post-head {{ display:flex; align-items:center; gap:11px; margin-bottom:10px; }}
        .post-avatar {{ width:42px; height:42px; background:#EEF0FE; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:22px; flex-shrink:0; }}
        .post-author {{ font-weight:750; color:{TEXT}; }}
        .post-meta {{ color:{MUTED}; font-size:.82rem; }}
        .post-text {{ color:#273449; line-height:1.58; font-size:.98rem; margin:6px 0 12px; }}
        .group-tag {{ display:inline-block; background:#F0FDFA; color:#0F766E; border:1px solid #CCFBF1; border-radius:999px; padding:4px 9px; font-size:.75rem; font-weight:700; }}
        .comment-box {{ background:#F8FAFC; border-radius:10px; padding:9px 12px; margin:7px 0; font-size:.88rem; color:#475569; }}
        .feedback-stars {{ font-size:1.1rem; letter-spacing:2px; margin-bottom:10px; color:#D97706; font-weight:700; }}
        .feedback-comment {{ color:#273449; line-height:1.6; font-size:.98rem; margin-bottom:12px; }}
        .feedback-author {{ color:{MUTED}; font-size:.82rem; font-weight:600; }}
        .rank-row {{ display:flex; align-items:center; gap:10px; padding:10px 0; border-bottom:1px solid #F1F5F9; }}
        .rank-pos {{ width:26px; font-weight:800; color:{PRIMARY}; }}
        .rank-avatar {{ width:34px; height:34px; border-radius:10px; background:#F1F5F9; display:flex; align-items:center; justify-content:center; }}
        .rank-name {{ flex:1; font-weight:650; color:{TEXT}; }}
        .rank-time {{ color:{MUTED}; font-size:.82rem; text-align:right; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand():
    st.sidebar.markdown(
        """
        <div class="brand">
            <div class="brand-logo">📚</div>
            <div class="brand-name">StudyTrack</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
