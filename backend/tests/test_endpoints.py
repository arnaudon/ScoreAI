"""End-to-end coverage for the three credit-gated agent endpoints.

These replace the `# pragma: no cover` markers that previously hid
`/complete_score`, `/imslp_agent`, and `/agent`. Each happy path asserts
the response shape and that ``consume_credit`` debited exactly one credit;
each failure path asserts the credit is refunded.
"""

import pytest
from fastapi.testclient import TestClient

from app import main
from app.rate_limit import limiter
from shared.responses import FullResponse, ImslpFullResponse, ImslpResponse, Response
from shared.user import User


@pytest.fixture(autouse=True)
def _disable_rate_limit():
    """slowapi limits /agent, /imslp_agent, /complete_score to 5/min; off for tests."""
    limiter.enabled = False
    yield
    limiter.enabled = True


def _credits(session, user_id: int) -> int:
    session.expire_all()
    return session.get(User, user_id).credits


def test_complete_score_debits_credit_and_returns_score(
    client: TestClient, session, test_user: User, monkeypatch: pytest.MonkeyPatch
):
    """Happy path — agent returns; credit is debited once."""
    start = _credits(session, test_user.id)

    async def fake_run_complete_agent(score, _model):
        return score

    monkeypatch.setattr(main, "run_complete_agent", fake_run_complete_agent)

    resp = client.post(
        "/complete_score",
        json={"title": "Nocturne", "composer": "Chopin"},
    )

    assert resp.status_code == 200
    assert resp.json()["title"] == "Nocturne"
    assert _credits(session, test_user.id) == start - 1


def test_complete_score_refunds_credit_on_agent_error(
    client: TestClient, session, test_user: User, monkeypatch: pytest.MonkeyPatch
):
    """Agent error → endpoint returns 500 and ``consume_credit`` refunds."""
    start = _credits(session, test_user.id)

    async def fake_run_complete_agent(_score, _model):
        raise RuntimeError("model exploded")

    monkeypatch.setattr(main, "run_complete_agent", fake_run_complete_agent)

    resp = client.post(
        "/complete_score",
        json={"title": "Nocturne", "composer": "Chopin"},
    )

    assert resp.status_code == 500
    assert _credits(session, test_user.id) == start


def test_imslp_agent_debits_credit_and_returns_response(
    client: TestClient, session, test_user: User, monkeypatch: pytest.MonkeyPatch
):
    """Happy path for the IMSLP SQL agent endpoint."""
    start = _credits(session, test_user.id)

    async def fake_run_imslp_agent(_prompt, message_history=None, model=None):
        return ImslpFullResponse(
            response=ImslpResponse(response="found 3 scores", score_ids=[1, 2, 3]),
            message_history=[],
        )

    monkeypatch.setattr(main, "run_imslp_agent", fake_run_imslp_agent)

    resp = client.post("/imslp_agent", json={"prompt": "piano concerto in D"})

    assert resp.status_code == 200
    assert resp.json()["response"]["score_ids"] == [1, 2, 3]
    assert _credits(session, test_user.id) == start - 1


def test_imslp_agent_refunds_credit_on_error(
    client: TestClient, session, test_user: User, monkeypatch: pytest.MonkeyPatch
):
    """IMSLP agent raises → refund path executes."""
    start = _credits(session, test_user.id)

    async def fake_run_imslp_agent(_prompt, message_history=None, model=None):
        raise RuntimeError("db down")

    monkeypatch.setattr(main, "run_imslp_agent", fake_run_imslp_agent)

    resp = client.post("/imslp_agent", json={"prompt": "whatever"})

    assert resp.status_code == 500
    assert _credits(session, test_user.id) == start


def test_main_agent_debits_credit_and_returns_response(
    client: TestClient, session, test_user: User, monkeypatch: pytest.MonkeyPatch
):
    """Happy path for the main chat agent endpoint."""
    start = _credits(session, test_user.id)

    async def fake_run_agent(_prompt, deps, message_history=None, model=None):
        assert deps.user.id == test_user.id
        return FullResponse(response=Response(response="play this one"), message_history=[])

    monkeypatch.setattr(main, "run_agent", fake_run_agent)

    resp = client.post(
        "/agent",
        json={"prompt": "what should I play?", "deps": '{"scores": []}'},
    )

    assert resp.status_code == 200
    assert resp.json()["response"]["response"] == "play this one"
    assert _credits(session, test_user.id) == start - 1


def test_main_agent_refunds_credit_on_error(
    client: TestClient, session, test_user: User, monkeypatch: pytest.MonkeyPatch
):
    """Main agent raises → refund path executes."""
    start = _credits(session, test_user.id)

    async def fake_run_agent(_prompt, deps, message_history=None, model=None):
        raise RuntimeError("llm timeout")

    monkeypatch.setattr(main, "run_agent", fake_run_agent)

    resp = client.post(
        "/agent",
        json={"prompt": "what should I play?", "deps": '{"scores": []}'},
    )

    assert resp.status_code == 500
    assert _credits(session, test_user.id) == start


def test_agent_endpoint_blocks_when_out_of_credits(
    client: TestClient, session, test_user: User, monkeypatch: pytest.MonkeyPatch
):
    """With credits=0, consume_credit returns 403 before the agent runs."""
    db_user = session.get(User, test_user.id)
    db_user.credits = 0
    session.add(db_user)
    session.commit()

    called = False

    async def fake_run_agent(*_a, **_kw):
        nonlocal called
        called = True
        return FullResponse(response=Response(response="x"), message_history=[])

    monkeypatch.setattr(main, "run_agent", fake_run_agent)

    resp = client.post(
        "/agent",
        json={"prompt": "p", "deps": '{"scores": []}'},
    )

    assert resp.status_code == 403
    assert "credits" in resp.json()["detail"].lower()
    assert called is False
