import pandas as pd
from pytest import fixture
from streamlit.testing.v1 import AppTest


@fixture
def at(test_scores):
    at = AppTest.from_file("src/scoreai/frontend/reader.py")
    at.session_state["selected_row"] = pd.Series(test_scores.scores[0].model_dump())
    at.run()
    return at


def test_pdf_viewer(at):
    pdf_viewer = at.session_state.pdf_viewers[at.session_state.selected_row["pdf_path"]]
    assert pdf_viewer.total == 3
    assert pdf_viewer.page
    assert pdf_viewer.page_number == 1
    pdf_viewer.page_number = 2
    assert pdf_viewer.page_number == 2
    # test too large page
    pdf_viewer.page_number = 20
    assert pdf_viewer.page_number == 3


def test_pdf_viewer_render(at):
    pdf_viewer = at.session_state.pdf_viewers[at.session_state.selected_row["pdf_path"]]
    pdf_viewer.page_number = 1
    pdf_viewer.render()
    at.number_input[0].set_value(2).run()
    assert pdf_viewer.page_number == 2
