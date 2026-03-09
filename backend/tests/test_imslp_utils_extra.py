"""
Extended coverage for imslp.py.

Includes error/empty cases for get_metadata/get_pdfs, and dummy coverage for get_page edge.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

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


@pytest.mark.asyncio
async def test_get_page_returns_data(monkeypatch):
    """Test get_page returns data."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"a": 1, "metadata": "meta"}
    async_mock_get = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(
        "app.imslp.httpx.AsyncClient.get",
        async_mock_get,
    )
    d = await imslp.get_page(0)
    assert d == {"a": 1}


@pytest.mark.asyncio
async def test_get_page_no_data(monkeypatch):
    """Test get_page returns empty."""
    # .json returns empty dict
    mock_response = MagicMock()
    mock_response.json.return_value = {"metadata": "meta"}
    async_mock_get = AsyncMock(return_value=mock_response)
    monkeypatch.setattr(
        "app.imslp.httpx.AsyncClient.get",
        async_mock_get,
    )
    d = await imslp.get_page(0)
    assert not d
