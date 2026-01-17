import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG & HIGH-CONTRAST UI ---
st.set_page_config(page_title="TagBuddy| Your Best Job Matcher", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    /* Professional Background */
    .stApp {
        background: url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* Hide Default Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main Glassmorphism Container */
    .main-container {
        background: rgba(0, 0, 0, 0.6);
        padding: 40px;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* CLEAN WHITE JOB CARDS WITH BLACK TEXT */
    .job-card {
        background-color: #ffffff !important;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 8px solid #0077b5;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    .job-title { color: #1a1a1a !important; font-size: 22px !important; font-weight: 800 !important; margin-bottom: 5px !important; }
    .job-company { color: #0077b5 !important; font-weight: 700 !important; font-size: 18px !important; }
    .job-meta { color: #333333 !important; font-size: 15px !important; margin-top: 5px !important; line-height: 1.4; }
    
    .apply-btn {
        background-color: #0077b5;
        color: white !important;
        padding: 12px 30px;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
        margin-top: 15px;
        border: none;
    }
    .apply-btn:hover { background-color: #005fa3; }

    /* Input Labels */
    label { color: white !important; font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECRETS ---
gemini_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini Key", type="password")
serper_key = st.secrets.get("SERPER_API_KEY") or st.sidebar.text_input("Serper Key", type="password")

# --- 3. CORE LOGIC ---
def get_pdf_text(file):
    reader = PdfReader(file)
    return " ".join([p.extract_text() for p in reader.pages])

def get_job_queries(resume_text, role, exp, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Resume: {resume_text[:2000]}. Role: {role}. Experience: {exp}. Create 2 short search queries for INDIVIDUAL job posts in India. Example: 'Management Trainee Strategy Pune'. Return JSON list."
    response = model.generate_content(prompt)
    return json.loads(response.text.strip().replace('```json', '').replace('```', ''))

# --- 4. UI ---
st.title("🎯 CareerFlow: Precision Job Matcher")
st.markdown("<p style='color:white; font-size:18px;'>Direct application links for individual roles.</p>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        role = st.selectbox("What role are you targeting?", ["Corporate Strategy Analyst", "Product Manager", "Strategy Consultant", "Data Engineer", "Cloud Engineer"])
    with c2:
        exp = st.selectbox("Experience Level", ["0-1 Years", "1-2 Years", "2-3 Years", "3-5 Years", "5-10 Years", "10+ Years"])
    
    resume = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    if st.button("🔍 Find Specific Openings"):
        if not resume or not gemini_key or not serper_key:
            st.warning("Ensure keys are in Secrets and Resume is uploaded.")
        else:
            with st.spinner("Directly mapping jobs from Google for Jobs..."):
                text = get_pdf_text(resume)
                queries = get_job_queries(text, role, exp, gemini_key)
                
                final_jobs = []
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                
                # USE SERPER GOOGLE JOBS ENDPOINT
                for q in queries:
                    # Pointing specifically to the jobs engine
                    res = requests.post("https://google.serper.dev/jobs", headers=headers, json={"q": q, "location": "India"})
                    data = res.json().get('jobs', [])
                    final_jobs.extend(data)

                # SHOW TOP 10 INDIVIDUAL JOBS
                top_10 = final_jobs[:10]
                
                if not top_10:
                    st.info("No individual posts found. Try a broader role title.")
                else:
                    st.markdown("<h2 style='color:white;'>✨ Top 10 Individual Matches</h2>", unsafe_allow_html=True)
                    for job in top_10:
                        st.markdown(f"""
                            <div class="job-card">
                                <div class="job-title">{job.get('title', 'Job Opening')}</div>
                                <div class="job-company">🏢 {job.get('company', 'Company')} | 📍 {job.get('location', 'India')}</div>
                                <div class="job-meta">
                                    {job.get('snippet', 'Click apply to view full details and requirements on the company portal.')[:300]}
                                </div>
                                <a class="apply-btn" href="{job.get('applyLink') or job.get('link')}" target="_blank">View & Apply Directly</a>
                            </div>
                        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
