import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd
import altair as alt

st.set_page_config(page_title="What to Wear Today 👕", page_icon="🧥", layout="centered")

#  CSS
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

# Main Title
st.markdown(
    """
    <h1 style="text-align:center;">👕 What to Wear Today</h1>
    <p style="text-align:center; color:gray; font-size:18px;">
        Your smart weather-based clothing recommender
    </p>
    """,
    unsafe_allow_html=True
)

# API Endpoints
BASE_URL = "https://docker-1034862203805.europe-west1.run.app"
WWTT_API = f"{BASE_URL}/predict"

city_country = {
    "london": "London, UK",
    "berlin": "Berlin, Germany",
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



# Session state initialization
# for key in ['temperature', 'rain', 'humidity', 'wind', 'temperature_min', 'temperature_max', 'recommended_clothes']:
#     if key not in st.session_state:
#         if key == 'recommended_clothes':

#         st.session_state[key] = None if key != "recommendations" and key != "hourly_data" else []

# --- City & Occasion Input ---
with st.container():
    st.markdown(
        "<div style='font-size:20px; font-weight:bold; margin-bottom:0px;'>Select Your City</div>",
        unsafe_allow_html=True
    )
    city = st.selectbox(
        "",
        options=[c.title() for c in city_coords.keys()],

    )

    st.markdown(
        "<div style='font-size:20px; font-weight:bold; margin-bottom:0px;'>Describe Your Occasion (optional)</div>",
        unsafe_allow_html=True
    )
    user_context = st.text_area(
        "",
        placeholder="e.g. I’ve got a party tonight but don’t know how to dress for the weather.",
        height=100
    )

# Button: fetch weather and recommendations
if st.button("✨ Get My Outfit"):
    if not city:
        st.warning("⚠️ Please select a city.")
    else:
        with st.spinner("Fetching your personalized outfit..."):
            try:
                city_country = city_country[city.lower()]
                city_lower = city.lower()

                all_response = requests.get(WWTT_API, params={'city': city_country})
                
                if all_response.status_code == 200:
                    data = all_response.json()
                    print(data.keys())
                    st.session_state.temperature = data.get("temperature", [])
                    st.session_state.rain = data.get("rain", [])
                    st.session_state.humidity = data.get("humidity", [])
                    st.session_state.wind = data.get("wind", [])
                    st.session_state.recommendations = data.get("recommended_clothes", [])
                    st.session_state.time = data.get("time", [])
                else:
                    print(all_response.status_code)

                st.session_state.coords = city_coords.get(city_lower, {"lat":0,"lon":0})

            except Exception as e:
                st.error(f"🚨 Something went wrong: {e}")


temperature = st.session_state.temperature
wind = st.session_state.wind
rain = st.session_state.rain
humidity = st.session_state.humidity
coords = st.session_state.coords
hourly = st.session_state.time

st.markdown("---")
st.markdown(f"<h3>Weather in {city.title()}</h3>", unsafe_allow_html=True)

# Determine pin color
if temperature < 15:
    pin_color = "blue"
elif temperature <= 20:
    pin_color = "green"
else:
    pin_color = "orange"

# Folium map
m = folium.Map(location=[coords["lat"], coords["lon"]], zoom_start=12)
folium.Marker(
    location=[coords["lat"], coords["lon"]],
    popup=f"{city.title()}: {temperature}°C",
    icon=folium.Icon(color=pin_color, icon="cloud")
).add_to(m)

# Cards and Map columns
cols = st.columns([4, 3])

with cols[0]:
    # All cards in a row
    st.markdown(f"""
    <div style="display:flex; gap:10px; flex-wrap:nowrap;">
        <div class="card" style="flex:1; min-width:80px; height:150px; text-align:center;">
            <div style="font-size:24px;">🌡️</div>
            <div style="font-weight:bold; margin-top:10px;">{temperature}°C</div>
            <div style="color:gray;font-size:9px;">Temperature</div>
        </div>
        <div class="card" style="flex:1; min-width:80px; height:150px; text-align:center;">
            <div style="font-size:24px;">💨</div>
            <div style="font-weight:bold; margin-top:10px;">{wind} km/h</div>
            <div style="color:gray;font-size:9px;">Wind</div>
        </div>
        <div class="card" style="flex:1; min-width:80px; height:150px; text-align:center;">
            <div style="font-size:24px;">💧</div>
            <div style="font-weight:bold; margin-top:10px;">{humidity}%</div>
            <div style="color:gray;font-size:9px;">Humidity</div>
        </div>
        <div class="card" style="flex:1; min-width:80px; height:150px; text-align:center;">
            <div style="font-size:24px;">🌧️</div>
            <div style="font-weight:bold; margin-top:10px;">{rain}%</div>
            <div style="color:gray;font-size:9px;">Rain</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with cols[1]:
    st_folium(m, width=300, height=150)


# 12-Hour Forecast with parameter selector
if st.session_state.time:
    df = pd.DataFrame(st.session_state.time)

    params = {
        "temperature": "°C",
        "humidity": "%",
        "rain": "%",
        "wind": "km/h"
    }

    # group title + dropdown
    with st.container():
        st.markdown(
            "<h5 style='text-align:left; color:#222; margin-bottom:5px;'>12-Hour Forecast</h5>",
            unsafe_allow_html=True
        )
        selected_param = st.selectbox(
            "",
            options=list(params.keys()),
            format_func=lambda x: x.title(),
            label_visibility="collapsed"
        )

    # min and max for the selected parameter
    y_min = df[selected_param].min() - 2
    y_max = df[selected_param].max() + 2

    chart = alt.Chart(df).mark_line(point=True, color="#1f77b4").encode(
        x=alt.X('hour', title='Hour'),
        y=alt.Y(
            f'{selected_param}',
            title=f'{selected_param.title()} ({params[selected_param]})',
            scale=alt.Scale(domain=[y_min, y_max])
        ),
        tooltip=[
            alt.Tooltip('hour', title='Hour'),
            alt.Tooltip(selected_param, title=f'{selected_param.title()} ({params[selected_param]})')
        ]
    ).properties(
        width=700,
        height=200
    ).interactive()

    st.altair_chart(chart)


# Recommended Outfit Section
if st.session_state.recommendations:

    st.markdown("<h3 style='text-align:left; color:#222;'>Recommended Outfit</h3>", unsafe_allow_html=True)

    cols = st.columns(len(st.session_state.recommendations))
    for i, item in enumerate(st.session_state.recommendations):
        #img_url = item.get("img_url", "")
        product_name = st.session_state.recommendations[item]
        category = item
        with cols[i]:
            st.markdown(f"""
                <div style="
                    background-color:white;
                    padding:15px;
                    border-radius:12px;
                    text-align:center;
                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                    margin-bottom:10px;">
                    <p style="font-size:16px; margin-top:10px;"><b>{product_name}</b></p>
                    <p style="font-size:12px; color:gray; margin-top:5px;">{category}</p>
                </div>
            """, unsafe_allow_html=True)

   # if st.button("🔄 Refresh Recommendations"):
        with st.spinner("Refreshing outfit ideas..."):
            try:
                rec_response = requests.get(BASE_URL, params={"city": city.lower()})
                if rec_response.status_code == 200:
                    refreshed = rec_response.json().get("recommendations", [])
                    st.session_state.recommendations = refreshed
                    st.success("✅ Recommendations refreshed!")
                    st.experimental_rerun()
                else:
                    st.error("Could not refresh recommendations. Please try again.")
            except Exception as e:
                st.error(f"🚨 Something went wrong: {e}")

#<img src="{img_url}" alt="{product_name}" style="border-radius:8px; width:100px; height:100px;">
