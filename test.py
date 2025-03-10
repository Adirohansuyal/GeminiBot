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
st.set_page_config(page_title="Aerri AI Image Search", layout="wide")

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
categories = ["Nature", "Animals", "Technology", "Travel", "Food"]
selected_category = st.radio("Quick Categories:", categories, horizontal=True)

# 🔍 User Search Input
query = st.text_input("Enter a search term:", selected_category)

# 🖼️ Image Filters
col1, col2 = st.columns(2)
with col1:
    num_images = st.slider("Number of images:", 5, 20, 10)
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
