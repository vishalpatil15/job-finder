import streamlit as st
import google.generativeai as genai
import requests
from pypdf import PdfReader
import json
import re  # Added for email extraction

# --- 1. PAGE CONFIG & UI ---
st.set_page_config(page_title="TagBuddy: Your Best Job Match Maker", page_icon="🏷️", layout="wide")

st.markdown("""
    <style>
    /* PREMIUM "EXTRAORDINARY" WALLPAPER */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
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
        background: rgba(20, 20, 30, 0.7);
        padding: 40px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
    }

    /* TEXT COLORS */
    h1, h2, h3 { color: #ffffff !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    p { color: #e2e8f0 !important; font-size: 16px; }
    
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

    /* ------------------------------------------- */
    /* RESULT CARD STYLES */
    /* ------------------------------------------- */
    
    /* TYPE 1: Standard Job Card (Green Border) */
    .job-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 6px solid #10b981; /* Green */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* TYPE 2: "Hidden Gem" Email Card (Purple Border) */
    .email-card {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 6px solid #8b5cf6; /* Purple */
        border-right: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* TYPOGRAPHY */
    .card-title { color: #1e293b; font-size: 18px; font-weight: 800; margin-bottom: 5px; }
    .card-meta { color: #64748b; font-size: 14px; margin-bottom: 10px; }
    .card-snippet { color: #334155; font-size: 14px; line-height: 1.5; margin-bottom: 15px; }
    
    /* Email Highlight Chip */
    .email-chip {
        background-color: #ede9fe;
        color: #6d28d9;
        padding: 4px 10
