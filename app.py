import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
from pypdf import PdfReader
import json
import re

# --- 1. PAGE CONFIG & UI ---
st.set_page_config(page_title="TagBuddy | Agentic Hunter", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp {
        background: radial-gradient(circle at top right, #020617, #0f172a, #000000);
        color: #ffffff;
    }

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
    
    /* GLASS SEARCH BOX */
    .main-container {
        background: rgba(255, 255, 255, 0.03);
        padding: 35px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        margin-bottom: 40px;
    }

    /* JOB CARDS */
    .job-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        border-left: 6px solid #3b82f6;
        color: #0f172a;
    }
    .prob-badge {
        padding: 6px 14px;
        border-radius: 50px;
        font-weight: 800;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 12px;
    }
    .match-high { background: #dcfce7; color: #166534; border: 1px solid #166534; }
    .match-mid { background: #fef9c3; color: #854d0e; border: 1px solid #854d0e; }
    .match-low { background: #fee2e2; color: #991b1b; border: 1px solid #991b1b; }

    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white; border: none; padding: 12px 40px; border-radius: 12px;
        font-weight: 700; width: 100%; transition: 0.3s;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. HELPERS ---
def get_pdf_text(file):
    reader = PdfReader(file)
    return "".join([p.extract_text() for p in reader.pages if p.extract_text()])

def get_job_score(api_key, resume_text, job_title, job_snippet):
    if not api_key or not resume_text: return 60
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analyze Match Probability (0-100%):
    Resume: {resume_text[:2000]}
    Job: {job_title}
    Snippet: {job_snippet}
    Provide ONLY the probability number.
    """
    try:
        response = model.generate_content(prompt)
        score = int(re.sub(r'\D', '', response.text.strip()))
        return min(max(score, 10), 98)
    except:
        return 65

# --- 3. UI LAYOUT ---
st.markdown("""
    <div class="brand-container">
        <img src="https://cdn-icons-png.flaticon.com/512/11104/11104255.png" width="80">
        <h1 class="main-title">TagBuddy</h1>
        <p style="color: #94a3b8; font-size: 1.2rem;">Democratized Job Hunter • No Limits • Powered by AI</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar for BYOK (Democratization)
with st.sidebar:
    st.header("🔑 API Settings")
    user_api_key = st.text_input("Gemini API Key", type="password", help="Get a free key from Google AI Studio")
    st.info("Using your own key keeps this app free and unlimited for everyone.")

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        role = st.text_input("Target Role", value="Product Manager")
    with c2:
        exp = st.selectbox("Experience", ["Fresher", "1-3 Years", "3-5 Years", "5+ Years", "8+ Years"])
    with c3:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    search_clicked = st.button("🚀 ACTIVATE GLOBAL SEARCH AGENTS")
    st.markdown('</div>', unsafe_allow_html=True)

if search_clicked:
    if not user_api_key:
        st.error("Please provide your Gemini API Key in the sidebar.")
    elif not uploaded_file:
        st.error("Please upload your resume to calculate match probability.")
    else:
        resume_text = get_pdf_text(uploaded_file)
        
        with st.spinner("🤖 Agents scanning the web (48h window)..."):
            all_results = []
            try:
                with DDGS() as ddgs:
                    # Search Queries
                    queries = [
                        f"site:linkedin.com/jobs/view {role} India {exp}",
                        f'site:linkedin.com/posts "{role}" "send resume to" India'
                    ]
                    for q in queries:
                        # 'd' limit for 24-48 hours freshness
                        ddgs_results = ddgs.text(q, region='in-en', timelimit='d')
                        for r in ddgs_results:
                            all_results.append({
                                'title': r['title'],
                                'link': r['href'],
                                'snippet': r['body']
                            })
                            if len(all_results) >= 15: break
            except Exception as e:
                st.error(f"Search failed: {e}")

        # --- RESULTS TABS ---
        t1, t2 = st.tabs(["🎯 Scored Opportunities", "📧 Direct HR Posts"])
        
        with t1:
            st.markdown("<br>", unsafe_allow_html=True)
            for i, job in enumerate(all_results[:10]):
                score = get_job_score(user_api_key, resume_text, job['title'], job['snippet'])
                status = "match-high" if score > 75 else "match-mid" if score > 45 else "match-low"
                
                st.markdown(f"""
                <div class="job-card">
                    <div class="prob-badge {status}">Shortlisting Probability: {score}%</div>
                    <div style="font-size: 20px; font-weight: 700;">{job['title']}</div>
                    <div style="color: #475569; font-size: 14px; margin: 10px 0;">{job['snippet']}</div>
                    <a href="{job['link']}" target="_blank" style="background:#3b82f6; color:white; padding:8px 20px; border-radius:8px; text-decoration:none; font-weight:bold; display:inline-block;">Apply Now ➜</a>
                </div>
                """, unsafe_allow_html=True)
                st.code(f"Share link: {job['link']}", language="text")

        with t2:
            st.markdown("<br>", unsafe_allow_html=True)
            email_results = [r for r in all_results if "@" in r['snippet']]
            if not email_results:
                st.info("No direct email posts found in the last 48 hours.")
            for post in email_results:
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', post['snippet'])
                email_chips = "".join([f'<span style="background:#f3e8ff; color:#7e22ce; padding:4px 10px; border-radius:20px; font-weight:bold; font-size:12px; margin-right:5px;">✉️ {e}</span>' for e in emails])
                
                st.markdown(f"""
                <div class="job-card" style="border-left-color: #8b5cf6;">
                    <div style="margin-bottom:12px;">{email_chips}</div>
                    <div style="font-size: 18px; font-weight: 700;">{post['title']}</div>
                    <div style="color: #475569; font-size: 14px; margin: 10px 0;">{post['snippet']}</div>
                    <a href="{post['link']}" target="_blank" style="color:#8b5cf6; font-weight:bold;">View Original Post ➜</a>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; color:#475569; margin-top:50px; font-size:12px;'>TagBuddy v2.5 • Open Source & Community Powered</div>", unsafe_allow_html=True)
