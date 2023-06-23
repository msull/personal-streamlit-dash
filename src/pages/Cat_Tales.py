import json

import openai
import streamlit as st
from auth_helpers import set_page_config
from common_settings import AppSettings
from cat_tales_helpers import *

set_page_config("Cat Tales", requires_auth=False)
settings = AppSettings()
saved_tales_dir = settings.streamlit_app_output_dir / "cat_tales" / "adventures"
saved_tales_dir.mkdir(parents=True, exist_ok=True)

def get_story_prompt_view():
    common_view()
    st.markdown(USER_INTRO_TEXT)


def main_view():
    common_view()


def common_view():
    st.header("🐾 Welcome to the Adventures of Everett and Forrest! 🐾")


if "cat_tales_init" not in st.session_state:
    get_story_prompt_view()
else:
    main_view()
