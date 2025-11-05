from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# Allow Streamlit frontend to call thus API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock weather endpoint
@app.get("/weather")
def get_weather(city: str):
    fake_data = {
        "london": {"temperature": 13, "label": "Cool and cloudy"},
        "berlin": {"temperature": 25, "label": "Warm and sunny"},
        "porto": {"temperature": 18, "label": "Mild with light breeze"},
        "marseille": {"temperature": 21, "label": "Warm and sunny"},
    }
    return fake_data.get(city.lower(), {"temperature": 20, "label": "Moderate"})

# Mock recommendation endpoint
@app.get("/recommend")
def get_recommendations(city: str):
    fake_outfits = {
        "5-14": ["T-shirt", "Shorts", "Sandals", "Sunglasses"],
        "15-20": ["Jeans", "Sweater", "Jacket", "Sneakers"],
        "21-40": ["Light trousers", "Shirt", "Loafers"],
    }

    temp = get_weather(city)["temperature"]

    if temp < 15:
        outfit = fake_outfits["5-14"]
    elif 15 <= temp <= 20:
        outfit = fake_outfits["15-20"]
    else:
        outfit = fake_outfits["21-40"]

    return {"recommendations": outfit}

# Mock 12-hour forecast endpoint
@app.get("/hourly")
def get_hourly(city: str):
    base_temp = get_weather(city)["temperature"]
    data = []
    for i in range(12):
        data.append({
            "hour": f"{6+i}:00",
            "temperature": base_temp + random.randint(-2, 2),
            "humidity": random.randint(60, 85),
            "precipitation": random.randint(0, 20),
            "wind": random.randint(3, 10)
        })
    return {"hourly": data}
