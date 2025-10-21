import streamlit as st
import pandas as pd
import uuid
from login import get_session_from_session_state

if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k adatabázi")
    st.stop()

database = st.session_state.get("sb_database", None)
tokens = st.session_state.get("sb_tokens", None)

session = None
cookies = None
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

if database is None:
    st.query_params.clear() 
    st.switch_page("pages/companies")

st.markdown("**Seznam partnerů**")
st.page_link("pages/_company.py", label="Detail")
try:
    database.rpc("create_owner_id").execute()
except:
    st.query_params.clear() 
    st.switch_page("companies")

companies = database.from_("company").select("*").order("name").execute()
if companies.data:
    df = pd.DataFrame(companies.data)
    df = df.assign(url=df.company_id)
    df["url"] = df["url"].apply(lambda x: f"{st.session_state['app_base_url']}/company?id={x}")
    df = df[["company_id", "name", "name_first", "name_last", "active", "note", "created_at", "url"]]
    df_view = st.data_editor(
        data=df,
        hide_index=True,
        disabled=["company_id", "name", "name_first", "name_last", "active", "note", "created_at"],
        column_config={
            #"_selected": st.column_config.CheckboxColumn("Vybrat", default=False),
            "url": st.column_config.LinkColumn("", width="large"), #, display_text="Detail"
            "name": st.column_config.TextColumn("Název partnera", width="large"),
            "active": st.column_config.CheckboxColumn("Aktivní", width="small"),
        },
        column_order=["name", "active", "url", "note"],
        use_container_width=True,
        key="companies_editor"
    )
else:
    st.write("Seznam je prázdný")
new_id_company = str(uuid.uuid4()).replace("-","")
st.link_button(url=f"company?id={new_id_company}&new=1", label="Nový partner")
