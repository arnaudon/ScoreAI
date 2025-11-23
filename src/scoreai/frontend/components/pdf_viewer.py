"""PDF viewer."""

import streamlit as st
from pdf2image import convert_from_path
from streamlit_image_coordinates import streamlit_image_coordinates


class PDFViewer:
    """PDF viewer."""

    def __init__(self, pdf_path, dpi=150):
        """Initialize the pdf viewer."""
        self.pdf_path = pdf_path
        self.dpi = dpi
        self.pages = convert_from_path(self.pdf_path, dpi=dpi)
        self.total = len(self.pages)
        self._init_state()

    def _init_state(self):
        """Record the page number per pdf for this session."""
        if "pdfviewer_page" not in st.session_state:
            st.session_state.pdfviewer_page = {}
        if self.pdf_path not in st.session_state.pdfviewer_page:
            st.session_state.pdfviewer_page[self.pdf_path] = 1

    @property
    def page(self):
        """Return current page"""
        return self.pages[st.session_state.pdfviewer_page[self.pdf_path] - 1]

    @property
    def page_number(self):
        """Return current page number"""
        return st.session_state.pdfviewer_page[self.pdf_path]

    @page_number.setter
    def page_number(self, value):
        """Set current page number and rerun"""
        if value <= self.total:
            st.session_state.pdfviewer_page[self.pdf_path] = value
            st.rerun()

    def render(self):
        """Render the pdf."""
        value = streamlit_image_coordinates(self.page, use_column_width=True)
        if value is not None:
            if value["x"] / value["width"] > 0.5:
                self.page_number += 1
            if value["x"] / value["width"] <= 0.5:
                self.page_number -= 1

        # the image is not clickable, but has fullscreen
        # st.image(self.page, width="stretch")
        new_page_number = st.number_input(
            "Page (1-" + str(self.total) + ")",
            min_value=1,
            max_value=self.total,
            step=1,
            value=self.page_number,
            width=150,
        )
        if new_page_number != self.page_number:
            self.page_number = new_page_number
            st.rerun()
