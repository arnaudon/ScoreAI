"""DB viewer."""

import os
from pathlib import Path

import streamlit as st
from shared import Score
from st_aggrid import AgGrid, GridOptionsBuilder
from ui.components.utils import s3_helper

from ui.components import api


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


class FileUploader:
    """File uploader wrapper of local and S3."""

    def __init__(self):
        """Initialize the file uploader."""
        if s3_helper is not None:
            self.location = "s3"
        elif os.getenv("DATA_PATH"):
            self.location = "local"
            self.data_path = Path(str(os.getenv("DATA_PATH")))
        else:
            raise ValueError("You need to set either DATA_PATH or S3_ENDPOINT")

    def upload(self, file, title: str, composer: str, user: str) -> str | None:
        """Save the file."""
        filename = self.get_filename(title, composer, user)
        if self.location == "local":
            path = self.data_path / filename
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            return str(path)

        if self.location == "s3":
            s3_helper["s3_client"].put_object(Bucket=s3_helper["bucket"], Key=filename, Body=file)
            return filename

        return None

    def get_filename(self, title, composer, user) -> str:
        """Get the filename."""
        return f"{title}_{composer}_{user}.pdf"


def add_score():
    """Add a score"""
    st.write("Add new score:")
    title = st.text_input("Title", key="title")
    composer = st.text_input("Composer", key="composer")
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])
    if st.button("Add score", key="add"):
        if uploaded_file is None:
            st.write("Please upload a file")
            st.stop()

        if "file_uploader" not in st.session_state:
            st.session_state.file_uploader = FileUploader()
        save_path = st.session_state.file_uploader.upload(
            uploaded_file, title, composer, st.session_state.user
        )

        score_data = Score(
            user_id=st.session_state.user_id,
            title=title,
            composer=composer,
            pdf_path=save_path,
            number_of_plays=0,
        )
        res = api.add_score(score_data)
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
            st.write(f"Selected: {Score(**row.to_dict()).model_dump()}")
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
