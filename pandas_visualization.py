from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


DATA_FILE = "remotive_jobs.csv"
CHARTS_DIR = Path("charts")


def load_data(file_path):
    if not Path(file_path).exists():
        print(f"Data file not found: {file_path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)
    except Exception as error:
        print(f"Error reading CSV file: {error}")
        return pd.DataFrame()

    return df


def clean_column_names(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    column_mapping = {
        "Title": "title",
        "Company": "company",
        "Location": "location",
        "Date Posted": "date_posted",
        "Date": "date_posted",
        "date": "date_posted"
    }

    df.rename(columns=column_mapping, inplace=True)

    return df


def prepare_data(df):
    df = clean_column_names(df)

    for column in ["title", "company", "location", "date_posted"]:
        if column not in df.columns:
            df[column] = "Not Available"

        df[column] = df[column].astype(str).str.strip()
        df[column] = df[column].replace(["", "nan", "None"], "Not Available")

    df["parsed_date"] = pd.to_datetime(df["date_posted"], errors="coerce")

    return df


def save_horizontal_bar(data, title, xlabel, ylabel, filename):
    if data.empty:
        print(f"No data available for {title}")
        return

    data = data.sort_values(ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(data.index, data.values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()

    output_path = CHARTS_DIR / filename
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Saved chart: {output_path}")


def save_line_chart(data, title, xlabel, ylabel, filename):
    if data.empty:
        print(f"No data available for {title}")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data.values, marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path = CHARTS_DIR / filename
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Saved chart: {output_path}")


def main():
    CHARTS_DIR.mkdir(exist_ok=True)

    df = load_data(DATA_FILE)

    if df.empty:
        print("No data available for analysis.")
        return

    df = prepare_data(df)

    print("\nPreview of Job Listings:\n")
    print(df[["title", "company", "location", "date_posted"]].head())

    print("\nDataset Summary:")
    print(f"Total jobs: {len(df)}")
    print(f"Unique job titles: {df['title'].nunique()}")
    print(f"Unique companies: {df['company'].nunique()}")
    print(f"Unique locations: {df['location'].nunique()}")

    top_titles = df["title"].value_counts().head(10)
    top_companies = df["company"].value_counts().head(10)
    top_locations = df["location"].value_counts().head(10)

    print("\nTop Job Titles:")
    print(top_titles)

    print("\nTop Companies:")
    print(top_companies)

    print("\nTop Locations:")
    print(top_locations)

    save_horizontal_bar(
        data=top_titles,
        title="Top Job Titles",
        xlabel="Number of Listings",
        ylabel="Job Title",
        filename="top_job_titles.png"
    )

    save_horizontal_bar(
        data=top_companies,
        title="Top Companies by Job Listings",
        xlabel="Number of Listings",
        ylabel="Company",
        filename="top_companies.png"
    )

    save_horizontal_bar(
        data=top_locations,
        title="Top Hiring Locations",
        xlabel="Number of Listings",
        ylabel="Location",
        filename="top_locations.png"
    )

    date_df = df.dropna(subset=["parsed_date"]).copy()

    if not date_df.empty:
        date_df["post_date"] = date_df["parsed_date"].dt.date
        trend_data = date_df["post_date"].value_counts().sort_index()

        save_line_chart(
            data=trend_data,
            title="Job Postings Over Time",
            xlabel="Date",
            ylabel="Number of Jobs",
            filename="posting_trend.png"
        )
    else:
        print("\nNo valid date data available for posting trend chart.")


if __name__ == "__main__":
    main()