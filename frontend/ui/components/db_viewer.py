"""DB viewer."""

import numpy as np
import pandas as pd
import streamlit as st
from shared.scores import Score
from st_aggrid import AgGrid, GridOptionsBuilder

from ui.components import api


def write_summary_db():
    """Write a summary of the db"""
    df = api.get_scores_df()
    if df.empty:
        st.write("You have no scores")
    else:
        st.write(
            f"{st.session_state.user['username']}, you have {len(df)} scores"
            f"with {len(df['composer'].unique())} different composers"
        )


def upload(file, title: str, composer: str, user: str) -> str:
    """Save the file locally or on S3."""
    filename = f"{title}_{composer}_{user}.pdf"
    api.upload_pdf(file, filename)
    return filename


def show_score_info(score):
    """Show score info"""
    st.subheader("Score informations")
    for key, value in score.items():
        if key not in ["id", "user_id", "number_of_plays", "pdf_path"]:
            col1, col2 = st.columns([1, 2])
            col1.markdown(f"**{key}:**")
            col2.write(value)


def add_imslp():
    """Add an IMSLP score"""
    if "question_prev" not in st.session_state:
        st.session_state.question_prev = ""
    if "message_history" not in st.session_state:
        st.session_state.message_history = []

    question = st.text_input("Question", key="question")
    if question and question != st.session_state.question_prev:
        st.write("Answering...")
        st.session_state.question_prev = question
        response = api.run_imslp_agent(question)
        scores = api.get_imslp_scores(response.score_ids)
        st.session_state.score_df = pd.DataFrame(
            [s.model_dump() for s in scores.scores]
        )
    if "score_df" in st.session_state:
        df = st.session_state.score_df
        if len(df):
            df = df[["title", "composer", "year", "instrumentation", "permlink"]]

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_selection("single")  # allow one row selection
            grid_options = gb.build()
            grid_response = AgGrid(
                df, gridOptions=grid_options, height=200, allow_unsafe_jscode=True
            )
            selected = grid_response["selected_rows"]
            if selected is not None:
                st.write(selected.iloc[0])
                st.session_state.score_data_input = Score(**selected.iloc[0].to_dict())
                st.write(st.session_state.score_data_input)
                _add_score(key="imslp")


def add_score():
    """Add a score"""
    # initialize empty score
    if (
        "score_data" not in st.session_state
        or st.session_state.score_data_input is None
    ):
        st.session_state.score_data_input = Score(
            user_id=st.session_state.user["id"], title="", composer=""
        )
    if "update_form" not in st.session_state:
        st.session_state.update_form = True

    # user input title and composer
    title = st.text_input("Title", key="title")
    composer = st.text_input("Composer", key="composer")

    if title:
        st.session_state.score_data_input.title = title
    if composer:
        st.session_state.score_data_input.composer = composer

    _add_score()


def _add_score(key="manual"):
    # complete data with AI
    if st.button("Complete score data with AI", key=f"complete_{key}"):
        st.session_state.score_data_output = api.complete_score_data(
            st.session_state.score_data_input
        )
        st.rerun()

    # show completed data
    if "score_data_output" in st.session_state:
        show_score_info(st.session_state.score_data_output.model_dump())

    # add pdf and submit data
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"], key=key)
    if st.button("Add score", key=f"add_{key}"):
        if uploaded_file is None:
            st.write("Please upload a file")
            st.stop()

        if "score_data_output" not in st.session_state:
            st.session_state.score_data_output = api.complete_score_data(
                st.session_state.score_data_input
            )
        st.session_state.score_data_output.pdf_path = upload(
            uploaded_file,
            st.session_state.score_data_output.title,
            st.session_state.score_data_output.composer,
            st.session_state.user["username"],
        )

        res = api.add_score(st.session_state.score_data_output)
        st.success(res)
        del st.session_state.score_data_input
        del st.session_state.score_data_output
        st.rerun()


def show_db(select=True):
    """Show the db"""
    df = api.get_scores_df()
    if len(df):
        reduced_df = df[
            ["id", "title", "composer", "period", "genre", "year", "number_of_plays"]
        ]
    else:
        reduced_df = df
    st.write("Score List:")
    gb = GridOptionsBuilder.from_dataframe(reduced_df)

    if select:
        gb.configure_selection("single")  # allow one row selection
        grid_options = gb.build()
        grid_response = AgGrid(
            df, gridOptions=grid_options, height=200, allow_unsafe_jscode=True
        )
        selected = grid_response["selected_rows"]
        if selected is not None:
            row = selected.iloc[0]
            st.session_state.selected_row = row
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Open PDF", key="open"):  # pragma: no cover
                    st.switch_page(st.session_state.reader_page)
            with col2:
                with st.popover("Delete", use_container_width=True):
                    st.warning("Are you sure?")
                    col_cancel, col_confirm = st.columns(2)

                    with col_confirm:
                        if st.button("Delete", key="delete"):
                            api.delete_score(row)
                            st.rerun()
                    with col_cancel:
                        if st.button(
                            "Cancel",
                            key="cancel",
                            type="secondary",
                            use_container_width=True,
                        ):
                            st.toast("Deletion cancelled.", icon="🚫")
            show_score_info(row)

    add_score()
    add_imslp()
