import streamlit as st

if st.checkbox("Show session state"):
    st.write(st.session_state)
