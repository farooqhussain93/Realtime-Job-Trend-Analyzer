import os
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Job Trend Analyzer",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
@st.cache_data
def load_data(file_path, file_modified_time):
    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

    return df


def clean_column_names(df):
    df = df.copy()

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    # Standard column name mapping
    column_mapping = {
        "Title": "title",
        "Company": "company",
        "Location": "location",
        "Date Posted": "date_posted",
        "date_posted": "date_posted",
        "Date": "date_posted",
        "date": "date_posted"
    }

    df.rename(columns=column_mapping, inplace=True)

    return df


def prepare_data(df):
    df = clean_column_names(df)

    required_columns = ["title", "company", "location"]

    for col in required_columns:
        if col not in df.columns:
            df[col] = "Not Available"

    if "date_posted" not in df.columns:
        df["date_posted"] = "Not Available"

    # Clean text values
    for col in ["title", "company", "location", "date_posted"]:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["nan", "None", ""], "Not Available")

    # Convert date safely
    df["parsed_date"] = pd.to_datetime(df["date_posted"], errors="coerce")

    return df


def filter_data(df, keyword, selected_company, selected_location):
    filtered_df = df.copy()

    if keyword:
        keyword = keyword.strip().lower()

        filtered_df = filtered_df[
            filtered_df["title"].str.lower().str.contains(keyword, na=False)
            | filtered_df["company"].str.lower().str.contains(keyword, na=False)
            | filtered_df["location"].str.lower().str.contains(keyword, na=False)
            | filtered_df["date_posted"].str.lower().str.contains(keyword, na=False)
        ]

    if selected_company != "All":
        filtered_df = filtered_df[filtered_df["company"] == selected_company]

    if selected_location != "All":
        filtered_df = filtered_df[filtered_df["location"] == selected_location]

    return filtered_df


def plot_horizontal_bar(data, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(9, 5))

    data = data.sort_values(ascending=True)

    ax.barh(data.index, data.values)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    for index, value in enumerate(data.values):
        ax.text(value, index, f" {value}", va="center", fontsize=10)

    plt.tight_layout()
    return fig


def plot_line_chart(data, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(data.index, data.values, marker="o")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    return fig


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "remotive_jobs.csv"

file_modified_time = os.path.getmtime(DATA_FILE) if os.path.exists(DATA_FILE) else 0
raw_df = load_data(DATA_FILE, file_modified_time)


# --------------------------------------------------
# App Header
# --------------------------------------------------
st.title("📊 Job Trend Analyzer")
st.caption("A Streamlit data analytics dashboard for analyzing job market trends from scraped job listing data.")

st.divider()


# --------------------------------------------------
# Empty Data Handling
# --------------------------------------------------
if raw_df.empty:
    st.error("No job data found. Please make sure `remotive_jobs.csv` exists in the same folder as `streamlit_app.py` and contains valid data.")
    st.stop()


df = prepare_data(raw_df)

if df.empty:
    st.error("The dataset is empty after cleaning. Please check your CSV file.")
    st.stop()


# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

keyword = st.sidebar.text_input(
    "Search keyword",
    placeholder="Example: Data Analyst, Python, Marketing"
)

company_options = ["All"] + sorted(df["company"].dropna().unique().tolist())
location_options = ["All"] + sorted(df["location"].dropna().unique().tolist())

selected_company = st.sidebar.selectbox("Filter by company", company_options)
selected_location = st.sidebar.selectbox("Filter by location", location_options)

filtered_df = filter_data(df, keyword, selected_company, selected_location)


# --------------------------------------------------
# No Result Handling
# --------------------------------------------------
if filtered_df.empty:
    st.warning("No jobs found for the selected filters. Try a different keyword, company, or location.")
    st.stop()


# --------------------------------------------------
# Dashboard Cards
# --------------------------------------------------
total_jobs = len(filtered_df)
unique_titles = filtered_df["title"].nunique()
unique_companies = filtered_df["company"].nunique()
unique_locations = filtered_df["location"].nunique()

valid_dates = filtered_df["parsed_date"].dropna()

if not valid_dates.empty:
    latest_date = valid_dates.max().strftime("%d %b %Y")
else:
    latest_date = "Not Available"

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Jobs", total_jobs)

with col2:
    st.metric("Unique Job Titles", unique_titles)

with col3:
    st.metric("Companies", unique_companies)

with col4:
    st.metric("Locations", unique_locations)

with col5:
    st.metric("Latest Posting", latest_date)


st.divider()


# --------------------------------------------------
# Data Preview
# --------------------------------------------------
st.subheader("📄 Job Listings Preview")

display_columns = ["title", "company", "location", "date_posted"]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True
)

csv_data = filtered_df[display_columns].to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered CSV",
    data=csv_data,
    file_name="filtered_job_trends.csv",
    mime="text/csv"
)


st.divider()


# --------------------------------------------------
# Charts Section
# --------------------------------------------------
st.subheader("📈 Job Market Insights")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("### Top Job Titles")

    top_titles = filtered_df["title"].value_counts().head(10)

    if top_titles.empty:
        st.info("No job title data available.")
    else:
        fig_titles = plot_horizontal_bar(
            data=top_titles,
            title="Top Job Titles",
            xlabel="Number of Listings",
            ylabel="Job Title"
        )
        st.pyplot(fig_titles)

with chart_col2:
    st.write("### Top Companies")

    top_companies = filtered_df["company"].value_counts().head(10)

    if top_companies.empty:
        st.info("No company data available.")
    else:
        fig_companies = plot_horizontal_bar(
            data=top_companies,
            title="Top Companies by Job Listings",
            xlabel="Number of Listings",
            ylabel="Company"
        )
        st.pyplot(fig_companies)


chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.write("### Top Locations")

    top_locations = filtered_df["location"].value_counts().head(10)

    if top_locations.empty:
        st.info("No location data available.")
    else:
        fig_locations = plot_horizontal_bar(
            data=top_locations,
            title="Top Hiring Locations",
            xlabel="Number of Listings",
            ylabel="Location"
        )
        st.pyplot(fig_locations)

with chart_col4:
    st.write("### Posting Trend Over Time")

    date_df = filtered_df.dropna(subset=["parsed_date"]).copy()

    if date_df.empty:
        st.info("No valid date data available for posting trend analysis.")
    else:
        date_df["post_date"] = date_df["parsed_date"].dt.date
        trend_data = date_df["post_date"].value_counts().sort_index()

        fig_trend = plot_line_chart(
            data=trend_data,
            title="Job Postings Over Time",
            xlabel="Date",
            ylabel="Number of Jobs"
        )
        st.pyplot(fig_trend)


st.divider()


# --------------------------------------------------
# Summary Section
# --------------------------------------------------
st.subheader("🧾 Quick Summary")

most_common_title = filtered_df["title"].value_counts().idxmax()
most_common_company = filtered_df["company"].value_counts().idxmax()
most_common_location = filtered_df["location"].value_counts().idxmax()

st.write(
    f"""
    Based on the current filtered dataset, the most common job title is **{most_common_title}**.
    The company with the highest number of listings is **{most_common_company}**.
    The most frequent location/category in the dataset is **{most_common_location}**.
    """
)