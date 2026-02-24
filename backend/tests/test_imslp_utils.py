"""Tests for IMSLP parsing logic in imslp.py."""

import requests
from app import imslp


def test_get_metadata_returns_dict():
    class DummyResponse:
        text = """
        <span id='General_Information'></span>
        <table><tr><th>Work Title</th><td>Symphony No. 5</td></tr><tr><th>Composer</th><td>Beethoven</td></tr></table>
        """

    meta = imslp.get_metadata(DummyResponse())
    assert meta["Work Title"] == "Symphony No. 5"
    assert meta["Composer"] == "Beethoven"


def test_get_metadata_returns_empty_when_none_found():
    class DummyResponse:
        text = "<html></html>"

    assert imslp.get_metadata(DummyResponse()) == {}


def test_get_pdfs_extracts_pdf_urls(monkeypatch):
    class DummyResponse:
        text = '<a href="Special:ImagefromIndex/123">Download</a>'

    # Patch requests.Session.get and .head for test isolation
    with monkeypatch.context() as m:

        class MockSession:
            def get(self, url, **kwargs):
                return type(
                    "Resp",
                    (),
                    {"text": '<span id="sm_dl_wait" data-id="url.pdf"></span>'},
                )()

            def head(self, url, **kwargs):
                return type("Resp", (), {"url": "url.pdf"})()

        m.setattr(requests, "Session", lambda: MockSession())
        urls = imslp.get_pdfs(DummyResponse())
        assert "url.pdf" in urls
