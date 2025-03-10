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

st.title("📄 PDF Language Detection & Translation")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

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

def extract_text_from_scanned_pdf(uploaded_pdf):
    """Extract text using OCR from scanned PDFs."""
    images = convert_from_bytes(uploaded_pdf.getvalue())
    extracted_text = "\n".join([pytesseract.image_to_string(img) for img in images])
    return extracted_text

def text_to_speech(text, lang):
    """Convert text to speech and return a playable audio stream."""
    tts = gTTS(text=text, lang=lang)
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

def save_translated_pdf(translated_text):
    """Save translated text into a PDF and return its path."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, translated_text)

    pdf_file_path = "translated_document.pdf"
    pdf.output(pdf_file_path)

    return pdf_file_path

if uploaded_file is not None:
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    
    st.subheader("📑 Select Pages to Translate")
    total_pages = len(pdf_document)
    selected_pages = st.multiselect("Select pages:", list(range(1, total_pages + 1)), default=[1])

    text = ""
    for page_num in selected_pages:
        text += pdf_document[page_num - 1].get_text("text") + "\n"

    if not text.strip():  # If no text is found, try OCR
        st.warning("No text found in the PDF. Trying OCR...")
        text = extract_text_from_scanned_pdf(uploaded_file)

    if text.strip():
        detected_language_code = detect(text)
        detected_language_full = Language.make(language=detected_language_code).display_name()
        st.write(f"**Detected Language:** {detected_language_full} ({detected_language_code})")

        target_language = st.selectbox("Select Target Language", list(language_map.keys()))

        if st.button("Translate"):
            target_code = language_map[target_language]
            translated_text = GoogleTranslator(source="auto", target=target_code).translate(text)
            st.text_area("Translated Text", translated_text, height=300)

            # **Download Translated Text**
            st.download_button(
                label="📥 Download Translated Text",
                data=translated_text,
                file_name="translated_text.txt",
                mime="text/plain"
            )

            # **Download Translated PDF**
            if st.button("📄 Download as PDF"):
                pdf_path = save_translated_pdf(translated_text)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button("Download PDF", pdf_file, "translated_document.pdf", "application/pdf")

            # **Listen to Translated Text**
            if st.button("🎧 Listen to Translated Text"):
                audio_stream = text_to_speech(translated_text, target_code)
                st.audio(audio_stream, format="audio/mp3")

    else:
        st.error("No text could be extracted from the PDF.")
