from typing import Tuple, Optional, Dict, Literal
from uuid import uuid4

import streamlit as st
from diskcache import Index
from logzero import logger
from pydantic import BaseModel, BaseSettings
from streamlit_authenticator.authenticate import Authenticate

from common_settings import AppSettings


class DefaultUser(BaseSettings):
    initial_name: str
    initial_password: str
    initial_username: str
    initial_email: str


class AuthUser(BaseModel):
    email: str
    name: str
    password: str


class AuthSettings(BaseModel):
    credentials: Dict[Literal["usernames"], Dict[str, AuthUser]]
    cookie_name: str
    key: str
    cookie_expiry_days: int = 30
    preauthorized: list = None


def save_auth_db(authenticate: Authenticate):
    logger.info("Saving change to Auth DB")
    app_settings = AppSettings()
    credentials_data = Index(str(app_settings.credentials_dir))
    credentials_data["credentials"] = authenticate.credentials
    credentials_data["cookie_name"] = authenticate.cookie_name
    credentials_data["key"] = authenticate.key
    credentials_data["cookie_expiry_days"] = authenticate.cookie_expiry_days
    credentials_data["preauthorized"] = authenticate.preauthorized


@st.cache_resource(experimental_allow_widgets=True)
def load_auth_config() -> AuthSettings:
    app_settings = AppSettings()
    credentials_data = Index(str(app_settings.credentials_dir))

    if not credentials_data.get("credentials"):
        default_user = DefaultUser()
        logger.warning("No auth database present; loading default authorization data")
        auth_settings = AuthSettings.parse_obj(
            {
                "credentials": {
                    "usernames": {
                        default_user.initial_username: {
                            "email": default_user.initial_email,
                            "name": default_user.initial_name,
                            "password": default_user.initial_password,
                        }
                    }
                },
                "cookie_name": "dashboard-auth-cookie",
                "key": uuid4().hex,
                "cookie_expiry_days": 30,
                "preauthorized": None,
            }
        )
        credentials_data["credentials"] = auth_settings.credentials
        credentials_data["cookie_name"] = auth_settings.cookie_name
        credentials_data["key"] = auth_settings.key
        credentials_data["cookie_expiry_days"] = auth_settings.cookie_expiry_days
        credentials_data["preauthorized"] = auth_settings.preauthorized
    else:
        logger.debug("Loading auth database")
        auth_settings = AuthSettings.parse_obj(
            {
                "credentials": credentials_data["credentials"],
                "cookie_name": credentials_data["cookie_name"],
                "key": credentials_data["key"],
                "cookie_expiry_days": credentials_data["cookie_expiry_days"],
                "preauthorized": credentials_data["preauthorized"],
            }
        )

    return auth_settings


@st.cache_resource(experimental_allow_widgets=True)
def create_authenticator(config):
    return Authenticate(
        config["credentials"],
        config["cookie_name"],
        config["key"],
        config["cookie_expiry_days"],
        config["preauthorized"],
    )


class LoginRequired(RuntimeError):
    pass


def set_page_config(page_title: str, requires_auth: bool = False, **kwargs) -> Optional[Tuple[Authenticate, str]]:
    st.set_page_config(page_title=page_title, **kwargs)

    if requires_auth:
        for key in ["authentication_status", "name", "username", "logout", "init"]:
            if key not in st.session_state:
                st.session_state[key] = None
        config = load_auth_config()
        authenticator = create_authenticator(config.dict())

        name, authentication_status, username = authenticator.login("Login", "main")
        if authentication_status is False:
            st.error("Username/password is incorrect")
        elif authentication_status is None:
            st.warning("Please enter your username and password")

        if not authentication_status:
            raise LoginRequired()

        return authenticator, username
