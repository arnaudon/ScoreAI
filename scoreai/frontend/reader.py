"""View a pdf"""

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

# TODO: improve this writing
if hasattr(st.session_state, "selected_row"):
    st.write(f"Selected: {st.session_state.selected_row.to_dict()}")
    pdf_viewer(st.session_state.selected_row["pdf_path"])
else:
    st.write("Please select a score")
