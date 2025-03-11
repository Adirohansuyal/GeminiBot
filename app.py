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

if "favorites" not in st.session_state:
        st.session_state.favorites = []

# 🔑 Load API Key
load_dotenv()
API_KEY = "AIzaSyB_dWktJovtRo_uej_NJSAV0wfUQ0D8ITI"
if not API_KEY:
    raise ValueError("API Key is missing! Set GOOGLE_API_KEY in .env")

genai.configure(api_key=API_KEY)

# 📌 Version Management
CURRENT_VERSION = "4.8.0" \
" w.e.f 10 March 2025"
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
    update_data = {"Version": [CURRENT_VERSION], "Details": ["Updating to the latest version of this app."]}
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
page = st.sidebar.radio("Go to", ["🏠 Home", "📄 PDF Processing", "💬 Chat with AI", "🔔 Updates", " 🛠️Detection and Translation Tool", " 📸 Aerri AI Image Search ", " 🗺️ Aerri AI Maps ", "🌉 Aerri AI Image Generator"])

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
    st.markdown("🔥 **RECENT UPDATES (Lastly Updated on 10 March 2025):**")
    st.markdown("**📌 PDF Upload & Text Extraction and Downloadable PDF Feature ✅**")
    st.markdown("**📌 Image Upload & Analysis ✅**")
    st.markdown("**📌 Language Detection & Translation using Google Translator ✅**")

    # 🚨 Update Notification
    if check_for_updates():
        st.markdown(f"<h3 style='color:red;'>⚡ New Update Available! (v{CURRENT_VERSION})</h3>", unsafe_allow_html=True)
        if st.button("✅ Dismiss Update Notification"):
            dismiss_update()
            st.rerun()

