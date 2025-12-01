from ui.components import api


def test_get_scores():
    """Test the get_scores function."""
    scores = api.get_scores()
    assert len(scores.scores) > 0


def test_get_scores_df():
    """Test the get_scores function."""
    scores_df = api.get_scores_df()
    assert len(scores_df.index) > 0


def test_add_score():
    """Test the add_score function."""
    score = {
        "composer": "another_composer",
        "title": "another_title",
        "pdf_path": "another_score.pdf",
    }
    response = api.add_score(score_data=score)
    assert response["composer"] == score["composer"]
    assert response["title"] == score["title"]
    assert response["pdf_path"] == score["pdf_path"]


def test_reset_score_cache():
    """Test the reset_score_cache function."""
    api.get_scores()
    api.reset_score_cache()
    assert api._scores == None


def test_delete_score():
    """Test the delete_score function."""
    score = {
        "composer": "another_composer",
        "title": "another_title",
        "pdf_path": "another_score.pdf",
    }
    api.add_score(score_data=score)

    scores = api.get_scores()
    score_id = len(scores)
    api.delete_score(score_id=score_id)
    scores = api.get_scores()
    assert len(scores) == score_id - 1


def test_add_play():
    """Test the add_play function."""
    score_id = 1
    response = api.add_play(score_id=score_id)
    assert response["number_of_plays"] == 1


# def test_run_agent(client: TestClient, agent: None):
#    """Test the run_agent function."""
#    if "message_history" not in st.session_state:
#        st.session_state.message_history = []
#    response = api.run_agent("test", client=client)
#    assert isinstance(response, Response)
