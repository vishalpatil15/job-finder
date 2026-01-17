import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG & MODERN UI ---
st.set_page_config(page_title="CareerFlow AI | Job Matcher", page_icon="💼", layout="wide")

# Custom CSS for Glassmorphism UI and Background
st.markdown("""
    <style>
    /* Professional Background Image */
    .stApp {
        background: url('https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=2000');
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Glassmorphism Card Style */
    .main-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 30px;
        color: white;
    }
    
    .job-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 6px solid #0077b5; /* LinkedIn Blue */
        color: #1a1a1a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .apply-btn {
        background-color: #0077b5;
        color: white !important;
        padding: 10px 25px;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        font-weight: 600;
        margin-top: 10px;
    }
    
    h1, h2, h3, p { color: white !important; }
    label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR / SECRETS ---
gemini_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini Key", type="password")
serper_key = st.secrets.get("SERPER_API_KEY") or st.sidebar.text_input("Serper Key", type="password")

# --- 3. HELPER FUNCTIONS ---
def get_pdf_text(file):
    reader = PdfReader(file)
    return "".join([p.extract_text() for p in reader.pages])

def get_precise_jobs(resume_text, role, exp, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    User Resume: {resume_text[:3000]}
    Target Role: {role}
    Experience Level: {exp}
    
    Task: Based on the resume and the target role/experience, generate 4 specific Google Search queries.
    Focus on specific individual job posts on LinkedIn, Naukri, and IIMJobs in India (Pune/Bangalore).
    Queries should look like: 'site:linkedin.com/jobs "Corporate Strategy" Pune'
    Return ONLY a JSON list of 4 strings.
    """
    response = model.generate_content(prompt)
    return json.loads(response.text.strip().replace('```json', '').replace('```', ''))

# --- 4. MAIN UI LAYOUT ---
st.title("💼 CareerFlow AI")
st.subheader("Your Personalized Strategy & Tech Job Concierge")

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        selected_role = st.selectbox("Target Role", 
            ["Strategy Consultant", "Corporate Strategy Analyst", "Product Manager", 
             "Data Engineer", "Cloud Engineer", "Software Developer", "Business Analyst"])
    with col2:
        work_ex = st.selectbox("Work Experience", 
            ["0-1 Years", "1-2 Years", "2-3 Years", "3-5 Years", "5-10 Years", "10+ Years"])
    
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
    
    if st.button("🚀 Find My Top 10 Opportunities"):
        if not uploaded_file or not gemini_key or not serper_key:
            st.error("Please provide keys and upload your resume.")
        else:
            with st.spinner("Analyzing profile and scanning platforms..."):
                text = get_pdf_text(uploaded_file)
                queries = get_precise_jobs(text, selected_role, work_ex, gemini_key)
                
                all_raw_jobs = []
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                for q in queries:
                    res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5})
                    all_raw_jobs.extend(res.json().get('organic', []))

                # Filtering Logic for "Top 10" and unique links
                unique_links = set()
                top_10 = []
                for job in all_raw_jobs:
                    if job['link'] not in unique_links and len(top_10) < 10:
                        unique_links.add(job['link'])
                        top_10.append(job)
                
                st.markdown("## ✨ Recommended for You")
                for job in top_10:
                    st.markdown(f"""
                        <div class="job-card">
                            <h3 style='color:#1a1a1a !important;'>{job['title']}</h3>
                            <p style='color:#444 !important;'>{job.get('snippet', 'No description available...')[:250]}...</p>
                            <a class="apply-btn" href="{job['link']}" target="_blank">Direct Apply</a>
                        </div>
                    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
