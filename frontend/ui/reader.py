"""View a pdf"""

import streamlit as st

from ui.components import api
from ui.components.pdf_viewer import PDFViewer

if hasattr(st.session_state, "selected_row"):
    st.write(f"Selected: {st.session_state.selected_row.to_dict()}")
    pdf_path = st.session_state.selected_row["pdf_path"]

    if "pdf_viewers" not in st.session_state:
        st.session_state.pdf_viewers = {}

    if pdf_path not in st.session_state.pdf_viewers:
        st.session_state.pdf_viewers[pdf_path] = PDFViewer(pdf_path)
        # we increment the number of play only the first time we open in a session
        api.add_play(st.session_state.selected_row["id"])

    if "pdf_viewers" in st.session_state and pdf_path in st.session_state.pdf_viewers:
        st.session_state.pdf_viewers[pdf_path].render()
else:
    st.write("Please select a score")
