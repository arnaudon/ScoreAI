"""DB viewer."""

import os
from pathlib import Path

import streamlit as st
from shared import Score
from st_aggrid import AgGrid, GridOptionsBuilder

from ui.components import api
from ui.components.utils import s3_helper


def write_summary_db():
    """Write a summary of the db"""
    df = api.get_scores_df()
    if df.empty:
        st.write("You have no scores")
    else:
        st.write(
            f"{st.session_state.user}, you have {len(df)} scores"
            f"with {len(df['composer'].unique())} different composers"
        )


def upload(file, title: str, composer: str, user: str) -> str | None:
    """Save the file locally or on S3."""
    filename = f"{title}_{composer}_{user}.pdf"
    if s3_helper is not None:
        s3_helper["s3_client"].put_object(Bucket=s3_helper["bucket"], Key=filename, Body=file)
        return filename

    path = Path(str(os.getenv("DATA_PATH"))) / filename
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    return str(path)


def add_score():
    """Add a score"""
    st.write("Add new score:")

    if "score_data" not in st.session_state or st.session_state.score_data is None:
        st.session_state.score_data = Score(user_id=st.session_state.user_id, title="", composer="")
    if "update_form" not in st.session_state:
        st.session_state.update_form = True

    if st.session_state.update_form:
        st.session_state.title = st.session_state.score_data.title
        st.session_state.composer = st.session_state.score_data.composer
        st.session_state.period = st.session_state.score_data.period
        st.session_state.genre = st.session_state.score_data.genre
        st.session_state.year = (
            str(st.session_state.score_data.year)
            if st.session_state.score_data.year is not None
            else None
        )
        st.session_state.update_form = False

    title = st.text_input("Title", key="title")
    composer = st.text_input("Composer", key="composer")

    if title:
        st.session_state.score_data.title = title
    if composer:
        st.session_state.score_data.composer = composer

    if st.button("Complete form with AI", key="complete"):
        st.session_state.score_data = api.complete_score_data(st.session_state.score_data)
        st.session_state.update_form = True
        st.rerun()

    st.subheader("Score informations")
    for key, value in st.session_state.score_data.model_dump().items():
        if key not in ["id", "user_id", "number_of_plays", "pdf_path"]:
            col1, col2 = st.columns([1, 2])
            col1.markdown(f"**{key}:**")
            col2.write(value)

    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])
    if st.button("Add score", key="add"):
        if uploaded_file is None:
            st.write("Please upload a file")
            st.stop()

        st.session_state.score_data.pdf_path = upload(
            uploaded_file, title, composer, st.session_state.user
        )

        res = api.add_score(st.session_state.score_data)
        st.success(res)
        st.rerun()


def delete_score(row):
    """Delete a score"""
    if s3_helper is not None:
        s3_helper["s3_client"].delete_object(Bucket=s3_helper["bucket"], Key=row["pdf_path"])
    else:
        try:
            os.remove(row["pdf_path"])
        except FileNotFoundError:
            pass


def show_db(select=True):
    """Show the db"""
    df = api.get_scores_df()
    st.write("Score List:")
    gb = GridOptionsBuilder.from_dataframe(df)

    if select:
        gb.configure_selection("single")  # allow one row selection
        grid_options = gb.build()
        grid_response = AgGrid(df, gridOptions=grid_options, height=200, allow_unsafe_jscode=True)
        selected = grid_response["selected_rows"]
        if selected is not None:
            row = selected.iloc[0]
            st.session_state.selected_row = row
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Open PDF", key="open"):  # pragma: no cover
                    print(st.session_state.reader_page.__dict__)
                    st.switch_page(st.session_state.reader_page)
            with col2:
                with st.popover("Delete", use_container_width=True):
                    st.warning("Are you sure?")
                    col_cancel, col_confirm = st.columns(2)

                    with col_confirm:
                        if st.button("Delete", key="delete"):
                            api.delete_score(row["id"])
                            delete_score(row)
                            st.rerun()
                    with col_cancel:
                        if st.button(
                            "Cancel", key="cancel", type="secondary", use_container_width=True
                        ):
                            st.toast("Deletion cancelled.", icon="🚫")

    add_score()
