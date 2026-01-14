import streamlit as st
import os
import re
import tempfile
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini
try:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        model = None
except Exception:
    model = None


# Deterministic Fallback (works without API)
def _fallback_analysis(text):
    urls = re.findall(r'https?://[^\s)]+', text, flags=re.IGNORECASE)
    t = text.lower()

    urgency = [k for k in ["urgent","immediately","act now","24 hours","expired","final notice"] if k in t]
    fear = [k for k in ["account locked","suspended","legal action","arrest","compromised","breach"] if k in t]
    greed = [k for k in ["you won","winner","jackpot","lottery","prize","payout","refund","grant"] if k in t]
    sensitive = [k for k in ["password","otp","2fa","verification code","bank","ssn","seed phrase","private key"] if k in t]

    def _host(u):
        try:
            s = u.split("://", 1)[1]
            return s.split("/", 1)[0].lower()
        except Exception:
            return ""
    
    shorteners = {"bit.ly","t.co","tinyurl.com","goo.gl","ow.ly","is.gd","buff.ly","rebrand.ly","shorturl.at","trib.al","lnkd.in"}
    has_shortener = any(_host(u) in shorteners for u in urls)
    sus_tlds = {"ru","cn","tk","gq","ml","cf"}
    has_bad_tld = any((_host(u).split(".")[-1] in sus_tlds) for u in urls if _host(u))

    score = 0
    if urgency: score += 18
    if fear: score += 24
    if greed: score += 20
    if sensitive: score += 26
    if has_shortener: score += 18
    if has_bad_tld: score += 16
    if len(urls) >= 2: score += 10
    score = max(0, min(100, score))
    verdict = "SAFE" if score < 40 else ("SUSPICIOUS" if score < 70 else "MALICIOUS")

    def _category():
        if any(w in t for w in ["sms","text message","mms"]):
            return "Smishing"
        if any(w in t for w in ["login","verify","update account","confirm"]) and urls:
            return "Phishing"
        if any(w in t for w in ["tech support","microsoft","virus","malware","teamviewer","anydesk"]):
            return "Tech Support Scam"
        if any(w in t for w in ["advance fee","processing fee","investment","inheritance"]):
            return "Advance Fee Fraud"
        if any(w in t for w in ["romance","love","relationship"]):
            return "Romance Scam"
        return "General Fraud / Unknown"
    
    category = _category()
    recommendation = "Do not click any links. Do not reply. Block the sender and report."
    if category == "Tech Support Scam":
        recommendation = "Do not call or grant remote access. Close the page and run trusted security software."
    elif category == "Smishing":
        recommendation = "Do not tap links from SMS. Delete and report to your carrier."
    elif category == "Advance Fee Fraud":
        recommendation = "Never pay upfront fees. Stop communication and report."
    elif category == "Romance Scam":
        recommendation = "Do not send money or gifts. Verify identity via trusted channels."
    elif category == "Phishing":
        recommendation = "Do not authenticate via the link. Use the official site and change passwords if interacted."

    lines = [
        "### 🛡️ Security Analysis",
        f"* **Risk Score:** {score}%",
        f"* **Verdict:** {verdict}",
        f"* **Detected Category:** {category}",
        "",
        "### 🚩 Red Flags Detected"
    ]
    
    flags = []
    if urgency: flags.append(("Urgency", f"Detected terms: {', '.join(sorted(set(urgency)))}"))
    if fear: flags.append(("Fear", f"Detected terms: {', '.join(sorted(set(fear)))}"))
    if greed: flags.append(("Greed", f"Detected terms: {', '.join(sorted(set(greed)))}"))
    if sensitive: flags.append(("Sensitive Data Request", f"Detected terms: {', '.join(sorted(set(sensitive)))}"))
    if has_shortener: flags.append(("Link Shortener", "Shortened URL obscures destination"))
    if has_bad_tld: flags.append(("Suspicious TLD", "Links use high-risk TLDs"))
    
    if flags:
        for k, v in flags[:6]:
            lines.append(f"* {k}: {v}")
    else:
        lines.append("* None significant detected.")
    
    lines.extend([
        "",
        "### 💡 Safety Recommendation",
        recommendation
    ])
    return "\n".join(lines)


