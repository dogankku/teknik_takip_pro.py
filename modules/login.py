import streamlit as st
from auth import login, ensure_default_admin


def render():
    ensure_default_admin()

    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stAppViewContainer"] > .main {
        background:
            radial-gradient(at 20% 20%, rgba(99,102,241,.18) 0px, transparent 50%),
            radial-gradient(at 80% 0%,  rgba(236,72,153,.15) 0px, transparent 50%),
            radial-gradient(at 0% 80%,  rgba(6,182,212,.15) 0px, transparent 50%),
            radial-gradient(at 80% 80%, rgba(139,92,246,.18) 0px, transparent 50%),
            #FAFBFF !important;
    }
    .main .block-container {
        padding-top: 4rem !important;
        max-width: 480px !important;
        margin: 0 auto !important;
    }
    .lg-logo {
        width: 64px; height: 64px;
        margin: 0 auto 20px;
        border-radius: 18px;
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.8rem; color: white;
        box-shadow: 0 12px 32px rgba(99,102,241,.4);
        text-align: center;
        line-height: 64px;
    }
    .lg-title {
        text-align: center;
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 6px;
        letter-spacing: -.02em;
    }
    .lg-sub {
        text-align: center;
        font-size: .85rem;
        color: #64748B;
        margin-bottom: 32px;
    }
    .lg-hint {
        margin-top: 22px;
        padding: 14px 16px;
        background: rgba(99,102,241,.06);
        border: 1px solid rgba(99,102,241,.15);
        border-radius: 12px;
    }
    .lg-hint-label {
        font-size: .7rem;
        font-weight: 700;
        color: #4F46E5;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-bottom: 6px;
    }
    .lg-hint-row {
        font-size: .82rem;
        color: #475569;
    }
    .lg-hint-row code {
        background: white;
        border: 1px solid #E0E7FF;
        color: #4F46E5;
        padding: 2px 8px;
        border-radius: 6px;
        font-family: 'SF Mono', Monaco, monospace;
        font-size: .78rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="lg-logo">🏢</div>', unsafe_allow_html=True)
    st.markdown('<div class="lg-title">Hoşgeldiniz</div>', unsafe_allow_html=True)
    st.markdown('<div class="lg-sub">Teknik Operasyon Yönetim Sistemi\'ne giriş yapın</div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        ka = st.text_input("Kullanıcı Adı", placeholder="admin")
        sf = st.text_input("Şifre", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Giriş Yap →",
                                          type="primary",
                                          use_container_width=True)
        if submitted:
            if ka and sf:
                u = login(ka, sf)
                if u:
                    st.session_state["current_user"] = u
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre.")
            else:
                st.warning("Lütfen tüm alanları doldurun.")

    st.markdown("""
    <div class="lg-hint">
        <div class="lg-hint-label">İlk kurulum bilgileri</div>
        <div class="lg-hint-row">
            Kullanıcı: <code>admin</code> &nbsp; Şifre: <code>admin123</code>
        </div>
    </div>
    """, unsafe_allow_html=True)
