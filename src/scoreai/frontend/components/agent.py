"""Agent widgets."""

import streamlit as st

from scoreai.frontend.components import api


def run_agent():
    """Run the agent"""
    question = st.text_input("Question", key="question")
    if "message_history" not in st.session_state:
        st.session_state.message_history = []
    if question:
        response = api.run_agent(question)
        st.write(response.response)
        if response and response.score_id:
            df = api.get_scores_df()
            st.session_state.selected_row = df.loc[response.score_id - 1]
            if st.button("Open PDF"):  # pragma: no cover
                st.switch_page("reader.py")

    st.caption(
        """
           Here is how to use me:\n
    - Ask me a question about a score or a composer\n
    - I can give you a random score from a composer\n
    - etc...
"""
    )
    if st.button("clean history"):
        st.session_state.message_history = []
