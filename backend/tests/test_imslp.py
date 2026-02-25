import json
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.imslp import (
    get_pdfs,
    get_page,
    fix_entry,
    add_entry,
    get_works,
    router,
    progress_tracker,
    get_metadata
)
from shared.scores import IMSLP, ScoreBase
from app.main import app
from app.users import get_admin_user

client = TestClient(app)

# --- Fixtures & Mocks ---

@pytest.fixture
def mock_requests_get():
    with patch("app.imslp.requests.get") as mock:
        yield mock

@pytest.fixture
def mock_requests_session():
    with patch("app.imslp.requests.Session") as mock:
        yield mock

@pytest.fixture
def mock_agent():
    with patch("app.imslp.Agent") as mock:
        yield mock

@pytest.fixture(name="session")
def session_fixture(session: Session):
    return session

def override_get_admin_user():
    return True

app.dependency_overrides[get_admin_user] = override_get_admin_user

# --- Tests for Helper Functions ---

def test_get_metadata():
    html = """
    <html>
        <span id="General_Information"></span>
        <table>
            <tr><th>Work Title</th><td>Symphony No. 5</td></tr>
            <tr><th>Composer</th><td>Beethoven</td></tr>
        </table>
    </html>
    """
    mock_response = MagicMock()
    mock_response.text = html
    
    metadata = get_metadata(mock_response)
    assert metadata["Work Title"] == "Symphony No. 5"
    assert metadata["Composer"] == "Beethoven"

    # Test bypass
    assert get_metadata(None, bypass=True) == {}

    # Test missing General_Information
    mock_response.text = "<html></html>"
    assert get_metadata(mock_response) == {}

    # Test missing table
    mock_response.text = "<html><span id='General_Information'></span></html>"
    assert get_metadata(mock_response) == {}


def test_get_pdfs(mock_requests_session):
    html_landing = """
    <html>
        <a href="Special:ImagefromIndex/12345">Link 1</a>
        <a href="OtherLink">Link 2</a>
    </html>
    """
    html_page = """
    <html>
        <span id="sm_dl_wait" data-id="http://example.com/score.pdf"></span>
    </html>
    """
    
    mock_response_landing = MagicMock()
    mock_response_landing.text = html_landing
    
    mock_session_instance = mock_requests_session.return_value
    mock_response_page = MagicMock()
    mock_response_page.text = html_page
    
    mock_session_instance.get.return_value = mock_response_page
    
    # Test with direct link found
    pdfs = get_pdfs(mock_response_landing)
    assert pdfs == ["http://example.com/score.pdf"]

    # Test with redirect (no sm_dl_wait)
    html_page_redirect = "<html></html>"
    mock_response_page.text = html_page_redirect
    
    mock_head_response = MagicMock()
    mock_head_response.url = "http://example.com/redirected.pdf"
    mock_session_instance.head.return_value = mock_head_response
    
    pdfs = get_pdfs(mock_response_landing)
    assert pdfs == ["http://example.com/redirected.pdf"]

    # Test with redirect not PDF
    mock_head_response.url = "http://example.com/redirected.html"
    pdfs = get_pdfs(mock_response_landing)
    assert pdfs == []

def test_get_page(mock_requests_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "metadata": {"some": "meta"},
        "1": {"title": "Work 1"}
    }
    mock_requests_get.return_value = mock_response
    
    data = get_page(0)
    assert "metadata" not in data
    assert "1" in data


@pytest.mark.asyncio
async def test_fix_entry(mock_agent):
    mock_agent_instance = mock_agent.return_value
    mock_run_result = AsyncMock()
    mock_run_result.output = ScoreBase(title="Fixed Title", composer="Fixed Composer")
    mock_agent_instance.run.return_value = mock_run_result
    
    entry = IMSLP(title="Old Title")
    await fix_entry(entry)
    
    assert entry.title == "Fixed Title"
    assert entry.composer == "Fixed Composer"


