"""Main frontent entry point."""

import time

import extra_streamlit_components as stx
import streamlit as st

from ui.components import api
from ui.components.db_viewer import write_summary_db
from ui.locales import _, init_i18n_gettext, language_selector


def login(welcome_page, cookie_manager):
    """Login/logout sidebar logic."""
    if getattr(st.session_state, "token", None) is None:
        st.subheader(_("Login"))
        user = st.text_input(_("Username"))
        pw = st.text_input(_("Password"), type="password")
        if st.button(_("Login")):
            res = api.login_user(user, pw)
            if res.status_code == 200:
                # reset db cache
                api.reset_score_cache()
                # reset pdf cache
                if "pdf_viewers" in st.session_state:
                    del st.session_state.pdf_viewers
                token = res.json().get("access_token")
                st.session_state.token = token
                st.session_state.user = user
                cookie_manager.set("token", token, key="save_token")
                cookie_manager.set("user", token, key="save_user")
                st.switch_page(welcome_page)
            else:
                st.error(_("Invalid credentials"))
    else:
        if st.button(_("Logout")):
            st.session_state.token = None
            st.rerun()


def main():
    """Render the main navigation app."""
    init_i18n_gettext()

    cookie_manager = stx.CookieManager()

    # load cookie with a little waiting
    saved_token = cookie_manager.get(cookie="token")
    if saved_token is None:
        with st.spinner("Authenticating..."):
            time.sleep(0.5)
            saved_token = cookie_manager.get(cookie="token")

    if saved_token and "token" not in st.session_state:
        st.session_state.token = saved_token
        st.session_state.user = cookie_manager.get(cookie="user")
        st.session_state.user_id = cookie_manager.get(cookie="user_id")

    if "token" not in st.session_state:
        st.session_state.token = None

    welcome_page = st.Page("welcome.py", title=_("Choose a score"))
    database_page = st.Page("database.py", title=_("View database"))
    account_page = st.Page("account.py", title=_("Manage your account"))
    reader_page = st.Page("reader.py", title=_("View a score"))
    st.session_state.reader_page = reader_page

    with st.sidebar:
        if st.session_state.token is not None:
            write_summary_db()
            language_selector()
        login(welcome_page, cookie_manager)
        st.button("reset cache", on_click=api.reset_score_cache)

    if st.session_state.token is not None:
        pages = [welcome_page, database_page, reader_page, account_page]
    else:
        pages = [account_page]

    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":  # pragma: no cover
    main()
