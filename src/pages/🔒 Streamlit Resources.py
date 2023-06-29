import streamlit as st
from auth_helpers import set_page_config

set_page_config("Streamlit Resources", requires_auth=True)


def main():
    st.write("I'm logged in")


main()
