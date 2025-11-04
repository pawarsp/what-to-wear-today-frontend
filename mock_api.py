from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Mock weather endpoint ---
@app.get("/weather")
def get_weather(city: str):
    fake_data = {
        "london": {"temperature": 13, "label": "Cool and cloudy"},
        "athens": {"temperature": 25, "label": "Warm and sunny"},
        "osaka": {"temperature": 18, "label": "Mild with light breeze"},
    }
    result = fake_data.get(city.lower(), {"temperature": 20, "label": "Moderate"})
    return result

# --- Mock recommendation endpoint ---
@app.get("/recommend")
def get_recommendations(city: str):
    fake_outfits = {
        "15-20 degress": ["Jeans", "Sweater", "Jacket", "Sneakers"],
        "5-14 degrees": ["T-shirt", "Shorts", "Sandals", "Sunglasses"],
        "21-40 degrees": ["Light trousers", "Shirt", "Loafers"],
    }

    # Decide based on weather
    temp = get_weather(city)["temperature"]

    if temp < 15:
        outfit = fake_outfits["5-14 degrees"]
    elif 15 <= temp <= 20:
        outfit = fake_outfits["15-20 degrees"]
    else:
        outfit = fake_outfits["21-40 degrees"]

    return {"recommendations": outfit}
