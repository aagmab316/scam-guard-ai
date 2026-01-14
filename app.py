import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 2. Initialize the AI Client
client = None
if api_key:
    client = OpenAI(  api_key="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")

# 3. Define the Analysis Function
def analyze_scam(text):
    if not client:
        return "⚠️ Error: OpenAI API Key is missing. Please set it in the .env file."
    
    if not text:
        return "Please paste some text first."
    
    prompt = f"""
    Analyze this message for scam patterns.
    Message: "{text}"
    
    1. Scam Score (0-10):
    2. Red Flags:
    3. Verdict (SAFE/SUSPICIOUS/DANGEROUS):
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# 4. The Website UI
st.set_page_config(page_title="ScamGuard AI", page_icon="🛡️")

st.title("🛡️ ScamGuard: AI Fraud Detector")
st.write("Paste a suspicious message below to check for fraud.")

user_input = st.text_area("Message:", height=150)

if st.button("Analyze Risk"):
    with st.spinner("Analyzing..."):
        result = analyze_scam(user_input)
        st.info(result)