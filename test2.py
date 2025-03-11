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
            st.image(image_url, caption=f"{place_name} - Image from Aerri AI",width=300, use_column_width=False)
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