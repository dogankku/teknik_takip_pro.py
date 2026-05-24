"""İlk kurulum sihirbazı — hiç admin kullanıcı yokken gösterilir."""
from __future__ import annotations

import streamlit as st

# ── Renk sabitleri (style.py C dict'inden elle alındı — import yok) ──────────
_PRIMARY = "#1677FF"
_PRIMARY_LIGHT = "#E6F4FF"
_GRAY = "rgba(0,0,0,0.45)"
_TEXT = "rgba(0,0,0,0.88)"
_BG_CARD = "#FFFFFF"
_BORDER_2 = "#F0F0F0"
_SUCCESS = "#52C41A"
_SUCCESS_BG = "#F6FFED"
_SUCCESS_BD = "#B7EB8F"


# ── Sidebar gizle ─────────────────────────────────────────────────────────────

def _hide_sidebar():
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none!important}</style>",
        unsafe_allow_html=True,
    )


# ── Adım ilerleme göstergesi ──────────────────────────────────────────────────

def _step_progress(current: int):
    """Üstte 'Tesis → Admin → Hazır' göstergesi; aktif adım kalın + mavi."""
    steps = [(1, "① Tesis"), (2, "② Admin"), (3, "③ Hazır")]
    parts = []
    for i, (num, label) in enumerate(steps):
        if num == current:
            style = (
                f"font-weight:700;color:{_PRIMARY};font-size:15px"
            )
        else:
            style = f"color:{_GRAY};font-size:15px"
        parts.append(f'<span style="{style}">{label}</span>')
        if i < len(steps) - 1:
            parts.append(
                f'<span style="color:{_GRAY};margin:0 8px">→</span>'
            )

    st.markdown(
        f'<div style="text-align:center;padding:16px 0 24px;'
        f'border-bottom:1px solid {_BORDER_2};margin-bottom:24px">'
        + "".join(parts)
        + "</div>",
        unsafe_allow_html=True,
    )


# ── Adım 1: Tesis Bilgileri ───────────────────────────────────────────────────

def _step1(col):
    with col:
        st.subheader("🏢 Tesis Bilgileri")
        tesis_adi = st.text_input(
            "Tesis / Bina Adı *", placeholder="Örn: Güneş Residence"
        )
        adres = st.text_area("Adres", height=80)
        # logo_file = st.file_uploader("Logo (PNG/JPG)", type=["png","jpg","jpeg"])
        if st.button("İleri →", type="primary", use_container_width=True):
            if tesis_adi.strip():
                st.session_state["wiz_tesis_adi"] = tesis_adi.strip()
                st.session_state["wiz_adres"] = adres.strip()
                st.session_state["wizard_step"] = 2
                st.rerun()
            else:
                st.error("Tesis adı zorunludur.")


# ── Adım 2: Admin Hesabı ──────────────────────────────────────────────────────