elif page == "🌉 Aerri AI Image Generator":
    import streamlit as st
    import requests
    import time
    import base64





    # 🎨 Streamlit App Title
    
    st.title("🎨 Free AI Image Generator (Stable Diffusion)")
    
    st.markdown(
        """
        <style>
        html, body, .main {
            background: linear-gradient(135deg, #5a007f, #a64ac9) !important;
            color: white !important;
            height: 100vh !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
    
        /* Container Styling */
        .block-container {
            background: rgba(255, 255, 255, 0.1) !important;
            padding: 40px !important;
            border-radius: 15px !important;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2) !important;
            width: 90% !important;
            max-width: 1100px !important;
            margin: auto !important;
        }
    
        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: white !important;
            font-weight: bold !important;
            text-align: center !important;
            text-shadow: 2px 2px 10px rgba(255, 255, 255, 0.3) !important;
        }
    
        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #5a007f, #a64ac9) !important;
            color: white !important;
            border-radius: 10px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            transition: all 0.3s ease-in-out !important;
        }
    
        .stButton>button:hover {
            background: linear-gradient(135deg, #a64ac9, #d29bff) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0px 5px 12px rgba(166, 74, 201, 0.4) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    
    
    
    
    
    
    
    
    
    # 🚀 API Key & Endpoint
    HF_API_KEY = "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"  # Replace with your own key
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    
    # 📌 Headers for API request
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    # 🎭 Model Selection
    models = {
        "Stable Diffusion 2.1": "stabilityai/stable-diffusion-2-1",
        "Stable Diffusion 1.5": "runwayml/stable-diffusion-v1-5",
        "Stable Diffusion XL": "stabilityai/stable-diffusion-xl-base-1.0"
    }
    selected_model = st.selectbox("🖼️ Choose a model:", list(models.keys()))
    API_URL = f"https://api-inference.huggingface.co/models/{models[selected_model]}"
    
    # 🎨 Style Selection
    styles = ["Realistic", "Anime", "Pixel Art", "Cyberpunk", "Watercolor"]
    style_choice = st.selectbox("🎭 Choose an image style:", styles)
    
    # 📐 Image Resolution Selection
    resolutions = {
        "Standard (512x512)": (512, 512),
        "High Quality (768x768)": (768, 768)
    }
    resolution_label = st.radio("📏 Select Image Resolution:", list(resolutions.keys()))
    width, height = resolutions[resolution_label]
    
    # 📝 User Prompt Input
    prompt = st.text_area("✏️ Enter a prompt for the AI to generate an image:", "A futuristic city at night with neon lights.")
    
    # ❌ Negative Prompt
    negative_prompt = st.text_area("❌ Things to Avoid:", "low quality, blurry, watermark")
    
    # 🚀 Generate Image Button
    if st.button("🔄 Generate Image"):
        if not prompt.strip():
            st.error("⚠️ Please enter a valid prompt.")
        else:
            st.info("⏳ Generating image... Please wait.")
    
            # 🌍 API Request Data
            data = {
                "inputs": f"{prompt}, in {style_choice} style",
                "parameters": {
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height
                }
            }
    
            # ⏳ Timer Start
            start_time = time.time()
    
            try:
                response = requests.post(API_URL, headers=headers, json=data)
                end_time = time.time()
    
                if response.status_code == 200:
                    image_bytes = response.content
                    image_filename = "generated_image.png"
    
                    # Save Image Locally
                    with open(image_filename, "wb") as f:
                        f.write(image_bytes)
    
                    # Display Image
                    st.image(image_filename, caption="🎨 Generated Image", use_container_width=True)
    
                    st.success(f"✅ Image generated in {end_time - start_time:.2f} seconds!")
    
                    # Save Image to History
                    if "image_history" not in st.session_state:
                        st.session_state.image_history = []
    
                    st.session_state.image_history.append(image_filename)
    
                    # Download Button
                    b64_image = base64.b64encode(image_bytes).decode()
                    href = f'<a href="data:file/png;base64,{b64_image}" download="AI_image.png">⬇️ Download Image</a>'
                    st.markdown(href, unsafe_allow_html=True)
    
                else:
                    st.error(f"⚠️ API Error: {response.json()}")
    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection error: {e}")
    
    
    
elif page == " 🗺️ Aerri AI Maps ":
    import streamlit as st
    import requests
    import folium
    import google.generativeai as genai
    from streamlit_folium import folium_static
    
    # Set up Gemini API Key
    GEMINI_API_KEY = "AIzaSyBG5CL9MIA5XpILTVvA528WAQ3e5XYr_r8"
    genai.configure(api_key=GEMINI_API_KEY)
    
    # TomTom API Key
    TOMTOM_API_KEY = "Kij3I3I8FxRkw6k9lS9I7HjJQ44iwAHa"
    
    # Pexels API Key (Replace with your actual key)
    PEXELS_API_KEY = "HUEEXguBPn0FmAJbQyI4JBLcq20PjZw5r4zIfwusEH2KtWOuXsmxvsQm"
    
    st.title("🌍 Aerri AI Maps")
    st.write("Search for locations, find nearby places, and get directions!")
    
    # User input for place search
    place_name = st.text_input("🔍 Enter a place name:")
    
    # Function to get coordinates using TomTom Search API
    def get_location(place):
        url = f"https://api.tomtom.com/search/2/search/{place}.json?key={TOMTOM_API_KEY}"
        response = requests.get(url)
        data = response.json()
    
        if "results" in data and len(data["results"]) > 0:
            position = data["results"][0]["position"]
            return position["lat"], position["lon"]
        else:
            return None, None
    
    # Function to get nearby places (POI)
    
    
        
    
    # Function to get 10 key points about a place using Gemini API
    def get_gemini_info(place):
        prompt = f"Give me 5 interesting facts about {place}."
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return response.text.split("\n")  # Splitting response into list items
    
    # Function to fetch an image from Pexels
    def get_pexels_image(query):
        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["photos"]:
                return data["photos"][0]["src"]["large"]  # Get the first image
        return None
    
    # Fetch location on button click
    if st.button("📍 Search Location"):
        lat, lon = get_location(place_name)
    
        if lat and lon:
            st.success(f"✅ Found {place_name} at ({lat}, {lon})")
    
            # Fetch Pexels Image
            st.subheader("📸 Location Image")
            image_url = get_pexels_image(place_name)
            if image_url:
                st.image(image_url, caption=f"{place_name} - Image from Aerri AI",width=300, use_container_width=False)
            else:
                st.warning("⚠ No image found for this location.")
    
            # Map setup
            m = folium.Map(location=[lat, lon], zoom_start=12, tiles="OpenStreetMap")
    
            # Add marker for searched place
            folium.Marker([lat, lon], popup=f"{place_name} 📍", tooltip="Click for details", icon=folium.Icon(color="red")).add_to(m)
    
            # Nearby places search (default: restaurants)
            
    
           
    
            # Display the map
            folium_static(m)
    
            # Fetch and display Gemini-generated information
            st.subheader(f"🌎 5 Interesting Facts about {place_name}")
            facts = get_gemini_info(place_name)
            for fact in facts:
                if fact.strip():  # Avoid empty lines
                    st.write(f"• {fact}")
    
        else:
            st.error("❌ Location not found. Try another search.")
    
elif page == " 📸 Aerri AI Image Search ":
    import streamlit as st
    import zipfile
    import requests
    from transformers import BlipProcessor, BlipForConditionalGeneration
    from PIL import Image
    from io import BytesIO
    
    

    # 🔑 Replace this with your actual API key
    PEXELS_API_KEY = "HUEEXguBPn0FmAJbQyI4JBLcq20PjZw5r4zIfwusEH2KtWOuXsmxvsQm"
    PEXELS_API_URL = "https://api.pexels.com/v1/search"

# 🎨 Page Configuration
    st.title("Aerri AI Image Search")
    st.write("Find high-quality images with AI-powered captions!")

    # 🌟 Custom Background and Styling
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] { background: linear-gradient(to right, #141E30, #243B55); }
        [data-testid="stMarkdownContainer"], .stTextInput, .stRadio, .stSlider, label { color: #ffffff !important; }
        .stTextInput>div>div>input { color: #ffffff !important; background-color: #1e2a38 !important; border-radius: 8px; padding: 5px; caret-color: #00ffff !important; border: 1px solid #00ffff; }
        h1, h2, h3, h4, h5, h6 { color: #00ffff !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("📸Aerri AI Image Search ")
    st.write("🔍 Find high-quality images with AI-powered captions!")
    

    # 🎯 Quick Search Categories
    categories = ["Nature", "Animals", "Technology", "Travel", "Food", "Business", "Fashion", "Health", "Music", "Cars"]
    selected_category = st.radio("Quick Categories:", categories, horizontal=True)
    

# 🔍 User Search Input
    query = st.text_input("Enter a search term:", selected_category)

# 🖼️ Image Filters
    col1, col2 = st.columns(2)
    with col1:
        num_images = st.slider("Number of images:", 0, 5, 10)
    with col2:
        orientation = st.selectbox("Image Orientation:", ["All", "Landscape", "Portrait", "Square"])

# 📥 Fetch Images from Pexels API
    def fetch_images(query, per_page=10, orientation=None):
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": per_page}
    
        if orientation and orientation != "All":
             params["orientation"] = orientation.lower()

        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
    
        if response.status_code == 200:
            return response.json().get("photos", [])
        else:
            st.error("❌ Failed to fetch images. Please check your API key.")
        return []

# 🤖 AI Captioning Setup
    MODEL_NAME = "Salesforce/blip-image-captioning-base"
    processor = BlipProcessor.from_pretrained(MODEL_NAME)
    model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)

# 🔥 Function to Generate AI Captions
    def generate_caption(image_url):
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
    
        inputs = processor(image, return_tensors="pt")
        caption_ids = model.generate(**inputs)
        caption = processor.batch_decode(caption_ids, skip_special_tokens=True)[0]
    
        return caption

# ⭐ Favorites Feature
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    
    def add_to_favorites(photo):
        if photo not in st.session_state.favorites:
            st.session_state.favorites.append(photo)
            st.success("Added to favorites!")
    
    def remove_from_favorites(photo):
        if photo in st.session_state.favorites:
            st.session_state.favorites.remove(photo)
            st.warning("Removed from favorites.")
    def download_favorites_as_zip():
        if not st.session_state.favorites:
            st.error("No favorites to download!")
            return None
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for index, fav in enumerate(st.session_state.favorites):
                image_url = fav["src"]["original"]
                image_data = requests.get(image_url).content
                zip_file.writestr(f"image_{index + 1}.jpg", image_data)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    # 🔄 Load More Button
    if "page" not in st.session_state:
        st.session_state.page = 1
    
    if st.button("🔍 Search") or st.session_state.page > 1:
        st.session_state.page += 1
        photos = fetch_images(query, per_page=num_images, orientation=orientation)
    
        if photos:
            cols = st.columns(4)
            for index, photo in enumerate(photos):
                with cols[index % 4]:
                    st.image(photo["src"]["medium"], caption=photo["photographer"], use_container_width=True)
    
                    # 🔥 Generate AI Caption
                    with st.spinner("Generating AI caption... 🤖"):
                        caption = generate_caption(photo["src"]["original"])
                    st.write(f"📝 **AI Caption:** {caption}")
    
                    st.markdown(f"[🔗 View HD]({photo['src']['original']})", unsafe_allow_html=True)
                    
                    # ⭐ Favorite Button
                    if st.button("⭐ Add to Favorites", key=f"fav_{photo['id']}"):
                        add_to_favorites(photo)
    
                    # ⬇ Download Button
                    image_data = requests.get(photo["src"]["original"]).content
                    st.download_button("📥 Download", image_data, file_name=f"{photo['id']}.jpg", mime="image/jpeg", key=f"download_{photo['id']}")
        else:
            st.warning("⚠ No images found. Try a different search term.")
    
# ❤️ Display Favorites Section
st.sidebar.header("⭐ Favorite Images")
if st.session_state.favorites:
    for fav in st.session_state.favorites:
        st.sidebar.image(fav["src"]["medium"], caption=fav["photographer"], use_container_width=True)
        if st.sidebar.button("❌ Remove", key=f"remove_{fav['id']}"):
            remove_from_favorites(fav)

    zip_file = download_favorites_as_zip()
    if zip_file:
        st.sidebar.download_button("📥 Download All as ZIP", zip_file, file_name="favorite_images.zip", mime="application/zip")

    else:
        st.sidebar.write("No favorites yet. Add some!")


    

elif page == " 🛠️Detection and Translation Tool":
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
        extracted_text = ""  # Initialize extracted_text to prevent NameError

        if file_type in ["image/jpeg", "image/jpg", "image/png"]:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            # **Generate Image Description**
            st.subheader("🖼️ Image Analysis & Description")
            description = generate_image_description(image, lang=description_language)
            st.write("**Detailed Description:**", description)

            # **Ask Questions About the Image**
            


        elif file_type == "application/pdf":
            st.subheader("📜 PDF Text Extraction")
            pdf_bytes = uploaded_file.read()
            extracted_text = extract_text_from_pdf(pdf_bytes)

            if not extracted_text:  # If normal extraction fails, use OCR
                extracted_text = extract_text_from_scanned_pdf(BytesIO(pdf_bytes))

            if extracted_text:  # Only proceed if text is extracted
                detected_language = detect(extracted_text)
                st.write(f"**Detected Language:** {Language.make(language=detected_language).display_name()}")

                language_choices = get_language_choices()
                target_language = st.selectbox("Select target language for translation:", list(language_choices.keys()))

                if target_language != Language.make(language=detected_language).display_name():
                    translated_text = GoogleTranslator(source=detected_language, target=language_choices[target_language]).translate(extracted_text)
                    st.text_area("Translated Text", translated_text, height=300)
                    text_to_download = translated_text
                else:
                    st.text_area("Extracted Text", extracted_text, height=300)
                    text_to_download = extracted_text

                # Function to create a downloadable PDF
                def create_pdf(text):
                    from io import BytesIO
                    from reportlab.lib.pagesizes import letter
                    from reportlab.pdfgen import canvas

                    buffer = BytesIO()
                    pdf_canvas = canvas.Canvas(buffer, pagesize=letter)
                    pdf_canvas.setFont("Helvetica", 12)

                    lines = text.split("\n")
                    y = 750  

                    for line in lines:
                        if y < 50:  
                            pdf_canvas.showPage()
                            pdf_canvas.setFont("Helvetica", 12)
                            y = 750
                        pdf_canvas.drawString(50, y, line)
                        y -= 20  

                    pdf_canvas.save()
                    buffer.seek(0)
                    return buffer

                # Generate PDF and provide download button
                pdf_buffer = create_pdf(text_to_download)
                st.download_button(
                    label="📥 Download as PDF",
                    data=pdf_buffer,
                    file_name="extracted_text.pdf",
                    mime="application/pdf"
                )

            else:
                st.warning("Could not extract text from the PDF. Try another file.")



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
    st.title("📂 PDF Processing by Aerri AI")

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
