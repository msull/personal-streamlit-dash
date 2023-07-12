import json

import numpy as np
import pandas as pd
import streamlit as st
from auth_helpers import set_page_config
from page_helpers import item_paginator, reset_paginator

set_page_config("Data Explorer", requires_auth=True)


# Function to load data
def load_data(file):
    # Load the data
    if file.type == "text/csv":
        data = pd.read_csv(file, dtype=str, low_memory=False)
    elif file.type == "text/tab-separated-values":
        data = pd.read_csv(file, dtype=str, low_memory=False, sep="\t")
    elif (
        file.type == "application/vnd.ms-excel"
        or file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        data = pd.read_excel(file, dtype=str)
    elif file.type == "application/json":
        data = pd.read_json(file, dtype=str)
    elif file.type == "application/octet-stream":  # Assuming this is a Parquet file
        data = pd.read_parquet(file, dtype=str)
    else:
        raise RuntimeError(f"Unknown / unsupported file type {file.type}")

    return data.replace({np.NAN: None})


@st.cache_data
def filter_and_group_and_sort(data, filter_text, group_by_columns, sort_by_columns):
    filtered_df = (
        data[data.astype(str).apply(lambda x: x.str.contains(filter_text, case=False)).any(axis=1)]
        if filter_text
        else data
    )

    if group_by_columns:
        filtered_df = group_by_data(filtered_df, group_by_columns).aggregate(list)

    if sort_by_columns:
        filtered_df = filtered_df.sort_values(sort_by_columns)

    return filtered_df


# Function to display data
def display_data(df):
    if st.checkbox("Row Explorer", on_change=reset_paginator, args=("Row Explorer",)):
        # reset the paginator when filtering changes
        filter_text = st.text_input("Filter rows", on_change=reset_paginator, args=("Row Explorer",))
        group_by_columns = st.multiselect(
            "Select columns to group by", df.columns, on_change=reset_paginator, args=("Row Explorer",)
        )
        if group_by_columns:
            autogroup_single_value_lists = st.checkbox("Auto-group single value lists")
        else:
            autogroup_single_value_lists = False
        sort_by_columns = st.multiselect(
            "Select columns to sort by", df.columns, on_change=reset_paginator, args=("Row Explorer",)
        )

        filtered_df = filter_and_group_and_sort(df, filter_text, group_by_columns, sort_by_columns)

        if st.checkbox("Show dataframe"):
            number = st.number_input("Number of rows to view", min_value=1, value=50)
            st.dataframe(filtered_df.head(number))

        def _display_row(idx: int):
            st.subheader(f"Row {idx + 1}")
            row_data = filtered_df.iloc[idx]

            display_data = {}
            for column in df.columns:
                data = row_data[column]
                if autogroup_single_value_lists:
                    if isinstance(data, list) and len(set(data)) == 1:
                        data = data[0]
                display_data[column] = data

            st.code(json.dumps(display_data, indent=2))

        item_paginator("Row Explorer", filtered_df.shape[0], _display_row, enable_keypress_nav=True)
        st.divider()

    if st.checkbox("Column Explorer", on_change=reset_paginator, args=("Column Explorer",)):
        # Function to display an individual column item
        def _display_column(idx: int):
            column_name = df.columns.tolist()[idx]
            column_data = df[column_name]
            column_count = len(column_data)
            unique_items = column_data.nunique()
            st.subheader(f"Column {column_name}")
            st.write("Count:", column_count)
            st.write("Unique Items:", unique_items)

            if st.checkbox("Show unique items"):
                column_data = column_data.astype(str)
                unique_items, item_counts = np.unique(column_data, return_counts=True)
                unique_items_df = pd.DataFrame({"Unique Items": unique_items, "Count": item_counts})
                st.dataframe(unique_items_df)

            if st.checkbox("Show all values"):
                st.write(column_data)

        item_paginator(
            "Column Explorer", df.columns.tolist(), _display_column, enable_keypress_nav=True, display_item_names=True
        )
        st.divider()


# Function to show column details
def show_details(df):
    st.subheader("Data Details")
    st.write("Rows: ", df.shape[0], "Columns: ", df.shape[1], "Missing values: ", df.isnull().sum().sum())

    if st.checkbox("Show column details"):
        column_names = df.columns.tolist()
        column_types = [df[column].dtype for column in column_names]
        unique_counts = [df[column].nunique() for column in column_names]
        is_unique = [count == df.shape[0] for count in unique_counts]
        most_common = []
        for column in column_names:
            if df[column].nunique() > 0:
                most_common.append(df[column].value_counts().idxmax())
            else:
                most_common.append(None)
        details_df = pd.DataFrame(
            {
                "Column Name": column_names,
                "Data Type": column_types,
                "Unique Items": unique_counts,
                "Every Value Unique": is_unique,
                "Most Common Item": most_common,
            }
        )
        st.dataframe(details_df)
        st.divider()


# Function to show basic statistics
def basic_stats(df):
    if st.checkbox("Show basic stats"):
        st.table(df.describe())
        st.divider()


def group_by_data(data, group_by_columns):
    grouped_data = data.groupby(group_by_columns, as_index=False)
    return grouped_data


# Main function to control the application
def main():
    st.title("Data Explorer")

    # Upload the dataset
    file = st.file_uploader(
        "Upload a CSV, Excel, JSON, or Parquet file", type=["csv", "tsv", "xls", "xlsx", "json", "parquet"]
    )

    # Load and display the data
    if file is not None:
        data = load_data(file)
        show_details(data)
        display_data(data)
        basic_stats(data)


if __name__ == "__main__":
    main()
