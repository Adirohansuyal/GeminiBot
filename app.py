import streamlit as st
import time
import io
import os
import fitz  # PyMuPDF for PDF text extraction
import google.generativeai as genai
import google.api_core.exceptions
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from dotenv import load_dotenv

# 🔑 Load API Key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API Key is missing! Set GOOGLE_API_KEY in .env")

genai.configure(api_key=API_KEY)

# 📌 Version Management
CURRENT_VERSION = "1.2.0"  # Update this when pushing new versions
VERSION_FILE = "version.txt"

def check_for_updates():
    try:
        with open(VERSION_FILE, "r") as f:
            last_version = f.read().strip()
    except FileNotFoundError:
        last_version = "0.0.0"

    return last_version != CURRENT_VERSION

def update_version_file():
    with open(VERSION_FILE, "w") as f:
        f.write(CURRENT_VERSION)

# 🎨 UI Styling
st.markdown("""
    <style>
        body, .main, .stApp { font-family: 'Arial', sans-serif; }
        .sidebar .sidebar-content { background: linear-gradient(to right, #004d7a, #008793); color: white; }
        .stDownloadButton > button { background-color: #008793; color: white; font-size: 14px; }
        .stButton > button { background-color: #004d7a; color: white; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# 🌙 Theme Handling
theme_choice = st.sidebar.toggle("🌙 Dark Mode", value=True)
if theme_choice:
    st.markdown("""
        <style>
            body, .main, .stApp { background: linear-gradient(to right, #000000, #434343); color: white !important; }
            h1, h2, h3, p, .stMarkdown { color: white !important; }
        </style>
    """, unsafe_allow_html=True)

# 🎨 Sidebar Navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📄 PDF Processing", "💬 Chat with AI", "🔔 Updates"])

# 🎯 Home Page
if page == "🏠 Home":
    st.title("Aerri AI 👾")
    
    # 🚨 Flashing Update Message
    if check_for_updates():
        for _ in range(1):  # Blink 5 times
            st.markdown("<h3 style='color:red;'>⚡ New Update Available! [Check Updates](#updates)</h3>", unsafe_allow_html=True)
            time.sleep(0.5)
            st.markdown("")  # Clear the message
            time.sleep(0.5)

        # Update version file so message doesn't show next time
        update_version_file()

    st.write("🚀 Your AI-powered assistant for PDF processing, summarization, and Q&A.")

    st.markdown("""
    **Features:**
    - 📂 Upload PDFs and extract text
    - 🤖 AI-powered text summarization
    - 📌 Bullet-point summaries
    - 🎤 Voice input for queries
    - 💬 Interactive AI chatbot
    - 📥 Download AI-generated summaries
    """)

# 📄 PDF Processing Page
elif page == "📄 PDF Processing":
    st.title("📂 PDF Processing")

    uploaded_file = st.file_uploader("📂 Upload a PDF file", type=["pdf"])

    def extract_text_from_pdf(pdf_file):
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return "\n".join([page.get_text("text") for page in doc])

    def generate_pdf(content, filename="summary.pdf"):
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 12)

        lines = simpleSplit(content, "Helvetica", 12, width - 100)
        y_position = height - 50

        for line in lines:
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
        with st.spinner("🔍 Extracting text..."):
            pdf_text = extract_text_from_pdf(uploaded_file)

        if pdf_text.strip():
            with st.expander("📄 **View Extracted Text**", expanded=False):
                st.text_area("PDF Content", pdf_text[:5000], height=300)

            summary_format = st.radio("Choose Summary Format:", ["📄 Paragraph", "📌 Bullet Points"], horizontal=True)

            try:
                with st.spinner("🤖 Aerri AI is generating..."):
                    model = genai.GenerativeModel("gemini-1.5-pro-latest")

                    if summary_format == "📄 Paragraph":
                        prompt = f"Summarize this text in a concise paragraph:\n\n{pdf_text[:8000]}"
                    else:
                        prompt = f"""
                        Summarize this text in **bullet points**:
                        - **Use concise sentences**
                        - **Group related points together**
                        - **Start each point with 📌**
                        
                        Text to summarize:
                        {pdf_text[:8000]}
                        """

                    response = model.generate_content(prompt)
                    summary = response.text

            except google.api_core.exceptions.ResourceExhausted:
                summary = "⚠️ Server Error. Please try again."
            except google.api_core.exceptions.GoogleAPIError:
                summary = "⚠️ An error occurred. Try later."

            st.success("Summary Created!")
            st.markdown(summary.replace("\n", "\n\n"))

            pdf_file = generate_pdf(summary, "summary.pdf")
            st.download_button(
                label="📥 Download Summary as PDF",
                data=pdf_file,
                file_name="summary.pdf",
                mime="application/pdf"
            )

# 💬 Chatbot Section
elif page == "💬 Chat with Ai":
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

        try:
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            response = model.generate_content(user_input)
            bot_reply = response.text
        except google.api_core.exceptions.GoogleAPIError:
            bot_reply = "⚠️ Error. Please try again."

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

# 🔔 Updates Section
elif page == "🔔 Updates":
    st.title("🔔 Latest Updates")
    st.write("📢 Version 1.1.0 - Added Update Notifications & Chat Enhancements!")
