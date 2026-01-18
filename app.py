import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json
import re
import html
import urllib.parse

# --- 1. PAGE CONFIG & ULTRA-MODERN UI ---
st.set_page_config(page_title="TagBuddy: AI Job Architect", page_icon="🧬", layout="wide")

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
    
    /* DYNAMIC LAMP LOGO STYLING */
    .lamp-container {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.2) 0%, rgba(0,0,0,0) 70%);
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
    .lamp-img {
        width: 120px;
        height: auto;
        filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.6));
    }

    /* TYPOGRAPHY */
    h1 { 
        color: #ffffff !important; 
        font-weight: 800 !important;
        font-size: 3.5rem !important;
        letter-spacing: -2px;
        margin: 0 !important;
        text-align: center;
        background: -webkit-linear-gradient(#eee, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    p.subtitle { 
        color: #94a3b8 !important; 
        font-size: 1.2rem !important; 
        text-align: center;
        font-weight: 300;
        max-width: 600px;
        margin-top: 5px !important;
    }

    /* SEARCH CONTAINER */
    .search-container {
        background: rgba(30, 41, 59, 0.4);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-bottom: 40px;
    }

    .stSelectbox label, .stFileUploader label {
        color: #e2e8f0 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* BUTTON */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 700;
        padding: 16px 40px;
        border-radius: 50px;
        border: none;
        font-size: 1.1rem;
        width: 100%;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.4);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 30px -5px rgba(37, 99, 235, 0.6);
    }

    /* JOB CARDS */
    .job-card {
        background: rgba(255, 255, 255, 0.96);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.2s;
        overflow: hidden; /* Ensures content stays inside */
    }
    .job-card:hover { transform: translateY(-3px); }

    .match-badge {
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 6px 14px;
        border-radius: 30px;
        font-weight: 800;
        font-size: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        z-index: 10;
    }
    .high-match { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .med-match { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
    .low-match { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

    .job-title { color: #0f172a; font-size: 20px; font-weight: 700; margin-bottom: 6px; padding-right: 100px; }
    .job-source { color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 12px; }
    .job-snippet { color: #334155; font-size: 14px; line-height: 1.6; margin-bottom: 20px; }

    /* LINKS */
    a.apply-link {
        display: inline-block;
        background: #0f172a;
        color: white !important;
        text-decoration: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        transition: background 0.2s;
        border: none;
    }
    a.apply-link:hover { background: #334155; color: white !important; }
    
    .share-box {
        background: #f1f5f9;
        padding: 10px;
        border-radius: 8px;
        border: 1px dashed #cbd5e1;
        margin-top: 15px;
        font-family: monospace;
        font-size: 12px;
        color: #475569;
        word-break: break-all;
        user-select: all; /* Makes it easy to select */
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 20px; margin-bottom: 40px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.05);
        color: #94a3b8;
        border-radius: 50px;
        padding: 10px 30px;
        height: auto;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
        border-color: #3b82f6;
    }
    
    .stAlert { border-radius: 12px; }
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
def get_search_queries(role, exp, api_key, query_type="standard"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    if query_type == "standard":
        prompt = f"""
        Generate 3 Google search queries for formal job posts.
        Role: {role}, Experience: {exp}, Location: India.
        Rules: Use 'site:linkedin.com/jobs/view' or 'site:naukri.com/job-listings'.
        Return ONLY JSON list of strings.
        """
    else:
        prompt = f"""
        Generate 3 Google search queries for recent LinkedIn posts where HRs ask for resumes.
        Role: {role}. Keywords: "send resume to", "hiring now", "@gmail.com".
        Return ONLY JSON list of strings.
        """
        
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    except:
        return [f"site:linkedin.com/jobs/view {role}"] if query_type=="standard" else [f'site:linkedin.com/posts "{role}" "send resume"']

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
    TASK: Calculate "Shortlist Probability" (0-100%) for each job.
    OUTPUT FORMAT: JSON dictionary {{ "0": 85, "1": 40 }}
    """
    
    try:
        response = model.generate_content(prompt)
        match_scores = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
        return match_scores
    except:
        return {} 

# --- 4. MAIN LAYOUT ---

# CENTERED HEADER WITH DYNAMIC LAMP LOGO
st.markdown("""
    <div class="header-container">
        <div class="lamp-container">
            <img src="https://media.tenor.com/J3iM0i_W8QoAAAAi/lamp-light.gif" class="lamp-img">
        </div>
        <h1>TagBuddy</h1>
        <p class="subtitle">Agentic Job Intelligence. Resume Analysis. Direct Matches.</p>
    </div>
""", unsafe_allow_html=True)

# SEARCH CONTAINER
with st.container():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.5, 1.5, 2])
    
    with c1:
        role = st.selectbox("Target Role", [
            "Corporate Strategy", "Product Manager", "Strategy Consultant", 
            "Management Trainee", "Operations Associate", "Planning Associate",
            "Area Sales Manager", "SAP Functional Consultant", "SAP Technical Consultant",
            "Business Analyst", "Data Scientist", "MBA Freshers", "BTech Freshers"
        ])
    with c2:
        exp = st.selectbox("Experience", ["0-1 Years", "1-3 Years", "3-5 Years", "5-8 Years", "8+ Years"])
    with c3:
        st.markdown('<label style="color:#e2e8f0; font-size:0.9rem; font-weight:600;">UPLOAD RESUME (PDF) <span style="color:#ef4444">*</span></label>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")

    if st.button("🚀 Run Analysis & Find Jobs"):
        if not uploaded_file or not gemini_key or not serper_key:
            st.error("⚠️ System Halted: Missing API Keys or Resume.")
        else:
            with st.spinner("🔄 Reading Resume & Deploying Search Agents..."):
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                resume_text = get_pdf_text(uploaded_file)
                
                # 1. SEARCH FOR JOBS
                std_queries = get_search_queries(role, exp, gemini_key, "standard")
                std_raw_results = []
                for q in std_queries:
                    res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5})
                    std_raw_results.extend(res.json().get('organic', []))
                
                # Filter Top 10 Unique
                seen_links = set()
                top_jobs = []
                for job in std_raw_results:
                    if job['link'] not in seen_links and len(top_jobs) < 10:
                        seen_links.add(job['link'])
                        top_jobs.append(job)
                
                # 2. EMAIL SEARCH (Freshness Filter)
                email_queries = get_search_queries(role, exp, gemini_key, "email")
                email_raw_results = []
                for q in email_queries:
                    # Time filter qdr:h48 (last 48 hours)
                    res = requests.post("https://google.serper.dev/search?tbs=qdr:h48", headers=headers, json={"q": q, "num": 5})
                    email_raw_results.extend(res.json().get('organic', []))

            # 3. AI RECRUITER AGENT: CALCULATE MATCH SCORES
            if top_jobs:
                with st.spinner("🧠 AI Recruiter is calculating your shortlist probability..."):
                    match_scores = analyze_match_batch(resume_text, top_jobs, gemini_key)
            else:
                match_scores = {}

            st.markdown('</div>', unsafe_allow_html=True) # Close Search Container

            # --- DISPLAY RESULTS ---
            tab1, tab2 = st.tabs(["🎯 Top Matches (Scored)", "📨 Fresh HR Emails"])
            
            # TAB 1: SCORED JOBS
            with tab1:
                if not top_jobs:
                    st.info("No jobs found matching criteria.")
                
                for i, job in enumerate(top_jobs):
                    score = match_scores.get(str(i), match_scores.get(i, 50))
                    
                    badge_class = "med-match"
                    if score >= 80: badge_class = "high-match"
                    elif score < 50: badge_class = "low-match"

                    # --- KEY FIX: SANITIZE EVERYTHING ---
                    # We use html.escape to make sure no weird characters break the UI
                    clean_title = html.escape(job.get('title', 'Job Role'))
                    clean_snippet = html.escape(job.get('snippet', ''))
                    clean_source = html.escape(job.get('source', 'Job Portal'))
                    
                    # Safe URL encoding
                    raw_link = job['link']
                    
                    # We render the card HTML carefully
                    st.markdown(f"""
                    <div class="job-card">
                        <div class="match-badge {badge_class}">⚡ {score}% Match</div>
                        <div class="job-title">{clean_title}</div>
                        <div class="job-source">📍 {clean_source}</div>
                        <div class="job-snippet">{clean_snippet}</div>
                        
                        <div style="margin-top:20px;">
                            <a href="{raw_link}" target="_blank" class="apply-link">Apply Now ➜</a>
                        </div>
                        <div class="share-box">🔗 {raw_link}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # TAB 2: HR EMAILS
            with tab2:
                email_count = 0
                seen_emails = set()
                for post in email_raw_results:
                    found_emails = extract_emails(post.get('snippet', ''))
                    if found_emails and post['link'] not in seen_emails:
                        seen_emails.add(post['link'])
                        
                        clean_title = html.escape(post.get('title', 'Social Post'))
                        clean_snippet = html.escape(post.get('snippet', ''))
                        raw_link = post['link']
                        
                        email_chips = "".join([f"<span style='background:#ede9fe; color:#6d28d9; padding:4px 8px; border-radius:4px; margin-right:5px; font-weight:bold;'>✉️ {e}</span>" for e in found_emails])
                        
                        st.markdown(f"""
                        <div class="job-card" style="border-left: 5px solid #8b5cf6;">
                            <div class="job-title">{clean_title}</div>
                            <div class="job-source">🔗 Social Post (Last 48 Hours)</div>
                            <div style="margin-bottom:15px;">{email_chips}</div>
                            <div class="job-snippet">{clean_snippet}</div>
                            <a href="{raw_link}" target="_blank" style="color:#8b5cf6; font-weight:bold; text-decoration:none;">View Post ➜</a>
                        </div>
                        """, unsafe_allow_html=True)
                        email_count += 1
                
                if email_count == 0:
                    st.warning("No fresh HR email posts found in the last 48 hours.")
