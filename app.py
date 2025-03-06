import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import io
import google.generativeai as genai
import google.api_core.exceptions
import fitz  # PyMuPDF for PDF text extraction
from dotenv import load_dotenv
import os

# 🔑 Load API Key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API Key is missing! Set GOOGLE_API_KEY in .env")

genai.configure(api_key=API_KEY)

# 📌 Define App Version
CURRENT_VERSION = "1.1.0"  # Change this when updating

# 📂 File to Store Last Notified Version
VERSION_FILE = "version.txt"

# 🚀 Check for Updates
def check_for_updates():
    try:
        with open(VERSION_FILE, "r") as f:
            last_version = f.read().strip()
    except FileNotFoundError:
        last_version = "0.0.0"  # Default if no version file exists

    if last_version != CURRENT_VERSION:
        st.sidebar.markdown("⚡ **New Update Available!** [Check Updates](#updates)")
        with open(VERSION_FILE, "w") as f:
            f.write(CURRENT_VERSION)

# 🌙 Theme Handling
st.markdown("""
    <style>
        body, .main, .stApp { font-family: 'Arial', sans-serif; }
        .sidebar .sidebar-content { background: linear-gradient(to right, #004d7a, #008793); color: white; }
        .stDownloadButton > button { background-color: #008793; color: white; font-size: 14px; }
        .stButton > button { background-color: #004d7a; color: white; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# 🎨 Sidebar Navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📄 PDF Processing", "💬 Chat with AI", "🔔 Updates"])

# ✅ Check for Updates
check_for_updates()

# 🏠 Home Page
if page == "🏠 Home":
    st.title("Aerri AI 👾")
    st.write("🚀 Your AI-powered assistant for PDF processing, summarization, and Q&A.")

    # 🚨 Flashing Message for Updates
    with open(VERSION_FILE, "r") as f:
        last_version = f.read().strip()
    if last_version != CURRENT_VERSION:
        st.markdown("⚡ **New Update Available!** [Check Updates](#updates)", unsafe_allow_html=True)

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

    # 📄 PDF Upload
    uploaded_file = st.file_uploader("📂 Upload a PDF file", type=["pdf"])

    # 📜 Function to Extract Text from PDF
    def extract_text_from_pdf(pdf_file):
        pdf_bytes = pdf_file.read()  # Read the file as bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")  # Open PDF with PyMuPDF
        return "\n".join([page.get_text("text") for page in doc])  # Extract text

    # 📄 Function to Generate PDF
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

    # 🟢 Extract Text and Process AI Summaries
    if uploaded_file:
        with st.spinner("🔍 Extracting text..."):
            pdf_text = extract_text_from_pdf(uploaded_file)

        if pdf_text.strip():
            with st.expander("📄 **View Extracted Text**", expanded=False):
                st.text_area("PDF Content", pdf_text[:5000], height=300)

            # 🎯 Choose Summary Type
            summary_format = st.radio("Choose Summary Format:", ["📄 Paragraph", "📌 Bullet Points"], horizontal=True)

            # 🤖 AI-Powered Summary
            try:
                with st.spinner("🤖 Aerri AI is generating..."):
                    model = genai.GenerativeModel("gemini-1.5-pro-latest")

                    prompt = f"Summarize this text in a {'paragraph' if summary_format == '📄 Paragraph' else 'bullet point list'}:\n\n{pdf_text[:8000]}"
                    response = model.generate_content(prompt)
                    summary = response.text

            except google.api_core.exceptions.ResourceExhausted:
                summary = "⚠️ Can't Connect to the Server, Please relaunch the app."
            except google.api_core.exceptions.GoogleAPIError:
                summary = "⚠️ An error occurred. Please try again later."

            st.success("Summary Created!")

            # 📌 Display Summary Properly
            st.markdown(summary)

            # 📥 Download AI Summary as PDF
            pdf_file = generate_pdf(summary, "summary.pdf")
            st.download_button(
                label="📥 Download Summary as PDF",
                data=pdf_file,
                file_name="summary.pdf",
                mime="application/pdf"
            )

# 💬 Chatbot Section
elif page == "💬 Chat with AI":
    st.title("💬 Chat with Aerri AI")

    # 🔄 Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 📌 Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 💬 User Chat Input
    user_input = st.chat_input("💬 Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 🤖 AI Response
        try:
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            response = model.generate_content([msg["content"] for msg in st.session_state.messages[-5:]])
            bot_reply = response.text
        except google.api_core.exceptions.ResourceExhausted:
            bot_reply = "⚠️ Can't Connect to the Server, Please try again."
        except google.api_core.exceptions.GoogleAPIError:
            bot_reply = "⚠️ An error occurred. Please try again later."

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

# 🔔 Updates Section
elif page == "🔔 Updates":
    st.title("🔔 Latest Updates")
    st.markdown("""
    - 📢 **v1.1.0 (New Update!):** Flashing notification for new updates added.
    - 🔥 **v1.0.0:** Initial release with AI-powered PDF summarization & chatbot.
    """)

