import json

import openai
from common_settings import AppSettings
from page_helpers import date_id, save_session, load_session, item_paginator, check_or_x
import streamlit as st

st.set_page_config(
    layout="wide",
    initial_sidebar_state="auto",
    page_title="GPT Chat",
)
settings = AppSettings()
date_id()
recent_conversations = settings.streamlit_app_output_dir / "gpt_chat" / "recent"
recent_conversations.mkdir(parents=True, exist_ok=True)
saved_conversations = settings.streamlit_app_output_dir / "gpt_chat" / "saved"
saved_conversations.mkdir(parents=True, exist_ok=True)


@st.cache_data
def list_models():
    return sorted(openai.Model.list().data, key=lambda x: x.id)


gpt_models = [x for x in list_models() if "gpt" in x.id]
gpt_model_ids = [x.id for x in gpt_models]

if not "loaded_name" in st.session_state:
    st.session_state.loaded_name = None

if not "messages" in st.session_state:
    st.session_state.messages = []
    st.session_state.results = {}
    st.session_state.session_id = None


def reset_state():
    st.session_state.loaded_name = None
    st.session_state.messages = []
    st.session_state.results = {}
    st.session_state.session_id = None


def main():
    st.write("Load previous")
    columns = iter(st.columns(2))
    with next(columns):
        load_recent_convo()
    with next(columns):
        load_saved_convo()

    with st.expander("Messages"):
        c1, c2 = st.columns((1, 3))
        with c1:
            st.write("Add message")
            # Create input fields for message and select box
            role = st.selectbox("Role", ["system", "user", "assistant"])
            message = st.text_area("Message")

            # Create an "Add" button to add the message to the list
            if st.button("Add") and message and role:
                st.session_state.messages.append({"role": role, "content": message})
                st.session_state.session_id = None
                st.session_state.results = {}

        with c2:
            if st.session_state.session_id:
                st.subheader(st.session_state.session_id)

            messages = st.session_state.messages[:]

            def delete_message(idx):
                st.session_state.session_id = None
                st.session_state.results = {}
                st.session_state.messages.pop(idx)
                st.experimental_rerun()

            def display_message(idx):
                message = st.session_state.messages[idx]
                if st.checkbox("edit"):
                    choices = ["system", "user", "assistant"]
                    with st.form("Update message"):
                        updated_role = st.selectbox(
                            "Role", choices, index=choices.index(message["role"]), key="update-role-choice"
                        )
                        updated_message = st.text_area("Message", value=message["content"], height=500)
                        if st.form_submit_button("Save") and updated_message:
                            messages[idx]["role"] = updated_role
                            messages[idx]["content"] = updated_message
                            st.session_state.session_id = None
                            st.session_state.results = {}
                            st.session_state.messages = messages
                            st.experimental_rerun()
                    if st.button("Delete Message", type="primary"):
                        delete_message(idx)
                else:
                    st.write(messages[idx])

            try:
                item_paginator("Chat Messages", len(messages), display_message)
            except Exception as e:
                st.error(e)
                st.json(st.session_state)
            # # Display the st.session_state.messages in a table
            # if st.session_state.messages:
            #     if st.checkbox("Edit messages"):
            #         edited_messages = st.data_editor(st.session_state.messages)
            #         if edited_messages != st.session_state.messages:
            #             st.session_state.messages = edited_messages
            #     st.table(st.session_state.messages)
            # else:
            #     st.write("No messages yet.")

    with st.form("Evaluate"):
        selected_models = st.multiselect("Use which model(s)", gpt_model_ids)
        if st.form_submit_button("Generate Response"):
            any_error = False
            if not selected_models:
                st.error("Select models before submitting")
                any_error = True
            if not st.session_state.messages:
                st.error("Add messages to the chat history before submitting")
                any_error = True
            if any_error:
                return

            call_chat(selected_models)
            st.experimental_rerun()

    display_results()


