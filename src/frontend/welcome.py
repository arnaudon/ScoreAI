"""Welcome module."""

import streamlit as st

import frontend.components.ui_widgets as ui
from frontend.locales import _

st.title("ScoreAI")
st.write(_("Welcome to ScoreAI, ask me about which score you want to play today"))
ui.run_agent()
