# Job Scraper & Skill Analyzer - MVP Version

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import spacy
import streamlit as st

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

# Pre-defined skills list (expandable)
skills_list = ['python', 'java', 'c++', 'sql', 'excel', 'javascript', 'react', 'node', 'aws', 'django', 'rest api', 'tensorflow', 'pytorch']

# Function to scrape job listings from Indeed
def scrape_indeed_jobs(query="software engineer", location="India", num_pages=1):
    job_data = []
    for page in range(num_pages):
        url = f"https://www.indeed.com/jobs?q={query}&l={location}&start={page*10}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        for job_card in soup.find_all("div", class_="job_seen_beacon"):
            title = job_card.find("h2").text.strip() if job_card.find("h2") else ""
            company = job_card.find("span", class_="companyName").text.strip() if job_card.find("span", class_="companyName") else ""
            location = job_card.find("div", class_="companyLocation").text.strip() if job_card.find("div", class_="companyLocation") else ""
            description = job_card.find("div", class_="job-snippet").text.strip() if job_card.find("div", class_="job-snippet") else ""

            job_data.append({
                "title": title,
                "company": company,
                "location": location,
                "description": description
            })
    return pd.DataFrame(job_data)

# Function to extract skills from job description
def extract_skills(description):
    found = []
    text = description.lower()
    for skill in skills_list:
        if skill in text:
            found.append(skill)
    return ", ".join(found) if found else "Not Mentioned"

# Streamlit UI
def run_streamlit_app():
    st.title("Job Scraper & Skill Analyzer")
    st.write("Scrapes Indeed and shows required skills for various roles")

    query = st.text_input("Job Title", "software engineer")
    location = st.text_input("Location", "India")
    num_pages = st.slider("Number of pages to scrape", 1, 5, 1)

    if st.button("Scrape Jobs"):
        with st.spinner("Scraping job data..."):
            df = scrape_indeed_jobs(query, location, num_pages)
            df["skills"] = df["description"].apply(extract_skills)
            st.success(f"Scraped {len(df)} jobs!")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "job_data.csv", "text/csv")

if __name__ == "__main__":
    run_streamlit_app()
