from pathlib import Path
from typing import Optional, Type, TypeVar

import streamlit as st
from pydantic import BaseModel, Field

from page_helpers import date_id

T = TypeVar("T", bound=BaseModel)


class SessionDataBase(BaseModel):
    session_id: str = Field(default_factory=date_id)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        self.save_to_session_state()

    def save_to_session_state(self):
        for k, v in self.dict().items():
            st.session_state[k] = v

    def persist_session_state(self, session_dir: Path, set_query_param=True):
        if set_query_param:
            st.experimental_set_query_params(s=st.session_state.session_id)

        path = session_dir / (st.session_state.session_id + ".json")
        path.write_text(self.json())

    def clear_session(self):
        st.experimental_set_query_params(s="")
        for field in self.__fields__.values():
            if field.name in st.session_state:
                del st.session_state[field.name]

    @classmethod
    def init_session(cls: Type[T], session_dir: Optional[Path] = None) -> T:
        # if we have a saved sessions dir and a query param, check correct session is loaded
        query_session = st.experimental_get_query_params().get("s")
        if query_session:
            query_session = query_session[0]
        if session_dir and query_session:
            # we have a session dir and session id -- is it already loaded?
            if st.session_state.get("session_id") != query_session:
                # no, the requested session isn't loaded -- clear out any existing session data
                for field in cls.__fields__.values():
                    if field.name in st.session_state:
                        del st.session_state[field.name]

        session: Optional[T] = None
        if st.session_state.get("session_id"):
            # since we have a session id in the session_state already, we've done an init and can load the data
            session = cls.parse_obj(st.session_state)
        elif session_dir and query_session:
            path = session_dir / (query_session + ".json")
            if path.exists():
                session = cls.parse_raw(path.read_text())

        if not session:
            session: T = cls(session_dir=session_dir)
        session.save_to_session_state()
        return session
