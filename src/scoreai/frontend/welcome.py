"""Welcome module."""

import streamlit as st

from scoreai.frontend.components.agent import run_agent
from scoreai.frontend.locales import _

st.title("ScoreAI")
st.write(_("Welcome to ScoreAI, ask me about which score you want to play today"))
run_agent()
