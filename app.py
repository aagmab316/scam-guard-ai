import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load the Key from your .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 2. Setup the Brain
client = None
if api_key:
    client = OpenAI(api_key=api_key)

# 3. Analysis Functions
def analyze_text(text):
    if not client: return "⚠️ Error: OpenAI API Key is missing. Check your .env file."
    
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

def analyze_audio(audio_file):
    if not client: return "⚠️ Error: Missing API Key.", ""
    try:
        # Transcribe
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        text = transcription.text
        return text, analyze_text(text)
    except Exception as e:
        return f"Error processing audio: {e}", ""

# 4. The App UI
st.set_page_config(page_title="ScamGuard AI", page_icon="🛡️")
st.title("🛡️ ScamGuard: AI Fraud Detector")

# Tabs for Text vs Audio
tab1, tab2 = st.tabs(["📝 Text/SMS Check", "🎤 Audio/Call Check"])

with tab1:
    st.header("Check Suspicious Messages")
    user_input = st.text_area("Paste message here:", height=150)
    if st.button("Analyze Text"):
        with st.spinner("Scanning..."):
            result = analyze_text(user_input)
            st.info(result)

with tab2:
    st.header("Check Suspicious Voice Notes")
    audio_file = st.file_uploader("Upload audio (mp3, wav)", type=['mp3', 'wav'])
    if audio_file and st.button("Analyze Audio"):
        with st.spinner("Listening and Analyzing..."):
            text_result, analysis_result = analyze_audio(audio_file)
            st.warning(f"**Transcript:** {text_result}")
            st.info(f"**Analysis:**\n{analysis_result}")