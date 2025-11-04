import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="What to Wear Today 👕", page_icon="🧥", layout="centered")

# --- CSS Styling ---
st.markdown(
    """
    <style>
    .card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .card .icon {
        font-size: 24px;
    }
    .card .metric {
        font-size: 20px;
        font-weight: bold;
        margin: 5px 0;
    }
    .card .label {
        font-size: 16px;
        color: gray;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Main Title ---
st.markdown(
    """
    <h1 style="text-align:center;">👕 What to Wear Today</h1>
    <p style="text-align:center; color:gray; font-size:18px;">
        Your smart weather-based clothing recommender
    </p>
    """,
    unsafe_allow_html=True
)

# --- API Endpoints ---
BASE_URL = "http://127.0.0.1:8000"
WEATHER_API = f"{BASE_URL}/weather"
RECOMMEND_API = f"{BASE_URL}/recommend"

# --- Supported city coordinates ---
city_coords = {
    "london": {"lat": 51.5074, "lon": -0.1278},
    "athens": {"lat": 37.9838, "lon": 23.7275},
    "osaka": {"lat": 34.6937, "lon": 135.5023},
}

# --- Session state initialization ---
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "coords" not in st.session_state:
    st.session_state.coords = None
if "temperature" not in st.session_state:
    st.session_state.temperature = None
if "weather_label" not in st.session_state:
    st.session_state.weather_label = None

# --- City & Occasion Input ---
with st.container():
    st.markdown("##### Enter Your City")
    city = st.text_input("", placeholder="e.g. London, Berlin, Marseille, Porto")

    st.markdown("##### Describe Your Occasion (Optional)")
    user_context = st.text_area(
        "",
        placeholder="e.g. I’ve got a party tonight but don’t know how to dress for the weather.",
        height=100
    )

# --- Button: fetch weather and recommendations ---
if st.button("✨ Get My Outfit"):
    if not city:
        st.warning("⚠️ Please enter a city name.")
    else:
        with st.spinner("Fetching your personalized outfit..."):
            try:
                # Call weather API
                weather_response = requests.get(WEATHER_API, params={"city": city})
                if weather_response.status_code != 200:
                    st.error("Could not fetch weather data. Please try again.")
                else:
                    weather_data = weather_response.json()
                    st.session_state.weather_data = weather_data
                    st.session_state.temperature = weather_data.get("temperature", "N/A")
                    st.session_state.weather_label = weather_data.get("label", "Unknown")

                # Call recommendation API
                rec_response = requests.get(RECOMMEND_API, params={"city": city})
                if rec_response.status_code == 200:
                    st.session_state.recommendations = rec_response.json().get("recommendations", [])
                else:
                    st.session_state.recommendations = []

                # Store coordinates
                st.session_state.coords = city_coords.get(city.lower(), {"lat":0,"lon":0})

            except Exception as e:
                st.error(f"🚨 Something went wrong: {e}")

# --- Display weather cards if data exists ---
if st.session_state.weather_data:
    temperature = st.session_state.temperature
    weather_label = st.session_state.weather_label

    st.markdown("---")
    st.markdown(
        f"""
        <div class="section-title">
            <h3 style="text-align:left; color:#222; margin:0;">Weather in {city.title()}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4, gap="small")
    with cols[0]:
        st.markdown(f"""
            <div class="card">
                <div class="icon">☀️</div>
                <div class="metric">{temperature}°C</div>
                <div class="label">Temperature</div>
            </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""
            <div class="card">
                <div class="icon">💨</div>
                <div class="metric">7 km/h</div>
                <div class="label">Wind</div>
            </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""
            <div class="card">
                <div class="icon">💧</div>
                <div class="metric">75%</div>
                <div class="label">Humidity</div>
            </div>
        """, unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"""
            <div class="card">
                <div class="icon">🌧️</div>
                <div class="metric">80%</div>
                <div class="label">Precipitation</div>
            </div>
        """, unsafe_allow_html=True)

# --- Map Section ---
if st.session_state.coords:
    coords = st.session_state.coords
    temperature = st.session_state.temperature
    weather_label = st.session_state.weather_label

    # Determine pin color
    if temperature < 15:
        pin_color = "blue"
    elif temperature <= 20:
        pin_color = "green"
    else:
        pin_color = "orange"

    # Zoomed-in map
    m = folium.Map(location=[coords["lat"], coords["lon"]], zoom_start=12)
    folium.Marker(
        location=[coords["lat"], coords["lon"]],
        popup=f"{city.title()}: {temperature}°C, {weather_label}",
        icon=folium.Icon(color=pin_color, icon="cloud")
    ).add_to(m)

    st.markdown(
        f"""
        <div class="section-title">
            <h3 style="text-align:left; color:#222; margin:0;">City Map</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st_folium(m, width=700, height=400)

# --- Recommended Outfit Section ---
if st.session_state.recommendations:
    st.markdown(
        f"""
        <div class="section-title">
            <h3 style="text-align:left; color:#222; margin:0;">Recommended Outfit</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(st.session_state.recommendations))
    for i, item in enumerate(st.session_state.recommendations):
        with cols[i]:
            st.markdown(f"""
                <div style="
                    background-color:white;
                    padding:15px;
                    border-radius:12px;
                    text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                    margin-bottom:10px;">
                    <img src="https://placehold.co/100x100?text={item}"
                         alt="{item}" style="border-radius:8px;">
                    <p style="font-size:16px; margin-top:10px;"><b>{item}</b></p>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Refresh Recommendations Button ---
    if st.button("🔄 Refresh Recommendations"):
        with st.spinner("Refreshing outfit ideas..."):
            try:
                rec_response = requests.get(RECOMMEND_API, params={"city": city})
                if rec_response.status_code == 200:
                    refreshed = rec_response.json().get("recommendations", [])
                    st.session_state.recommendations = refreshed
                    st.success("✅ Recommendations refreshed!")
                    st.experimental_rerun()
                else:
                    st.error("Could not refresh recommendations. Please try again.")
            except Exception as e:
                st.error(f"🚨 Something went wrong: {e}")
