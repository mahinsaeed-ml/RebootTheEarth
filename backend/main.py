import os
import yaml
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from backend.providers.open_meteo import OpenMeteoProvider
from backend.risk_engine import summarize_stress
from backend.guidance_engine import actions_from_signals
from backend.pest_detector import PestDetector
from backend.notifier import SMSNotifier

app = FastAPI(title="AI Greenhouse Early Warning")

# Load thresholds
with open("configs/thresholds.yaml", "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

weather = OpenMeteoProvider()
detector = PestDetector()
notifier = SMSNotifier()

class SensorPayload(BaseModel):
    temp_c: float
    rh_pct: float

class PestPayload(BaseModel):
    whitefly: int = 0
    thrips: int = 0
    tuta_miner_traces: int = 0

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/forecast")
def forecast(hours: int = 6):
    weather = OpenMeteoProvider(lat=25.3, lon=51.5)  # Doha coords
    return {"hourly": weather.get_hourly_forecast(hours)}

@app.post("/pests")
async def detect_pests(file: UploadFile = File(...)):
    tmp = "temp_upload.jpg"
    with open(tmp, "wb") as f:
        f.write(await file.read())
    counts = detector.detect(tmp)
    return {"counts": counts}

from backend.notifier import SMSNotifier
import os

notifier = SMSNotifier()

@app.post("/analyze")
def analyze(payload: dict):
    sensors = payload.get("sensors", {})
    pests = payload.get("pests", {})

    # use new method
    forecast = weather.get_hourly_forecast(hours=24)

    temp = sensors.get("temp_c")
    rh = sensors.get("rh_pct")

    # Calculate VPD (simplified)
    vpd_band = "normal"
    if temp and rh:
        vpd = (1 - rh / 100) * (0.6108 * 2.718 ** ((17.27 * temp) / (temp + 237.3)))
        if vpd > 2.0:
            vpd_band = "high"
        elif vpd < 0.5:
            vpd_band = "low"

    # --- ALERT LOGIC ---
    alerts = []

    # Pest thresholds
    if pests.get("whitefly", 0) > 5:
        alerts.append(f"🪰 Whitefly infestation detected: {pests['whitefly']} flies")
    if pests.get("thrips", 0) > 5:
        alerts.append(f"🪲 Thrips population high: {pests['thrips']}")
    if pests.get("tuta_miner_traces", 0) > 0:
        alerts.append("🍅 Tuta miner traces found on tomato leaves")

    # Climate thresholds
    if vpd_band == "high":
        alerts.append(f"⚠️ High VPD detected at {temp}°C / {rh}% RH. Increase humidity or cooling.")
    elif vpd_band == "low":
        alerts.append(f"⚠️ Low VPD detected at {temp}°C / {rh}% RH. Improve ventilation.")

    # Send SMS (batch into one message)
    if alerts:
        message = " | ".join(alerts)
        notifier.send_sms("+97450608769", message)

    return {
        "risk": {"vpd_band": vpd_band},
        "forecast": forecast,
        "pests": pests,
        "alerts": alerts
    }

