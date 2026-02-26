"""Tests for IMSLP parsing logic in imslp.py."""

import requests
from app import imslp


def test_get_metadata_returns_dict():
    """Test that metadata is extracted correctly from HTML."""
    class DummyResponse:  # pylint: disable=too-few-public-methods
        """Mock response object."""
        text = """
        <span id='General_Information'></span>
        <table><tr><th>Work Title</th><td>Symphony No. 5</td></tr><tr><th>Composer</th><td>Beethoven</td></tr></table>
        """

    meta = imslp.get_metadata(DummyResponse())
    assert meta["Work Title"] == "Symphony No. 5"
    assert meta["Composer"] == "Beethoven"


def test_get_metadata_returns_empty_when_none_found():
    """Test that empty metadata is returned when no info is found."""
    class DummyResponse:  # pylint: disable=too-few-public-methods
        """Mock response object."""
        text = "<html></html>"

    assert not imslp.get_metadata(DummyResponse())


def test_get_pdfs_extracts_pdf_urls(monkeypatch):
    """Test that PDF URLs are extracted correctly."""
    class DummyResponse:  # pylint: disable=too-few-public-methods
        """Mock response object."""
        text = '<a href="Special:ImagefromIndex/123">Download</a>'

    # Patch requests.Session.get and .head for test isolation
    with monkeypatch.context() as m:

        class MockSession:
            """Mock requests session."""
            def get(self, url, **kwargs):  # pylint: disable=unused-argument
                """Mock get request."""
                return type(
                    "Resp",
                    (),
                    {"text": '<span id="sm_dl_wait" data-id="url.pdf"></span>'},
                )()

            def head(self, url, **kwargs):  # pylint: disable=unused-argument
                """Mock head request."""
                return type("Resp", (), {"url": "url.pdf"})()

        m.setattr(requests, "Session", MockSession)
        urls = imslp.get_pdfs(DummyResponse())
        assert "url.pdf" in urls


def test_get_pdfs_handles_non_pdf_redirect(monkeypatch):
    """Test handling of redirects that do not result in a PDF."""
    class DummyResponse:  # pylint: disable=too-few-public-methods
        """Mock response object."""
        text = '<a href="Special:ImagefromIndex/456">Download</a>'

    with monkeypatch.context() as m:

        class MockSession:
            """Mock requests session."""
            def get(self, url, **kwargs):  # pylint: disable=unused-argument
                """Mock get request."""
                # No 'sm_dl_wait', so it goes to else block
                return type("Resp", (), {"text": "<html></html>"})()

            def head(self, url, **kwargs):  # pylint: disable=unused-argument
                """Mock head request."""
                # Redirects to non-pdf
                return type("Resp", (), {"url": "http://example.com/not_a_pdf.html"})()

        m.setattr(requests, "Session", MockSession)
        # Capture print output
        import io  # pylint: disable=import-outside-toplevel
        import sys  # pylint: disable=import-outside-toplevel

        captured_output = io.StringIO()
        sys.stdout = captured_output
        urls = imslp.get_pdfs(DummyResponse())
        sys.stdout = sys.__stdout__

        assert "http://example.com/not_a_pdf.html" in captured_output.getvalue()
        assert urls == []
