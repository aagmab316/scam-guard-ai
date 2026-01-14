# 🛡️ ScamGuard AI
> **Protecting seniors from digital fraud using AI-powered Text & Audio analysis.**

## 🚨 The Problem
Every year, seniors lose **billions of dollars** to phishing scams, fake bank alerts, and "grandchild in trouble" voice scams. They often struggle to identify the subtle psychological triggers in these messages.

## 💡 The Solution
**ScamGuard AI** is a real-time detection tool that acts as a digital bodyguard.
* **📝 Text Analysis:** Scans SMS/Emails for urgency, threats, and suspicious links.
* **🎤 Audio Analysis:** Transcribes voice notes to detect "fake emergency" calls using OpenAI Whisper.
* **🧠 Simple Verdicts:** Gives a clear "Safe" or "Dangerous" score so users don't have to guess.

## ⚙️ How It Works
1.  **Frontend:** Built with Streamlit for an accessible, high-contrast UI.
2.  **Intelligence:** Uses `GPT-4o-mini` to analyze linguistic patterns (fear, greed, urgency).
3.  **Audio:** Uses `Whisper-1` to convert audio to text for deep analysis.

## 🚀 How to Run Locally
1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/aagmab316/scam-guard-ai.git](https://github.com/aagmab316/scam-guard-ai.git)
    cd scam-guard-ai
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up keys:**
    Create a `.env` file and add: `OPENAI_API_KEY=your_key_here`
4.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

## 🏆 Hackathon Tracks
* AI for Social Good
* Senior Safety
