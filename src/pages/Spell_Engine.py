from typing import List

import streamlit as st
from logzero import logger
from pydantic import Field

from auth_helpers import set_page_config
from chat_session import ChatSession, check_for_flagged_content
from common_settings import AppSettings as _AppSettings
from session_manager import SessionDataBase
from spell_engine_helpers import (
    AI_ASSISTANT_MSG,
    AI_REINFORCEMENT_MSG,
    add_examples_to_chat,
    generate_inventory,
    generate_reagents_pouch,
    generate_system_message_for_spellcast,
    SCENARIOS,
)

set_page_config("Spell Engine", requires_auth=True)


class AppSettings(_AppSettings):
    @property
    def session_dir(self):
        session_dir = self.streamlit_app_output_dir / "spell-engine-sessions"
        if not session_dir.exists():
            session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir


class SessionData(SessionDataBase):
    total_tokens_used: int = 0
    mission: str = "Spellcasting test"
    trolls_mood: str = "angry"
    chat_history: List[str] = []
    game_started: bool = False
    inventory: List[str] = Field(default_factory=generate_inventory)
    reagents: List[str] = Field(default_factory=generate_reagents_pouch)

    spell_cast_level: str = ""
    spell_description: str = ""
    spell_scenario: str = "The player is confronting a troll on a stone bridge. There is no one else nearby."
    spell_description_saved: str = ""
    spell_items_used: List[str] = []
    spell_reagents: List[str] = []
    spell_result: str = ""
    spell_raw_result: dict = {}


settings = AppSettings()
session_data = SessionData.init_session(session_dir=settings.session_dir)


def game_setup_view():
    st.write(session_data.mission)

    if st.button("Reroll Inventory", use_container_width=True):
        session_data.inventory = generate_inventory()
        session_data.reagents = generate_reagents_pouch()

        st.experimental_rerun()

    inventory_display_cols()

    def start_game():
        session_data.game_started = True
        session_data.persist_session_state(settings.session_dir)

    st.button("Begin", type="primary", use_container_width=True, on_click=start_game)


def game_play_view():
    with st.expander("Intro"):
        st.write(session_data.mission)

    if not session_data.spell_description:
        main_column, side_column = st.columns((2, 1))
        with side_column:
            selected = select_inventory_display()

        with main_column:
            with st.form("game form"):
                st.write("Cast a spell")
                cast_level = st.selectbox("Cast as wizard level", ("apprentice", "adept", "sorcerer", "archmage"))
                scenario = st.selectbox("Scenario", SCENARIOS)
                custom_scenario = st.text_input("Custom scenario")
                description = st.text_area(
                    "Spell effect (reference your used ingredients / tools)", session_data.spell_description_saved
                )
                if st.form_submit_button() and description:
                    session_data.spell_description = description
                    session_data.spell_scenario = custom_scenario or scenario
                    session_data.spell_cast_level = cast_level
                    session_data.spell_items_used = selected["items"]
                    session_data.spell_reagents = selected["reagents"]
                    st.experimental_rerun()

                if items := selected["items"]:
                    st.caption("Using: " + ", ".join(items))
                if reagents := selected["reagents"]:
                    st.caption("Using reagents: " + ", ".join(reagents))

    else:
        spell_result_view()


def spell_result_view():
    main_column, side_column = st.columns((2, 1))
    with side_column:
        st.subheader("Cast with")
        with st.expander("Items", expanded=True):
            for r in session_data.spell_items_used:
                st.write(r)

        with st.expander("Reagents", expanded=True):
            for r in session_data.spell_reagents:
                st.write(r)

    with main_column:
        cast_level = st.selectbox("Cast as wizard level", ("apprentice", "adept", "sorcerer", "archmage"))
        with st.form("game form"):
            if session_data.spell_scenario:
                st.write("**Scenario**")
                st.write(session_data.spell_scenario)

            st.write("**The player casts a spell**")
            st.write(f'_"{session_data.spell_description}"_')
            st.write("**Cast using**")
            st.write("**Tools:**", ", ".join(session_data.spell_items_used))
            st.write("**Reagents:**", ", ".join(session_data.spell_reagents))

            if not session_data.spell_result:
                with st.spinner(f"Casting spell as {cast_level}..."):
                    generate_spell_result(cast_level)
            st.write("**Cast at level:**", session_data.spell_cast_level)
            st.write(session_data.spell_result)

            def clear_result():
                session_data.spell_result = ""
                session_data.spell_cast_level = cast_level

            st.form_submit_button("Generate again", on_click=clear_result)

    def edit():
        session_data.spell_description_saved = session_data.spell_description
        session_data.spell_description = ""
        session_data.spell_result = ""

    st.button("Edit", use_container_width=True, on_click=edit)


def generate_spell_result(wizard_level: str):
    assert wizard_level in {"apprentice", "adept", "sorcerer", "archmage"}

    check_for_flagged_content(session_data.spell_description)

    chat_session = ChatSession()
    chat_session.system_says(AI_ASSISTANT_MSG)
    add_examples_to_chat(chat_session)
    chat_session.user_says(session_data.spell_description)
    chat_session.system_says(
        generate_system_message_for_spellcast(
            wizard_level,
            session_data.spell_items_used,
            session_data.spell_reagents,
            scenario=session_data.spell_scenario,
        )
    )
    logger.debug(chat_session.history[-3:])
    chat_session.system_says(AI_REINFORCEMENT_MSG)
    response = chat_session.get_ai_response()
    session_data.spell_result = response["choices"][0]["message"]["content"]
    session_data.spell_raw_result = response.to_dict()
    session_data.total_tokens_used += response["usage"]["total_tokens"]


def main():
    if not session_data.game_started:
        game_setup_view()
    else:
        game_play_view()
        st.button(
            "Restart",
            type="primary",
            use_container_width=True,
            on_click=session_data.clear_session,
        )


def select_inventory_display(expanded=True):
    checked = {"items": [], "reagents": []}
    with st.expander("Inventory", expanded=expanded):
        for item in session_data.inventory:
            if st.checkbox(item, value=item in session_data.spell_items_used):
                checked["items"].append(item)

    with st.expander("Reagents", expanded=expanded):
        for reagent in session_data.reagents:
            if st.checkbox(reagent, value=reagent in session_data.spell_reagents):
                checked["reagents"].append(reagent)
    return checked


def inventory_display_cols(expanded=True):
    columns = iter(st.columns((1, 2, 2, 1)))
    next(columns)  # formatting
    with next(columns):
        with st.expander("Inventory", expanded=expanded):
            for r in session_data.inventory:
                st.write(r)
    with next(columns):
        with st.expander("Reagents", expanded=expanded):
            for r in session_data.reagents:
                st.write(r)


try:
    main()
finally:
    with st.expander("Session"):
        st.write(st.session_state)
