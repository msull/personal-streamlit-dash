import json

import streamlit as st
import openai
import pandas as pd
from page_helpers import item_paginator

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title="GPT Chat",
)


@st.cache_data
def list_models():
    return sorted(openai.Model.list().data, key=lambda x: x.id)


gpt_models = [x for x in list_models() if "gpt" in x.id]
gpt_model_ids = [x.id for x in gpt_models]

if not "messages" in st.session_state:
    st.session_state.messages = []
    st.session_state.results = {}


def main():
    with st.expander("Message Form", expanded=not bool(st.session_state.results)):
        # Create input fields for message and select box
        role = st.selectbox("Role", ["system", "user", "assistant"])
        message = st.text_area("Message")

        # Create an "Add" button to add the message to the list
        if st.button("Add") and message and role:
            st.session_state.messages.append({"role": role, "content": message})

    # Display the st.session_state.messages in a table
    if st.session_state.messages:
        if st.checkbox("Edit messages"):
            edited_messages = st.data_editor(st.session_state.messages)
            if edited_messages != st.session_state.messages:
                st.session_state.messages = edited_messages
        st.table(st.session_state.messages)
    else:
        st.write("No messages yet.")

    with st.form("Evaluate"):
        selected_models = st.multiselect("Use which model(s)", gpt_model_ids)
        if st.form_submit_button() and selected_models and st.session_state.messages:
            call_chat(selected_models)
            st.experimental_rerun()

    if st.session_state.results:
        cols = st.columns(len(st.session_state.results))
        for idx, model in enumerate(st.session_state.results):
            with cols[idx]:
                with st.expander("Model Results", expanded=True):
                    st.subheader(model)
                    st.write(st.session_state.results[model])


def call_chat(models):
    for model in models:
        with st.spinner(f"Generating AI response for {model}"):
            response = openai.ChatCompletion.create(model=model, messages=st.session_state.messages)
            st.session_state.results[model] = response


if __name__ == "__main__":
    main()


st.write(
    json.loads(
        '{"future_events": [{"date": "2023-07-29", "event": "String and Shadow puppet show"}], "notes": ["Figure out kids artwork display in my office"], "people": {"Jess": {"notes": "Good friends", "conversation_topics": []}, "Forrest": {"notes": "", "conversation_topics": []}, "Everett": {"notes": "Made a cool spy message card and flashlight-card", "conversation_topics": []}, "Tawnya": {"notes": "Moving to Olympia", "conversation_topics": []}, "Ronn": {"notes": "Moving to Olympia, potential new friend. Looking for remote work or new position", "conversation_topics": ["His move to Olympia", "His application", "His commute to Seattle"]}}}'
    )
)
