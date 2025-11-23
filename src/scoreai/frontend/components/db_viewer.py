"""DB viewer."""

from pathlib import Path

import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

from scoreai.frontend.components import api
from scoreai.shared_models.scores import Score


def write_summary_db():
    """Write a summary of the db"""
    df = api.get_scores_df()
    if df.empty:
        st.write("You have no scores")
    else:
        st.write(
            f"You have {len(df)} scores, with {len(df['composer'].unique())} different composers"
        )


def add_score():
    """Add a score"""
    st.write("Add new score:")
    title = st.text_input("Title")
    composer = st.text_input("Composer")
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])
    if st.button("Add score"):
        save_path = f"data/{title}_{composer}.pdf"
        if uploaded_file is None:
            st.write("Please upload a file")
            st.stop()

        if Path(save_path).exists():
            st.write(f"File {save_path} already exists")
            st.stop()

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        score_data = {
            "title": title,
            "composer": composer,
            "pdf_path": save_path,
            "number_of_plays": 0,
        }
        res = api.add_score(score_data)
        st.success(res)
        st.rerun()


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
                if st.button("Open PDF"):
                    st.switch_page("reader.py")
            with col2:
                with st.popover("Delete", use_container_width=True):
                    st.warning("Are you sure?")
                    col_cancel, col_confirm = st.columns(2)

                    with col_confirm:
                        if st.button("Delete"):
                            api.delete_score(row["id"])
                            st.rerun()
                    with col_cancel:
                        if st.button("Cancel", type="secondary", use_container_width=True):
                            st.toast("Deletion cancelled.", icon="🚫")

    add_score()
