import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG & CUSTOM STYLING ---
st.set_page_config(page_title="Vishal's Career Dashboard", layout="wide")

# Custom CSS for the "Actual Webpage" look
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .job-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #2e7d32;
        transition: transform 0.2s;
    }
    .job-card:hover {
        transform: scale(1.01);
    }
    .apply-btn {
        background-color: #2e7d32;
        color: white !important;
        padding: 8px 20px;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💼 Strategy & Product Matcher")
st.markdown("Finding the top 10 opportunities for your profile...")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("🔑 API Access")
    gemini_key = st.text_input("Gemini API Key", type="password")
    serper_key = st.text_input("Serper API Key", type="password")

# --- 3. LOGIC FUNCTIONS ---
def get_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "".join([page.extract_text() for page in reader.pages])

def get_smart_queries(resume_text, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Resume: {resume_text[:3000]}. Based on this, give me 3 optimized Google search strings to find high-level Strategy or Product jobs in Pune/Bangalore on LinkedIn or Naukri. Return ONLY a JSON list."
    response = model.generate_content(prompt)
    return json.loads(response.text.strip().replace('```json', '').replace('```', ''))

# --- 4. MAIN UI ---
uploaded_file = st.file_uploader("Drop your resume here", type="pdf")

if uploaded_file and gemini_key and serper_key:
    if st.button("Generate My Top 10"):
        with st.spinner("Scraping platforms for matches..."):
            resume_text = get_pdf_text(uploaded_file)
            queries = get_smart_queries(resume_text, gemini_key)
            
            all_jobs = []
            headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
            
            # Fetch results from all queries
            for q in queries:
                res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5})
                all_jobs.extend(res.json().get('organic', []))
            
            # 5. DISPLAY TOP 10 ONLY
            top_10 = all_jobs[:10]
            
            if not top_10:
                st.warning("No fresh openings found. Try refining your resume keywords.")
            else:
                for job in top_10:
                    st.markdown(f"""
                        <div class="job-card">
                            <h3 style='margin-top:0;'>{job['title']}</h3>
                            <p style='color: #666;'>{job.get('snippet', 'Check link for description...')[:200]}...</p>
                            <p><b>Source:</b> {job.get('link', '').split('/')[2]}</p>
                            <a class="apply-btn" href="{job['link']}" target="_blank">View & Apply Now</a>
                        </div>
                    """, unsafe_allow_html=True)
