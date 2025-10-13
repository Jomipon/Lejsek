import streamlit as st
import pandas as pd
import uuid
from login import get_session_from_session_state

if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k adatabázi")    
    st.stop()

database = st.session_state["sb_database"]
tokens = st.session_state["sb_tokens"]

session = None
cookies = None
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

st.markdown("**Seznam partnerů**")
companies = database.from_("company").select("*").order("created_at").execute()
if companies.data:
    df = pd.DataFrame(companies.data)
    df = df.assign(url=df.company_id)
    #df["url"] = df["url"].apply(lambda x: f"{APP_BASE_URL}?company={x}")
    df = df[["company_id", "name", "name_first", "name_last", "active", "note", "created_at", "url"]]
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
        column_order=["name", "active", "url", "note"],
        use_container_width=True,
        key="companies_editor"
    )
else:
    st.write("Seznam je prázdný")

if st.expander("Přidat partnera"):
    with st.form("novy_partner"):
        if st.form_submit_button("Přidat partnera"):
            name = str(uuid.uuid4()).replace("-","")
            try:
                database.from_("company").insert({"name": name, "active": True, "note": "", "name_first": "", "name_last": ""}).execute()
            except Exception as e:
                st.write(e)
"""

#if st.expander("Přidat partnera"):
#    #with st.form("company_add_new_expander", clear_on_submit=True):
#        company_new_name = st.text_input("Název partnera:")
#        #if st.form_submit_button("Přidat partnera"):
#        if st.button("Přidat partnera"):
#            try:
#                database.from_("company").insert({"name":company_new_name.strip(), "active": True, "note": "", "name_first": "", "name_last": ""}).execute()
#                st.session_state["companies_new_show_added_ok"] = True
#                st.session_state.pop("companies_new_show", None)
#            except Exception as e:
#                st.session_state["companies_new_show_added_wrong"] = True
#                st.session_state["companies_new_show_added_wrong_error"] = e
#            st.rerun()

if st.button("Přidat"):
    st.session_state["companies_new_show"] = True
    #partner_new_dialog(database)

if "companies_new_show" in st.session_state and st.session_state["companies_new_show"]:
    with st.form("company_add_new", clear_on_submit=True):
        company_new_name = st.text_input("Název partnera:")
        if st.form_submit_button("Přidat partnera"):
            #try:
            database.from_("company").insert({"name":company_new_name.strip(), "active": True, "note": "", "name_first": "", "name_last": ""}).execute()
            st.session_state["companies_new_show_added_ok"] = True
            st.session_state["companies_new_show"] = False
            st.session_state.pop("companies_new_show", None)
            #except Exception as e:
            #    st.session_state["companies_new_show_added_wrong"] = True
            #    st.session_state["companies_new_show_added_wrong_error"] = e
            #st.rerun()
        if st.form_submit_button("Skrýt"):
            st.session_state["companies_new_show"] = False
            st.session_state.pop("companies_new_show", None)
            st.rerun()
if st.session_state.get("companies_new_show_added_ok", False):
    st.success("Partner byl přidán")
    st.session_state.pop("companies_new_show_added_ok", False)
if "companies_new_show_added_wrong" in st.session_state:
    st.error("Nepovedlo se přidat nového partnera")
    st.error(st.session_state["companies_new_show_added_wrong_error"])
    st.session_state.pop("companies_new_show_added_wrong", False)
    st.session_state.pop("companies_new_show_added_wrong_error", False)

"""