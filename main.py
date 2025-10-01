import os
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client
from login import set_session_from_session_state, get_login_pageframe, show_login_notifications

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://jomipon-beruska-prototyp.streamlit.app")
APP_NAME = os.getenv("APP_NAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def get_database_client():
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

database = get_database_client()

st.set_page_config(page_title="Lejsec") # page_icon
st.title("L.E.J.S.E.C.")

if st.button("Znovu načíst stránku"):
    st.rerun()

session = None 

code = st.query_params.get("code")
if code and "sb_tokens" not in st.session_state: #st.session_state.get("oauth_started")
    try:
        sess = database.auth.exchange_code_for_session({"auth_code": code})
        st.session_state.sb_tokens = (sess.session.access_token, sess.session.refresh_token)
        # úklid
        st.query_params.pop("code", None)
        session = sess
        #st.session_state.oauth_started = False
    except Exception as e:
        # typicky právě „code challenge … does not match …“
        st.error(f"OAuth výměna selhala: {e}")
        st.query_params.pop("code", None)       # zahodíme starý code
        #st.session_state.oauth_started = False  # reset stavu
    finally:
        st.rerun()


session = set_session_from_session_state(session, database)
get_login_pageframe(database, session)
show_login_notifications()
if session:
    if st.button("Odhlásit"):
        try:
            database.auth.sign_out()
            st.session_state["show_loged_out"] = True
        finally:
            st.session_state.pop("token", None)
            st.session_state.pop("sb_tokens", None)
        st.rerun()
else:
    st.warning("Nepřihlášený")

st.write("-"*30)

if session:
    #rozcestník
    params_dict = st.query_params.to_dict()
    st.write(f"{params_dict=}")
    #params_all = st.query_params.get_all()
    #st.write(f"{params_all=}")
    params_items = st.query_params.items()
    for params_item in params_items:
        st.write(f"{params_item=}")
    params_keys = st.query_params.keys()
    for params_key in params_keys:
        st.write(f"{params_key=}")
    st.write(f"fnu {'foods' in st.query_params}")
    company_param = st.query_params.get("company_list")
    #item_param = st.query_params.get("item")
    if "settings" in st.query_params:
        #nastavení
        st.markdown("**settings**")
    #central
    elif "companies" in st.query_params:
        #companies
        st.markdown("**Companies**")
    elif "store" in st.query_params:
        #sklad
        st.markdown("**store**")
    elif "chickens" in st.query_params:
        #slepičky
        st.markdown("**chickens**")
    elif "import_data" in st.query_params:
        #import
        st.markdown("**import_data**")
    elif "eport_data" in st.query_params:
        #export
        st.markdown("**eport_data**")
    elif "reports" in st.query_params:
        #tisky
        st.markdown("**reports**")
    elif "templates" in st.query_params:
        #šablony
        st.markdown("**templates**")
    #tiskové sestavy
    #přehledy - diagramy
    
