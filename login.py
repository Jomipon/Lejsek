import streamlit as st
import datetime

def set_session_from_params(database):
    st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 1 - 1")
    code = st.query_params.get("code")
    if code and "sb_tokens" not in st.session_state:
        try:
            st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 1 - 2")
            sess = database.auth.exchange_code_for_session({"auth_code": code})
            st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 1 - 3")
            # ulož tokeny do session_state pro další render
            st.session_state["sb_tokens"] = (
                sess.session.access_token,
                sess.session.refresh_token,
            )
            st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 1 - 4")
        except Exception as e:
            st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 1 - 5 {e}")
            st.error(f"OAuth výměna selhala: {e}")
        finally:
            # smaž ?code=... z URL a rerun
            st.query_params.clear()
        st.rerun()
def get_session_from_session_state(session, database, cookies):
    st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 2 - 1")
    if session is None and "sb_tokens" in st.session_state:
        try:
            st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 2 - 2")
            at, rt = st.session_state["sb_tokens"]
            if cookies is not None:
                cookies["acceess_token"] = at
                cookies["refresh_token"] = rt
                st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 2 - 3")
                cookies.save()
                st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 2 - 4")
            database.auth.set_session(at, rt)
            st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 2 - 5")
            session = database.auth.get_session()
            st.write(f"{datetime.datetime.now().strftime("%H:%M:%S")} - 2 - 6")
        except Exception as e:
            pass
        
    return session
def get_session_from_cookies(session, database, cookies):
    if session is None and (not session or "sb_tokens" not in st.session_state) and "acceess_token" in cookies and "refresh_token" in cookies:
        try:
            at = cookies["acceess_token"]
            rt = cookies["refresh_token"]
            database.auth.set_session(at, rt)
            st.session_state["sb_tokens"] = (at,rt,)
        except Exception as e:
            pass
        session = database.auth.get_session()
    return session



def set_session_from_session_state(session, database):
    if "sb_tokens" in st.session_state:
        try:
            at, rt = st.session_state["sb_tokens"]
            database.auth.set_session(at, rt)
        except:
            pass
        session = database.auth.get_session()
    return session

def get_login_pageframe(database, session):
    if not session or "sb_tokens" not in st.session_state:
        with st.form("login", clear_on_submit=True):
            input_username = st.text_input("Username:")
            input_password = st.text_input("Password:", type="password")
            if st.form_submit_button("Přihlásit"):
                try:
                    user = database.auth.sign_in_with_password({"email": input_username, "password": input_password})
                except Exception as e:
                    user = None
                if user:
                    session = database.auth.get_session()
                    st.session_state["sb_tokens"] = (
                        session.access_token,
                        session.refresh_token,
                    )
                    st.session_state["show_loged_in"] = True
                else:
                    st.session_state["show_loged_in_wrong"] = True
                st.rerun()
def show_login_notifications():
    if st.session_state.get("show_loged_in", False):
        st.success("Přihlášeno")
        st.session_state.pop("show_loged_in", None)
    if st.session_state.get("show_loged_out", False):
        st.success("Odhlášeno")
        st.session_state.pop("show_loged_out")
    if st.session_state.get("show_loged_in_wrong", False):
        st.error("Jméno nebo heslo je neplatné")
        st.session_state.pop("show_loged_in_wrong")



def login_pageframe_by_gmail(database, app_base_url):
    st.markdown("**Google**")
    res = database.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {"redirect_to": app_base_url}
    })
    auth_url = getattr(res, "url", None) or res.get("url")
    # …a raději odkaz otevři VE STEJNÉM TABU (ne novém):
    st.markdown(f'<a href="{auth_url}" target="_self" class="st-emotion-cache-7ym5gk ea3mdgi1">Přihlásit pomocí Google účtu</a>', unsafe_allow_html=True)
    #st.markdown(f"[Přihlásit pomocí Google účtu ]({auth_url})", unsafe_allow_html=True)
    if st.form_submit_button("Skrýt"):
        st.session_state["show_login"] = False
        st.rerun()

