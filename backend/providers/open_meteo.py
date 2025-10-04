import requests

class OpenMeteoProvider:
    def __init__(self, lat=25.3, lon=51.5):
        # Default: Doha, Qatar
        self.lat = lat
        self.lon = lon
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_hourly_forecast(self, hours=6):
        """
        Fetch hourly weather forecast limited to given hours.
        Returns: dict with current temp and list of hourly entries.
        """
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "hourly": ["temperature_2m", "relative_humidity_2m"],
            "current": ["temperature_2m"],
            "timezone": "auto"
        }

        resp = requests.get(self.base_url, params=params, timeout=10)
        data = resp.json()

        # Defensive checks
        hourly_times = data.get("hourly", {}).get("time", [])
        temps = data.get("hourly", {}).get("temperature_2m", [])
        rhs = data.get("hourly", {}).get("relative_humidity_2m", [])

        hourly = []
        for i in range(min(hours, len(hourly_times))):
            hourly.append({
                "time": hourly_times[i],
                "temp_c": temps[i],
                "rh_pct": rhs[i]
            })

        return {
            "current_temp": data.get("current", {}).get("temperature_2m"),
            "hourly": hourly
        }
