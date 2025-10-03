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
def forecast(hours: int = 24):
    return {"hourly": weather.get_hourly_forecast(hours)}

@app.post("/pests")
async def detect_pests(file: UploadFile = File(...)):
    tmp = "temp_upload.jpg"
    with open(tmp, "wb") as f:
        f.write(await file.read())
    counts = detector.detect(tmp)
    return {"counts": counts}

@app.post("/analyze")
def analyze(sensors: SensorPayload, pests: PestPayload, dust_index: float = 0.2):
    forecast = weather.get_hourly_forecast(24)
    current = {"temp_c": sensors.temp_c, "rh_pct": sensors.rh_pct}
    risk = summarize_stress(current, forecast, dust_index)
    actions = actions_from_signals(pests.dict(), {}, risk, CFG)
    return {"risk": risk, "actions": actions}
