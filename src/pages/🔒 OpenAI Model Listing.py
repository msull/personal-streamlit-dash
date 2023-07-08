import openai
import streamlit as st
from auth_helpers import set_page_config
from page_helpers import item_paginator

set_page_config("OpenAI Model Listing", requires_auth=True)


def display_item(idx):
    st.write(models[idx])


item_paginator("Models", model_ids, display_item, display_item_names=True, enable_keypress_nav=True)
