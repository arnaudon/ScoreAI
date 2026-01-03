"""Account module."""
from ui.components import api

import streamlit as st

st.title("Manage your account")
st.write("Add new user:")
username= st.text_input("Username", key="username")
first_name= st.text_input("First Name", key="first_name")
last_name= st.text_input("Last Name", key="last_name")
email= st.text_input("Email", key="email")
password= st.text_input("Password", key="password", type="password")
if st.button("Add user", key="add_user"):
    user_data = {
        "username": username,
    "first_name": first_name,
    "last_name": last_name,
    "email": email,
    "password": password,}
    res = api.add_user(user_data)
    st.success(res)
    st.rerun()

