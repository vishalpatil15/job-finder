import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
from pypdf import PdfReader
import json
import re
import time

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="TagBuddy | Open Job Hunter", page_icon="🎯", layout="wide")

# Modern UI Styling (Same as requested)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus+Jakarta+Sans', sans-serif; }
    .stApp { background: radial-gradient(circle at top right, #020617, #0f172a, #000000); color: #ffffff; }
    #MainMenu, footer, header {visibility: hidden;}
    .brand-container { display: flex; flex-direction: column; align-items: center; padding: 20px 0; text-align: center; }
    .main-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(to right, #60a5fa, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; }
    .main-container { background: rgba(255, 255, 255, 0.03); padding: 30px; border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(12px); margin-bottom: 30px; }
    .job-card { background: rgba(255, 255, 255, 0.98); padding: 20px; border-radius: 16px; margin-bottom: 15px; border-left: 6px solid #3b82f6; }
    .prob-badge { padding: 4px 12px; border-radius: 50px; font-weight: 800; font-size: 12px; margin-bottom: 10px; display: inline-block; }
    .match-high { background: #dcfce7; color: #166534; }
    .match-mid { background: #fef9c3; color: #854d0e; }
    .match-low { background: #fee2e2; color: #991b1b; }
    .card-title { color: #0f172a; font-size: 18px; font-weight: 700; }
    .stButton > button { background: linear-gradient(90deg, #3b82f6, #8b5cf6); color: white; border: none; padding: 10px; border-radius: 10px; width: 100%; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIC FUNCTIONS (FREE) ---

def get_pdf_text(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() or "" for page in reader.pages])

@st.cache_data(ttl=3600) # Cache search results for 1 hour to save API calls
def free_search(query):
    """Uses DuckDuckGo Search (Free/Unlimited-ish)"""
    results = []
    try:
        with DDGS() as ddgs:
            # We filter for 'past month' using 'm' to get relatively fresh results
            ddgs_gen = ddgs.text(query, region='in-en', safesearch='off', timelimit='m')
            for r in ddgs_gen:
                results.append({
                    'title': r['title'],
                    'link': r['href'],
                    'snippet': r['body'],
                    'source': 'Web'
                })
                if len(results) >= 5: break
    except Exception as e:
        st.error(f"Search Error: {e}")
    return results

def get_job_score(api_key, resume_text, job_title, job_snippet):
    if not api_key: return 50
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Resume: {resume_text[:2000]}\nJob: {job_title}\nSnippet: {job_snippet}\nMatch score 0-100. Return only number."
    try:
        response = model.generate_content(prompt)
        return int(re.sub(r'\D', '', response.text.strip()))
    except:
        return 65

# --- 3. UI ---

st.markdown("""
    <div class="brand-container">
        <h1 class="main-title">TagBuddy</h1>
        <p style="color: #94a3b8;">Democratized Job Hunting • No Paywalls • Free Forever</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar for Democratization
with st.sidebar:
    st.header("⚙️ Configuration")
    user_gemini_key = st.text_input("Enter your Gemini API Key", type="password", help="Get a free key at aistudio.google.com")
    st.info("To make this app free for everyone, we use your own Gemini Key. Search is powered by DuckDuckGo (Free).")

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        role = st.text_input("Target Role", value="Product Manager")
        exp = st.selectbox("Experience", ["Fresher", "1-3 Years", "3-5 Years", "5+ Years"])
    with c2:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    search_btn = st.button("🚀 FIND JOBS")
    st.markdown('</div>', unsafe_allow_html=True)

if search_btn:
    if not user_gemini_key:
        st.warning("Please enter your Gemini API Key in the sidebar to analyze jobs.")
    
    resume_text = get_pdf_text(uploaded_file) if uploaded_file else ""
    
    with st.spinner("Agent scanning DuckDuckGo..."):
        # Construct free queries
        queries = [
            f"site:linkedin.com/jobs/view {role} India {exp}",
            f'site:linkedin.com/posts "{role}" "send resume to"'
        ]
        
        all_results = []
        for q in queries:
            all_results.extend(free_search(q))

    # Display
    t1, t2 = st.tabs(["🎯 Scored Opportunities", "📧 Direct HR Contacts"])
    
    with t1:
        for job in all_results[:8]:
            score = get_job_score(user_gemini_key, resume_text, job['title'], job['snippet'])
            badge_class = "match-high" if score > 75 else "match-mid" if score > 50 else "match-low"
            
            st.markdown(f"""
            <div class="job-card">
                <div class="prob-badge {badge_class}">Match: {score}%</div>
                <div class="card-title">{job['title']}</div>
                <div class="card-snippet">{job['snippet']}</div>
                <a href="{job['link']}" target="_blank" style="color:#3b82f6; font-weight:bold; text-decoration:none;">Apply on Portal ➜</a>
            </div>
            """, unsafe_allow_html=True)

    with t2:
        # Filter snippets containing @ to find HRs
        email_posts = [r for r in all_results if "@" in r['snippet']]
        if not email_posts:
            st.info("No direct emails found in current search window.")
        for post in email_posts:
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', post['snippet'])
            st.markdown(f"""
            <div class="job-card" style="border-left-color:#a855f7;">
                <div style="margin-bottom:10px;">{" ".join([f'<span style="background:#f3e8ff; color:#7e22ce; padding:2px 8px; border-radius:10px; font-size:12px; margin-right:5px;">{e}</span>' for e in emails])}</div>
                <div class="card-title">{post['title']}</div>
                <a href="{post['link']}" target="_blank" style="color:#a855f7; font-weight:bold; text-decoration:none;">View HR Post ➜</a>
            </div>
            """, unsafe_allow_html=True)
