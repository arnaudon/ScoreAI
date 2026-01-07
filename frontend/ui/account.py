"""Account module."""

import streamlit as st
from shared.user import User

from ui.components import api


def main():
    """Render the account management page."""
    st.title("Account management")
    st.write("You can create a new account here, eventually do other things later")

    token = getattr(st.session_state, "token", None)

    if token is None:
        st.subheader("Create New Account")
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        first_name = st.text_input("First Name", placeholder="Optional")
        last_name = st.text_input("Last Name", placeholder="Optional")
        email = st.text_input("Email", placeholder="Optional")
        new_user = User(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        if st.button("Sign Up", key="signup"):
            res = api.register_user(new_user)
            if res.status_code == 200:
                st.success("Registration successful! Please log in.")
            else:
                st.error(f"Error: {res.json().get('detail')}")
    else:
        st.subheader("Logout before creating a new user")
        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()


if __name__ == "__main__":  # pragma: no cover
    main()