def load_recent_convo():
    with st.form("Load recent"):
        selected_convo: str = st.selectbox("Load recent session", list_recent_conversations())
        if st.form_submit_button("Load") and selected_convo:
            view_mode = st.session_state.get("view_mode")
            reset_state()
            st.experimental_set_query_params(s=selected_convo)
            load_session(recent_conversations)
            st.session_state.view_mode = view_mode
            st.experimental_set_query_params(s="")
            st.experimental_rerun()


def load_saved_convo():
    with st.form("Load saved"):
        selected_convo: str = st.selectbox("Load saved session", list_saved_conversations())
        if st.form_submit_button("Load") and selected_convo:
            view_mode = st.session_state.get("view_mode")
            reset_state()
            st.experimental_set_query_params(s=selected_convo)

            load_session(saved_conversations)
            st.session_state.view_mode = view_mode
            st.session_state.loaded_name = selected_convo
            st.experimental_set_query_params(s="")
            st.experimental_rerun()


def display_results():
    columns = iter(st.columns(2))
    choices = ["Side-by-side", "One at a time"]
    with next(columns):
        if "view_mode" in st.session_state:
            sel_idx = choices.index(st.session_state.view_mode)
            view_mode = st.selectbox("View results", choices, index=sel_idx)
        else:
            view_mode = st.selectbox("View results", choices)
        st.session_state.view_mode = view_mode
    with next(columns):
        if st.session_state.messages:
            with st.form("Save session"):
                save_name = st.text_input("Save as", value=st.session_state.loaded_name or "")
                if st.form_submit_button("Save") and save_name:
                    st.session_state.session_id = save_name
                    st.session_state.loaded_name = save_name
                    st.experimental_set_query_params(s="")

                    save_session(saved_conversations, set_query_param=False)
                    st.experimental_rerun()

    if not st.session_state.messages:
        return

    if not st.session_state.results:
        if st.session_state.session_id:
            st.subheader(st.session_state.session_id)
        st.subheader("Chat History")
        st.caption("No generated responses to this chat history")
        st.json(json.dumps(st.session_state.messages))
    else:
        st.subheader(st.session_state.session_id)

        def clear_results():
            st.session_state.results = {}
            st.session_state.session_id = None

        st.button("Clear Responses", on_click=clear_results)

        if view_mode == "Side-by-side":
            columns = iter(st.columns(len(st.session_state.results) + 1))
            with next(columns):
                st.subheader("Chat History")
                st.json(json.dumps(st.session_state.messages))
            for model in st.session_state.results:
                with next(columns):
                    display_model_result(model)
        else:

            def _handle_selection(idx):
                if idx == 0:
                    st.subheader("Chat History")
                    st.json(json.dumps(st.session_state.messages))
                else:
                    model_keys = list(st.session_state.results.keys())
                    model: str = model_keys[idx - 1]
                    display_model_result(model)

            item_paginator(
                "Chat and responses",
                ["Submitted Chat"] + [x for x in st.session_state.results],
                _handle_selection,
                display_item_names=True,
            )


def call_chat(models):
    st.session_state.results = {}
    for model in models:
        with st.spinner(f"Generating AI response for {model}"):
            response = openai.ChatCompletion.create(model=model, messages=st.session_state.messages)
            st.session_state.results[model] = response

    # save to recent sessions
    st.session_state.session_id = date_id()
    st.experimental_set_query_params(s="")
    save_session(recent_conversations, set_query_param=False)


def display_model_result(model_name: str):
    st.subheader(model_name + " response")
    response = st.session_state.results[model_name]
    content = response["choices"][0]["message"]["content"]
    try:
        json_content = json.loads(content)
    except Exception:
        json_content = None

    st.write("Response is valid JSON", check_or_x(bool(json_content)))

    if json_content:
        st.write(json_content)
    else:
        st.write(content)

    with st.expander("Raw Response", expanded=False):
        st.write(response)


def list_recent_conversations():
    return sorted((x.name.removesuffix(".json") for x in recent_conversations.iterdir()), reverse=True)


def list_saved_conversations():
    return sorted((x.name.removesuffix(".json") for x in saved_conversations.iterdir()), reverse=True)


if __name__ == "__main__":
    main()
    with st.expander("Session State"):
        st.json(st.session_state)
