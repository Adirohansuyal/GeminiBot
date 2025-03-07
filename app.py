import streamlit as st
import base64
import os
import time
import io
import fitz  # PyMuPDF for PDF text extraction
import google.generativeai as genai
import google.api_core.exceptions
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dotenv import load_dotenv

# 🔑 Load API Key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API Key is missing! Set GOOGLE_API_KEY in .env")

genai.configure(api_key=API_KEY)

# 📌 Version Management
CURRENT_VERSION = "4.1.0"
VERSION_FILE = "version.txt"
DISMISS_FILE = "dismissed_update.txt"
EXCEL_FILE = "update_log.xlsx"

def get_stored_version(file):
    """Retrieve the stored version from a file."""
    if os.path.exists(file):
        with open(file, "r") as f:
            return f.read().strip()
    return "0.0.0"

def update_version_file():
    """Update the stored version when an update is detected."""
    with open(VERSION_FILE, "w") as f:
        f.write(CURRENT_VERSION)
    log_version_update()

def log_version_update():
    """Log version updates to an Excel file."""
    update_data = {"Version": [CURRENT_VERSION], "Details": ["Updating to the latest version."]}
    df = pd.DataFrame(update_data)

    if os.path.exists(EXCEL_FILE):
        existing_df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_excel(EXCEL_FILE, index=False)

def check_for_updates():
    """Check for new updates."""
    last_version = get_stored_version(VERSION_FILE)
    dismissed_version = get_stored_version(DISMISS_FILE)

    if last_version != CURRENT_VERSION:
        update_version_file()
        return True
    return dismissed_version != CURRENT_VERSION

def dismiss_update():
    """Dismiss the current update notification."""
    with open(DISMISS_FILE, "w") as f:
        f.write(CURRENT_VERSION)

# 🎨 UI Styling
st.markdown("""
    <style>
        body, .main, .stApp { font-family: 'Arial', sans-serif; }
        .stDownloadButton > button, .stButton > button {
            background-color: #004d7a; color: white; border-radius: 5px;
        }
        .sidebar .sidebar-content { background: linear-gradient(to right, #004d7a, #008793); color: white; }
    </style>
""", unsafe_allow_html=True)

# 🌙 Dark Mode
if st.sidebar.toggle("🌙 Dark Mode", value=True):
    st.markdown("""
        <style>
            body, .main, .stApp { background: linear-gradient(to right, #000000, #434343); color: white !important; }
            h1, h2, h3, p, .stMarkdown { color: white !important; }
        </style>
    """, unsafe_allow_html=True)

# 🎨 Sidebar Navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📄 PDF Processing", "💬 Chat with AI", "🔔 Updates"])

# 🚀 Home Page
if page == "🏠 Home":
    st.title("Aerri AI - Your Personal AI Assistant")

    # Set Background Image
    background_image_path = "ai.jpg"
    if os.path.exists(background_image_path):
        with open(background_image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode()
        st.markdown(f"""
            <style>
                .stApp {{
                    background: url("data:image/jpg;base64,{encoded_image}") no-repeat center center fixed;
                    background-size: cover;
                }}
            </style>
        """, unsafe_allow_html=True)

    st.markdown('<p style="color : orange; font-weight: bold;">🚀 Your AI-powered assistant for PDF processing, summarization, and Q&A.</p>', unsafe_allow_html=True)

    st.markdown("\n\n")
    st.markdown("\n\n")
    st.markdown("🔥 **RECENT UPDATES:**")
    st.markdown("**📌 Enhances the Background Image ✅**")
    st.markdown("**📌 Improved Chatbot Experience ✅**")
    st.markdown("**📌 Added PDF Processing Feature ✅**")


    # 🚨 Update Notification
    if check_for_updates():
        st.markdown(f"<h3 style='color:red;'>⚡ New Update Available! (v{CURRENT_VERSION})</h3>", unsafe_allow_html=True)
        if st.button("✅ Dismiss Update Notification"):
            dismiss_update()
            st.rerun()

# 🔔 Updates Page
elif page == "🔔 Updates":
    st.title("🔔 Latest Updates")
    st.write(f"🚀 **Current Version:** {CURRENT_VERSION}")
    if check_for_updates():
        st.markdown("<h3 style='color:red;'>⚡ New Update Available!</h3>", unsafe_allow_html=True)
        if st.button("✅ Dismiss Update Notification"):
            dismiss_update()
            st.rerun()

# 📄 PDF Processing Page
elif page == "📄 PDF Processing":
    st.title("📂 PDF Processing")

    uploaded_file = st.file_uploader("📂 Upload a PDF file", type=["pdf"])

    def extract_text_from_pdf(pdf_file):
        """Extract text from a PDF."""
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return "\n".join([page.get_text("text") for page in doc])

    def generate_pdf(content):
        """Generate a PDF with summarized content."""
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 12)

        y_position = height - 50
        for line in content.split("\n"):
            if y_position < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 50
            c.drawString(50, y_position, line)
            y_position -= 20

        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer

    if uploaded_file:
        pdf_text = extract_text_from_pdf(uploaded_file)
        if pdf_text.strip():
            st.text_area("PDF Content", pdf_text[:5000], height=300)

            summary_format = st.radio("Choose Summary Format:", ["📄 Paragraph", "📌 Bullet Points"], horizontal=True)

            try:
                model = genai.GenerativeModel("gemini-1.5-pro-latest")
                prompt = f"Summarize this text in {'a paragraph' if summary_format == '📄 Paragraph' else 'bullet points'}:\n\n{pdf_text[:8000]}"
                response = model.generate_content(prompt)
                summary = response.text
            except google.api_core.exceptions.GoogleAPIError:
                summary = "⚠️ Error. Please try again."

            st.success("Summary Created!")
            st.markdown(summary.replace("\n", "\n\n"))

            pdf_file = generate_pdf(summary)
            st.download_button("📥 Download Summary as PDF", data=pdf_file, file_name="summary.pdf", mime="application/pdf")

# 💬 Chatbot Page
# 💬 Chatbot Page
elif page == "💬 Chat with AI":
    st.title("💬 Chat with Aerri AI")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("💬 Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                model = genai.GenerativeModel("gemini-1.5-pro-latest")
                response = model.generate_content(user_input)
                bot_reply = response.text
            except google.api_core.exceptions.GoogleAPIError:
                bot_reply = "⚠️ Error. Please try again."

            # ⌨️ Typing Animation Effect
            for char in bot_reply:
                full_response += char
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.02)  # Simulating typing speed

            message_placeholder.markdown(full_response)  # Final response without cursor
            st.session_state.messages.append({"role": "assistant", "content": full_response})
