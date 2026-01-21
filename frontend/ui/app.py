"""Main frontent entry point."""

import time
from datetime import datetime, timedelta

import extra_streamlit_components as stx
import streamlit as st

from ui.components import api
from ui.components.db_viewer import write_summary_db
from ui.locales import _, init_i18n_gettext, language_selector

COOKIE_EXPIRES = datetime.now() + timedelta(days=1)


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
                if "pdf_viewers" in st.session_state:  # pragma: no cover
                    del st.session_state.pdf_viewers
                token = res.json().get("access_token")
                user_id = res.json().get("user_id")
                st.session_state.token = token
                st.session_state.user = user
                st.session_state.user_id = user_id
                cookie_manager.set("token", token, key="save_token", expires_at=COOKIE_EXPIRES)
                cookie_manager.set("user", user, key="save_user", expires_at=COOKIE_EXPIRES)
                cookie_manager.set(
                    "user_id", user_id, key="save_user_id", expires_at=COOKIE_EXPIRES
                )
                st.switch_page(welcome_page)
            else:
                st.error(_("Invalid credentials"))
    else:
        if st.button(_("Logout")):  # pragma: no cover
            st.session_state.token = None
            cookie_manager.delete("token")


import requests

from ui.components.api import API_URL


def _load_token(cookie_manager: stx.CookieManager):
    """load cookie with a little waiting"""
    saved_token = cookie_manager.get(cookie="token")
    if saved_token is None:
        with st.spinner("Authenticating..."):
            time.sleep(0.5)
            saved_token = cookie_manager.get(cookie="token")

    if saved_token and "token" not in st.session_state:  # pragma: no cover
        st.session_state.token = saved_token
        st.session_state.user = cookie_manager.get(cookie="user")
        st.session_state.user_id = cookie_manager.get(cookie="user_id")

    if "token" not in st.session_state:  # pragma: no cover
        st.session_state.token = None

    if not api.valid_token():
        st.session_state.token = None


def main():
    """Render the main navigation app."""

    init_i18n_gettext()
    cookie_manager = stx.CookieManager()

    _load_token(cookie_manager)
    welcome_page = st.Page("welcome.py", title=_("Choose a score"))
    database_page = st.Page("database.py", title=_("View database"))
    account_page = st.Page("account.py", title=_("Manage your account"))
    reader_page = st.Page("reader.py", title=_("View a score"))
    admin_page = st.Page("admin.py", title=_("Admin"))
    st.session_state.reader_page = reader_page

    if "is_admin" not in st.session_state:
        st.session_state.is_admin = api.is_admin()

    with st.sidebar:
        if st.session_state.token is not None:
            write_summary_db()
            language_selector()
        login(welcome_page, cookie_manager)
        st.button("reset cache", on_click=api.reset_score_cache)

    if st.session_state.token is not None:
        pages = [welcome_page, database_page, reader_page, account_page]

        if st.session_state.is_admin:
            pages.append(admin_page)
    else:
        pages = [account_page]
    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":  # pragma: no cover
    main()
