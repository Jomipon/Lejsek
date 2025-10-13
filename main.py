import os
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import uuid
from login import set_session_from_params, get_session_from_session_state, get_session_from_cookies
import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://jomipon-beruska-prototyp.streamlit.app")
APP_NAME = os.getenv("APP_NAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

cookies = EncryptedCookieManager(prefix=APP_NAME, password=APP_PASSWORD)
if not cookies.ready():
    st.stop()

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

database = get_client()
if "sb_database" not in st.session_state:
    st.session_state["sb_database"] = database

st.set_page_config(page_title="Lejsec") # page_icon

session = None

set_session_from_params(st.session_state["sb_database"])
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)
session = get_session_from_cookies(session, st.session_state["sb_database"], cookies)

col1, col2 = st.columns(2)
with col1:
    with st.container(width=250):
        st.write("# L.E.J.S.E.C.")
        st.image("lejsek_sedy_kresba.png", use_container_width=True)
with col2:
    if not session or "sb_tokens" not in st.session_state:
        tab_login, tab_register = st.tabs(["Přihlásit", "Registrace"])
        with tab_login:
            with st.form("login", clear_on_submit=True):
                input_username = st.text_input("Email:")
                input_password = st.text_input("Heslo:", type="password")
                if st.form_submit_button("Přihlásit"):
                    try:
                        user = st.session_state["sb_database"].auth.sign_in_with_password({"email": input_username, "password": input_password})
                    except Exception as e:
                        user = None
                    if user:
                        session = st.session_state["sb_database"].auth.get_session()
                        at = session.access_token
                        rt = session.refresh_token
                        st.session_state["sb_tokens"] = (
                            session.access_token,
                            session.refresh_token,
                        )
                        cookies["acceess_token"] = at
                        cookies["refresh_token"] = rt
                        cookies.save()
                        st.session_state["zobrazit_prihlaseno"] = True
                    else:
                        st.error("Jméno nebo heslo je neplatné")
                    st.rerun()
                res = st.session_state["sb_database"].auth.sign_in_with_oauth({
                    "provider": "google",
                    "options": {"redirect_to": APP_BASE_URL}
                })
                auth_url = getattr(res, "url", None) or res.get("url")
                # …a raději odkaz otevři VE STEJNÉM TABU (ne novém):
                #st.markdown(f'<a href="{auth_url}" target="_self" class="st-emotion-cache-7ym5gk ea3mdgi1">Pokračovat na Google</a>', unsafe_allow_html=True)
                #st.markdown(f"[Pokračovat na Google]({auth_url})", unsafe_allow_html=True)
                #st.button("Přihlásit pomocí Google", on_click=)
        with tab_register:
            with st.form("register", clear_on_submit=True):
                register_email = st.text_input("Email:")
                regiter_password = st.text_input("Heslo:", type="password")
                if st.form_submit_button("Vytvořit uživatele"):
                    created_user = st.session_state["sb_database"].auth.sign_up({"email": register_email, "password": regiter_password})
    if session:
        st.write(f"Přihlášený uživatel: {session.user.email}")
        if st.button("Odhlásit"):
            try:
                st.session_state["sb_database"].auth.sign_out()
                st.session_state["show_loged_out"] = True
            finally:
                st.session_state.pop("token", None)
                st.session_state.pop("sb_tokens", None)
            try:
                cookies["acceess_token"] = ""
                cookies["refresh_token"] = ""
                cookies.save()
            except:
                pass
            st.rerun()
    else:
        st.warning("Nepřihlášený")

@st.dialog("Nový partner")
def partner_new_dialog(database):
    st.write("Nový partner")
    name = st.text_input("Název:")
    note = st.text_input("Poznámka:")
    if st.button("Přidat"):
        try:
            ins = database.from_("company").insert({"name": name.strip(), "name_first": name.strip(), "name_last": name.strip(), "active": True, "note": note.strip()}).execute()
            st.success(f"Přidáno: {name}")
            st.rerun()
        except Exception as e:
            st.error(f"Nepovedlo se uložit do databáze: {e}")

if session:
    page_board = st.Page("board.py", title="Board")
    page_comapanies = st.Page("companies.py", title="Seznam partnerů")
    pg = st.navigation([page_board,page_comapanies])
    st.set_page_config(page_title="LEJSEK")
    pg.run()

    #nastavení
    #st.markdown("**settings**")
    #central
    #companies
    #sklad
    #slepičky
    #import
    #export
    #tisky
    #šablony
    #tiskové sestavy
    #přehledy - diagramy

