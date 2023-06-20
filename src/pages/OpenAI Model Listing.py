import streamlit as st
import openai

from page_helpers import item_paginator

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title="OpenAI Model Listing",
)

@st.cache_data
def list_models():
    return sorted(openai.Model.list().data, key=lambda x: x.id)


models = list_models()
model_ids = [x.id for x in models]
gpt_models = [x for x in models if 'gpt' in x.id]
gpt_model_ids = [x.id for x in gpt_models]

def display_item(idx):
    st.write(models[idx])

item_paginator('Models', model_ids, display_item, display_item_names=True, enable_keypress_nav=True)
