import streamlit as st
import openai
from pydantic import BaseModel


class ModelListing(BaseModel):
    models = list_models()
    model_ids = [x.id for x in models]
    gpt_models = [x for x in models if "gpt" in x.id]
    gpt_model_ids = [x.id for x in gpt_models]


@st.cache_resource
def list_models():
    return sorted(openai.Model.list().data, key=lambda x: x.id)
