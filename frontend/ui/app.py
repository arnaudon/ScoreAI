"""Main frontent entry point."""

from ui.components import api
import streamlit as st

from ui.components.db_viewer import write_summary_db
from ui.locales import _, init_i18n_gettext, language_selector

init_i18n_gettext()

if "token" not in st.session_state:
    st.session_state.token = None

welcome_page = st.Page("welcome.py", title=_("Choose a score"))
database_page = st.Page("database.py", title=_("View database"))
account_page = st.Page("account.py", title=_("Manage your account"))


def login():
    """Login logic"""
    if st.session_state.token is None:
        st.subheader(_("Login"))
        user = st.text_input(_("Username"))
        pw = st.text_input(_("Password"), type="password")
        if st.button(_("Login")):
            res = api.login_user(user, pw)
            if res.status_code == 200:
                # Store the token from your FastAPI response
                st.session_state.token = res.json().get("access_token")
                st.switch_page(welcome_page)
                st.rerun()
            else:
                st.error(_("Invalid credentials"))
    else:
        if st.button(_("Logout")):
            st.session_state.token = None
            st.rerun()


with st.sidebar:
    if st.session_state.token is not None:
        write_summary_db()
        language_selector()
    login()

if st.session_state.token is not None:
    pages = [welcome_page, database_page, account_page]
else:
    pages = [account_page]

pg = st.navigation(pages)
pg.run()
