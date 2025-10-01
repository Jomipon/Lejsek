import os
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client
from login import set_session_from_session_state, get_login_pageframe, show_login_notifications
import pandas as pd

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
    if st.button("Partneři"):
        st.query_params["companies"] = ""
        st.query_params.update(st.query_params) 
        st.rerun()    
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
        st.markdown("**Seznam partnerů**")
        #st.query_params.pop("companies", None)
        companies = database.from_("company").select("*").order("created_at").execute()
        if companies.data:
            df = pd.DataFrame(companies.data)
            #df = df.assign(_selected=False)
            df = df.assign(url=df.company_id)
            df["url"] = df["url"].apply(lambda x: f"{APP_BASE_URL}?company={x}")
            # zobrazme jen potřebné sloupce (tvoje verze Streamlitu 1.33 nemá visible=False)
            df = df[["company_id", "name", "name_first", "name_last", "active", "note", "created_at"]]
            #company_id uuid
            #owner_id text
            #name text
            #name_first text
            #name_last text
            #active boolean
            #note text
            #created_at timestamp
            #"company_id", "owner_id", "name", "name_first", "name_last", "active", "note", "created_at"
            df_view = st.data_editor(
                data=df,
                hide_index=True,
                disabled=["company_id", "name", "name_first", "name_last", "active", "note", "created_at"],
                column_config={
                    #"_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
                    "url": st.column_config.LinkColumn("", display_text="Detail"),
                },
                column_order=["name", "active", "note"],
                use_container_width=True,
                key="companies_editor"
            )
        else:
            st.write("Seznam je prázdný")
        if st.button("Přidat"):
            st.session_state["companies_new_show"] = True
        if "companies_new_show" in st.session_state and st.session_state["companies_new_show"]:
            with st.form("company_add_new", clear_on_submit=True):
                company_new_name = st.text_input("Název partnera:")
                if st.form_submit_button("Přidat partnera"):
                    try:
                        database.from_("company").insert({"name":company_new_name.strip(), "active": True, "note": "", "name_first": "", "name_last": ""}).execute()
                        st.session_state["companies_new_show_added_ok"] = True
                        st.session_state.pop("companies_new_show", None)
                    except Exception as e:
                        st.session_state["companies_new_show_added_wrong"] = True
                        st.session_state["companies_new_show_added_wrong_error"] = e
                    st.rerun()
                if st.form_submit_button("Skrýt"):
                    st.session_state.pop("companies_new_show", None)
                    st.rerun()
        if st.session_state.get("companies_new_show_added_ok", False):
            st.success("Partner byl přidán")
            st.session_state.pop("companies_new_show_added_ok", False)
        if st.session_state.get("companies_new_show_added_wrong", False):
            st.error("Nepovedlo se přidat nového partnera")
            st.error(st.session_state["companies_new_show_added_wrong_error"])
            st.session_state.pop("companies_new_show_added_wrong", False)
            st.session_state.pop("companies_new_show_added_wrong_error", False)


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
    
