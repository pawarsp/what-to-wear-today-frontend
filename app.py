import streamlit as st
import requests

st.set_page_config(page_title="What to Wear Today 👕", page_icon="🧥", layout="centered")

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
BASE_URL = "http://127.0.0.1:8000"
WEATHER_API = f"{BASE_URL}/weather"
RECOMMEND_API = f"{BASE_URL}/recommend"

# City Input
with st.container():
    st.markdown("### Enter Your City")
    city = st.text_input("City name", placeholder="e.g. London, Paris, Berlin, Porto")

# Predict Button
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
                    temperature = weather_data.get("temperature", "N/A")
                    weather_label = weather_data.get("label", "Unknown")

                    # Call recommendation API
                    rec_response = requests.get(RECOMMEND_API, params={"city": city})
                    recommendations = (
                        rec_response.json().get("recommendations", [])
                        if rec_response.status_code == 200 else []
                    )

                    # Layout for results
                    with st.container():
                        st.markdown("---")
                        st.markdown(
                            f"""
                            <div style="
                                background-color:#f0f2f6;
                                padding:20px;
                                border-radius:15px;
                                box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                text-align:center;">
                                <h2 style="color:#333;"> Weather in {city.title()}</h2>
                            </div>
                            <div style="
                                display:flex;
                                justify-content:space-around;
                                flex-wrap:wrap;
                                gap:15px;
                                margin-top:20px;
                            ">
                                <div style="
                                    background-color:#f0f2f6;
                                    padding:20px;
                                    border-radius:15px;
                                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                    text-align:center;">
                                    <p style="font-size:24px;">☀️</p>
                                    <p style="font-size:20px; font-weight:bold; margin:5px 0;">{temperature}°C</p>
                                    <p style="font-size:16px; color:gray;">Temperature</p>
                                </div>
                                <div style="
                                    background-color:#f0f2f6;
                                    padding:20px;
                                    border-radius:15px;
                                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                    text-align:center;">
                                    <p style="font-size:24px;">💨</p>
                                    <p style="font-size:20px; font-weight:bold; margin:5px 0;">12 km/h</p>
                                    <p style="font-size:16px; color:gray;">Wind</p>
                                </div>
                                <div style="
                                    background-color:#f0f2f6;
                                    padding:20px;
                                    border-radius:15px;
                                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                    text-align:center;">
                                    <p style="font-size:24px;">💧</p>
                                    <p style="font-size:20px; font-weight:bold; margin:5px 0;">80%</p>
                                    <p style="font-size:16px; color:gray;">Humidity</p>
                                </div>
                                <div style="
                                    background-color:#f0f2f6;
                                    padding:20px;
                                    border-radius:15px;
                                    box-shadow:0 2px 6px rgba(0,0,0,0.1);
                                    text-align:center;">
                                    <p style="font-size:24px;">🌧️</p>
                                    <p style="font-size:20px; font-weight:bold; margin:5px 0;">60%</p>
                                    <p style="font-size:16px; color:gray;">Precipitation</p>
                                </div>
                            </div>
                                """,
                                unsafe_allow_html=True
                            )

                    st.markdown("### Recommended Outfit")

                    if recommendations:
                        cols = st.columns(len(recommendations))
                        for i, item in enumerate(recommendations):
                            with cols[i]:
                                st.markdown(
                                    f"""
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
                                    """,
                                    unsafe_allow_html=True
                                )
                    else:
                        st.info("No recommendations available for this weather yet.")

            except Exception as e:
                st.error(f"🚨 Something went wrong: {e}")
