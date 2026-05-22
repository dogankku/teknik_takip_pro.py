import streamlit as st
from auth import login as auth_login, ensure_default_admin


def render():
    ensure_default_admin()

    # Sidebar'ı gizle
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none!important}</style>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown(
            """
            <div style="text-align:center;margin-bottom:8px">
                <span style="font-size:2.5rem">🏢</span>
            </div>
            <h2 style="text-align:center;margin-bottom:4px;font-weight:800">
                Teknik Operasyon Sistemi
            </h2>
            <p style="text-align:center;color:#6B7280;margin-bottom:24px;font-size:.95rem">
                Hesabınıza giriş yapın
            </p>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            ka = st.text_input("👤 Kullanıcı Adı", placeholder="admin")
            sf = st.text_input("🔒 Şifre", type="password", placeholder="••••••••")
            submitted = st.form_submit_button(
                "Giriş Yap →",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if ka and sf:
                u = auth_login(ka.strip(), sf)
                if u:
                    st.session_state["current_user"] = u
                    st.rerun()
                else:
                    st.error("❌ Hatalı kullanıcı adı veya şifre.")
            else:
                st.warning("⚠️ Kullanıcı adı ve şifre gereklidir.")

        st.info("🔑 İlk kurulum: kullanıcı **admin** · şifre **admin123**")
