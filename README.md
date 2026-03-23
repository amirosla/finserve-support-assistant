# FinServe — AI Support Assistant

A proof-of-concept AI tool for automating client support at FinServe, a financial services company offering lending and credit products to SMEs and retail clients.

## What it does

Client support teams at FinServe currently handle every incoming email and ticket manually — no shared knowledge base, no standard responses, no prioritization system. This tool addresses that problem by:

- **Classifying** incoming client messages into categories (loan status, payment issues, KYC, complaints, etc.)
- **Assessing priority** (High / Medium / Low) based on urgency and business impact
- **Generating a draft response** in the client's language (Polish or English), ready to review and send
- **Tracking ticket history** within the session so agents have context at a glance

The interface is available in Polish and English.

## Tech stack

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/) — web interface
- [Anthropic Claude API](https://www.anthropic.com/) — classification and response generation
- [python-dotenv](https://pypi.org/project/python-dotenv/) — environment variable management

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/amirosla/finserve-support-assistant.git
   cd finserve-support-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the provided template:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Open your browser at `http://localhost:8501`

## Project context

Built as part of an assessment task simulating a real AI automation project for a financial services company. The goal was to identify business problems suitable for AI/automation and deliver a working proof-of-concept within a few hours.
