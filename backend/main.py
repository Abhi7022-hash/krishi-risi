from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import requests

from crop_model import predict_crop
from pest_detection import detect_pest

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---

class CropInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class ChatInput(BaseModel):
    message: str

# --- Endpoints ---

@app.post("/predict-crop")
def crop_recommendation(data: CropInput):
    """Predict the best crop based on soil and weather data."""
    crop = predict_crop(data.N, data.P, data.K, data.temperature, data.humidity, data.ph, data.rainfall)
    return {"crop": crop}

@app.post("/detect-pest")
async def pest_detection(file: UploadFile = File(...)):
    """Detect pest/disease from uploaded leaf image (simulated)."""
    result = detect_pest(file.filename)
    return result

@app.get("/weather")
def get_weather(city: str):
    """Get weather data from OpenWeather API."""
    API_KEY = "YOUR_OPENWEATHER_API_KEY"  # Replace with your key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return {"error": "City not found"}

        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["description"],
            "advice": get_farming_advice(data["main"]["temp"], data["main"]["humidity"])
        }
        return weather
    except Exception as e:
        return {"error": str(e)}

def get_farming_advice(temp, humidity):
    """Simple farming advice based on weather."""
    if temp > 35:
        return "Very hot! Water your crops early morning or late evening."
    elif temp < 15:
        return "Cold weather. Protect crops from frost."
    elif humidity > 80:
        return "High humidity. Watch for fungal diseases."
    else:
        return "Good weather for farming. Monitor crops regularly."

@app.get("/market-prices")
def market_prices():
    """Return sample market prices from JSON file."""
    with open("market_data.json", "r") as f:
        data = json.load(f)
    return data

@app.post("/chatbot")
def chatbot(data: ChatInput):
    """Simple rule-based farming chatbot."""
    message = data.message.lower()

    if "crop" in message or "grow" in message:
        reply = "Based on your region, consider growing Rice, Wheat, or Maize. Use the Crop Recommendation tool for a precise suggestion!"
    elif "pest" in message or "disease" in message or "insect" in message:
        reply = "For common pests, use Neem oil spray. For fungal diseases, apply copper-based fungicide. Upload a leaf image in Pest Detection for specific advice."
    elif "fertilizer" in message or "nutrient" in message:
        reply = "Use NPK fertilizer based on soil test. Generally: Urea for Nitrogen, DAP for Phosphorus, MOP for Potassium."
    elif "water" in message or "irrigation" in message:
        reply = "Drip irrigation saves water. Water early morning. Sandy soil needs more frequent watering than clay soil."
    elif "weather" in message or "rain" in message:
        reply = "Check the Weather Advisory module for your city's forecast and farming tips."
    elif "price" in message or "market" in message or "sell" in message:
        reply = "Check the Market Prices module for current crop rates. Sell when trend is Up!"
    elif "hello" in message or "hi" in message:
        reply = "Namaste! I am Krishi Siri, your farming assistant. Ask me about crops, pests, fertilizers, or weather!"
    else:
        reply = "I can help with: crop advice, pest control, fertilizers, irrigation, weather tips, and market prices. Try asking about any of these!"

    return {"reply": reply}
