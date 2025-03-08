import streamlit as st

st.set_page_config(page_title="Aerri AI", page_icon="ai.jpg", layout="centered", initial_sidebar_state="expanded")

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
API_KEY = "AIzaSyB_dWktJovtRo_uej_NJSAV0wfUQ0D8ITI"
if not API_KEY:
    raise ValueError("API Key is missing! Set GOOGLE_API_KEY in .env")

genai.configure(api_key=API_KEY)

# 📌 Version Management
CURRENT_VERSION = "4.5.0" \
" w.e.f 7 March 2025"
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
        /* Sidebar background color */
        section[data-testid="stSidebar"] {
            background: linear-gradient(to bottom, #004d7a, #008793);
            color: white;
        }
        /* Sidebar content */
        .sidebar .sidebar-content {
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# 🌙 Dark Mode
if st.sidebar.toggle("☀️ Light Mode", value=True):
    st.markdown("""
        <style>
            body, .main, .stApp { background: linear-gradient(to right, #000000, #434343); color: white !important; }
            h1, h2, h3, p, .stMarkdown { color: white !important; }
        </style>
    """, unsafe_allow_html=True)

# 🎨 Sidebar Navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📄 PDF Processing", "💬 Chat with AI", "🔔 Updates", " 🛠️Detection and Translation Tool"])

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
    st.markdown("**📌 Resolved Error of blank pdf ✅**")
    st.markdown("**📌 Improved Chatbot Experience ✅**")
    st.markdown("**📌 Added PDF Processing Feature ✅**")


    # 🚨 Update Notification
    if check_for_updates():
        st.markdown(f"<h3 style='color:red;'>⚡ New Update Available! (v{CURRENT_VERSION})</h3>", unsafe_allow_html=True)
        if st.button("✅ Dismiss Update Notification"):
            dismiss_update()
            st.rerun()


elif page == "PDF Preprocessing 2":



    import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes
from langdetect import detect
from io import BytesIO
from gtts import gTTS
from fpdf import FPDF
from langcodes import Language
from deep_translator import GoogleTranslator
import streamlit as st
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

st.title("📄 PDF & Image Analysis Tool")

uploaded_file = st.file_uploader("Upload a PDF or an Image", type=["pdf", "jpeg", "jpg", "png"])

# Load AI models for image description & question answering
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
description_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
vqa_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-vqa-base")

# **Language Mapping for gTTS**
language_map = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Hindi": "hi",
    "Chinese": "zh",
    "Japanese": "ja",
    "Arabic": "ar",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru"
}

def generate_image_description(image):
    """Generate a detailed description of an image using BLIP model."""
    inputs = processor(image, return_tensors="pt")
    output = description_model.generate(**inputs, max_length=150)
    description = processor.decode(output[0], skip_special_tokens=True)
    return description

def answer_image_question(image, question):
    """Answer a user question about the image using the VQA model."""
    inputs = processor(image, question, return_tensors="pt")
    output = vqa_model.generate(**inputs, max_length=50)
    answer = processor.decode(output[0], skip_special_tokens=True)
    return answer

if uploaded_file is not None:
    file_type = uploaded_file.type

    if file_type in ["image/jpeg", "image/jpg", "image/png"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # **Generate Image Description**
        st.subheader("🖼️ Image Analysis & Description")
        description = generate_image_description(image)
        st.write("**Detailed Description:**", description)

        # **Ask Questions About the Image**
        st.subheader("❓ Ask a Question About the Image")
        user_question = st.text_input("Enter your question:")

        if user_question:
            answer = answer_image_question(image, user_question)
            st.write("**Answer:**", answer)

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
# 📄 PDF Processing Page
# 📄 PDF Processing Page
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
            st.session_state["pdf_text"] = pdf_text  # Store in session state
            st.text_area("📜 PDF Content", pdf_text[:5000], height=300)

            # 📝 Choose Summary Length
            summary_length = st.selectbox("📏 Choose Summary Length:", ["Short", "Medium", "Long"])

            # 📌 Choose Summary Format
            summary_format = st.radio("📄 Choose Summary Format:", ["📄 Paragraph", "📌 Bullet Points"], horizontal=True)

            # 🔄 Define Summary Length Limits
            length_limits = {"Short": 500, "Medium": 1000, "Long": 2000}

            try:
                model = genai.GenerativeModel("gemini-1.5-pro-latest")
                prompt = f"Summarize this text in {'a paragraph' if summary_format == '📄 Paragraph' else 'bullet points'}, keeping it {summary_length.lower()} (around {length_limits[summary_length]} words):\n\n{pdf_text[:8000]}"
                response = model.generate_content(prompt)
                summary = response.text
            except google.api_core.exceptions.GoogleAPIError:
                summary = "⚠️ Error. Please try again."

            st.success(f"✅ {summary_length} Summary Created!")
            st.markdown(summary.replace("\n", "\n\n"))

            # 📥 Generate & Download Summary PDF
            pdf_file = generate_pdf(summary)
            st.download_button("📥 Download Summary as PDF", data=pdf_file, file_name="summary.pdf", mime="application/pdf")

            # 📌 **Question Suggestions for Chatbot**
            st.markdown("### ❓ Suggested Questions")
            suggested_questions = [
                "What is the main topic of this document?",
                "Summarize the key findings in this PDF.",
                "Are there any important statistics or data points?",
                "What conclusions are drawn in this document?",
                "List the key points discussed.",
            ]

            # Show suggested questions as buttons
            for question in suggested_questions:
                if st.button(question):
                    st.session_state["pdf_question"] = question

            # 📌 **Ask a Custom Question Section**
            if "ask_question" not in st.session_state:
                st.session_state["ask_question"] = False

            if st.button("💬 Ask a Question"):
                st.session_state["ask_question"] = True

            if st.session_state["ask_question"]:
                user_question = st.text_input("🔍 Type your question here:")
                if user_question:
                    try:
                        prompt = f"Based on the following PDF content, answer this question:\n\nPDF Content:\n{pdf_text[:8000]}\n\nQuestion: {user_question}"
                        response = model.generate_content(prompt)
                        st.markdown(f"**🤖 Answer:**\n{response.text}")
                    except google.api_core.exceptions.GoogleAPIError:
                        st.error("⚠️ Error fetching response. Please try again.")

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
