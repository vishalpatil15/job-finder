It looks like the previous code cut off at the very end, which caused that "unterminated string" error (basically, the computer was still waiting for the closing quotes `"""`).

Here is the **Complete, Fixed Code** for **TagBuddy Phase 2**. I have double-checked that all sections are closed properly.

### 💎 TagBuddy Phase 2: Complete Code

Replace your entire `app.py` with this.

```python
import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json
import re

# --- 1. PAGE CONFIG & UI ---
st.set_page_config(page_title="TagBuddy: Agentic Job Hunter", page_icon="🕵️", layout="wide")

st.markdown("""
    <style>
    /* PREMIUM WALLPAPER */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
                    url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Hide Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* UPPER SECTION: Glass Container */
    .main-container {
        background: rgba(20, 20, 30, 0.8);
        padding: 40px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
        backdrop-filter: blur(10px);
    }

    /* TEXT COLORS */
    h1, h2, h3 { color: #ffffff !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    p { color: #cbd5e1 !important; font-size: 16px; }
    
    /* Input Labels */
    .stSelectbox label, .stFileUploader label {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* BUTTON STYLING */
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
        padding: 12px 30px;
        border-radius: 8px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
    }

    /* --- CARD STYLES --- */
    
    /* TYPE 1: Standard Job Card (Green Border) */
    .job-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 6px solid #10b981;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* TYPE 2: Hidden Email Card (Purple Border) */
    .email-card {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 6px solid #8b5cf6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Typography inside cards */
    .card-title { color: #1e293b; font-size: 18px; font-weight: 800; margin-bottom: 5px; }
    .card-meta { color: #64748b; font-size: 14px; margin-bottom: 10px; font-weight: 600; }
    .card-snippet { color: #334155; font-size: 14px; line-height: 1.5; margin-bottom: 15px; }
    
    /* Email Highlight Chip */
    .email-chip {
        background-color: #ede9fe;
        color: #6d28d9;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 13px;
        border: 1px solid #ddd6fe;
        display: inline-block;
        margin-top: 5px;
        margin-right: 5px;
    }
    
    /* Links */
    a.std-link { color: #059669; font-weight: bold; text-decoration: none; }
    a.email-link { color: #7c3aed; font-weight: bold; text-decoration: none; }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255,255,255,0.1);
        border-radius: 4px;
        color: white;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
    }
    
    /* Error Messages */
    .stAlert { background-color: #fff; color: #000; }
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

# --- AGENT 2: HR Email Hunter ---
def get_email_queries(role, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Generate 3 Google search queries to find LinkedIn posts where HRs ask for resumes via email.
    Role: {role}.
    Keywords: "send resume to", "hiring", "@gmail.com" OR "@company.com".
    Format: JSON list of strings.
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    except:
        return [f'site:linkedin.com/posts "{role}" "send resume to"']

# --- 4. MAIN APP ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2950/2950637.png", width=80)
with col2:
    st.title("TagBuddy Phase 2")
    st.markdown("<p style='margin-top: -15px;'>The Agentic Job Hunter (Direct Links + Hidden HR Emails)</p>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        role = st.selectbox("Target Role", [
            "Corporate Strategy", "Product Manager", "Strategy Consultant", 
            "Management Trainee", "Operations Associate", "Planning Associate",
            "Area Sales Manager", "SAP Functional Consultant", "SAP Technical Consultant",
            "Business Analyst", "Data Scientist", "MBA Freshers", "BTech Freshers"
        ])
    with c2:
        exp = st.selectbox("Experience", ["0-1 Years", "1-3 Years", "3-5 Years", "5-8 Years", "8+ Years"])
    
    st.markdown('<label style="color:white; font-size:1.1rem; font-weight:600;">Upload Resume (PDF)<span style="color:red">*</span></label>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")
    
    if st.button("🚀 Activate Agents"):
        if not uploaded_file or not gemini_key or not serper_key:
            st.error("Please ensure keys are entered and resume is uploaded.")
        else:
            with st.spinner("🤖 Agents are scanning the web..."):
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                
                # 1. Run Standard Agent
                std_queries = get_standard_queries(role, exp, gemini_key)
                std_results = []
                for q in std_queries:
                    res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5})
                    std_results.extend(res.json().get('organic', []))
                
                # 2. Run Email Hunter Agent
                email_queries = get_email_queries(role, gemini_key)
                email_results = []
                for q in email_queries:
                    res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 5})
                    email_results.extend(res.json().get('organic', []))
            
            st.markdown('</div>', unsafe_allow_html=True) # Close Container
            
            # --- DISPLAY RESULTS ---
            tab1, tab2 = st.tabs(["🔗 Direct Apply Links", "📧 Hidden HR Emails"])
            
            # TAB 1: STANDARD JOBS
            with tab1:
                st.markdown("<h3 style='color:white !important; margin-bottom:20px;'>Official Job Portals</h3>", unsafe_allow_html=True)
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
                            <a class="std-link" href="{job['link']}" target="_blank">Apply Now ➜</a>
                        </div>
                        """, unsafe_allow_html=True)
                if count == 0:
                    st.info("No standard links found.")

            # TAB 2: EMAIL POSTS
            with tab2:
                st.markdown("<h3 style='color:white !important; margin-bottom:20px;'>Social Posts with HR Emails</h3>", unsafe_allow_html=True)
                email_count = 0
                seen_emails = set()
                
                for post in email_results:
                    snippet = post.get('snippet', '')
                    found_emails = extract_emails(snippet)
                    
                    if found_emails and post['link'] not in seen_emails:
                        seen_emails.add(post['link'])
                        # Create HTML chips for emails
                        email_chip_html = "".join([f'<span class="email-chip">✉️ {e}</span>' for e in found_emails])
                        
                        st.markdown(f"""
                        <div class="email-card">
                            <div class="card-title">{post['title']}</div>
                            <div class="card-meta">🔗 LinkedIn / Social Post</div>
                            <div style="margin-bottom:10px;">{email_chip_html}</div>
                            <div class="card-snippet">{snippet}</div>
                            <a class="email-link" href="{post['link']}" target="_blank">View Post ➜</a>
                        </div>
                        """, unsafe_allow_html=True)
                        email_count += 1
                
                if email_count == 0:
                    st.info("No direct email posts found right now. Try a broader role name.")

```
