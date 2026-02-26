"""
Extended coverage for imslp.py.

Includes error/empty cases for get_metadata/get_pdfs, and dummy coverage for get_page edge.
"""

from app import imslp


def test_get_metadata_bypass_true():
    """Test bypass in get_metadata."""
    class DummyResp:  # pylint: disable=too-few-public-methods
        """Mock response."""
        text = "something"

    assert not imslp.get_metadata(DummyResp(), bypass=True)


def test_get_metadata_no_table():
    """Test get_metadata missing table."""
    class DummyResp:  # pylint: disable=too-few-public-methods
        """Mock response."""
        text = "<span id='General_Information'></span>"

    assert not imslp.get_metadata(DummyResp())


def test_get_pdfs_no_pdf_found():
    """Test get_pdfs no pdf found."""
    class DummyResp:  # pylint: disable=too-few-public-methods
        """Mock response."""
        text = "<html></html>"

    result = imslp.get_pdfs(DummyResp())
    assert not result


def test_get_page_returns_data(monkeypatch):
    """Test get_page returns data."""
    monkeypatch.setattr(
        imslp.requests,
        "get",
        lambda url, **kwargs: type(
            "Resp", (), {"json": lambda self: {"a": 1, "metadata": "meta"}}
        )(),
    )
    d = imslp.get_page(0)
    assert d == {"a": 1}


def test_get_page_no_data(monkeypatch):
    """Test get_page returns empty."""
    # .json returns empty dict
    monkeypatch.setattr(
        imslp.requests,
        "get",
        lambda url, **kwargs: type("Resp", (), {"json": lambda self: {"metadata": "meta"}})(),
    )
    d = imslp.get_page(0)
    assert not d
