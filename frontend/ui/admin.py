"""Admin page."""

import time

import streamlit as st

from ui.components import api

st.title("Admin page")

# Check if a task is already running in the backend
if "monitoring" not in st.session_state:
    try:
        current_status = api.get_imslp_progress()
        if current_status.get("status") in ["running", "pending"]:
            st.session_state.monitoring = True
    except Exception:
        pass

st.subheader("All users table")
users = api.get_all_users()
st.write(users)
st.divider()
st.subheader("IMSLP database table")
stats = api.get_imslp_stats()
st.write(
    f"IMSLP database contains {stats['total_works']} works and "
    f"{stats['total_composers']} composers."
)
col1, col2 = st.columns(2)
with col1:
    if st.button("Update IMSLP database"):
        try:
            response = api.start_imslp_update(max_pages=300)
            if response.status_code == 200:
                st.success("Task started successfully!")
                st.session_state.monitoring = True
            else:
                st.error(f"Failed to start: {response.status_code}")
        except Exception as e:  # pylint: disable=broad-exception-caught
            st.error(f"Connection error: {e}")
with col2:
    with st.popover("Delete all data", use_container_width=True):
        st.warning("Are you sure?")
        col_cancel, col_confirm = st.columns(2)

        with col_confirm:
            if st.button("Delete", key="delete"):
                response = api.empty_imslp_database()
                if response.status_code == 200:
                    st.success("Database empty successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to empty: {response.status_code}")
        with col_cancel:
            if st.button("Cancel", key="cancel", type="secondary", use_container_width=True):
                st.toast("Deletion cancelled.", icon="🚫")

if st.session_state.get("monitoring"):
    status_container = st.empty()
    progress_bar = st.progress(0)

    stop_button = st.button("🛑 Cancel Task")

    if stop_button:
        api.cancel_imslp()
        st.warning("Cancellation request sent.")

    while True:
        try:
            res = api.get_imslp_progress()
            p_page = res.get("page", 0)
            p_total = res.get("total", 0)
            p_status = res.get("status", "idle")

            progress_bar.progress(p_page / p_total)
            status_container.info(f"Current Status: **{p_status.upper()}** ({p_page}/{p_total})")

            if p_status in ["completed", "cancelled", "idle"]:
                if p_status == "completed":
                    st.success("Task Finished!")
                st.session_state.monitoring = False
                st.session_state.finished = True
                st.rerun()

            time.sleep(2)
            st.rerun()

        except Exception as e:  # pylint: disable=broad-exception-caught, unused-variable
            st.error("Lost connection to backend.")
            break

if st.session_state.get("finished"):
    st.success("Task Finished!")
