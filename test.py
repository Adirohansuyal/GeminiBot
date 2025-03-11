import streamlit as st
import requests
import time
import base64





# 🎨 Streamlit App Title
st.set_page_config(page_title="AI Image Generator", page_icon="🎨", layout="wide")
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

