from pathlib import Path
from tempfile import NamedTemporaryFile

import pypdfium2
import streamlit as st
from auth_helpers import set_page_config
from common_settings import AppSettings
from page_helpers import item_paginator

set_page_config("PDF Explorer", requires_auth=True)


@st.cache_resource
def get_app_setings():
    return AppSettings()


settings = get_app_setings()

if flash_msg := st.session_state.get("flash_msg"):
    st.info(flash_msg)
    del st.session_state.flash_msg


if active_pdf := st.session_state.get("active_pdf"):
    pdf = pypdfium2.PdfDocument(settings.pdf_uploads / active_pdf)

    def _display_page(page_num: int):
        page = pdf[page_num]
        extracted = page.get_textpage().get_text_range()
        display_mode = st.radio(
            "Display Mode",
            ("Both", "Page", "Content"),
            horizontal=True,
        )
        if display_mode == "Both":
            c2, c3 = st.columns(2)
        else:
            c2 = st.columns(1)[0]
            c3 = c2

        if display_mode == "Both" or display_mode == "Content":
            c3.code(extracted)

        if display_mode == "Both" or display_mode == "Page":
            with NamedTemporaryFile("wb", suffix=".jpg") as f:
                f.close()
                page.render(scale=2).to_pil().save(f.name)
                c2.image(f.name)

    def _do_delete_file(*args):
        (settings.pdf_uploads / active_pdf).unlink()
        del st.session_state.active_pdf
        del st.session_state.page_num
        st.session_state.flash_msg = f"Deleted {active_pdf}"
        st.experimental_rerun()

    if st.button("Close", use_container_width=True, key="close1"):
        del st.session_state.active_pdf
        del st.session_state.page_num
        st.experimental_rerun()

    item_paginator(
        active_pdf,
        items=len(pdf),
        item_handler_fn=_display_page,
        item_actions={"Delete File": _do_delete_file},
        enable_keypress_nav=True,
    )

    if st.button("Close", use_container_width=True, key="close2"):
        del st.session_state.active_pdf
        del st.session_state.page_num
        st.experimental_rerun()


settings.pdf_uploads.mkdir(parents=True, exist_ok=True)
with st.form("upload-file", clear_on_submit=True):
    uploaded = st.file_uploader("Upload PDF")
    if st.form_submit_button("Upload file") and uploaded:
        if not uploaded.name.endswith(".pdf"):
            st.error("Only PDF uploads are supported")
        else:
            (settings.pdf_uploads / uploaded.name).write_bytes(uploaded.read())
            st.session_state.flash_msg = f"Uploaded {uploaded.name}"
            st.experimental_rerun()

available_pdfs = [x.name for x in settings.pdf_uploads.iterdir()]
if available_pdfs:
    with st.form("Open PDF"):
        st.write("Choose PDF")
        selected = st.selectbox("Which File", available_pdfs)

        if st.form_submit_button("Open File") and selected:
            st.session_state.active_pdf = selected
            st.session_state.page_num = 0
            st.experimental_rerun()


with st.expander("Session State"):
    st.write(st.session_state)
