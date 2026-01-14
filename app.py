import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import tempfile

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Configure Gemini
if not api_key:
    st.error("⚠️ GEMINI_API_KEY missing. Check your .env file.")
else:
    genai.configure(api_key=api_key)

def analyze_content(content_input, is_audio=False):
    """
    Analyzes Text OR Audio using Gemini 1.5 Flash.
    """
    try:
        # Use 'gemini-1.5-flash' for speed and multimodal capabilities
        model = genai.GenerativeModel('gemini-1.5-flash')

        # The "Neutral Analyst" Persona Prompt
        base_prompt = """
        Act as a Neutral Senior Cybersecurity Analyst. Analyze the provided content for fraud.
        
        Perform these specific checks:
        1. **Psychological Triggers:** Look for Urgency (e.g., "Act now"), Fear (e.g., "Account locked"), or Greed (e.g., "You won").
        2. **Technical Red Flags:** Look for suspicious links, strange requests (gift cards), or mismatched domains.
        3. **Scam Category:** Classify it (e.g., Phishing, Smishing, Vishing, Grandparent Scam).
        
        Output Format (Use Markdown):
        ### 🛡️ Security Analysis
        * **Risk Score:** [0-100]%
        * **Verdict:** [SAFE / SUSPICIOUS / MALICIOUS]
        * **Detected Category:** [Category Name]
        
        ### 🚩 Red Flags Detected
        * [Trigger 1]: [Explanation]
        * [Trigger 2]: [Explanation]
        
        ### 💡 Safety Recommendation
        [Specific advice based on the scam type]
        """

        with st.spinner("Consulting Gemini AI..."):
            if is_audio:
                # Gemini can process the audio file directly!
                response = model.generate_content([base_prompt, content_input])
            else:
                # Text analysis
                response = model.generate_content(f"{base_prompt}\n\nMessage to Analyze:\n{content_input}")
                
            return response.text
            
    except Exception as e:
        return f"Error connecting to Gemini: {e}"

 # 3. Streamlit UI
st.set_page_config(page_title="ScamGuard (Gemini Edition)", page_icon="🛡️")
st.title("🛡️ ScamGuard: AI Fraud Detector")
st.caption("Powered by Google Gemini 1.5 Flash")

tab1, tab2 = st.tabs(["📝 Text/SMS Check", "🎤 Audio/Call Check"])

# --- Tab 1: Text Analysis ---
with tab1:
    st.header("Check Suspicious Messages")
    user_input = st.text_area("Paste message here:", height=150)
    if st.button("Analyze Text"):
        if user_input:
            result = analyze_content(user_input, is_audio=False)
            st.markdown(result)
        else:
            st.warning("Please paste some text first.")

# --- Tab 2: Audio Analysis ---
with tab2:
    st.header("Check Suspicious Voice Notes")
    audio_file = st.file_uploader("Upload audio (mp3, wav)", type=['mp3', 'wav', 'm4a'])
    
    if audio_file and st.button("Analyze Audio"):
        # Gemini needs a file path, so we save the upload to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name

        try:
            # Upload the file to Gemini
            uploaded_file = genai.upload_file(tmp_path)
            
            # Analyze
            result = analyze_content(uploaded_file, is_audio=True)
            st.markdown(result)
            
        except Exception as e:
            st.error(f"Audio processing error: {e}")
        finally:
            # Cleanup: Remove temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)