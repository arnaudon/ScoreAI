"""PDF viewer."""

import streamlit as st
from pdf2image import convert_from_path, convert_from_bytes
from streamlit_image_coordinates import streamlit_image_coordinates
from ui.components.utils import s3_helper


class PDFViewer:
    """PDF viewer."""

    def __init__(self, pdf_path, dpi=150):
        """Initialize the pdf viewer."""
        self.pdf_path = pdf_path
        self.dpi = dpi
        self.pages = self._get_pdf()
        self.total = len(self.pages)
        self._current_page = 1

    def _get_pdf(self):
        """Get the pdf."""
        if s3_helper is not None:
            response = s3_helper["s3_client"].get_object(
                Bucket=s3_helper["bucket"], Key=self.pdf_path
            )
            return convert_from_bytes(response["Body"].read(), dpi=self.dpi)
        else:
            return convert_from_path(self.pdf_path, dpi=self.dpi)

    @property
    def page(self):
        """Return current page"""
        return self.pages[self._current_page - 1]

    @property
    def page_number(self):
        """Return current page number"""
        return self._current_page

    @page_number.setter
    def page_number(self, value):
        """Set current page number and rerun"""
        self._current_page = min(value, self.total)
        st.rerun()

    def render(self):
        """Render the pdf."""
        value = streamlit_image_coordinates(self.page, use_column_width=True)
        if value is not None:  # pragma: no cover
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
            st.rerun()  # pragma: no cover
