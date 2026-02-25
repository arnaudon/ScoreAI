"""
Extended coverage for imslp.py - error/empty cases for get_metadata/get_pdfs, and dummy coverage for get_page edge.
"""

import pytest
from app import imslp


def test_get_metadata_bypass_true():
    class DummyResp:
        text = "something"

    assert imslp.get_metadata(DummyResp(), bypass=True) == {}


def test_get_metadata_no_table():
    class DummyResp:
        text = "<span id='General_Information'></span>"

    assert imslp.get_metadata(DummyResp()) == {}


def test_get_pdfs_no_pdf_found():
    class DummyResp:
        text = "<html></html>"

    result = imslp.get_pdfs(DummyResp())
    assert result == []


def test_get_page_returns_data(monkeypatch):
    monkeypatch.setattr(
        imslp.requests,
        "get",
        lambda url, **kwargs: type("Resp", (), {"json": lambda self: {"a": 1, "metadata": "meta"}})(),
    )
    d = imslp.get_page(0)
    assert d == {"a": 1}


def test_get_page_no_data(monkeypatch):
    # .json returns empty dict
    monkeypatch.setattr(
        imslp.requests,
        "get",
        lambda url, **kwargs: type("Resp", (), {"json": lambda self: {"metadata": "meta"}})(),
    )
    d = imslp.get_page(0)
    assert d == {}