def analyze_text(text):
    text = (text or "").strip()
    if not text:
        return "⚠️ Error: No text provided."
    
    if not model:
        return _fallback_analysis(text)

    prompt = f"""
You are a neutral Senior Cybersecurity Analyst. Analyze the following message for fraud.

Message:
\"\"\"{text}\"\"\"

Perform these checks:
1. Psychological Triggers: Urgency, Fear, Greed.
2. Technical Red Flags: mismatched domains, link shorteners, requests for sensitive data (passwords, 2FA/OTP).
3. Scam Category: Phishing, Smishing, Advance Fee Fraud, Romance Scam, Tech Support Scam.

Output Format (Markdown only):
### 🛡️ Security Analysis
* **Risk Score:** [0-100]%
* **Verdict:** [SAFE / SUSPICIOUS / MALICIOUS]
* **Detected Category:** [Category Name]

### 🚩 Red Flags Detected
* [Trigger 1]: [Explanation]
* [Trigger 2]: [Explanation]

### 💡 Safety Recommendation
[Specific advice based on the scam type]
""".strip()

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        if not content.startswith("### 🛡️ Security Analysis"):
            return _fallback_analysis(text)
        return content
    except Exception:
        return _fallback_analysis(text)


def analyze_audio(audio_file):
    if not model:
        return "⚠️ Error: Gemini API Key is missing. Check your .env file."
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.name).suffix) as tmp:
            tmp.write(audio_file.read())
            tmp_path = tmp.name
        
        # Upload to Gemini
        uploaded = genai.upload_file(tmp_path)
        
        prompt = """
You are a neutral Senior Cybersecurity Analyst. Listen to this audio message and analyze it for fraud.

Perform these checks:
1. Psychological Triggers: Urgency, Fear, Greed in the speaker's tone and words.
2. Technical Red Flags: requests for sensitive data (passwords, 2FA/OTP, bank details).
3. Scam Category: Phishing, Tech Support Scam, Vishing, Advance Fee Fraud, Romance Scam.

Output Format (Markdown only):
### 🛡️ Security Analysis
* **Risk Score:** [0-100]%
* **Verdict:** [SAFE / SUSPICIOUS / MALICIOUS]
* **Detected Category:** [Category Name]

### 🚩 Red Flags Detected
* [Trigger 1]: [Explanation]
* [Trigger 2]: [Explanation]

### 💡 Safety Recommendation
[Specific advice based on the scam type]
""".strip()
        
        response = model.generate_content([prompt, uploaded])
        
        # Cleanup
        os.unlink(tmp_path)
        uploaded.delete()
        
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error analyzing audio: {e}"


# Streamlit UI
st.set_page_config(page_title="🛡️ Scam Guard AI", page_icon="🛡️", layout="wide")

st.title("🛡️ Scam Guard AI")
st.caption("Powered by Google Gemini 1.5 Flash | Detects Phishing, Smishing, Vishing & More")

tab1, tab2 = st.tabs(["📝 Text Analysis", "🎤 Audio Analysis"])

with tab1:
    st.subheader("Paste a suspicious message")
    text_input = st.text_area("Message", placeholder="Paste the text here...", height=150)
    
    if st.button("🔍 Analyze Text", type="primary"):
        if text_input.strip():
            with st.spinner("Analyzing..."):
                result = analyze_text(text_input)
            st.markdown(result)
        else:
            st.warning("Please enter some text to analyze.")

with tab2:
    st.subheader("Upload a suspicious audio file")
    audio_file = st.file_uploader("Audio File", type=["mp3", "wav", "m4a", "ogg"], help="Upload voicemail or call recording")
    
    if st.button("🎧 Analyze Audio", type="primary"):
        if audio_file:
            with st.spinner("Processing audio..."):
                result = analyze_audio(audio_file)
            st.markdown(result)
        else:
            st.warning("Please upload an audio file.")

st.divider()
st.markdown("**🔐 Privacy:** All analysis happens securely. Your data is not stored.")