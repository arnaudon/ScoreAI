"""View a pdf"""

import streamlit as st

from ui.components import api


def render_pdf(pdf_path):
    """Render the pdf."""
    url = api.get_pdf_url(pdf_path)
    st.markdown(
        f"""
            <iframe 
        src="{url}"
        width="100%"
        height="800px"
        style="border:none;"
        allowfullscreen="true"
        webkitallowfullscreen="true"
        mozallowfullscreen="true"
        allow="fullscreen">
            </iframe>
        """,
        unsafe_allow_html=True,
    )


if hasattr(st.session_state, "selected_row"):
    pdf_path = st.session_state.selected_row["pdf_path"]
    api.add_play(st.session_state.selected_row["id"])
    render_pdf(pdf_path)
else:
    st.write("Please select a score")
