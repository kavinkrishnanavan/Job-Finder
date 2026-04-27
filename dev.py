import streamlit as st
import http.client
import urllib.parse
import json

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Job Search Engine",
    page_icon="💼",
    layout="wide"
)

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div style='text-align:center;'>
        <h1>Job Search Engine</h1>
        <p>Made By Kavin</p>
        <hr>
    </div>
    """,
    unsafe_allow_html=True
)



# -----------------------------
# Session State Init
# -----------------------------
if "jobs" not in st.session_state:
    st.session_state.jobs = []
if "page" not in st.session_state:
    st.session_state.page = 1
if "query" not in st.session_state:
    st.session_state.query = ""
if "country" not in st.session_state:
    st.session_state.country = "us"
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# -----------------------------
# Sidebar Inputs
# -----------------------------
with st.sidebar:
    st.header("Search Filters")

    search_query = st.text_input("Job Title / Keyword", "developer")
    country = st.text_input("Country Code (e.g. us, in, my)", "us")
    api_key = st.secrets['API']

    search_btn = st.button("Search Jobs")

# -----------------------------
# API Function
# -----------------------------
def fetch_jobs(query, country, page, api_key):
    conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": query,
        "page": str(page),
        "num_pages": "1",
        "country": country,
        "date_posted": "all"
    }

    query_string = urllib.parse.urlencode(params)

    conn.request("GET", f"/search?{query_string}", headers=headers)

    res = conn.getresponse()
    data = res.read()

    return json.loads(data.decode("utf-8"))

# -----------------------------
# Search Action
# -----------------------------
if search_btn:
    if not api_key:
        st.error("Please enter your RapidAPI key.")
    else:
        st.session_state.jobs = []
        st.session_state.page = 1
        st.session_state.query = search_query
        st.session_state.country = country
        st.session_state.api_key = api_key

        with st.spinner("Fetching jobs..."):
            response = fetch_jobs(search_query, country, 1, api_key)
            st.session_state.jobs = response.get("data", [])
            st.session_state.page = 2

# -----------------------------
# Load More Action
# -----------------------------
if st.session_state.api_key and st.session_state.query:
    if st.button("Load More Jobs"):
        with st.spinner("Loading more jobs..."):
            response = fetch_jobs(
                st.session_state.query,
                st.session_state.country,
                st.session_state.page,
                st.session_state.api_key
            )

            new_jobs = response.get("data", [])

            if new_jobs:
                st.session_state.jobs.extend(new_jobs)
                st.session_state.page += 1
            else:
                st.info("No more jobs found.")

            st.rerun()

# -----------------------------
# Results Section
# -----------------------------
if st.session_state.jobs:
    st.success(f"Showing {len(st.session_state.jobs)} jobs")

    for job in st.session_state.jobs:
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {job.get('job_title', 'N/A')}")
                st.markdown(f"**Company:** {job.get('employer_name', 'N/A')}")
                st.markdown(f"**Location:** {job.get('job_city', 'N/A')}, {job.get('job_country', '')}")
                
                desc = job.get("job_description", "")
                if desc:
                    st.markdown("**Description:**")
                    st.markdown(desc)

            with col2:
                apply_link = job.get("job_apply_link", "")
                if apply_link:
                    st.markdown(f"[Apply Now]({apply_link})")

            st.markdown("---")

# -----------------------------
# Footer
# -----------------------------
