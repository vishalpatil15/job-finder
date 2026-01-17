import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG & UI ---
st.set_page_config(page_title="TagBuddy: Your Best Job Match Maker", page_icon="🏷️", layout="wide")

st.markdown("""
    <style>
    /* PREMIUM WALLPAPER WITH READABILITY OVERLAY */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.6), rgba(15, 23, 42, 0.6)),
                    url('https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=2029&auto=format&fit=crop');
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
        background: rgba(30, 41, 59, 0.6);
        padding: 40px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    /* TEXT COLORS - FORCE WHITE FOR HEADINGS & INPUTS */
    h1, h2, h3 { color: #ffffff !important; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    p { color: #e2e8f0 !important; font-size: 16px; }
    
    /* Force specific input labels to be white */
    .stSelectbox label, .stFileUploader label {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Upload Box Styling */
    .stFileUploader { padding-top: 15px; }
    .stFileUploader > div > div {
         background-color: rgba(255,255,255,0.05);
         border: 1px dashed rgba(255,255,255,0.3);
    }
    
    /* BUTTON STYLING */
    .stButton > button {
        background-color: #10b981;
        color: white;
        font-weight: bold;
        padding: 12px 30px;
        border-radius: 8px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    .stButton > button:hover {
        background-color: #059669;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }

    /* SEARCH RESULTS: White Card + Green Border */
    .job-card {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 6px solid #10b981;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s;
        backdrop-filter: blur(5px);
    }
    .job-card:hover { transform: translateY(-3px); }
    
    .job-title { 
        color: #1e293b !important; 
        font-size: 20px !important; 
        font-weight: 800 !important; 
        margin-bottom: 8px !important; 
    }
    .job-source { 
        color: #10b981 !important; 
        font-weight: 700 !important; 
        font-size: 13px !important; 
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .job-snippet { 
        color: #475569 !important; 
        font-size: 15px !important; 
        line-height: 1.5; 
        margin-top: 10px !important; 
    }
    
    /* Apply Button inside card */
    .apply-btn {
        background-color: #10b981;
        color: white !important;
        padding: 10px 25px;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        font-weight: 600;
        margin-top: 15px;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .apply-btn:hover { background-color: #059669; }
    
    .stAlert { background-color: rgba(255,255,255,0.95); color: #000; border-radius: 10px; }
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
st.title("🏷️ TagBuddy")
st.markdown("<p style='margin-top: -15px; margin-bottom: 30px;'>Your Intelligent Job Matcher</p>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        # UPDATED ROLE LIST
        role = st.selectbox("Target Role", [
            "Corporate Strategy", 
            "Product Manager", 
            "Strategy Consultant", 
            "Management Trainee",
            "Operations Associate",
            "Planning Associate",
            "Area Sales Manager",
            "SAP Functional Consultant",
            "SAP Technical Consultant",
            "Business Analyst",
            "Data Scientist",
            "MBA Freshers Open Roles",
            "BTech Freshers Open Roles"
        ])
    with c2:
        exp = st.selectbox("Experience", ["0-1 Years", "1-3 Years", "3-5 Years", "5-8 Years", "8+ Years"])
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    if st.button("🚀 Find Direct Jobs"):
        if not uploaded_file or not gemini_key or not serper_key:
            st.error("Please ensure keys are entered and resume is uploaded.")
        else:
            with st.spinner("Analyzing resume and scanning top platforms..."):
                queries = get_smart_queries(role, exp, gemini_key)
                
                all_results = []
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                
                for q in queries:
                    res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q, "num": 10})
                    results = res.json().get('organic', [])
                    all_results.extend(results)
                
                seen_links = set()
                top_jobs = []
                
                for job in all_results:
                    link = job.get('link', '')
                    if link not in seen_links and "search" not in link and "jobs/collections" not in link:
                        seen_links.add(link)
                        top_jobs.append(job)
                    if len(top_jobs) >= 10:
                        break
                
                st.markdown('</div>', unsafe_allow_html=True) # Close container
                
                if not top_jobs:
                    st.warning("No specific listings found. Try changing the role.")
                else:
                    # FIXED: Added explicit white color styling to this Header
                    st.markdown("<h3 style='margin-top: 30px; margin-bottom: 20px; color: white !important;'>✨ Top 10 Direct Matches</h3>", unsafe_allow_html=True)
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
