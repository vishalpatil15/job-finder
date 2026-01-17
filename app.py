import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json

# 1. SETUP PAGE
st.set_page_config(page_title="Vishal's Career Matcher", layout="wide")
st.title("🎯 Strategy & Product Job Finder")
st.markdown("---")

# 2. SIDEBAR
with st.sidebar:
    st.header("🔑 API Setup")
    gemini_key = st.text_input("Gemini API Key", type="password")
    serper_key = st.text_input("Serper API Key", type="password")
    st.info("Get keys from Google AI Studio and Serper.dev")

# 3. HELPER FUNCTIONS (This is where get_search_queries lives!)
def get_pdf_text(pdf_docs):
    text = ""
    pdf_reader = PdfReader(pdf_docs)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_search_queries(resume_text, api_key):
    genai.configure(api_key=api_key)
    # Using the standard 2026 model: Gemini 3 Flash
    model = genai.GenerativeModel('gemini-3-flash') 
    
    prompt = f"""
    Analyze this resume and generate 3 specific Google search strings.
    Target roles: Corporate Strategy, Strategy Consulting, or Product Management.
    Location: Focus on Pune and Bangalore.
    Format: ONLY a JSON list of strings.
    Example: ["site:linkedin.com/jobs 'Strategy Analyst' Pune"]
    Resume text: {resume_text[:4000]}
    """
    
    response = model.generate_content(prompt)
    # Cleaning the response to ensure it's pure JSON
    clean_json = response.text.strip().replace('```json', '').replace('```', '')
    return json.loads(clean_json)

# 4. MAIN INTERFACE
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

if uploaded_file and gemini_key and serper_key:
    if st.button("Find Matching Jobs"):
        with st.spinner("Analyzing your profile for Strategy & Product roles..."):
            # Step A: Read PDF
            resume_content = get_pdf_text(uploaded_file)
            
            # Step B: Get Queries from Gemini
            try:
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
                            st.write(f"Source: {job.get('link', 'Link not found')}")
                            st.markdown(f"[Apply Now]({job['link']})")
                            st.divider()
            except Exception as e:
                st.error(f"Something went wrong: {e}")
