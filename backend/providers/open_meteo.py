import requests

class OpenMeteoProvider:
    def __init__(self, lat: float = 25.2854, lon: float = 51.5310):
        self.lat = lat
        self.lon = lon
        self.base = "https://api.open-meteo.com/v1/forecast"

    def get_hourly_forecast(self, hours: int = 24):
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "hourly": "temperature_2m,relativehumidity_2m",
            "timezone": "auto"
        }
        resp = requests.get(self.base, params=params)
        data = resp.json()
        result = []
        for t, temp, rh in zip(
            data["hourly"]["time"][:hours],
            data["hourly"]["temperature_2m"][:hours],
            data["hourly"]["relativehumidity_2m"][:hours],
        ):
            result.append({"time": t, "temp_c": temp, "rh_pct": rh})
        return result
