"""Main frontent entry point."""

import streamlit as st

from scoreai.frontend.components.ui_widgets import write_summary_db
from scoreai.frontend.locales import _, init_i18n_gettext, language_selector

init_i18n_gettext()

with st.sidebar:
    write_summary_db()
    language_selector()

pages = {
    _("Welcome"): [
        st.Page("welcome.py", title=_("Choose a score")),
        st.Page("account.py", title=_("Manage your account")),
    ],
    _("Score Database"): [
        st.Page("database.py", title=_("View database")),
        st.Page("add_score.py", title=_("Add score")),
    ],
    _("Score Reader"): [st.Page("reader.py", title=_("View score"))],
}

pg = st.navigation(pages)
pg.run()