def _step2(col):
    with col:
        st.subheader("👤 Admin Hesabı Oluştur")
        ad_soyad = st.text_input("Ad Soyad *")
        email = st.text_input("E-posta *")
        kullanici_adi = st.text_input(
            "Kullanıcı Adı *", placeholder="min. 3 karakter"
        )
        sifre = st.text_input(
            "Şifre *", type="password", placeholder="min. 8 karakter"
        )
        sifre2 = st.text_input("Şifre Tekrar *", type="password")

        col1, col2 = st.columns(2)
        if col1.button("← Geri"):
            st.session_state["wizard_step"] = 1
            st.rerun()
        if col2.button("İleri →", type="primary", use_container_width=True):
            errors = []
            if not ad_soyad.strip():
                errors.append("Ad Soyad zorunludur.")
            if not email.strip():
                errors.append("E-posta zorunludur.")
            if len(kullanici_adi.strip()) < 3:
                errors.append("Kullanıcı adı en az 3 karakter olmalıdır.")
            if len(sifre) < 8:
                errors.append("Şifre en az 8 karakter olmalıdır.")
            if sifre != sifre2:
                errors.append("Şifreler eşleşmiyor.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.session_state["wiz_ad_soyad"] = ad_soyad.strip()
                st.session_state["wiz_email"] = email.strip()
                st.session_state["wiz_kullanici_adi"] = kullanici_adi.strip()
                st.session_state["wiz_sifre"] = sifre
                st.session_state["wizard_step"] = 3
                st.rerun()


# ── Adım 3: Hazır ─────────────────────────────────────────────────────────────

def _step3(col):
    with col:
        st.subheader("✅ Her Şey Hazır!")

        tesis = st.session_state.get("wiz_tesis_adi", "")
        admin_name = st.session_state.get("wiz_ad_soyad", "")
        admin_email = st.session_state.get("wiz_email", "")
        adres = st.session_state.get("wiz_adres", "") or "—"

        # Başarı özet kartı
        summary_rows = ""
        for label, value in [
            ("🏢 Tesis", tesis),
            ("📍 Adres", adres),
            ("👤 Admin", admin_name),
            ("📧 E-posta", admin_email),
        ]:
            summary_rows += (
                f'<div style="display:flex;justify-content:space-between;'
                f'padding:10px 0;border-bottom:1px solid {_BORDER_2};">'
                f'<span style="color:{_GRAY};font-size:13px">{label}</span>'
                f'<span style="color:{_TEXT};font-size:13px;font-weight:500">'
                f"{value}</span></div>"
            )

        st.markdown(
            f'<div style="background:{_SUCCESS_BG};border:1px solid {_SUCCESS_BD};'
            f"border-radius:8px;padding:20px;margin-bottom:20px;"
            f'box-shadow:0 1px 2px rgba(0,0,0,0.04)">'
            f'<div style="color:{_SUCCESS};font-size:16px;font-weight:600;'
            f'margin-bottom:12px">Kurulum tamamlanmaya hazır</div>'
            f"{summary_rows}"
            f"</div>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        if col1.button("← Geri"):
            st.session_state["wizard_step"] = 2
            st.rerun()

        if col2.button(
            "🚀 Sistemi Başlat", type="primary", use_container_width=True
        ):
            from auth import add_user

            ok, msg = add_user(
                kullanici_adi=st.session_state["wiz_kullanici_adi"],
                sifre=st.session_state["wiz_sifre"],
                ad_soyad=st.session_state["wiz_ad_soyad"],
                rol="Admin",
                email=st.session_state["wiz_email"],
            )
            if ok:
                st.session_state["bina_adi"] = st.session_state["wiz_tesis_adi"]
                st.session_state["bina_adres"] = st.session_state.get(
                    "wiz_adres", ""
                )
                # Otomatik giriş
                from auth import login as auth_login

                u = auth_login(
                    st.session_state["wiz_kullanici_adi"],
                    st.session_state["wiz_sifre"],
                )
                if u:
                    st.session_state["current_user"] = u
                st.rerun()
            else:
                st.error(msg)


# ── Ana giriş noktası ─────────────────────────────────────────────────────────

def render():
    """Kurulum sihirbazını render et."""
    _hide_sidebar()

    # Sayfa üst boşluğunu azalt
    st.markdown(
        "<style>.block-container{padding-top:40px!important}</style>",
        unsafe_allow_html=True,
    )

    # Wizard adımını başlat
    if "wizard_step" not in st.session_state:
        st.session_state["wizard_step"] = 1

    current_step = st.session_state["wizard_step"]

    # Sayfa başlığı
    st.markdown(
        f'<div style="text-align:center;margin-bottom:8px">'
        f'<span style="font-size:36px">🏢</span></div>'
        f'<h2 style="text-align:center;color:{_TEXT};margin:0 0 4px;'
        f'font-size:24px;font-weight:700">Teknik Takip Pro</h2>'
        f'<p style="text-align:center;color:{_GRAY};margin-bottom:0;font-size:14px">'
        f"İlk kurulum — birkaç adımda sisteminizi hazırlayın</p>",
        unsafe_allow_html=True,
    )

    # İçeriği ortala
    left, mid, right = st.columns([1, 2, 1])

    with mid:
        _step_progress(current_step)

    if current_step == 1:
        _step1(mid)
    elif current_step == 2:
        _step2(mid)
    elif current_step == 3:
        _step3(mid)
