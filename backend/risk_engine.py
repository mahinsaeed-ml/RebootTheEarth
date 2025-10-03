import math
import random

def simulate_dust_index():
    """
    Fake dust storm risk between 0.0–1.0
    (0 = no risk, 1 = very high risk)
    For demo, random value. You could improve this
    using humidity, windspeed, or a real dust API.
    """
    return round(random.uniform(0, 1), 2)

def sat_vapor_pressure_kpa(T_c):
    return 0.6108 * math.exp((17.27 * T_c) / (T_c + 237.3))

def vpd_kpa(T_c, RH_pct):
    es = sat_vapor_pressure_kpa(T_c)
    ea = es * (RH_pct/100.0)
    return max(0.0, es - ea)

def summarize_stress(sensor, forecast, dust_index=None):
    T, RH = sensor["temp_c"], sensor["rh_pct"]
    vpd = vpd_kpa(T, RH)
    return {
        "vpd_now_kpa": round(vpd, 2),
        "dust_risk": dust_index if dust_index is not None else simulate_dust_index(),
        "vpd_band": "low" if vpd < 0.5 else "optimal" if vpd < 1.6 else "high"
    }

