"""Translation support."""

import gettext

import streamlit as st

DEFAULT_LANG = "fr"
LANGUAGES = {"en": "English", "fr": "Français"}


def initialize_translator(language):
    """Initializes the translator."""
    try:
        translator = gettext.translation(
            "messages", localedir="locales", languages=[language]
        )
    except FileNotFoundError:  # pragma: no cover
        translator = gettext.NullTranslations()

    st.session_state.gettext = translator.gettext
    st.session_state.language = language


def init_i18n_gettext():
    """Initializes language settings on first run."""
    if "gettext" not in st.session_state:
        initialize_translator(DEFAULT_LANG)


def _(key: str) -> str:
    """Convenience function to get the translated string."""
    if "gettext" not in st.session_state:
        initialize_translator(DEFAULT_LANG)
    return st.session_state.gettext(key)


def language_selector():
    """Adds a language selector to the sidebar and updates the translator."""
    current_lang_code = st.session_state.language

    current_index = list(LANGUAGES.keys()).index(current_lang_code)

    new_lang_code = st.sidebar.selectbox(
        "Select Language:",
        options=list(LANGUAGES.keys()),
        format_func=lambda code: LANGUAGES[code],
        index=current_index,
        key="lang",
    )

    if new_lang_code != current_lang_code:
        initialize_translator(new_lang_code)
        st.rerun()
