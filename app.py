import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json
import re

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
    
    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* CENTERED HEADER UTILITIES */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 3rem;
        margin-bottom: 2rem;
    }
    
    /* LOGO ANIMATION */
    .logo-img {
        width: 120px;
        margin-bottom: 15px;
        filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.5));
        transition: transform 0.3s ease;
    }
    .logo-img:hover {
        transform: scale(1.05);
    }

    /* TYPOGRAPHY */
    h1 { 
        color: #ffffff !important; 
        font-weight: 800 !important;
        font-size: 4rem !important;
        letter-spacing: -2px;
        margin: 0 !important;
        text-align: center;
        background: -webkit-linear-gradient(#eee, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    p.subtitle { 
        color: #94a3b8 !important; 
        font-size: 1.3rem !important; 
        text-align: center;
        font-weight: 300;
        max-width: 600px;
        margin-top: 10px !important;
    }

    /* GLASS SEARCH BAR CONTAINER */
    .search-container {
        background: rgba(30, 41, 59, 0.4);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-bottom: 40px;
    }

    /* INPUT STYLING */
    .stSelectbox label, .stFileUploader label {
        color: #e2e8f0 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ACTION BUTTON */
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

    /* --- INTELLIGENT JOB CARDS --- */
    
    .job-card {
        background: rgba(255, 255, 255, 0.96);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.2s;
    }
    .job-card:hover { transform: translateY(-3px); }

    /* MATCH SCORE BADGE */
    .match-badge {
        position: absolute;
        top: 20px;
        right: 20px;
        padding: 6px 14px;
        border-radius: 30px;
        font-weight: 800;
        font-size: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .high-match { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; } /* Green */
    .med-match { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; } /* Yellow */
    .low-match { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; } /* Red */

    /* Typography */
    .job-title { color: #0f172a; font-size: 20px; font-weight: 700; margin-bottom: 6px; }
    .job-source { color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 12px; }
    .job-snippet { color: #334155; font-size: 14px; line-height: 1.6; margin-bottom: 20px; max-width: 85%; }

    /* Links */
    a.apply-link {
        display: inline-block;
        background: #0f172a;
        color: white;
        text-decoration: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        transition: background 0.2s;
    }
    a.apply-link:hover { background: #334155; }
    
    .share-link {
        font-family: monospace;
        font-size: 11px;
        background: #f1f5f9;
        padding: 8px;
        border-radius: 6px;
        color: #64748b;
        margin-top: 15px;
        border: 1px dashed #cbd5e1;
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
    
    /* ALERTS */
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

# --- AGENT 2: THE "AI RECRUITER" (MATCH SCORING) ---
def analyze_match_batch(resume_text, jobs_list, api_key):
    """
    Sends a batch of job snippets + resume to Gemini to calculate probability scores.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Prepare a minimal JSON of jobs to save tokens
    jobs_summary = []
    for i, job in enumerate(jobs_list):
        jobs_summary.append({
            "id": i,
            "title": job.get('title', ''),
            "snippet": job.get('snippet', '')[:200]
        })
    
    prompt = f"""
    Act as a Senior Recruiter. Compare this Resume Summary against the Job Descriptions.
    
    RESUME SUMMARY:
    {resume_text[:2000]}
    
    JOB LIST:
    {json.dumps(jobs_summary)}
    
    TASK:
    For each job, calculate a "Shortlist Probability" (0-100%) based on keyword matching and relevance.
    
    OUTPUT FORMAT:
    Return ONLY a JSON dictionary where keys are the Job IDs (as strings) and values are the percentage integers.
    Example: {{"0": 85, "1": 40, "2": 95}}
    """
    
    try:
        response = model.generate_content(prompt)
        match_scores = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
        return match_scores
    except:
        return {} # Return empty if AI fails

# --- 4. MAIN LAYOUT ---

# CENTERED HEADER WITH LOGO
st.markdown("""
    <div class="header-container">
        <img src="https://cdn-icons-png.flaticon.com/512/12392/12392769.png" class="logo-img">
        <h1>TagBuddy</h1>
        <p class="subtitle">Agentic Job Intelligence. Resume Analysis. Direct Matches.</p>
    </div>
""", unsafe_allow_html=True)

# GLASS SEARCH CONTAINER
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
                    # Get score from AI (default to 50% if failed)
                    score = match_scores.get(str(i), match_scores.get(i, 50))
                    
                    # Badge Color Logic
                    badge_class = "med-match"
                    if score >= 80: badge_class = "high-match"
                    elif score < 50: badge_class = "low-match"

                    st.markdown(f"""
                    <div class="job-card">
                        <div class="match-badge {badge_class}">⚡ {score}% Match</div>
                        <div class="job-title">{job['title']}</div>
                        <div class="job-source">📍 {job.get('source', 'Job Portal')}</div>
                        <div class="job-snippet">{job.get('snippet', '')}</div>
                        
                        <div style="display:flex; flex-direction:column; gap:10px;">
                            <a href="{job['link']}" target="_blank" class="apply-link">Apply Now ➜</a>
                            <div class="share-link">🔗 Copy Link: {job['link']}</div>
                        </div>
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
                        email_chips = "".join([f"<span style='background:#ede9fe; color:#6d28d9; padding:4px 8px; border-radius:4px; margin-right:5px; font-weight:bold;'>✉️ {e}</span>" for e in found_emails])
                        
                        st.markdown(f"""
                        <div class="job-card" style="border-left: 5px solid #8b5cf6;">
                            <div class="job-title">{post['title']}</div>
                            <div class="job-source">🔗 Social Post (Last 48 Hours)</div>
                            <div style="margin-bottom:15px;">{email_chips}</div>
                            <div class="job-snippet">{post.get('snippet', '')}</div>
                            <a href="{post['link']}" target="_blank" style="color:#8b5cf6; font-weight:bold;">View Post ➜</a>
                        </div>
                        """, unsafe_allow_html=True)
                        email_count += 1
                
                if email_count == 0:
                    st.warning("No fresh HR email posts found in the last 48 hours.")
