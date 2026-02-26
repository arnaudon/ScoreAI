"""Database module."""

import streamlit as st

# We need to ensure ui.components.db_viewer is imported properly for mocking
import ui.components.db_viewer as db_viewer_module

st.title("Score Database")
db_viewer_module.show_db()
