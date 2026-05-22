import streamlit as st
from auth import login, ensure_default_admin


def render():
    ensure_default_admin()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏢 Teknik Operasyon Sistemi")
        st.caption("Otel / Rezidans / Toplu Konut Yönetim Platformu")
        st.markdown("---")

        with st.form("login_form"):
            st.subheader("🔐 Giriş")
            ka = st.text_input("Kullanıcı Adı")
            sf = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş Yap", type="primary", use_container_width=True):
                u = login(ka, sf)
                if u:
                    st.session_state["current_user"] = u
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre.")

        with st.expander("ℹ️ İlk Kurulum Bilgisi"):
            st.info("""
            **Varsayılan Admin:**
            - Kullanıcı adı: `admin`
            - Şifre: `admin123`

            ⚠️ İlk girişten sonra **Kullanıcı Yönetimi** sayfasından admin şifresini değiştirin.
            """)
