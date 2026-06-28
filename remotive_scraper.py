import csv
import requests
from datetime import datetime


# --------------------------------------------------
# Scraper Settings
# --------------------------------------------------
OUTPUT_FILE = "remotive_jobs.csv"

# Public remote jobs API source
API_URL = "https://remotive.com/api/remote-jobs"

# Change this keyword if you want specific jobs
SEARCH_KEYWORD = "python"


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def clean_text(value):
    if value is None:
        return "Not Available"

    value = str(value).replace("\n", " ").strip()
    return value if value else "Not Available"


def format_date(date_value):
    if not date_value:
        return "Not Available"

    try:
        parsed_date = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return parsed_date.strftime("%B %d, %Y")
    except Exception:
        return clean_text(date_value)


def fetch_jobs():
    params = {
        "search": SEARCH_KEYWORD
    }

    try:
        response = requests.get(API_URL, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()
        jobs = data.get("jobs", [])

        return jobs

    except requests.exceptions.RequestException as error:
        print(f"Request error: {error}")
        return []

    except ValueError:
        print("Error: Could not parse API response as JSON.")
        return []


def transform_jobs(raw_jobs):
    cleaned_jobs = []

    for job in raw_jobs:
        title = clean_text(job.get("title"))
        company = clean_text(job.get("company_name"))
        location = clean_text(job.get("candidate_required_location"))
        date_posted = format_date(job.get("publication_date"))
        job_url = clean_text(job.get("url"))

        if title == "Not Available":
            continue

        cleaned_jobs.append({
            "Title": title,
            "Company": company,
            "Location": location,
            "Date Posted": date_posted,
            "Job URL": job_url
        })

    return cleaned_jobs


def remove_duplicates(jobs):
    unique_jobs = []
    seen = set()

    for job in jobs:
        key = (
            job["Title"].lower(),
            job["Company"].lower(),
            job["Location"].lower(),
            job["Job URL"].lower()
        )

        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs


def save_to_csv(jobs):
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["Title", "Company", "Location", "Date Posted", "Job URL"]
        )

        writer.writeheader()
        writer.writerows(jobs)


# --------------------------------------------------
# Main Function
# --------------------------------------------------
def scrape_jobs():
    print("----------------------------------------")
    print("Job Trend Analyzer Scraper Started")
    print(f"Source: Remotive Public Jobs API")
    print(f"Search keyword: {SEARCH_KEYWORD}")
    print("----------------------------------------")

    raw_jobs = fetch_jobs()

    if not raw_jobs:
        print("No jobs found or API request failed.")
        save_to_csv([])
        return

    cleaned_jobs = transform_jobs(raw_jobs)
    unique_jobs = remove_duplicates(cleaned_jobs)

    save_to_csv(unique_jobs)

    print("----------------------------------------")
    print("Scraping completed.")
    print(f"Total jobs saved: {len(unique_jobs)}")
    print(f"Output file: {OUTPUT_FILE}")
    print("----------------------------------------")


if __name__ == "__main__":
    scrape_jobs()