import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json
import re
from datetime import datetime

# --- 1. PAGE CONFIG & GOOGLE RESEARCH UI ---
st.set_page_config(page_title="Language Explorer | Job Hunter", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');

    /* Global Theme */
    .stApp {
        background-color: #000000;
        background-image: radial-gradient(circle at 50% 50%, #0a192f 0%, #000000 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit Elements */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 2rem;}

    /* Navigation Bar */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 80px;
    }

    /* Globe Background Simulation */
    .globe-overlay {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 600px;
        height: 600px;
        background: url('https://www.transparenttextures.com/patterns/stardust.png');
        opacity: 0.3;
        z-index: -1;
        mask-image: radial-gradient(circle, black 30%, transparent 70%);
    }

    /* Hero Section */
    .hero-title {
        font-size: 64px;
        font-weight: 300;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        color: #94a3b8;
        text-align: center;
        font-size: 16px;
        margin-bottom: 40px;
    }

    /* Search Box Wrapper */
    .search-container {
        max-width: 800px;
        margin: 0 auto;
        position: relative;
    }

    /* CUSTOM INPUT STYLING */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 30px !important;
        color: white !important;
        padding: 10px 25px !important;
    }

    /* Job Card Styling */
    .result-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .result-card:hover {
        border-color: #3b82f6;
        background: rgba(255, 255, 255, 0.05);
    }
    .tag {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #3b82f6;
        margin-bottom: 8px;
        display: block;
    }
    .card-link {
        color: #ffffff;
        text-decoration: none;
        font-size: 18px;
        font-weight: 500;
    }
    .card-snippet {
        color: #94a3b8;
        font-size: 14px;
        margin: 12px 0;
        line-height: 1.6;
    }

    /* Copy Button UI */
    .copy-btn {
        background: transparent;
        border: 1px solid rgba(255,255,255,0.2);
        color: #94a3b8;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
    }
    
    /* Stats Section (Bottom Right) */
    .stats-panel {
        position: fixed;
        bottom: 40px;
        right: 40px;
        text-align: right;
        font-size: 11px;
        color: #64748b;
        line-height: 1.8;
    }
    </style>
    <div class="globe-overlay"></div>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & API SETUP ---
gemini_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini Key", type="password")
serper_key = st.secrets.get("SERPER_API_KEY") or st.sidebar.text_input("Serper Key", type="password")

def get_recent_jobs(role, api_key, search_type="standard"):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if search_type == "standard":
        prompt = f"Generate 3 Google search queries for latest {role} jobs in India. Focus on linkedin.com/jobs/view. Return ONLY a JSON list of strings."
    else:
        prompt = f"Generate 3 Google search queries to find LinkedIn posts from the last 24 hours where HRs share email IDs for {role} hiring. Return ONLY a JSON list of strings."
    
    try:
        response = model.generate_content(prompt)
        # Cleaning JSON formatting
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except:
        return [f'"{role}" hiring email 2024']

def extract_emails(text):
    return list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))

# --- 3. UI LAYOUT ---
# Header
st.markdown("""
    <div class="nav-bar">
        <div style="font-weight:bold; font-size: 20px;">Google <span style="font-weight:300;">Research</span> &nbsp; <span style="color:#64748b; font-weight:300;">Job Explorer</span></div>
        <div style="display: flex; gap: 30px; font-size: 13px; color: #94a3b8;">
            <span>Current Vacancies</span>
            <span>HR Directory</span>
            <span>Fresh Posts (48h)</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Hero
st.markdown('<h1 class="hero-title">Explore career opportunities</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Agentic search across India\'s top job portals and social networks, filtered for the last 48 hours.</p>', unsafe_allow_html=True)

# Main Controls
with st.container():
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        role_input = st.selectbox("Target Role", ["Product Manager", "Strategy Consultant", "Data Scientist", "Business Analyst", "Operations Associate", "MBA Fresher", "Software Engineer"], label_visibility="collapsed")
    with col_b:
        exp_input = st.selectbox("Exp", ["0-2 Years", "2-5 Years", "5+ Years"], label_visibility="collapsed")
    with col_c:
        if st.button("Search Jobs", use_container_width=True):
            st.session_state.search_clicked = True

# --- 4. EXECUTION & RESULTS ---
if st.session_state.get('search_clicked'):
    with st.spinner("Scanning for recent posts..."):
        headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
        
        # We use 'tbs': 'qdr:d2' to filter results to the past 2 days
        queries = get_recent_jobs(role_input, gemini_key, "standard") + get_recent_jobs(role_input, gemini_key, "email")
        
        all_results = []
        for q in queries[:4]: # Limit queries for speed
            payload = {"q": q, "num": 8, "tbs": "qdr:d2"} # THE MAGIC PARAMETER FOR FRESHNESS
            res = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
            if res.status_code == 200:
                all_results.extend(res.json().get('organic', []))

    # Tabs for Display
    t1, t2 = st.tabs(["Direct Apply", "HR Contact Posts"])
    
    with t1:
        st.markdown("<br>", unsafe_allow_html=True)
        seen = set()
        for i, item in enumerate(all_results):
            if item['link'] not in seen and len(seen) < 10:
                seen.add(item['link'])
                emails = extract_emails(item.get('snippet', ''))
                
                st.markdown(f"""
                <div class="result-card">
                    <span class="tag">RECENT POST • {item.get('source', 'Web')}</span>
                    <a href="{item['link']}" class="card-link" target="_blank">{item['title']}</a>
                    <div class="card-snippet">{item.get('snippet', '')}</div>
                    <div style="display:flex; justify-content: space-between; align-items: center;">
                        <span style="color:#3b82f6; font-size:12px;">{' | '.join(emails) if emails else 'Portal Application'}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Copy Link Feature
                st.button(f"🔗 Copy Link", key=f"btn_{i}", on_click=lambda l=item['link']: st.write(f"Link Copied: {l}"))

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        email_posts = [r for r in all_results if extract_emails(r.get('snippet', ''))]
        if not email_posts:
            st.info("No direct email posts found in the last 48 hours. Try a broader role.")
        else:
            for i, post in enumerate(email_posts):
                emails = extract_emails(post.get('snippet', ''))
                st.markdown(f"""
                <div class="result-card" style="border-left: 2px solid #8b5cf6;">
                    <span class="tag" style="color:#8b5cf6;">DIRECT HR EMAIL</span>
                    <a href="{post['link']}" class="card-link" target="_blank">{post['title']}</a>
                    <div class="card-snippet">{post['snippet']}</div>
                    <div style="background: rgba(139, 92, 246, 0.1); padding: 8px; border-radius: 4px; color: #c4b5fd; font-size: 13px;">
                        📧 Emails found: {', '.join(emails)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"🔗 Copy Post Link", key=f"email_btn_{i}", on_click=lambda l=post['link']: st.write(f"Link Copied: {l}"))

# Stats Panel (Bottom Right)
st.markdown(f"""
    <div class="stats-panel">
        World Overview<br>
        Active Leads: 100+<br>
        Freshness: 48h Window<br>
        Status: Agents Active<br><br>
        <div style="border: 1px solid rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; text-align:center;">
            Updated {datetime.now().strftime('%H:%M')}
        </div>
    </div>
    <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); color: #475569; font-size: 10px;">
        This site is best experienced with intent and a fresh resume
    </div>
""", unsafe_allow_html=True)
