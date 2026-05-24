"""Giriş sayfası — cookie geri yükleme + şifre sıfırlama destekli."""
from __future__ import annotations

import streamlit as st
from auth import login as auth_login, ensure_default_admin
from session_helper import save_session_cookie, restore_from_cookie


# ── Ortak stil ────────────────────────────────────────────────────────────────

_CARD_CSS = """
<style>
[data-testid='stSidebar']{display:none!important}
.block-container{padding-top:40px!important}
</style>
"""

_PRIMARY = "#1677FF"
_GRAY = "rgba(0,0,0,0.45)"
_TEXT = "rgba(0,0,0,0.88)"
_BORDER = "#D9D9D9"
_BG_CARD = "#FFFFFF"


def _center_card(content_fn):
    """İçeriği sayfada ortalar."""
    st.markdown(_CARD_CSS, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        content_fn()


# ── Ana giriş formu ───────────────────────────────────────────────────────────

def _login_form():
    st.markdown(
        f"""
        <div style="text-align:center;margin-bottom:8px">
            <span style="font-size:2.5rem">🏢</span>
        </div>
        <h2 style="text-align:center;margin-bottom:4px;font-weight:800;color:{_TEXT}">
            Teknik Operasyon Sistemi
        </h2>
        <p style="text-align:center;color:{_GRAY};margin-bottom:24px;font-size:.95rem">
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
                # Cookie'ye kaydet (kütüphane kuruluysa)
                try:
                    save_session_cookie(ka.strip())
                except Exception:
                    pass
                st.rerun()
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre.")
        else:
            st.warning("⚠️ Kullanıcı adı ve şifre gereklidir.")

    # Şifremi unuttum bağlantısı
    col_l, col_r = st.columns([1, 1])
    if col_r.button("🔑 Şifremi Unuttum", use_container_width=True, key="btn_forgot"):
        st.session_state["login_view"] = "forgot"
        st.rerun()


# ── Şifremi unuttum formu ─────────────────────────────────────────────────────

def _forgot_form():
    st.markdown(
        f"""
        <h3 style="text-align:center;color:{_TEXT};margin-bottom:4px">🔑 Şifre Sıfırla</h3>
        <p style="text-align:center;color:{_GRAY};font-size:.9rem;margin-bottom:20px">
            E-posta veya kullanıcı adınızı girin, sıfırlama bağlantısı göndereceğiz.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("forgot_form"):
        identifier = st.text_input(
            "E-posta veya Kullanıcı Adı",
            placeholder="admin@example.com veya admin",
        )
        base_url = st.text_input(
            "Uygulama URL'si (isteğe bağlı)",
            placeholder="https://uygulamaniz.streamlit.app",
        )
        submitted = st.form_submit_button(
            "📧 Sıfırlama Linki Gönder", type="primary", use_container_width=True
        )

    if submitted:
        if not identifier.strip():
            st.warning("E-posta veya kullanıcı adı giriniz.")
        else:
            _process_forgot(identifier.strip(), base_url.strip())

    if st.button("← Giriş Sayfasına Dön", key="btn_back_forgot"):
        st.session_state["login_view"] = "login"
        st.rerun()


def _process_forgot(identifier: str, base_url: str):
    try:
        from sifre_sifirlama import create_reset_token, send_reset_email
        from db import load_data

        result = create_reset_token(identifier)
        if result is None:
            # Güvenlik: varlık bilgisini ifşa etme
            st.success(
                "✅ Hesap bulunursa sıfırlama linki gönderilecek. Lütfen e-postanızı kontrol edin."
            )
            return

        token, kullanici_adi = result

        # Email adresini bul
        df = load_data("kullanici")
        df["Kullanici_Adi"] = df["Kullanici_Adi"].astype(str)
        row = df[df["Kullanici_Adi"].str.lower() == kullanici_adi.lower()]
        email = str(row.iloc[0]["Email"]) if not row.empty else ""

        if email:
            sent = send_reset_email(email, token, base_url)
            if sent:
                st.success(f"✅ Sıfırlama bağlantısı **{email}** adresine gönderildi.")
            else:
                # SMTP yapılandırılmamış — token'ı ekranda göster (sadece admin kullanır)
                st.warning("⚠️ E-posta gönderilemedi (SMTP yapılandırılmamış).")
                st.info(f"Sıfırlama token'ı: `{token}`  \nURL'ye `?reset={token}` ekleyerek sıfırlayabilirsiniz.")
        else:
            st.warning("Bu hesap için kayıtlı e-posta adresi yok.")
            st.info(f"Sıfırlama token'ı: `{token}`")
    except Exception as e:
        st.error(f"Hata: {e}")


# ── Şifre sıfırlama formu (URL param: ?reset=TOKEN) ──────────────────────────

def _reset_form(token: str):
    st.markdown(
        f"""
        <h3 style="text-align:center;color:{_TEXT};margin-bottom:4px">🔐 Yeni Şifre Belirle</h3>
        <p style="text-align:center;color:{_GRAY};font-size:.9rem;margin-bottom:20px">
            Lütfen yeni şifrenizi girin.
        </p>
        """,
        unsafe_allow_html=True,
    )

    try:
        from sifre_sifirlama import validate_reset_token, use_reset_token

        kullanici_adi = validate_reset_token(token)
        if not kullanici_adi:
            st.error("❌ Bu sıfırlama bağlantısı geçersiz veya süresi dolmuş.")
            if st.button("← Giriş Sayfasına Dön"):
                st.query_params.clear()
                st.session_state["login_view"] = "login"
                st.rerun()
            return

        st.info(f"**{kullanici_adi}** hesabı için şifre sıfırlama")

        with st.form("reset_form"):
            yeni = st.text_input(
                "Yeni Şifre *",
                type="password",
                placeholder="min. 8 karakter",
            )
            yeni2 = st.text_input("Yeni Şifre Tekrar *", type="password")
            submitted = st.form_submit_button(
                "💾 Şifreyi Güncelle", type="primary", use_container_width=True
            )

        if submitted:
            if len(yeni) < 8:
                st.error("Şifre en az 8 karakter olmalıdır.")
            elif yeni != yeni2:
                st.error("Şifreler eşleşmiyor.")
            else:
                if use_reset_token(token, yeni):
                    st.success("✅ Şifreniz güncellendi! Giriş yapabilirsiniz.")
                    st.query_params.clear()
                    st.session_state["login_view"] = "login"
                    st.rerun()
                else:
                    st.error("Şifre güncellenemedi. Token geçersiz olabilir.")
    except Exception as e:
        st.error(f"Hata: {e}")


# ── Ana render fonksiyonu ─────────────────────────────────────────────────────

def render():
    ensure_default_admin()

    # URL'de reset token var mı?
    reset_token = st.query_params.get("reset", "")
    if reset_token:
        _center_card(lambda: _reset_form(reset_token))
        return

    # Görünüm: login | forgot
    view = st.session_state.get("login_view", "login")

    if view == "forgot":
        _center_card(_forgot_form)
    else:
        _center_card(_login_form)
