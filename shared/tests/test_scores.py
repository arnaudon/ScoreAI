"""test scores"""

from shared.scores import Score, Scores


def test_scores():
    """test scores"""
    score = Score(
        id=1,
        pdf_path="path",
        title="title",
        composer="composer",
        number_of_plays=1,
        user_id=0,
    )
    assert score.id == 1
    assert score.pdf_path == "path"
    assert score.title == "title"
    assert score.composer == "composer"
    assert score.number_of_plays == 1
    scores = Scores(scores=[score])
    assert scores.scores[0].id == 1
    assert len(scores) == 1
