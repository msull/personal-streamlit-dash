import streamlit as st

from page_helpers import load_data_from_file


def find_state_id_key(dataframe) -> str:
    try:
        _ = dataframe["State ID"]
    except KeyError:
        return "StateID"
    else:
        return "State ID"


def _load_data(file_upload):
    df = load_data_from_file(file_upload)
    return df


cols = iter(st.columns(2))


first_year_ids = None

with next(cols):
    file1 = st.file_uploader("Start Year")
    if file1:
        df1 = _load_data(file1)
        id_key1 = find_state_id_key(df1)
        first_id = df1[id_key1][0]
        if " " in first_id:
            df1[[id_key1, "Last Name"]] = df1[id_key1].str.split(" ", n=1, expand=True)

        first_year_ids = [x for x in df1[id_key1].tolist() if x.strip()]

        st.metric("Number of students", len(first_year_ids))

        with st.expander("Student IDs"):
            st.write(df1[id_key1])


with next(cols):
    file2 = st.file_uploader("Next Year")
    if file2:
        df2 = _load_data(file2)
        id_key2 = find_state_id_key(df2)
        first_id = df2[id_key2][0]
        if " " in first_id:
            df2[[id_key2, "Last Name"]] = df2[id_key2].str.split(" ", n=1, expand=True)

        second_year_ids = [x for x in df2[id_key2].tolist() if x.strip()]
        st.metric("Number of students", len(second_year_ids))

        if first_year_ids:
            repeat_ids = [x for x in second_year_ids if x in first_year_ids]
            st.metric("Number returning", len(repeat_ids))






        with st.expander("Student IDs"):
            st.write(df2[id_key2])

