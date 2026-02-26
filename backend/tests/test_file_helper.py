"""Tests for file_helper.py (local storage logic, S3 mocked)."""

import io
import os
from pathlib import Path

import pytest
from app.file_helper import file_helper


@pytest.fixture(autouse=True)
def set_data_path_tmp(tmp_path, monkeypatch):
    """Set DATA_PATH env var to tmp_path."""
    monkeypatch.setenv("DATA_PATH", str(tmp_path))


def test_upload_and_download_and_delete_local(monkeypatch):
    """Test local file upload, download and delete."""
    # Ensure we're not using S3
    monkeypatch.setenv("S3_ENDPOINT", "")
    monkeypatch.setenv("S3_BUCKET", "")
    file_content = b"test pdf content"
    filename = "testfile.pdf"
    fileobj = io.BytesIO(file_content)

    # Upload (should store locally)
    file_helper.upload_pdf(filename, fileobj)
    written_file = Path(os.getenv("DATA_PATH")) / filename
    assert written_file.exists()

    # Download
    out = file_helper.download_pdf(filename)
    assert out["Body"].read() == file_content
    out["Body"].close()

    # Delete
    file_helper.delete_pdf(filename)
    assert not written_file.exists()


def test_upload_and_delete_local_handles_missing_file(monkeypatch):
    """Test deleting missing local file handles exception silently."""
    # This test ensures no exception raised if deleting a non-existent local file
    monkeypatch.setenv("S3_ENDPOINT", "")
    monkeypatch.setenv("S3_BUCKET", "")
    file_helper.delete_pdf("does_not_exist.pdf")
