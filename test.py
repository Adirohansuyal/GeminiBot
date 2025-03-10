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
