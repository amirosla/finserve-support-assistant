import os
import json
import anthropic
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

TRANSLATIONS = {
    "en": {
        "title": "FinServe — AI Support Assistant",
        "caption": "Proof of concept: automated ticket classification and response drafting",
        "load_example": "Load an example ticket",
        "client_message": "Client message",
        "placeholder": "Paste or type the client's message here...",
        "button": "Analyze & Draft Response",
        "warning": "Please enter a client message first.",
        "analyzing": "Analyzing ticket...",
        "category": "Category",
        "priority": "Priority",
        "confidence": "Confidence",
        "summary_label": "Summary",
        "draft_title": "Draft Response",
        "draft_caption": "Ready to send — edit before sending",
        "history_title": "Ticket History",
        "history_empty": "No tickets analyzed yet.",
        "raw_output": "Raw API output",
        "examples": {
            "Select an example...": "",
            "Loan status inquiry": "Hello, I would like to ask about the status of my loan application submitted 2 weeks ago. The application number is CR-2024-1892. When can I expect a decision?",
            "Payment issue": "Hi, I was supposed to receive my loan disbursement yesterday but nothing arrived in my account. My loan agreement number is LA-5521. This is urgent as I need the funds for payroll tomorrow.",
            "Complaint": "I am very dissatisfied with the service. I have been waiting 3 weeks for a response regarding my complaint about charged interest. No one has contacted me. I am considering escalating this to the financial regulator.",
            "KYC documents": "Hello, I received an email saying I need to provide additional documents for KYC verification. Could you let me know exactly what documents are needed and how to submit them?",
        },
    },
    "pl": {
        "title": "FinServe — Asystent Wsparcia AI",
        "caption": "Proof of concept: automatyczna klasyfikacja zgłoszeń i szkicowanie odpowiedzi",
        "load_example": "Załaduj przykładowe zgłoszenie",
        "client_message": "Wiadomość klienta",
        "placeholder": "Wklej lub wpisz wiadomość klienta...",
        "button": "Analizuj i przygotuj odpowiedź",
        "warning": "Najpierw wpisz wiadomość klienta.",
        "analyzing": "Analizowanie zgłoszenia...",
        "category": "Kategoria",
        "priority": "Priorytet",
        "confidence": "Pewność",
        "summary_label": "Podsumowanie",
        "draft_title": "Szkic odpowiedzi",
        "draft_caption": "Gotowe do wysłania — edytuj przed wysłaniem",
        "history_title": "Historia zgłoszeń",
        "history_empty": "Brak przeanalizowanych zgłoszeń.",
        "raw_output": "Surowa odpowiedź API",
        "examples": {
            "Wybierz przykład...": "",
            "Status wniosku": "Dzień dobry, chciałam zapytać o status mojego wniosku kredytowego złożonego 2 tygodnie temu. Numer wniosku to CR-2024-1892. Kiedy mogę spodziewać się decyzji?",
            "Problem z płatnością": "Dzień dobry, wczoraj miałam otrzymać wypłatę pożyczki, jednak nic nie wpłynęło na moje konto. Numer umowy to LA-5521. Sprawa jest pilna — jutro muszę wypłacić wynagrodzenia pracownikom.",
            "Skarga": "Jestem bardzo niezadowolona z obsługi. Czekam już 3 tygodnie na odpowiedź w sprawie mojej reklamacji dotyczącej naliczonych odsetek. Nikt się ze mną nie kontaktuje. Rozważam skierowanie sprawy do KNF.",
            "Weryfikacja dokumentów KYC": "Dzień dobry, otrzymałam email z informacją, że muszę dostarczyć dodatkowe dokumenty do weryfikacji KYC. Proszę o informację, jakie dokładnie dokumenty są wymagane i jak je przesłać.",
        },
    },
}

def build_system_prompt(lang: str) -> str:
    if lang == "pl":
        summary_instruction = "one sentence summary of the client's issue in Polish"
        categories = '"Zapytanie o status wniosku" / "Problem z płatnością" / "KYC i dokumentacja" / "Skarga" / "Wcześniejsza spłata" / "Zapytanie ogólne"'
    else:
        summary_instruction = "one sentence summary of the client's issue in English"
        categories = '"Loan Status Inquiry" / "Payment Issue" / "KYC & Documentation" / "Complaint" / "Early Repayment" / "General Inquiry"'

    return f"""You are a client support assistant for FinServe, a financial services company
offering lending and credit products to SMEs and retail clients.

Analyze the incoming client message and return a JSON object with exactly these fields:

{{
  "category": one of: {categories},
  "priority": one of: "High" / "Medium" / "Low",
  "confidence": integer from 0 to 100 representing how confident you are in your classification,
  "summary": {summary_instruction},
  "draft_response": a professional, empathetic response in the same language as the client's message (Polish if Polish, English if English). Address the concern, explain next steps, use [CLIENT_NAME] and [CASE_NUMBER] placeholders.
}}

Priority rules:
- High: complaints, payment failures, urgent legal/compliance issues
- Medium: loan status, documentation requests, repayment questions
- Low: general questions, information requests

Return only valid JSON, no extra text.
"""

PRIORITY_COLORS = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
PRIORITY_PL = {"High": "Wysoki", "Medium": "Średni", "Low": "Niski"}

st.set_page_config(page_title="FinServe AI Support", page_icon="🏦", layout="wide")

col_lang, _ = st.columns([1, 5])
with col_lang:
    lang = st.selectbox("", ["English", "Polski"], label_visibility="collapsed")

t = TRANSLATIONS["pl"] if lang == "Polski" else TRANSLATIONS["en"]

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.subheader(t["history_title"])
    if not st.session_state.history:
        st.caption(t["history_empty"])
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            priority = item["priority"]
            color = PRIORITY_COLORS.get(priority, "⚪")
            label = PRIORITY_PL.get(priority, priority) if lang == "Polski" else priority
            with st.container(border=True):
                st.caption(f"{color} {label} · {item['category']}")
                st.caption(item["summary"])

st.title(t["title"])
st.caption(t["caption"])
st.divider()

example = st.selectbox(t["load_example"], options=list(t["examples"].keys()))
ticket_text = st.text_area(
    t["client_message"],
    value=t["examples"][example],
    height=150,
    placeholder=t["placeholder"],
)

analyze = st.button(t["button"], type="primary", use_container_width=True)

if analyze:
    if not ticket_text.strip():
        st.warning(t["warning"])
    else:
        with st.spinner(t["analyzing"]):
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=build_system_prompt("pl" if lang == "Polski" else "en"),
                messages=[{"role": "user", "content": ticket_text}],
            )
            raw = message.content[0].text

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        try:
            data = json.loads(cleaned.strip())
        except json.JSONDecodeError:
            st.error("Failed to parse response. Try again.")
            st.code(raw)
            st.stop()

        st.session_state.history.append(data)

        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            category = data.get("category", "—")
            st.metric(t["category"], category)
        with col2:
            priority = data.get("priority", "—")
            color = PRIORITY_COLORS.get(priority, "⚪")
            label = PRIORITY_PL.get(priority, priority) if lang == "Polski" else priority
            st.metric(t["priority"], f"{color} {label}")
        with col3:
            confidence = data.get("confidence", 0)
            st.metric(t["confidence"], f"{confidence}%")

        summary = data.get("summary", "")
        if summary:
            st.info(f"**{t['summary_label']}:** {summary}")

        st.subheader(t["draft_title"])
        st.caption(t["draft_caption"])
        st.text_area(
            "",
            value=data.get("draft_response", "").strip(),
            height=220,
            label_visibility="collapsed",
        )