@pytest.mark.asyncio
async def test_add_entry(session, mock_requests_get, mock_agent):
    # Mock fix_entry dependencies
    mock_agent_instance = mock_agent.return_value
    mock_run_result = AsyncMock()
    mock_run_result.output = ScoreBase(title="Fixed Title", composer="Fixed Composer")
    mock_agent_instance.run.return_value = mock_run_result

    # Mock get_metadata dependencies
    html = """
    <html>
        <span id="General_Information"></span>
        <table>
            <tr><th>Work Title</th><td>Symphony No. 5</td></tr>
        </table>
    </html>
    """
    mock_response = MagicMock()
    mock_response.text = html
    mock_requests_get.return_value = mock_response

    item = {
        "permlink": "http://imslp.org/wiki/...",
        "intvals": {"worktitle": "Sym 5", "composer": "Beethoven"}
    }
    
    await add_entry(1, item, session)
    
    # Check DB
    result = session.exec(select(IMSLP).where(IMSLP.id == 1)).one()
    assert result.title == "Fixed Title"
    assert result.permlink == "http://imslp.org/wiki/..."


@pytest.mark.asyncio
async def test_get_works(session, mock_requests_get, mock_agent):
    # Mock fix_entry dependencies
    mock_agent_instance = mock_agent.return_value
    mock_run_result = AsyncMock()
    mock_run_result.output = ScoreBase(title="Fixed Title", composer="Fixed Composer")
    mock_agent_instance.run.return_value = mock_run_result

    # Mock get_page responses
    # First call returns data, second call (next page) returns empty
    mock_response_page1 = MagicMock()
    mock_response_page1.json.return_value = {
        "metadata": {},
        "0": {"permlink": "url1", "intvals": {"worktitle": "T1", "composer": "C1"}}
    }
    
    mock_response_metadata = MagicMock()
    mock_response_metadata.text = "<html></html>" # Empty metadata

    # We need to handle multiple calls to requests.get
    # 1. get_page -> API call
    # 2. add_entry -> permlink call
    
    def side_effect(url, **kwargs):
        if "API.ISCR.php" in url:
             if "start=0" in url:
                 return mock_response_page1
             else:
                 empty = MagicMock()
                 empty.json.return_value = {"metadata": {}}
                 return empty
        else:
            return mock_response_metadata

    mock_requests_get.side_effect = side_effect

    progress_tracker["total"] = 2
    progress_tracker["cancel_requested"] = False
    
    with patch("app.imslp.Session", return_value=session):
        await get_works()
    
    assert progress_tracker["status"] == "completed"
    
    # Check DB
    result = session.exec(select(IMSLP)).all()
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_works_cancel(session, mock_requests_get):
    progress_tracker["total"] = 10
    progress_tracker["cancel_requested"] = True
    
    # Mock get_page to return data so it enters the loop
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "metadata": {},
        "0": {"permlink": "url1", "intvals": {"worktitle": "T1", "composer": "C1"}}
    }
    mock_requests_get.return_value = mock_response

    # Mock add_entry to do nothing or pass
    with patch("app.imslp.add_entry", new_callable=AsyncMock) as mock_add:
         with patch("app.imslp.Session", return_value=session):
            await get_works()

    assert progress_tracker["status"] == "cancelled"


# --- Tests for Endpoints ---

def test_start_endpoint(mock_requests_get):
    response = client.post("/imslp/start/10")
    assert response.status_code == 200
    assert response.json() == {"message": "Task started successfully!"}
    assert progress_tracker["total"] == 10
    assert progress_tracker["status"] == "starting"

def test_progress_endpoint():
    response = client.post("/imslp/progress")
    assert response.status_code == 200
    assert "status" in response.json()

def test_cancel_endpoint():
    response = client.post("/imslp/cancel")
    assert response.status_code == 200
    assert progress_tracker["cancel_requested"] is True

def test_stats_endpoint(session):
    # Add dummy data
    entry = IMSLP(id=1, title="T", composer="C", score_metadata="{}")
    session.add(entry)
    session.commit()

    response = client.get("/imslp/stats")
    assert response.status_code == 200
    assert response.json() == {"total_works": 1, "total_composers": 1}

def test_empty_endpoint(session):
    entry = IMSLP(id=1, title="T", composer="C", score_metadata="{}")
    session.add(entry)
    session.commit()
    
    response = client.post("/imslp/empty")
    assert response.status_code == 200
    
    # Verify empty
    results = session.exec(select(IMSLP)).all()
    assert len(results) == 0

def test_get_by_ids(session):
    entry1 = IMSLP(id=1, title="T1", composer="C1", score_metadata="{}")
    entry2 = IMSLP(id=2, title="T2", composer="C2", score_metadata="{}")
    session.add(entry1)
    session.add(entry2)
    session.commit()

    response = client.get("/imslp/scores_by_ids", params={"score_ids": "[1, 2]"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2
