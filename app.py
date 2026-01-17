import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json

# 1. SETUP PAGE
st.set_page_config(page_title="Vishal's Job Matcher", layout="wide")
st.title("🎯 Strategy & Product Job Finder")
st.markdown("---")

# 2. SIDEBAR FOR API KEYS
with st.sidebar:
    st.header("🔑 API Setup")
    gemini_key = st.text_input("Gemini API Key", type="password")
    serper_key = st.text_input("Serper API Key", type="password")
    st.info("Get keys from Google AI Studio and Serper.dev")

# 3. HELPER FUNCTIONS
def get_pdf_text(uploaded_file):
    text = ""
    pdf_reader = PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_search_queries(resume_text, api_key):
    genai.configure(api_key=api_key)
    # Using the most stable 2026 model: Gemini 2.5 Flash
    model = genai.GenerativeModel('gemini-2.5-flash') 
    
    prompt = f"""
    Analyze this resume and generate 3 specific Google search strings.
    Target roles: Corporate Strategy, Strategy Consulting, or Product Management.
    Location: Focus on Pune and Bangalore.
    Format: ONLY a JSON list of strings.
    Example: ["site:linkedin.com/jobs 'Strategy Analyst' Pune"]
    Resume text: {resume_text[:4000]}
    """
    
    response = model.generate_content(prompt)
    clean_json = response.text.strip().replace('```json', '').replace('```', '')
    return json.loads(clean_json)

# 4. MAIN INTERFACE
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

if uploaded_file and gemini_key and serper_key:
    if st.button("Find Matching Jobs"):
        with st.spinner("Analyzing profile and searching for jobs..."):
            try:
                # Step A: Read PDF
                resume_content = get_pdf_text(uploaded_file)
                
                # Step B: Get Queries
                queries = get_search_queries(resume_content, gemini_key)
                
                # Step C: Search via Serper
                headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
                for q in queries:
                    st.write(f"🔍 Searching: {q}")
                    res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q})
                    results = res.json().get('organic', [])
                    
                    for job in results:
                        with st.container():
                            st.success(f"**{job['title']}**")
                            st.write(f"Source: {job.get('snippet', 'No description available')}")
                            st.markdown(f"[Apply Direct on {job.get('source', 'Link')}]({job['link']})")
                            st.divider()
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.info("Try updating your Gemini model name to 'gemini-2.5-flash-lite' if this persists.")
