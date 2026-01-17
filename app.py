import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json

# Page Layout
st.set_page_config(page_title="Vishal's Career Matcher", layout="wide")
st.title("🎯 Strategy & Product Job Finder")
st.markdown("---")

# Sidebar for your API Keys
with st.sidebar:
    st.header("🔑 API Setup")
    gemini_key = st.text_input("Gemini API Key", type="password")
    serper_key = st.text_input("Serper API Key", type="password")
    st.info("Get keys from Google AI Studio and Serper.dev")

# Function to read PDF
def get_pdf_text(pdf_docs):
    text = ""
    pdf_reader = PdfReader(pdf_docs)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Main App Logic
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

if uploaded_file and gemini_key and serper_key:
    if st.button("Find Matching Jobs"):
        with st.spinner("Analyzing your profile for Strategy & Product roles..."):
            # 1. Read the PDF
            resume_content = get_pdf_text(uploaded_file)
            
            # 2. Ask Gemini to create search queries
            genai.configure(api_key=gemini_key)
           model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"Resume text: {resume_content}. Give me 3 Google search strings for 'Corporate Strategy' or 'Product Management' jobs in Pune or Bangalore on site:naukri.com or site:linkedin.com/jobs. Return ONLY a JSON list of strings."
            
            response = model.generate_content(prompt)
            queries = json.loads(response.text.strip().replace('```json', '').replace('```', ''))

            # 3. Search via Serper
            headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
            for q in queries:
                res = requests.post("https://google.serper.dev/search", headers=headers, json={"q": q})
                results = res.json().get('organic', [])
                
                for job in results:
                    st.success(f"**{job['title']}**")
                    st.write(f"Link: {job['link']}")
                    st.markdown("---")
