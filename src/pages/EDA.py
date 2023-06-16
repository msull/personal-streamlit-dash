import numpy as np
import pandas as pd
import streamlit as st


# Function to load data
def load_data(file):
    # Load the data
    if file.type == "text/csv":
        data = pd.read_csv(file)
    elif file.type == "application/vnd.ms-excel":
        data = pd.read_excel(file)

    # Return the dataframe
    return data


# Function to display data
def display_data(df):
    if st.checkbox("Show dataframe"):
        number = st.number_input("Number of rows to view", min_value=1, value=50)
        st.dataframe(df.head(number))


# Function to show column details
def show_details(df):
    st.subheader('Data Details')
    st.write('Rows: ', df.shape[0])
    st.write('Columns: ', df.shape[1])
    st.write('Missing values: ', df.isnull().sum().sum())

    st.subheader('Column Details')
    column_names = df.columns.tolist()
    unique_counts = [df[column].nunique() for column in column_names]
    is_unique = [count == df.shape[0] for count in unique_counts]
    most_common = []
    for column in column_names:
        if df[column].nunique() > 0:
            most_common.append(df[column].value_counts().idxmax())
        else:
            most_common.append(None)
    details_df = pd.DataFrame({'Column Name': column_names, 'Unique Items': unique_counts, 'Every Value Unique': is_unique, 'Most Common Item': most_common})
    st.dataframe(details_df)




# Function to show basic statistics
def basic_stats(df):
    if st.checkbox("Show basic stats"):
        st.table(df.describe())


# Function for creating histograms
def create_hist(df):
    if st.checkbox("Show histograms"):
        st.write("Histograms will be shown here")


# Main function to control the application
def main():
    st.title("Data Exploration App")

    # Upload the dataset
    file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])

    # Load and display the data
    if file is not None:
        data = load_data(file)
        show_details(data)
        display_data(data)

        basic_stats(data)
        create_hist(data)


if __name__ == "__main__":
    main()
