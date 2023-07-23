from dataclasses import dataclass
from datetime import datetime
from typing import List

import streamlit as st

from auth_helpers import set_page_config
from common_settings import AppSettings as _AppSettings
from session_manager import SessionDataBase
from pydantic import Field

set_page_config("PTA Meetings", requires_auth=True)

NOW = datetime.now()


class AppSettings(_AppSettings):
    now: datetime = datetime.now()

    @property
    def meeting_data(self):
        meeting_data = self.streamlit_app_output_dir / "pta-items" / "meeting-data"
        if not meeting_data.exists():
            meeting_data.mkdir(parents=True, exist_ok=True)
        return meeting_data

    def available_meeting_data_files(self) -> List[str]:
        return sorted(str(x) for x in self.meeting_data.iterdir())


@st.cache_resource
def get_app_settings():
    return AppSettings()


settings = get_app_settings()


class MeetingData(SessionDataBase):
    meeting_date: datetime = Field(default_factory=lambda: datetime.now().replace(second=0, microsecond=0))
    meeting_location: str = ""

    def persist(self):
        self.persist_session_state(settings.meeting_data)


@dataclass
class FormDefaults:
    pass


meeting_data = MeetingData.init_session(session_dir=settings.meeting_data)


def main():
    st.title("PTA Meeting Minutes App")

    # Meeting Information
    st.header("Meeting Information")
    date = st.date_input("Date", value=settings.now)
    time = st.time_input("Time", value=settings.now)
    # Combine date and time into a datetime object
    meeting_datetime = datetime.combine(date, time).replace(second=0, microsecond=0)
    if meeting_datetime != meeting_data.meeting_date:
        meeting_data.meeting_date = meeting_datetime
        meeting_data.persist()
        st.toast("Updated meeting date / time")

    location = st.text_input("Location")
    if location != meeting_data.meeting_location:
        meeting_data.meeting_location = location
        meeting_data.persist()
        st.toast("Updated meeting location")

    attendees = st.text_area("Attendees")
    # TODO: Consider adding a feature to select attendees from a list of PTA members.

    # Agenda Section
    st.header("Agenda")
    agenda_items = st.text_area("Agenda Items")
    # TODO: Replace this with a dynamic list of text inputs, so you can add, remove, and reorder agenda items.

    # Notes Section
    st.header("Notes")
    notes = st.text_area("Notes")
    # TODO: Consider adding a feature to link notes to specific agenda items. This could be a dropdown menu or a tagging system.

    # Decisions and Action Items Section
    st.header("Decisions")
    decisions = st.text_area("Decisions")
    # TODO: Replace this with a dynamic list of text inputs, so you can add and remove decisions.

    st.header("Action Items")
    actions = st.text_area("Action Items")
    # TODO: Replace this with a dynamic list of text inputs, so you can add and remove action items. Consider adding fields for who the task was assigned to and any relevant deadlines.

    # Save and Export Buttons
    if st.button("Save"):
        st.success("Meeting minutes saved successfully.")
        # TODO: Implement the functionality to actually save the meeting minutes. This could involve writing the data to a file or storing it in a database.

    if st.button("Export"):
        st.success("Meeting minutes exported successfully.")
        # TODO: Implement the functionality to export the meeting minutes in a well-formatted document. This could involve generating a PDF or Word document.


try:
    main()
finally:
    with st.expander("Session"):
        st.write(st.session_state)
