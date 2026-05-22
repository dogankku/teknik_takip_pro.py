import streamlit as st
from auth import login, ensure_default_admin


def render():
    ensure_default_admin()

    # Full-page centered layout
    st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0F172A 0%, #1E3A6E 50%, #0F172A 100%) !important; }
    .main .block-container { padding-top: 5vh !important; }
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:40px 48px 32px;
                    background:rgba(255,255,255,.05);backdrop-filter:blur(12px);
                    border:1px solid rgba(255,255,255,.1);border-radius:20px;
                    box-shadow:0 25px 60px rgba(0,0,0,.4);">
            <div style="font-size:3.5rem;margin-bottom:8px;">🏢</div>
            <div style="font-size:1.5rem;font-weight:700;color:#F8FAFC;
                        margin-bottom:4px;">Teknik Operasyon</div>
            <div style="font-size:.8rem;color:#64748B;letter-spacing:.08em;
                        text-transform:uppercase;margin-bottom:32px;">
                Otel · Rezidans · Toplu Konut Yönetimi
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            ka = st.text_input("👤  Kullanıcı Adı", placeholder="kullanici.adi")
            sf = st.text_input("🔒  Şifre", type="password", placeholder="••••••••")
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
        <div style="margin-top:20px;background:rgba(255,255,255,.04);
                    border:1px solid rgba(255,255,255,.08);border-radius:10px;
                    padding:12px 16px;">
            <div style="font-size:.72rem;color:#475569;font-weight:600;
                        text-transform:uppercase;letter-spacing:.06em;
                        margin-bottom:6px;">İlk Kurulum</div>
            <div style="font-size:.8rem;color:#94A3B8;">
                Kullanıcı: <code style="background:rgba(255,255,255,.1);
                padding:1px 6px;border-radius:4px;color:#93C5FD;">admin</code>
                &nbsp;&nbsp;
                Şifre: <code style="background:rgba(255,255,255,.1);
                padding:1px 6px;border-radius:4px;color:#93C5FD;">admin123</code>
            </div>
        </div>
        """, unsafe_allow_html=True)
