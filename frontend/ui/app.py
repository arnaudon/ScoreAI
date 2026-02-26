"""Main frontent entry point."""

import time
from datetime import datetime, timedelta

import streamlit as st

try:
    import extra_streamlit_components as stx
except ImportError:
    stx = None

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
                st.session_state.token = token
                cookie_manager.set(
                    "token", token, key="save_token", expires_at=COOKIE_EXPIRES
                )
            else:
                st.error(_("Invalid credentials"))
    else:
        if st.button(_("Logout")):  # pragma: no cover
            st.session_state.token = None
            cookie_manager.delete("token")
            st.switch_page(welcome_page)


def _load_token(cookie_manager: stx.CookieManager):
    """load cookie with a little waiting"""
    saved_token = cookie_manager.get(cookie="token")
    if saved_token is None:
        with st.spinner("Authenticating..."):
            time.sleep(0.5)
            saved_token = cookie_manager.get(cookie="token")

    if saved_token and "token" not in st.session_state:  # pragma: no cover
        st.session_state.token = saved_token

    if "token" not in st.session_state:  # pragma: no cover
        st.session_state.token = None

    if not api.valid_token():
        st.session_state.token = None

    # set user data
    st.session_state.user = api.get_user()


def main():
    """Render the main navigation app."""

    init_i18n_gettext()

    if stx:
        cookie_manager = stx.CookieManager(key="user_cookie")
        _load_token(cookie_manager)
    else:
        cookie_manager = None

    welcome_page = st.Page("welcome.py", title=_("Choose a score"))
    database_page = st.Page("database.py", title=_("View database"))
    account_page = st.Page("account.py", title=_("Manage your account"))
    reader_page = st.Page("reader.py", title=_("View a score"))
    admin_page = st.Page("admin.py", title=_("Admin"))
    st.session_state.reader_page = reader_page

    st.session_state.is_admin = api.is_admin()

    with st.sidebar:
        if st.session_state.token is not None:
            write_summary_db()
            language_selector()
        if cookie_manager:
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
