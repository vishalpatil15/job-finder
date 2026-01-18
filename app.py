import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json
import re

# --- 1. PAGE CONFIG & ULTRA-MODERN UI ---
st.set_page_config(page_title="TagBuddy: Agentic Job Hunter", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    /* ULTRA-MODERN BACKGROUND */
    .stApp {
        /* Using a dark data-viz style background with a heavy dark overlay */
        background: linear-gradient(rgba(10, 10, 20, 0.85), rgba(10, 10, 20, 0.95)),
                    url('https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Hide Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* CENTERED LAYOUT UTILITIES */
    .block-container {
        padding-top: 5rem;
        max-width: 1200px;
    }
    .centered-text {
        text-align: center !important;
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
    }

    /* MAIN GLASS SEARCH CONTAINER */
    .main-container {
        background: rgba(30, 35, 50, 0.5); /* Highly transparent dark glass */
        padding: 30px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 30px;
        margin-bottom: 40px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }

    /* TYPOGRAPHY */
    h1 { 
        color: #ffffff !important; 
        font-weight: 300 !important; /* Thinner, cleaner font */
        font-size: 3.5rem !important;
        letter-spacing: -1px;
        margin-bottom: 10px !important;
    }
    p.subtitle { 
        color: #a0aec0 !important; 
        font-size: 1.2rem !important; 
        font-weight: 300;
        max-width: 700px;
        margin: 0 auto 30px auto !important;
    }
    
    /* INPUT LABELS - Force White and Clean */
    .stSelectbox label, .stFileUploader label {
        color: #e2e8f0 !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* CUSTOM FILE UPLOADER STYLING */
    .stFileUploader > div > div {
         background-color: rgba(255,255,255,0.05) !important;
         border: 1px solid rgba(255,255,255,0.1) !important;
         border-radius: 12px;
         padding: 10px;
    }
    
    /* MAIN ACTION BUTTON */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Modern blurple gradient */
        color: white;
        font-weight: 600;
        padding: 14px 40px;
        border-radius: 50px; /* Rounded pill button */
        border: none;
        font-size: 1.1rem;
        width: auto;
        min-width: 300px;
        display: block;
        margin: 30px auto 0 auto; /* Center the button */
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px -10px rgba(118, 75, 162, 0.5);
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px -10px rgba(118, 75, 162, 0.7);
    }

    /* --- CARD STYLES --- */
    
    /* STANDARD JOB CARD */
    .job-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 20px;
        border-left: 5px solid #3b82f6; /* Blue */
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* EMAIL CARD */
    .email-card {
        background-color: #f1f5f9;
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 20px;
        border-left: 5px solid #8b5cf6; /* Purple */
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }

    /* Typography inside cards */
    .card-title { color: #1e293b !important; font-size: 20px !important; font-weight: 700; margin-bottom: 8px; }
    .card-meta { color: #64748b !important; font-size: 14px; margin-bottom: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
    .card-snippet { color: #334155 !important; font-size: 15px; line-height: 1.6; margin-bottom: 20px; }
    
    /* Email Highlight Chip */
    .email-chip {
        background-color: #ede9fe; color: #6d28d9; padding: 6px 12px; border-radius: 30px;
        font-weight: bold; font-size: 13px; border: 1px solid #ddd6fe; display: inline-block; margin-right: 8px; margin-bottom: 8px;
    }
    
    /* Links */
    a.std-link, a.email-link {
        display: inline-block; padding: 10px 25px; border-radius: 8px; text-decoration: none; font-weight: bold;
    }
    a.std-link { background-color: #3b82f6; color: white !important; }
    a.email-link { background-color: #8b5cf6; color: white !important; }
    
    /* SHARE LINK STYLING */
    .share-section {
        margin-top: 20px;
        padding-top: 15px;
        border-top: 1px solid #e2e8f0;
    }
    .share-label { font-size: 12px; color: #64748b; font-weight: bold; margin-bottom: 5px; }
    /* Style the st.code block to fit the card */
    .stCode { font-size: 12px; }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; margin-bottom: 30px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; padding: 0 30px; background-color: rgba(255,255,255,0.05); border-radius: 30px; color: #a0aec0; font-weight: 600; border: 1px solid rgba(255,255,255,0.1); margin: 0 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #3b82f6; color: white; border: none;}
    
    /* Error Messages */
    .stAlert { background-color: #fff; color: #000; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECRETS ---
gemini_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini Key", type="password")
serper_key = st.secrets.get("SERPER_API_KEY") or st.sidebar.text_input("Serper Key", type="password")

# --- 3. HELPER FUNCTIONS ---
def get_pdf_text(file):
    reader = PdfReader(file)
    return " ".join([p.extract_text() for p in reader.pages])

def extract_emails(text):
    """Finds emails in text using Regex"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return list(set(emails))

# --- AGENT 1: Standard Link Hunter ---
def get_standard_queries(role, exp, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Generate 3 Google search queries to find formal job applications for:
    Role: {role}, Experience: {exp}, Location: India.
    Rules: Use 'site:linkedin.com/jobs/view' or 'site:naukri.com/job-listings'.
    Format: JSON list of strings.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    except:
        return [f"site:linkedin.com/jobs/view {role} India"]

# --- AGENT 2: HR Email Hunter (Updated for Freshness) ---
def get_email_queries(role, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Generate 3 Google search queries to find recent LinkedIn posts where HRs ask for resumes via email.
    Role: {role}.
    Keywords: "send resume to", "hiring now", "@gmail.com" OR "@company.com".
    Format: JSON list of strings.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    except:
        return [f'site:linkedin.com/posts "{role}" "send resume to"']

# --- 4. MAIN APP LAYOUT ---

# Centered Title Section
st.markdown('<div class="centered-text">', unsafe_allow_html=True)
st.image("https://cdn-icons-png.flaticon.com/512/2950/2950637.png", width=100)
st.title("TagBuddy")
st.markdown('<p class="subtitle">Explore the world\'s opportunities. Your agentic job hunter for direct links and hidden HR contacts.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# Main Glass Search Container
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Using columns to create a single "Search Bar" feel horizontally
    c1, c2, c3 = st.columns([1.5, 1.5, 2])
    with c1:
        role = st.selectbox("Target Role", [
            "Corporate Strategy", "Product Manager", "Strategy Consultant", 
            "Management Trainee", "Operations Associate", "Planning Associate",
            "Area Sales Manager", "SAP Functional Consultant", "SAP Technical Consultant",
            "Business Analyst", "Data Scientist", "MBA Freshers", "BTech Freshers"
        ])
    with c2:
        exp = st.selectbox("Experience Level", ["0-1 Years", "1-3 Years", "3-5 Years", "5-8 Years", "8+ Years"])
    
    with c3:
        # Custom styled label with asterisk
        st.markdown('<label style="color:#e2e8f0; font-size:0.9rem; font-weight:500; letter-spacing:1px;">UPLOAD RESUME (PDF)<span style="color:#ef4444">*</span></label>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")
    
    # Centered Main Action Button
    if st.button("🚀 Activate Global Search Agents"):
        if not uploaded_file or not gemini_key or not serper_key:
            st.error("Please ensure API keys are entered and a Resume is uploaded.")
        else:
            with st.spinner("🤖 Agents are scanning the web for recent opportunities..."):
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                
                # 1. Run Standard Agent (General Search)
                std_queries = get_standard_queries(role, exp, gemini_key)
                std_results = []
                for q in std_queries:
                    # Standard search for job portals
                    res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5})
                    std_results.extend(res.json().get('organic', []))
                
                # 2. Run Email Hunter Agent (TIME-BOXED to 48 Hours)
                email_queries = get_email_queries(role, gemini_key)
                email_results = []
                for q in email_queries:
                    # CRITICAL UPDATE: Added '?tbs=qdr:h48' to URL to filter for past 48 hours
                    res = requests.post("https://google.serper.dev/search?tbs=qdr:h48", headers=headers, json={"q": q, "num": 5})
                    email_results.extend(res.json().get('organic', []))
            
            st.markdown('</div>', unsafe_allow_html=True) # Close search container
            
            # --- DISPLAY RESULTS ---
            st.markdown("<h3 style='text-align:center; margin-bottom:30px; color:white !important;'>Search Results</h3>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["🔗 Top 10 Direct Links", "📧 Fresh HR Emails (Last 48h)"])
            
            # TAB 1: STANDARD JOBS WITH SHARE LINK
            with tab1:
                seen_links = set()
                count = 0
                for job in std_results:
                    if job['link'] not in seen_links and count < 10:
                        seen_links.add(job['link'])
                        count += 1
                        st.markdown(f"""
                        <div class="job-card">
                            <div class="card-title">{job['title']}</div>
                            <div class="card-meta">📍 {job.get('source', 'Job Portal')}</div>
                            <div class="card-snippet">{job.get('snippet', '')}</div>
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <a class="std-link" href="{job['link']}" target="_blank">Apply Now ➜</a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # SHARE LINK SECTION (Using Streamlit native code block for easy copying)
                        st.markdown('<div class="share-section"><div class="share-label">SHARE LINK</div>', unsafe_allow_html=True)
                        st.code(job['link'], language="text")
                        st.markdown('</div></div>', unsafe_allow_html=True) # Close share section and card

                if count == 0:
                    st.info("No standard links found matching criteria.")

            # TAB 2: FRESH EMAIL POSTS
            with tab2:
                email_count = 0
                seen_emails = set()
                
                for post in email_results:
                    snippet = post.get('snippet', '')
                    found_emails = extract_emails(snippet)
                    
                    # Ensure it's a recent post (double check date snippet if available, though API handles most)
                    time_snippet = post.get('date', '').lower()
                    is_recent = any(t in time_snippet for t in ['hour', 'day', '2 days']) or not time_snippet

                    if found_emails and post['link'] not in seen_emails and is_recent:
                        seen_emails.add(post['link'])
                        email_chip_html = "".join([f'<span class="email-chip">✉️ {e}</span>' for e in found_emails])
                        
                        st.markdown(f"""
                        <div class="email-card">
                            <div class="card-title">{post['title']}</div>
                            <div class="card-meta">🔗 LinkedIn / Social Post ({post.get('date', 'Recent')})</div>
                            <div style="margin-bottom:15px;">{email_chip_html}</div>
                            <div class="card-snippet">{snippet}</div>
                            <a class="email-link" href="{post['link']}" target="_blank">View Post ➜</a>
                        </div>
                        """, unsafe_allow_html=True)
                        email_count += 1
                
                if email_count == 0:
                    st.warning("No posts with emails found in the last 48 hours. Try broader keywords or check back later.")
