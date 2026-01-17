import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG & UI ---
st.set_page_config(page_title="TagBuddy: Your Best Job Match Maker", page_icon="🏷️", layout="wide")

st.markdown("""
    <style>
    /* Professional Dark Background */
    .stApp {
        background: url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop');
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* Hide Default Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* UPPER SECTION: Glassmorphism Container */
    .main-container {
        background: rgba(0, 0, 0, 0.75); /* Darker for better white text contrast */
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 30px;
    }

    /* UPPER SECTION: Text Colors (All White) */
    h1 { color: #ffffff !important; text-shadow: 0px 2px 4px rgba(0,0,0,0.5); }
    h2, h3 { color: #ffffff !important; }
    p { color: #f0f0f0 !important; font-size: 16px; }
    
    /* Input Labels - Force White */
    label { 
        color: #ffffff !important; 
        font-weight: 600 !important; 
        font-size: 16px !important; 
    }
    
    /* File Uploader Text */
    .stFileUploader label { color: white !important; }
    .stFileUploader div { color: white !important; }
    
    /* ------------------------------------------- */
    /* SEARCH RESULTS: White Card + Green Border */
    /* ------------------------------------------- */
    .job-card {
        background-color: #ffffff !important; /* Pure White Background */
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 8px solid #2e7d32; /* Success Green */
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .job-card:hover {
        transform: translateY(-3px);
    }
    
    /* Result Text Colors (Black/Dark Grey for readability on white) */
    .job-title { 
        color: #000000 !important; 
        font-size: 22px !important; 
        font-weight: 800 !important; 
        margin-bottom: 8px !important; 
    }
    .job-source { 
        color: #2e7d32 !important; 
        font-weight: 700 !important; 
        font-size: 14px !important; 
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .job-snippet { 
        color: #333333 !important; 
        font-size: 15px !important; 
        line-height: 1.5; 
        margin-top: 10px !important; 
    }
    
    /* Apply Button */
    .apply-btn {
        background-color: #2e7d32;
        color: white !important;
        padding: 10px 25px;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
        margin-top: 15px;
    }
    .apply-btn:hover { background-color: #1b5e20; }
    
    /* Error/Success Messages */
    .stAlert { color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECRETS ---
gemini_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini Key", type="password")
serper_key = st.secrets.get("SERPER_API_KEY") or st.sidebar.text_input("Serper Key", type="password")

# --- 3. LOGIC ---
def get_pdf_text(file):
    reader = PdfReader(file)
    return " ".join([p.extract_text() for p in reader.pages])

def get_smart_queries(role, exp, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Act as a recruitment expert. Generate 4 Google search queries to find individual job postings.
    Role: {role}
    Experience: {exp}
    Location: Pune or Bangalore
    
    Rules:
    1. Use 'site:linkedin.com/jobs/view' to find specific LinkedIn posts.
    2. Use 'site:naukri.com/job-listings' to find specific Naukri posts.
    3. Use 'site:iimjobs.com/j' to find specific IIMJobs posts.
    
    Format: Return ONLY a JSON list of strings.
    Example: ["site:linkedin.com/jobs/view 'Strategy Analyst' Pune", "site:naukri.com/job-listings 'Product Manager' Bangalore"]
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace('```json', '').replace('```', ''))
    except:
        return [f"site:linkedin.com/jobs/view {role} Pune", f"site:naukri.com/job-listings {role} Pune"]

# --- 4. MAIN APP ---
st.title("🏷️ TagBuddy: Your Best Job Match Maker")
st.markdown("Upload your resume and get the top 10 direct job links.")

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        role = st.selectbox("Target Role", ["Corporate Strategy", "Product Manager", "Strategy Consultant", "Business Analyst", "Data Scientist"])
    with c2:
        exp = st.selectbox("Experience", ["0-1 Years", "1-3 Years", "3-5 Years", "5-8 Years", "8+ Years"])
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    if st.button("🚀 Find Direct Jobs"):
        if not uploaded_file or not gemini_key or not serper_key:
            st.error("Please ensure keys are entered and resume is uploaded.")
        else:
            with st.spinner("Scanning LinkedIn, Naukri & IIMJobs for individual posts..."):
                # 1. Get Queries
                queries = get_smart_queries(role, exp, gemini_key)
                
                # 2. Search
                all_results = []
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                
                for q in queries:
                    res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 10})
                    results = res.json().get('organic', [])
                    all_results.extend(results)
                
                # 3. Filter
                seen_links = set()
                top_jobs = []
                
                for job in all_results:
                    link = job.get('link', '')
                    if link not in seen_links and "search" not in link and "jobs/collections" not in link:
                        seen_links.add(link)
                        top_jobs.append(job)
                    if len(top_jobs) >= 10:
                        break
                
                # 4. Display Results
                st.markdown('</div>', unsafe_allow_html=True) # Close the glass container before showing cards
                
                if not top_jobs:
                    st.warning("No specific listings found. Try changing the role.")
                else:
                    st.markdown("### ✨ Top 10 Direct Matches")
                    for job in top_jobs:
                        source_domain = job['link'].split('/')[2].replace('www.', '')
                        
                        st.markdown(f"""
                            <div class="job-card">
                                <div class="job-source">{source_domain}</div>
                                <div class="job-title">{job['title']}</div>
                                <div class="job-snippet">{job.get('snippet', 'Check the link for full details.')}</div>
                                <a class="apply-btn" href="{job['link']}" target="_blank">Apply Now ➜</a>
                            </div>
                        """, unsafe_allow_html=True)
