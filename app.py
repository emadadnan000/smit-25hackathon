import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter

def clean_and_standardize(df, source):
    # Standardize column names
    rename_map = {
        'title': 'job_title',
        'company': 'company_name',
        'date posted': 'scrapped_date',
        'date_posted': 'scrapped_date'
    }
    df = df.rename(columns=rename_map)
    # Ensure all columns exist
    for col in ['job_title', 'company_name', 'location', 'skills', 'scrapped_date']:
        if col not in df.columns:
            df[col] = None
    # Standardize date format
    df['scrapped_date'] = pd.to_datetime(df['scrapped_date'], errors='coerce').dt.date
    # Fill missing values
    df = df.fillna('')
    # Add source column
    df['source'] = source
    return df

# Clean and load data from original files
df_linkedin = pd.read_csv('cleaned_linkedin_jobs.csv')
df_indeed = pd.read_csv('cleaned_indeed_jobs.csv')

df_linkedin = clean_and_standardize(df_linkedin, 'LinkedIn')
df_indeed = clean_and_standardize(df_indeed, 'Indeed')

# Save cleaned data to new files
df_linkedin.to_csv('cleaned_linkedin_jobs.csv', index=False)
df_indeed.to_csv('cleaned_indeed_jobs.csv', index=False)

# Load cleaned data
df_linkedin_clean = pd.read_csv('cleaned_linkedin_jobs.csv')
df_indeed_clean = pd.read_csv('cleaned_indeed_jobs.csv')

# Combine cleaned data
df_combined = pd.concat([df_linkedin_clean, df_indeed_clean], ignore_index=True)
df = df_combined.copy()
df['scrapped_date'] = pd.to_datetime(df['scrapped_date'], errors='coerce')

st.title("📊 Real-Time Job Trend Analyzer")

# --- Top 5 Job Titles ---
st.subheader("💼 Top 5 Job Titles")
top_titles = df['job_title'].value_counts().head(5)
st.bar_chart(top_titles)

# --- Top 5 Hiring Cities ---
st.subheader("📍 Top Hiring Cities")
top_cities = df['location'].value_counts().head(5)
st.bar_chart(top_cities)

# --- Most Common Skills ---
st.subheader("🛠️ Most In-Demand Skills")
skill_keywords = ['Python', 'Java', 'SQL', 'Excel', 'AWS', 'JavaScript', 'C++', 'Power BI', 'Pandas', 'NumPy']
skill_counter = Counter()

for skills_text in df['skills'].dropna():
    for skill in skill_keywords:
        if skill.lower() in skills_text.lower():
            skill_counter[skill] += 1

skills_df = pd.DataFrame(skill_counter.items(), columns=['Skill', 'Count']).sort_values(by='Count', ascending=False)

fig_skills = px.bar(skills_df, x='Skill', y='Count', title="Top Skills in Demand")
st.plotly_chart(fig_skills)

# --- Posting Trends Over Time ---
st.subheader("📈 Job Postings Over Time")
timeline = df['scrapped_date'].value_counts().sort_index()
timeline_df = timeline.reset_index()
timeline_df.columns = ['Date', 'Postings']
fig_timeline = px.line(timeline_df, x='Date', y='Postings', title="Job Postings Trend")
st.plotly_chart(fig_timeline)