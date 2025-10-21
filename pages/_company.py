from login import get_session_from_session_state
import streamlit as st
from copy import deepcopy

if "sb_database" not in st.session_state:
    st.error("Nepovedlo se připojit k adatabázi")
    st.stop()

database = st.session_state["sb_database"]
tokens = st.session_state["sb_tokens"]

session = None
cookies = None
session = get_session_from_session_state(session, st.session_state["sb_database"], cookies)

def get_changes(old, new, path=()):
    changes = {}
    if isinstance(old, dict) and isinstance(new, dict):
        keys = set(old) | set(old)
        for key in keys:
            p = path + (key,)
            if key not in old:
                changes[p] = new[key]
            elif key not in new:
                changes[p] = None
            else:
                sub = get_changes(old[key], new[key], p)
                changes.update(sub)
    elif old != new:
        changes[path] = new
    return changes
id_company = st.query_params.get("id", None)
is_new = st.query_params.get("new", "0")
is_new = 1 if is_new.isdigit() and int(is_new) == 1 else 0
if not id_company:
    st.query_params.clear() 
    st.switch_page("companies")
else:
    try:
        company = database.from_("company").select("*").filter("company_id", "eq", str(id_company)).execute()
    except:
        st.query_params.clear() 
        st.switch_page("board")
    if company.data:
        #edit
        company = company.data[0]
        if is_new:
            st.query_params.pop("new")
            is_new = 0
    else:
        #new
        if is_new:
            company = { "company_id":id_company, "owner_id": None, "name": "", "name_first": "", "name_last": "", "active": True, "note": "", "created_at":None }
        else:
            st.query_params.clear() 
            st.switch_page("companies")

@st.dialog("Smazat partnera")
def partner_smazat(db, company_id, company_name):
    st.write("Opravdu chcete smazat partnera?")
    st.write(f"{company_name} - {company_id}")
    col_smazat, col_konec = st.columns(2)
    with col_smazat:
        if st.button("Smazat"):
            zavrit_dialog = False
            try:
                db.from_("company").delete().eq("company_id", company_id).execute()
                zavrit_dialog = True
            except Exception as e:
                st.error("Nepovedlo se smazat partnera")
                st.error(e)
            if zavrit_dialog:
                st.rerun()
    with col_konec:
        if st.button("Zavřít"):
            st.rerun()

if is_new:
    st.markdown("**Nový partner**")
else:
    st.markdown("**Detail partnera**")
if company:
    st.session_state[f"company_orig_{id_company}"] = company
    company_edited = deepcopy(st.session_state[f"company_orig_{id_company}"])
    company_edited["name"] = st.text_input("Název:", company_edited["name"])
    company_edited["active"] = st.checkbox("Aktivní:", company_edited["active"])
    company_edited["note"] = st.text_input("Poznámka:", company_edited["note"])

    if is_new:
        if st.button("Vytvořit"):
            insert_data = {
                "company_id":id_company,
                "name": company_edited["name"],
                "name_first": "",
                "name_last": "", 
                "active": company_edited["active"],
                "note": company_edited["note"]
            }
            try:
                database.from_("company").insert(insert_data).execute()
                st.query_params.pop("new", None)
            except:
                st.error("Nepovedlo se vytvořit partnera")
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Uložit"):
                changes = get_changes(st.session_state[f"company_orig_{id_company}"], company_edited, ())
                changes = {".".join(k): v for k, v in changes.items()}
                changes = {k: v for k, v in changes.items() if k}
                if not changes:
                    st.write("Nebylo co uložit")
                else:
                    try:
                        updated_data = database.from_("company").update(changes).eq("company_id", id_company).execute()
                        st.success("Uloženo")
                    except:
                        st.error("Nepovedlo se uložit data")
        with col2:
            if st.button("Smazat"):
                partner_smazat(database, id_company, company_edited["name"])
