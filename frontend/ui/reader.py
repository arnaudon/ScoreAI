"""View a pdf"""

import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
from ui.components import api

COOKIE_EXPIRES = datetime.now() + timedelta(days=1)


def render_pdf(pdf_path):
    """Render the pdf."""
    url = api.get_pdf_url(pdf_path)
    options = [
        "pagemode=none",
        "disableRange=true",
        "disableStream=true",
        "disableAutoFetch=false",
    ]
    st.markdown(
        f"""
            <iframe 
        src="{url}#{'&'.join(options)}"
        width="100%"
        height="800px"
        style="border:none;"
        allowfullscreen="true"
        webkitallowfullscreen="true"
        mozallowfullscreen="true"
        allow="fullscreen"
        ></iframe>
        """,
        unsafe_allow_html=True,
    )


cookie_manager = stx.CookieManager(key="pdf_cookie")
pdf_path = cookie_manager.get(cookie="pdf_path")
if hasattr(st.session_state, "selected_row"):
    pdf_path = st.session_state.selected_row["pdf_path"]
    cookie_manager.set("pdf_path", pdf_path, key="pdf_path", expires_at=COOKIE_EXPIRES)
    api.add_play(st.session_state.selected_row["id"])

if pdf_path:
    render_pdf(pdf_path)
else:
    st.write("Please select a score")
