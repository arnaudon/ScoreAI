"""Database module."""

import streamlit as st

from scoreai.frontend.components.db_viewer import show_db

st.title("Score Database")

show_db()
