import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json
import re

# --- 1. PAGE CONFIG & UI ---
st.set_page_config(page_title="TagBuddy | Agentic Job Hunter", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus+Jakarta+Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a, #000000);
        color: #ffffff;
    }

    #MainMenu, footer, header {visibility: hidden;}

    /* CENTERED BRANDING */
    .brand-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 0;
        text-align: center;
    }
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(to right, #60a5fa, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .subtitle { color: #94a3b8; font-size: 1.1rem; margin-top: 10px; }

    /* GLASS CONTAINER */
    .main-container {
        background: rgba(255, 255, 255, 0.03);
        padding: 35px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        margin-bottom: 40px;
    }

    /* PROBABILITY BADGE */
    .prob-badge {
        padding: 6px 14px;
        border-radius: 50px;
        font-weight: 800;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 10px;
    }
    .match-high { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    .match-mid { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid #eab308; }
    .match-low { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }

    /* JOB CARDS */
    .job-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        transition: transform 0.2s;
        border-left: 6px solid #3b82f6;
    }
    .job-card:hover { transform: translateY(-5px); }
    .card-title { color: #0f172a; font-size: 20px; font-weight: 700; }
    .card-snippet { color: #475569; font-size: 14px; margin: 12px 0; line-height: 1.6; }
    
    /* INPUTS */
    .stSelectbox label, .stFileUploader label { color: #cbd5e1 !important; font-weight: 600; }
    
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white; border: none; padding: 12px 40px; border-radius: 12px;
        font-weight: 700; width: 100%; transition: 0.3s;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. API KEYS ---
gemini_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini Key", type="password")
serper_key = st.secrets.get("SERPER_API_KEY") or st.sidebar.text_input("Serper Key", type="password")

# --- 3. LOGIC FUNCTIONS ---
def get_pdf_text(file):
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return ""

def get_job_score(resume_text, job_title, job_snippet):
    """Calculates shortlisting probability using Gemini"""
    if not resume_text: return 50
    
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Analyze the following Job and Resume. 
    Job: {job_title} - {job_snippet}
    Resume: {resume_text[:2000]} 
    
    Based on skills, keywords, and experience, provide a shortlisting probability (0 to 100).
    Return ONLY the number.
    """
    try:
        response = model.generate_content(prompt)
        score = int(re.sub(r'\D', '', response.text.strip()))
        return min(max(score, 10), 99) # Keep between 10-99
    except:
        return 65

def get_search_queries(role, exp, type="standard"):
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if type == "standard":
        prompt = f"Generate 3 Google search queries for {role} jobs in India for {exp} experience. Use site:linkedin.com/jobs/view. Return JSON list."
    else:
        prompt = f"Generate 3 queries to find LinkedIn posts where HRs share email for {role} hiring. Return JSON list."
    
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except:
        return [f"{role} jobs India"]

# --- 4. UI START ---
st.markdown("""
    <div class="brand-container">
        <img src="https://cdn-icons-png.flaticon.com/512/11104/11104255.png" width="80">
        <h1 class="main-title">TagBuddy</h1>
        <p class="subtitle">Agentic Job Hunter & Resume Analyzer</p>
    </div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        role = st.selectbox("Target Role", ["Product Manager", "Strategy Consultant", "Data Scientist", "Business Analyst", "Operations Associate", "MBA Fresher", "Software Engineer"])
    with c2:
        exp = st.selectbox("Experience", ["0-1 Years", "1-3 Years", "3-5 Years", "5-8 Years", "8+ Years"])
    with c3:
        uploaded_file = st.file_uploader("Upload Resume (PDF) for Probability Analysis", type="pdf")
    
    search_btn = st.button("🚀 ACTIVATE AGENTS")
    st.markdown('</div>', unsafe_allow_html=True)

if search_btn:
    if not uploaded_file or not gemini_key or not serper_key:
        st.error("Missing Resume or API Keys.")
    else:
        resume_text = get_pdf_text(uploaded_file)
        
        with st.spinner("🤖 Analyzing Resume & Scanning Web..."):
            headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
            
            # Get Standard Job Links
            std_queries = get_search_queries(role, exp, "standard")
            std_results = []
            for q in std_queries:
                res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5, "tbs": "qdr:d2"})
                std_results.extend(res.json().get('organic', []))

            # Get Email Posts
            email_queries = get_search_queries(role, exp, "email")
            email_results = []
            for q in email_queries:
                res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5, "tbs": "qdr:d2"})
                email_results.extend(res.json().get('organic', []))

        # --- DISPLAY ---
        tab1, tab2 = st.tabs(["🔗 Scored Job Links", "📧 Contact HR Directly"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            seen = set()
            for job in std_results[:10]:
                if job['link'] not in seen:
                    seen.add(job['link'])
                    # AI MATCH ANALYSIS
                    score = get_job_score(resume_text, job['title'], job.get('snippet', ''))
                    status_class = "match-high" if score > 80 else "match-mid" if score > 50 else "match-low"
                    
                    st.markdown(f"""
                    <div class="job-card">
                        <div class="prob-badge {status_class}">Shortlisting Probability: {score}%</div>
                        <div class="card-title">{job['title']}</div>
                        <div style="color: #64748b; font-size: 12px; margin-top:4px;">📍 {job.get('source', 'Job Portal')}</div>
                        <div class="card-snippet">{job.get('snippet', '')}</div>
                        <div style="display:flex; gap:10px;">
                            <a href="{job['link']}" target="_blank" style="background:#3b82f6; color:white; padding:8px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">Apply Now</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(f"Share Link: {job['link']}", language="text")

        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            email_seen = set()
            for post in email_results:
                emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', post.get('snippet', ''))))
                if emails and post['link'] not in email_seen:
                    email_seen.add(post['link'])
                    email_chips = "".join([f'<span style="background:#ede9fe; color:#6d28d9; padding:4px 10px; border-radius:20px; margin-right:5px; font-weight:bold; font-size:12px;">✉️ {e}</span>' for e in emails])
                    
                    st.markdown(f"""
                    <div class="job-card" style="border-left-color: #8b5cf6;">
                        <div style="margin-bottom:15px;">{email_chips}</div>
                        <div class="card-title">{post['title']}</div>
                        <div class="card-snippet">{post.get('snippet', '')}</div>
                        <a href="{post['link']}" target="_blank" style="background:#8b5cf6; color:white; padding:8px 20px; border-radius:8px; text-decoration:none; font-weight:bold;">View LinkedIn Post</a>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; color:#475569; margin-top:50px; font-size:12px;'>TagBuddy Agentic Engine v2.0 • Data refreshed every 48 hours</div>", unsafe_allow_html=True)
