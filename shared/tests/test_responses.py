"""test responses"""

from shared.responses import FullResponse, Response


def test_responses():
    """test responses"""
    resp = Response(response="test", score_id=1)
    assert resp.response == "test"
    assert resp.score_id == 1

    full_resp = FullResponse(response=resp, message_history=[])
    assert full_resp.response.response == "test"
    assert full_resp.response.score_id == 1
    assert full_resp.message_history == []
