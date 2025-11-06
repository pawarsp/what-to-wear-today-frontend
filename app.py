import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import altair as alt
import numpy as np
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="What to Wear Today",
    page_icon="👕",
    layout="centered"
    )

logo = Image.open("WhatToWearToday_White_new.png")

st.markdown(
    """
    <style>
    .stApp {
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create the hero container
st.markdown('<div class="hero">', unsafe_allow_html=True)

# Use columns to center everything
left_col, center_col, right_col = st.columns([1, 2, 1])

with center_col:
    # Logo
    st.image(logo, width=500, output_format="PNG")

st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'city' not in st.session_state:
    st.session_state.city = None
# API Endpoints
BASE_URL = "https://docker-1034862203805.europe-west1.run.app"
WWTT_API = f"{BASE_URL}/predict"
city_country = {
    "berlin": "Berlin, Germany",
    "london": "London, United Kingdom",
    "porto": "Porto, Portugal",
    "marseille": "Marseille, France",
}
# city coordinates
city_coords = {
    "london": {"lat": 51.5074, "lon": -0.1278},
    "berlin": {"lat": 52.5200, "lon": 13.4050},
    "porto": {"lat": 41.1579, "lon": -8.6291},
    "marseille": {"lat": 43.2965, "lon": 5.3698},
}
# Initialize session state variables
for key in ['coords', 'temperature', 'rain', 'humidity', 'wind', 'temperature_min',
           'temperature_max', 'recommended_clothes', 'time', 'recommendations']:
    if key not in st.session_state:
        st.session_state[key] = None

# --- City & Occasion Input ---
with st.container():
    st.markdown(
        "<div style='font-size:20px; font-weight:bold; margin-bottom:0px;'>Select Your City</div>",
        unsafe_allow_html=True
    )
    city = st.selectbox(
        "",
        options=[c.title() for c in city_coords.keys()],
        label_visibility="collapsed",
        key="city_select"
    )

# Button: fetch weather and recommendations
if st.button(":sparkles: Get My Outfit", key="get_outfit_btn"):
    if not city:
        st.warning(":warning: Please select a city.")
    else:
        with st.spinner("Fetching your personalized outfit..."):
            try:
                city_lower = city.lower()
                all_response = requests.get(WWTT_API, params={'city': city_lower})
                print(f"API Response Status: {all_response.status_code}")
                if all_response.status_code == 200:
                    data = all_response.json()
                    st.session_state.temperature = data.get("temperature", [])
                    st.session_state.temperature_min = data.get("temperature_min", [])
                    st.session_state.temperature_max = data.get("temperature_max", [])
                    st.session_state.rain = data.get("rain", [])
                    st.session_state.humidity = data.get("humidity", [])
                    st.session_state.wind = data.get("wind", [])
                    st.session_state.recommendations = data.get('recommended_clothes', {})
                    st.session_state.time = data.get("time", [])
                    st.session_state.coords = city_coords.get(city_lower, {"lat":0,"lon":0})
                    st.session_state.city = city
                    st.session_state.data_loaded = True
                else:
                    st.error(f"🚨 API returned status code: {all_response.status_code}")
            except Exception as e:
                st.error(f"🚨 Something went wrong: {e}")

# Only display weather data if we have loaded data
if st.session_state.data_loaded and st.session_state.city:
    temperature = st.session_state.temperature
    temperature_min = st.session_state.temperature_min
    temperature_max = st.session_state.temperature_max
    wind = st.session_state.wind
    rain = st.session_state.rain
    humidity = st.session_state.humidity
    coords = st.session_state.coords
    city = st.session_state.city
    time = st.session_state.time
    st.markdown("---")
    st.markdown(f"<h3>Weather in {city.title()}</h3>", unsafe_allow_html=True)
    # Determine pin color
    if temperature_max and temperature_max < 15:
        pin_color = "blue"
    elif temperature_max and temperature_max <= 20:
        pin_color = "green"
    else:
        pin_color = "orange"
    # Folium map
    if coords:
        m = folium.Map(location=[coords["lat"], coords["lon"]], zoom_start=12,tiles='CartoDB positron')
        folium.Marker(
            location=[coords["lat"], coords["lon"]],
            popup=f"{city.title()}",
            icon=folium.Icon(color=pin_color, icon="cloud")
        ).add_to(m)
    # --- Weather Metric Cards (First Row) ---
        temp_display = f"{np.mean(temperature):.1f} °C" if temperature else "N/A"
        wind_display = f"{np.mean(wind):.1f} km/h" if wind else "N/A"
        humidity_display = f"{np.median(humidity):.1f} %" if humidity else "N/A"
        rain_display = f"{np.mean(rain):.1f} mm" if rain else "N/A"
        st.markdown(f"""
        <div style="display:flex; justify-content:center; gap:20px; width:100%; margin:20px 0;">
            <div class="card" style="flex:0 1 180px; text-align:center;">
                <div style="font-size:28px;">🌡️</div>
                <div style="font-weight:bold; margin-top:10px; font-size:20px;">{temp_display}</div>
                <div style="color:gray;font-size:16px;">Temperature</div>
            </div>
            <div class="card" style="flex:0 1 180px; text-align:center;">
                <div style="font-size:28px;">💨</div>
                <div style="font-weight:bold; margin-top:10px; font-size:20px;">{wind_display}</div>
                <div style="color:gray;font-size:16px;">Wind</div>
            </div>
            <div class="card" style="flex:0 1 180px; text-align:center;">
                <div style="font-size:28px;">💧</div>
                <div style="font-weight:bold; margin-top:10px; font-size:20px;">{humidity_display}</div>
                <div style="color:gray;font-size:16px;">Humidity</div>
            </div>
            <div class="card" style="flex:0 1 180px; text-align:center;">
                <div style="font-size:28px;">🌧️</div>
                <div style="font-weight:bold; margin-top:10px; font-size:20px;">{rain_display}</div>
                <div style="color:gray;font-size:16px;">Rain</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Map
        if coords:
            st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
            st.markdown("#### 📍 Location")
            st_folium(m, use_container_width=True, height=200)

# 12-Hour Forecast with parameter selector
if st.session_state.time:
    # Combine time and temperature lists into a DataFrame
    df = pd.DataFrame({
        "hour": time,
        "temperature": temperature
    })

    y_min = st.session_state.temperature_min - 2
    y_max = st.session_state.temperature_max + 2
    chart = alt.Chart(df).mark_line(point=True, color="#1F77B4").encode(
        x=alt.X('hour:N', title='Hour', sort=df['hour'].tolist()),
        y=alt.Y('temperature', title='Temperature (°C)', scale=alt.Scale(domain=[y_min, y_max])),
        tooltip=[
            alt.Tooltip('hour', title='Hour'),
            alt.Tooltip('temperature', title='Temperature (°C)')
        ]
    ).properties(
        width=700,
        height=200
    ).interactive()
    st.markdown("<h5 style='text-align:left; color:#222; margin-bottom:5px;'>12-Hour Temperature Forecast</h5>", unsafe_allow_html=True)
    st.altair_chart(chart)

# Recommended Outfit Section
if st.session_state.recommendations:
    st.markdown("<h3 style='text-align:left; color:#222;'>Recommended Outfit</h3>", unsafe_allow_html=True)
    category_keys = [k for k in st.session_state.recommendations if not k.endswith("_link")]
    cols = st.columns(len(category_keys))
    for i, category in enumerate(category_keys):
        product_name = st.session_state.recommendations[category]
        image_link = st.session_state.recommendations.get(f"{category}_link", "")
        with cols[i]:
            st.markdown(f"""
                <div style="
                    background-color:white;
                    padding:10px;
                    border-radius:12px;
                    text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                    margin-bottom:10px;">
                    <img src="{image_link}" alt="{product_name}"
                        style="border-radius:12px; width:150px; height:250px; object-fit:cover; margin-bottom:10px;">
                    <p style="font-size:14px; font-weight:bold; margin:5px 0;">{product_name}</p>
                    <p style="font-size:12px; color:gray; margin:0;">{category.title()}</p>
                </div>
            """, unsafe_allow_html=True)

# --- Refresh Recommendations Button  ---
if st.session_state.recommendations:
    st.markdown("<hr style='margin-top:20px; margin-bottom:10px;'>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Recommendations", key="refresh_btn"):
        if not st.session_state.city:
            st.warning("Please select a city first.")
        else:
            with st.spinner("Refreshing outfit ideas..."):
                try:
                    city_lower = st.session_state.city.lower()
                    rec_response = requests.get(f"{WWTT_API}", params={"city": city_lower})
                    if rec_response.status_code == 200:
                        refreshed = rec_response.json().get("recommended_clothes", {})
                        if refreshed:
                            st.session_state.recommendations = refreshed
                            st.rerun()
                        else:
                            st.info("No new recommendations found.")
                    else:
                        st.error(f"API returned status code: {rec_response.status_code}")
                except Exception as e:
                    st.error(f"Error refreshing recommendations: {e}")

# Credits section
st.markdown("<br><br><br>", unsafe_allow_html=True)  # ajoute de l'espace pour descendre le bloc

st.markdown(
    """
    <div style='text-align: center; font-size: 14px; color: #555555;'>
        <p>👥 This project was developed by:</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style='display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;'>

      <a href="https://github.com/pawarsp" target="_blank">
        <img src="https://github.com/pawarsp.png" width="80" style="border-radius: 50%;"><br>
      </a>

      <a href="https://github.com/stfnlxndrslg" target="_blank">
        <img src="https://github.com/stfnlxndrslg.png" width="80" style="border-radius: 50%;"><br>
      </a>

      <a href="https://github.com/xicaseixas" target="_blank">
        <img src="https://github.com/xicaseixas.png" width="80" style="border-radius: 50%;"><br>
      </a>

      <a href="https://github.com/benjaminSimeoni" target="_blank">
        <img src="https://github.com/benjaminSimeoni.png" width="80" style="border-radius: 50%;"><br>
      </a>

      <a href="https://github.com/klaire03" target="_blank">
        <img src="https://github.com/klaire03.png" width="80" style="border-radius: 50%;"><br>
      </a>

    </div>

    <br>
    <p style='text-align: center;'>
    🔗 <a href="https://github.com/pawarsp/what-to-wear-today" target="_blank">View backend repository on GitHub</a>
    </p>
    """,
    unsafe_allow_html=True
)
