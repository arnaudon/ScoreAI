"""Admin page."""

import streamlit as st

from ui.components import api

st.title("Admin page")

st.write("All users table")
users = api.get_all_users()
st.write(users)

st.write("IMSLP database table")
