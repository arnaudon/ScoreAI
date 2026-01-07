"""Database module."""

import streamlit as st

from ui.components.db_viewer import show_db


def main():
    """Render the database page."""
    st.title("Score Database")
    show_db()


if __name__ == "__main__":  # pragma: no cover
    main()
