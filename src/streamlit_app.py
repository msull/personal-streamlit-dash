from functools import wraps

import streamlit as st
import yaml
from streamlit_authenticator.authenticate import Authenticate
from yaml.loader import SafeLoader

st.set_page_config(
    layout="wide",
    initial_sidebar_state="auto",
    page_title="GPT Chat",
)


@st.cache_data
def load_auth_config():
    with open("config.yaml") as file:
        return yaml.load(file, Loader=SafeLoader)


def create_authenticator(config):
    return Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config.get("preauthorized"),
    )


def requires_login(fn):
    @wraps(fn)
    def wrapper(authenticator):
        # creating a login widget
        name, authentication_status, username = authenticator.login("Login", "main")
        if authentication_status:
            fn(authenticator, username)
        elif authentication_status is False:
            st.error("Username/password is incorrect")
        elif authentication_status is None:
            st.warning("Please enter your username and password")

    return wrapper



@requires_login
def main(authenticator: Authenticate, username: str):
    navbar, profile = st.columns((3, 1))

    with profile:
        authenticator.logout("Logout", "main")
    st.write(f"Welcome *{username}*")
    st.title("Some content")

    # Creating a password reset widget
    try:
        if authenticator.reset_password(username, "Reset password"):
            st.success("Password modified successfully")
    except Exception as e:
        st.error(e)
    try:
        if authenticator.update_user_details(username, "Update user details"):
            st.success("Entries updated successfully")
    except Exception as e:
        st.error(e)


if __name__ == "__main__":
    config = load_auth_config()
    authenticator = create_authenticator(config)

    main(authenticator)
