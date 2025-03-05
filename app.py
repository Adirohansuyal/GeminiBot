import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import io
import google.generativeai as genai
import google.api_core.exceptions
import speech_recognition as sr
from PIL import Image
import fitz  # PyMuPDF for PDF text extraction

# 🔑 Configure API Key
genai.configure(api_key="AIzaSyDzX9W_XsaJOGDH0xnqesMEQJiBMILm0q4")

# 🌙 Theme State Handling
if "theme" not in st.session_state:
    st.session_state.theme = "light"  # Default theme

# 🎨 Theme Selection in Sidebar
st.sidebar.title("🎨 Theme Selection")
if st.sidebar.button("🌞 Light Theme"):
    st.session_state.theme = "light"
if st.sidebar.button("🌙 Dark Theme"):
    st.session_state.theme = "dark"

# 🎨 Apply Theme Styling
if st.session_state.theme == "dark":
    st.markdown("""
        <style>
            body, .main, .stApp { background: linear-gradient(to right, #000000, #434343); color: white !important; }
            h1, h2, h3, p, .stMarkdown { color: white !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body, .main, .stApp { background: linear-gradient(to right, #cbe8f8, #aee1fc); color: black !important; }
            h1, h2, h3, p, .stMarkdown { color: black !important; }
        </style>
    """, unsafe_allow_html=True)

# 🎨 Streamlit UI
st.title("Aerri AI 👾")
st.write("Ask me anything or upload a PDF to Aerri AI")

# 📄 PDF File Upload
uploaded_file = st.file_uploader("📂 Upload a PDF file", type=["pdf"])

# 📜 Function to Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

# 📄 Function to Generate PDF
def generate_pdf(content, filename="summary.pdf"):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)

    lines = simpleSplit(content, "Helvetica", 12, width - 100)  # Auto-wrap text
    y_position = height - 50  # Start position for text

    for line in lines:
        if y_position < 50:  # If text reaches bottom, create a new page
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50
        c.drawString(50, y_position, line)
        y_position -= 20  # Move to next line

    c.save()
    pdf_buffer.seek(0)  # Reset buffer position
    return pdf_buffer

# 🟢 If PDF is uploaded, extract and display text
if uploaded_file:
    with st.spinner("🔍 Extracting text..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    if pdf_text.strip():
        st.subheader("📄 Extracted Text")
        st.text_area("PDF Content", pdf_text[:2000], height=300)

        # 🤖 AI-Powered Summary
        try:
            with st.spinner("🤖 Aerri AI is generating..."):
                model = genai.GenerativeModel("gemini-1.5-pro-latest")
                response = model.generate_content(f"Summarize this text:\n\n{pdf_text[:8000]}")
                summary = response.text
        except google.api_core.exceptions.ResourceExhausted:
            summary = "⚠️ Can't Connect to the Server, Please relaunch the app."
        except google.api_core.exceptions.GoogleAPIError:
            summary = "⚠️ An error occurred. Please try again later."

        st.subheader("📌 AI-Generated Summary")
        st.success("Summary Created!")
        st.write(summary)

        # 📥 Download AI-Generated Summary as PDF
        pdf_file = generate_pdf(summary, "summary.pdf")
        st.download_button(
            label="📥 Download Summary as PDF",
            data=pdf_file,
            file_name="summary.pdf",
            mime="application/pdf"
        )

        # ❓ User Question Input
        question = st.text_input("💬 Ask a question about the document:")

        # 📌 Bullet Summary Button
        if st.button("📌 Generate Bullet Summary"):
            try:
                with st.spinner("🤖 Generating Bullet Summary..."):
                    bullet_summary_prompt = f"Summarize the following text into bullet points:\n\n{pdf_text[:8000]}"
                    bullet_response = model.generate_content(bullet_summary_prompt)
                    bullet_summary = bullet_response.text
            except google.api_core.exceptions.ResourceExhausted:
                bullet_summary = "⚠️ Can't Connect to the Server, Please try again."
            except google.api_core.exceptions.GoogleAPIError:
                bullet_summary = "⚠️ An error occurred. Please try again later."

            st.subheader("📌 Bullet-Point Summary")
            st.write(bullet_summary)

            # 📥 Download Bullet Summary as PDF
            pdf_file_bullet = generate_pdf(bullet_summary, "bullet_summary.pdf")
            st.download_button(
                label="📥 Download Bullet Summary as PDF",
                data=pdf_file_bullet,
                file_name="bullet_summary.pdf",
                mime="application/pdf"
            )

        # 🎤 **Voice Input Feature**
        def recognize_speech():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎙️ Speak now...")
                audio = r.listen(source)
                try:
                    return r.recognize_google(audio)
                except sr.UnknownValueError:
                    return "Could not understand audio"
                except sr.RequestError:
                    return "Error with the recognition service"

        # 🔊 Store voice question in session state
        if "voice_question" not in st.session_state:
            st.session_state.voice_question = ""

        if st.button("🎤 Ask with Voice"):
            st.session_state.voice_question = recognize_speech()

        # Display the voice input text
        question = st.text_input("Your Question:", st.session_state.voice_question)

        # 🤖 AI Response for Question
        if question:
            try:
                with st.spinner("🤖 Thinking..."):
                    response = model.generate_content(f"Based on the document:\n\n{pdf_text}\n\nAnswer this question: {question}")
                    answer = response.text
            except google.api_core.exceptions.ResourceExhausted:
                answer = "⚠️ Can't Connect to the Server, Please try again."
            except google.api_core.exceptions.GoogleAPIError:
                answer = "⚠️ An error occurred. Please try again later."

            st.subheader("🤖 AI Answer:")
            st.write(answer)
    else:
        st.error("No text found in the PDF. Try another file!")

# 🗨️ **AI Chatbot Section**

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
        response = model.generate_content([msg["content"] for msg in st.session_state.messages])
        bot_reply = response.text
    except google.api_core.exceptions.ResourceExhausted:
        bot_reply = "⚠️ Can't Connect to the Server, Please try again."
    except google.api_core.exceptions.GoogleAPIError:
        bot_reply = "⚠️ An error occurred. Please try again later."

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

# 🗑️ Clear Chat Button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
