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

# Language selection for descriptions
description_language = st.selectbox("Select description language:", ["English", "Hindi"])

# Function to generate an image description
def generate_image_description(image, lang="English"):
    """Generate a detailed description of an image using BLIP model and translate if needed."""
    image = image.convert("RGB")  # Ensure image is in RGB format
    inputs = processor(images=image, return_tensors="pt")
    output = description_model.generate(**inputs, max_length=150)
    description = processor.batch_decode(output, skip_special_tokens=True)[0]
    
    if lang != "English":
        description = GoogleTranslator(source="en", target=lang.lower()).translate(description)
    
    return description

# Function to answer a question about an image
def answer_image_question(image, question):
    """Answer a user question about the image using the VQA model."""
    image = image.convert("RGB")
    inputs = processor(images=image, text=question, return_tensors="pt")
    output = vqa_model.generate(**inputs, max_length=50)
    answer = processor.batch_decode(output, skip_special_tokens=True)[0]
    return answer

# Function to extract text from a normal PDF
def extract_text_from_pdf(pdf_bytes):
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "".join([page.get_text("text") for page in pdf_document])
    return text.strip()

# Function to extract text from a scanned PDF using OCR
def extract_text_from_scanned_pdf(pdf_bytes):
    images = convert_from_bytes(pdf_bytes.read())
    text = "".join([pytesseract.image_to_string(img) for img in images])
    return text.strip()

# Function to get a list of supported language names
def get_language_choices():
    language_codes = GoogleTranslator().get_supported_languages()
    return {Language.make(language=code).display_name(): code for code in language_codes}

if uploaded_file is not None:
    file_type = uploaded_file.type

    if file_type in ["image/jpeg", "image/jpg", "image/png"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # **Generate Image Description**
        st.subheader("🖼️ Image Analysis & Description")
        description = generate_image_description(image, lang=description_language)
        st.write("**Detailed Description:**", description)

        # **Ask Questions About the Image**
        st.subheader("❓ Ask a Question About the Image")
        user_question = st.text_input("Enter your question:")

        if user_question:
            answer = answer_image_question(image, user_question)
            st.write("**Answer:**", answer)
    
    elif file_type == "application/pdf":
        st.subheader("📜 PDF Text Extraction")
        pdf_bytes = uploaded_file.read()
        extracted_text = extract_text_from_pdf(pdf_bytes) or extract_text_from_scanned_pdf(BytesIO(pdf_bytes))
        
        if extracted_text:
            detected_language = detect(extracted_text)
            st.write(f"**Detected Language:** {Language.make(language=detected_language).display_name()}")
            
            language_choices = get_language_choices()
            target_language = st.selectbox("Select target language for translation:", list(language_choices.keys()))
            
            if target_language != Language.make(language=detected_language).display_name():
                translated_text = GoogleTranslator(source=detected_language, target=language_choices[target_language]).translate(extracted_text)
                st.text_area("Translated Text", translated_text, height=300)
            else:
                st.text_area("Extracted Text", extracted_text, height=300)
        else:
            st.warning("Could not extract text from the PDF. Try another file.")