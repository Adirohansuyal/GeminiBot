import streamlit as st
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

# 🎨 Theme Buttons
st.sidebar.title("🎨 Theme Selection")
if st.sidebar.button("🌞 Light Theme"):
    st.session_state.theme = "light"
if st.sidebar.button("🌙 Dark Theme"):
    st.session_state.theme = "dark"

# 🎨 Apply Full Page Background Theme
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

# 🟢 If PDF is uploaded, extract and display text
if uploaded_file:
    with st.spinner("🔍 Extracting text..."):
        pdf_text = extract_text_from_pdf(uploaded_file)

    if pdf_text.strip():
        st.subheader("📄 Extracted Text")
        st.text_area("PDF Content", pdf_text[:2000], height=300)

        # 🤖 AI-Powered Summary
        try:
            with st.spinner("🤖 AerriAI is generating..."):
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

        # 📥 Download Full Summary
        st.download_button("📥 Download Full Summary", summary, file_name="summary.txt")

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

            # 📥 Download Bullet Summary
            st.download_button("📥 Download Bullet Summary", bullet_summary, file_name="bullet_summary.txt")

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
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content([msg["content"] for msg in st.session_state.messages])
        bot_reply = response.text
    except google.api_core.exceptions.ResourceExhausted:
        bot_reply = "⚠️ Can't Connect to the Server, Please try again."
    except google.api_core.exceptions.GoogleAPIError:
        bot_reply = "⚠️ An error occurred. Please try again later."

    # 📝 Store & Display Bot Reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

# 🗑️ Clear Chat Button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
