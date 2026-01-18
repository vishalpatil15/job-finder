
import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json
import re
import html
import urllib.parse

# --- 1. PAGE CONFIG & ULTRA-MODERN UI ---
st.set_page_config(page_title="TagBuddy: AI Job Architect", page_icon="🏷️", layout="wide")

st.markdown("""
    <style>
    /* DATA-DRIVEN DARK BACKGROUND */
    .stApp {
        background: linear-gradient(rgba(10, 15, 30, 0.9), rgba(10, 15, 30, 0.95)),
                    url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* HIDE BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* CENTERED HEADER */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 2rem;
        margin-bottom: 2rem;
    }
    
    /* TAG LOGO ANIMATION */
    @keyframes tagPulse {
        0%, 100% { transform: scale(1) rotate(0deg); }
        25% { transform: scale(1.1) rotate(-5deg); }
        75% { transform: scale(1.1) rotate(5deg); }
    }
    
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 30px rgba(59, 130, 246, 0.4); }
        50% { box-shadow: 0 0 60px rgba(147, 51, 234, 0.8), 0 0 100px rgba(59, 130, 246, 0.6); }
    }
    
    .tag-logo-container {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
        animation: glowPulse 2.5s infinite ease-in-out;
        border: 3px solid rgba(255,255,255,0.2);
        position: relative;
    }
    
    .tag-icon {
        font-size: 70px;
        animation: tagPulse 3s infinite ease-in-out;
        filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3));
    }

    /* TYPOGRAPHY */
    h1 { 
        color: #ffffff !important; 
        font-weight: 800 !important;
        font-size: 3.5rem !important;
        letter-spacing: -2px;
        margin: 0 !important;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(147, 51, 234, 0.5);
    }
    p.subtitle { 
        color: #94a3b8 !important; 
        font-size: 1.2rem !important; 
        text-align: center;
        font-weight: 300;
        max-width: 600px;
        margin-top: 5px !important;
        margin-bottom: 25px !important;
    }

    /* ROTATING LOGO CAROUSEL */
    .logo-carousel {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 80px;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    
    @keyframes fadeInOut {
        0%, 100% { opacity: 0; transform: scale(0.8); }
        10%, 90% { opacity: 1; transform: scale(1); }
    }
    
    .carousel-logo {
        position: absolute;
        width: 120px;
        height: auto;
        opacity: 0;
        animation: fadeInOut 4s infinite;
    }
    
    .carousel-logo:nth-child(1) { animation-delay: 0s; }
    .carousel-logo:nth-child(2) { animation-delay: 1s; }
    .carousel-logo:nth-child(3) { animation-delay: 2s; }
    .carousel-logo:nth-child(4) { animation-delay: 3s; }

    /* SEARCH CONTAINER */
    .search-container {
        background: rgba(30, 41, 59, 0.6);
        padding: 35px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-bottom: 40px;
    }

    .stSelectbox label, .stFileUploader label {
        color: #e2e8f0 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    /* BUTTON */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        padding: 18px 50px;
        border-radius: 50px;
        border: none;
        font-size: 1.15rem;
        width: 100%;
        box-shadow: 0 15px 35px -5px rgba(118, 75, 162, 0.5);
        transition: all 0.3s;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 40px -5px rgba(118, 75, 162, 0.7);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    /* ENHANCED JOB CARDS */
    .job-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(249, 250, 251, 0.98) 100%);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        position: relative;
        border: 2px solid transparent;
        transition: all 0.3s;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    
    .job-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .job-card:hover { 
        transform: translateY(-5px) scale(1.01); 
        box-shadow: 0 25px 50px -12px rgba(102, 126, 234, 0.25);
        border-color: rgba(102, 126, 234, 0.3);
    }

    .match-badge {
        position: absolute;
        top: 24px;
        right: 24px;
        padding: 8px 18px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 15px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        z-index: 10;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .high-match { 
        background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%); 
        color: #065f46; 
        border: 2px solid #10b981; 
    }
    .med-match { 
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); 
        color: #92400e; 
        border: 2px solid #f59e0b; 
    }
    .low-match { 
        background: linear-gradient(135deg, #fab1a0 0%, #ff7675 100%); 
        color: #7f1d1d; 
        border: 2px solid #ef4444; 
    }

    .job-title { 
        color: #0f172a; 
        font-size: 22px; 
        font-weight: 800; 
        margin-bottom: 10px; 
        padding-right: 120px; 
        line-height: 1.3;
    }
    .job-source { 
        color: #64748b; 
        font-size: 13px; 
        font-weight: 700; 
        text-transform: uppercase; 
        margin-bottom: 15px; 
        letter-spacing: 1px;
    }
    .job-snippet { 
        color: #475569; 
        font-size: 14.5px; 
        line-height: 1.7; 
        margin-bottom: 20px; 
    }

    /* ENHANCED ACTION AREA */
    .action-row {
        display: flex;
        gap: 12px;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 2px solid #e2e8f0;
    }

    a.apply-link {
        flex: 1;
        display: block;
        text-align: center;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white !important;
        text-decoration: none;
        padding: 14px 28px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 14px;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    a.apply-link:hover { 
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.4);
    }
    
    .share-box-container {
        flex: 2;
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border: 2px solid #cbd5e1;
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 12px;
        color: #64748b;
    }
    .share-label { 
        font-weight: 800; 
        margin-right: 10px; 
        color: #334155; 
        white-space: nowrap; 
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .share-url { 
        font-family: 'Courier New', monospace; 
        word-break: break-all; 
        user-select: all;
        color: #3b82f6;
        font-weight: 600;
        font-size: 11px;
    }

    /* EMAIL CARDS */
    .email-card {
        background: linear-gradient(135deg, rgba(237, 233, 254, 0.95) 0%, rgba(221, 214, 254, 0.95) 100%);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        border-left: 6px solid #8b5cf6;
        box-shadow: 0 10px 30px -5px rgba(139, 92, 246, 0.2);
        transition: all 0.3s;
    }
    .email-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px -10px rgba(139, 92, 246, 0.3);
    }
    
    .email-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 15px 0;
    }
    
    .email-chip {
        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
        box-shadow: 0 3px 10px rgba(139, 92, 246, 0.3);
        letter-spacing: 0.3px;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] { 
        justify-content: center; 
        gap: 15px; 
        margin-bottom: 40px; 
        background: rgba(30, 41, 59, 0.3);
        padding: 10px;
        border-radius: 50px;
        backdrop-filter: blur(10px);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #94a3b8;
        border-radius: 50px;
        padding: 12px 35px;
        height: auto;
        border: 2px solid transparent;
        font-weight: 700;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: rgba(255,255,255,0.3);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stAlert { 
        border-radius: 16px; 
        border: 2px solid rgba(59, 130, 246, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* STATS BANNER */
    .stats-banner {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 30px;
        text-align: center;
        border: 2px solid rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .stats-text {
        color: #e2e8f0;
        font-size: 18px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .stats-number {
        color: #a78bfa;
        font-size: 32px;
        font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECRETS ---
gemini_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini Key", type="password")
serper_key = st.secrets.get("SERPER_API_KEY") or st.sidebar.text_input("Serper Key", type="password")

# --- 3. CORE LOGIC ---
def get_pdf_text(file):
    reader = PdfReader(file)
    return " ".join([p.extract_text() for p in reader.pages])

def extract_emails(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return list(set(re.findall(email_pattern, text)))

# --- AGENT 1: SEARCH QUERY GENERATOR ---
def get_search_queries(role, exp, industry, api_key, query_type="standard"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    if query_type == "standard":
        prompt = f"""
        Generate 3 Google search queries for formal job posts.
        Role: {role}, Experience: {exp}, Industry: {industry}, Location: India.
        Rules: Use 'site:linkedin.com/jobs/view' or 'site:naukri.com/job-listings'. Include industry keywords.
        Return ONLY JSON list of strings.
        """
    else:
        prompt = f"""
        Generate 3 Google search queries for recent LinkedIn posts where HRs ask for resumes.
        Role: {role}, Industry: {industry}. Keywords: "send resume to", "hiring now", "@gmail.com", "DM for details".
        Return ONLY JSON list of strings.
        """
        
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:]
        if text.endswith('```'): text = text[:-3]
        return json.loads(text)
    except:
        return [f"site:linkedin.com/jobs/view {role} {industry}"] if query_type=="standard" else [f'site:linkedin.com/posts "{role}" "{industry}" "send resume"']

# --- AGENT 2: AI RECRUITER (MATCH SCORING) ---
def analyze_match_batch(resume_text, jobs_list, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    jobs_summary = []
    for i, job in enumerate(jobs_list):
        jobs_summary.append({
            "id": i,
            "title": job.get('title', ''),
            "snippet": job.get('snippet', '')[:200]
        })
    
    prompt = f"""
    Act as a Senior Recruiter. Compare this Resume Summary against the Job Descriptions.
    RESUME SUMMARY: {resume_text[:2000]}
    JOB LIST: {json.dumps(jobs_summary)}
    TASK: Calculate "Shortlist Probability" (0-100%) for each job based on skills match, experience, and role fit.
    OUTPUT FORMAT: JSON dictionary {{ "0": 85, "1": 40 }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:]
        if text.endswith('```'): text = text[:-3]
        match_scores = json.loads(text)
        return match_scores
    except:
        return {} 

# --- 4. MAIN LAYOUT ---

# CENTERED HEADER WITH TAG LOGO
st.markdown("""
    <div class="header-container">
        <div class="tag-logo-container">
            <div class="tag-icon">🏷️</div>
        </div>
        <h1>TagBuddy</h1>
        <p class="subtitle">AI-Powered Job Intelligence • Resume Analysis • Direct Matches</p>
    </div>
""", unsafe_allow_html=True)

# ROTATING LOGO CAROUSEL
st.markdown("""
    <div class="logo-carousel">
        <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" class="carousel-logo" alt="LinkedIn">
        <img src="https://static.naukimg.com/s/0/0/i/new-homepage/android-app-icon.png" class="carousel-logo" alt="Naukri">
        <img src="https://www.monster.com/favicon.ico" class="carousel-logo" alt="Monster" style="width: 100px;">
        <img src="https://www.indeed.com/images/indeed-logo.svg" class="carousel-logo" alt="Indeed" style="width: 100px;">
    </div>
""", unsafe_allow_html=True)

# SEARCH CONTAINER
with st.container():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    # First Row: Role and Experience
    c1, c2 = st.columns(2)
    
    with c1:
        role = st.selectbox("🎯 Target Role", [
            "Corporate Strategy", "Product Manager", "Strategy Consultant", 
            "Management Trainee", "Operations Associate", "Planning Associate",
            "Area Sales Manager", "SAP Functional Consultant", "SAP Technical Consultant",
            "Business Analyst", "Data Scientist", "MBA Freshers", "BTech Freshers",
            "Software Engineer", "Marketing Manager", "HR Manager"
        ])
    
    with c2:
        exp = st.selectbox("📊 Experience Level", [
            "0-1 Years", "1-3 Years", "3-5 Years", "5-8 Years", "8+ Years"
        ])
    
    # Second Row: Industry and Resume Upload
    c3, c4 = st.columns(2)
    
    with c3:
        industry = st.selectbox("🏭 Industry Preference", [
            "Any Industry",
            "FMCG (Fast-Moving Consumer Goods)",
            "Manufacturing & Engineering",
            "Startups & Tech",
            "Automotive",
            "Information Technology",
            "Telecommunications",
            "Banking & Finance",
            "Consulting",
            "Healthcare & Pharma",
            "E-commerce & Retail",
            "Real Estate",
            "Education & EdTech"
        ])
    
    with c4:
        st.markdown('<label style="color:#e2e8f0; font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">📄 UPLOAD RESUME (PDF) <span style="color:#ef4444">*</span></label>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

    if st.button("🚀 Find Matching Jobs"):
        if not uploaded_file or not gemini_key or not serper_key:
            st.error("⚠️ System Halted: Missing API Keys or Resume.")
        else:
            with st.spinner("🔄 Analyzing Resume & Searching Global Job Platforms..."):
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                resume_text = get_pdf_text(uploaded_file)
                
                # 1. SEARCH FOR JOBS
                std_queries = get_search_queries(role, exp, industry, gemini_key, "standard")
                std_raw_results = []
                for q in std_queries:
                    try:
                        res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5})
                        if res.status_code == 200:
                            std_raw_results.extend(res.json().get('organic', []))
                    except: pass
                
                # Filter Top 10 Unique
                seen_links = set()
                top_jobs = []
                for job in std_raw_results:
