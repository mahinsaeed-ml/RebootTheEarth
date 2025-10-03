import streamlit as st
import requests
import pandas as pd

BACKEND = "http://localhost:8000"

st.set_page_config(page_title="GreenGuard AI Platform", layout="wide")

# Initialize session state
if "pest_counts" not in st.session_state:
    st.session_state.pest_counts = {"whitefly": 0, "thrips": 0, "tuta_miner_traces": 0}
if "last_temp" not in st.session_state:
    st.session_state.last_temp = None
if "last_rh" not in st.session_state:
    st.session_state.last_rh = None
if "critical_alerts" not in st.session_state:
    st.session_state.critical_alerts = 0
if "active_tasks" not in st.session_state:
    st.session_state.active_tasks = 0

# Sidebar navigation
menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Pest Detection", "Climate Monitor", "Alerts", "Recommendations"]
)

# ---- Dashboard ----
if menu == "Dashboard":
    st.title("🌱 GreenGuard Dashboard")
    st.caption("Monitor your greenhouse in real-time")

    # Fetch latest climate forecast (optional live update)
    try:
        forecast_resp = requests.get(f"{BACKEND}/forecast?hours=1").json()
        if "hourly" in forecast_resp and forecast_resp["hourly"]:
            st.session_state.last_temp = forecast_resp["hourly"][0]["temp_c"]
            st.session_state.last_rh = forecast_resp["hourly"][0]["rh_pct"]

            # Analyze risk
            analyze_payload = {
                "sensors": {
                    "temp_c": st.session_state.last_temp,
                    "rh_pct": st.session_state.last_rh
                },
                "pests": st.session_state.pest_counts
            }
            risk_resp = requests.post(f"{BACKEND}/analyze", json=analyze_payload).json()
            if risk_resp.get("risk", {}).get("vpd_band") == "high":
                st.session_state.critical_alerts += 1
                st.session_state.active_tasks += 1
    except Exception as e:
        st.warning(f"Climate data unavailable: {e}")

    # Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_pests = sum(st.session_state.pest_counts.values())
        st.metric("Pest Detections", total_pests)
    with col2:
        if st.session_state.last_temp is not None:
            st.metric("Current Temperature", f"{st.session_state.last_temp}°C")
        else:
            st.metric("Current Temperature", "--", "No data")
    with col3:
        st.metric("Critical Alerts", st.session_state.critical_alerts)
    with col4:
        st.metric("Active Tasks", st.session_state.active_tasks)

    st.subheader("System Status")
    st.success("AI Pest Detection ✅ Active")
    st.success("Climate Monitoring ✅ Active")
    st.success("Alert System ✅ Active")

# ---- Pest Detection ----
elif menu == "Pest Detection":
    st.header("🪰 Pest Detection")
    st.write("Capture sticky trap image via webcam")
    img = st.camera_input("Take Photo")
    if img:
        files = {"file": ("frame.jpg", img.getvalue(), "image/jpeg")}
        resp = requests.post(f"{BACKEND}/pests", files=files).json()
        counts = resp.get("counts", {})

        # Save to session state
        st.session_state.pest_counts = counts

        st.json(counts)
        if counts.get("whitefly", 0) > 10:  # Example alert condition
            st.session_state.critical_alerts += 1
            st.session_state.active_tasks += 1

# ---- Climate Monitor ----
elif menu == "Climate Monitor":
    st.header("🌡 Climate Monitor")

    if st.button("Get Latest Forecast"):
        resp = requests.get(f"{BACKEND}/forecast?hours=6").json()
        if "hourly" in resp and resp["hourly"]:
            st.session_state.last_temp = resp["hourly"][0]["temp_c"]
            st.session_state.last_rh = resp["hourly"][0]["rh_pct"]

            # Build dataframe
            df = pd.DataFrame(resp["hourly"])  # already has keys: time, temp_c, rh_pct

            # Fake dust index for demo
            import random
            df["dust_index"] = [round(random.uniform(0, 1), 2) for _ in range(len(df))]

            # Charts
            st.subheader("Forecast (Next 6 Hours)")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.line_chart(df, x="time", y="temp_c")
            with col2:
                st.line_chart(df, x="time", y="rh_pct")
            with col3:
                st.bar_chart(df, x="time", y="dust_index")

            # Current metrics
            st.metric("Current Temperature", f"{df['temp_c'].iloc[0]}°C")
            st.metric("Current Humidity", f"{df['rh_pct'].iloc[0]}%")
            st.metric("Dust Storm Risk", df['dust_index'].iloc[0])
        else:
            st.warning("No forecast data available.")


# ---- Alerts ----
elif menu == "Alerts":
    st.header("⚠️ Alerts")
    st.write(f"Critical alerts: {st.session_state.critical_alerts}")
    if st.session_state.critical_alerts > 0:
        st.warning("Immediate action required! Check pest counts and climate risks.")
    else:
        st.success("No critical alerts at this time.")

# ---- Recommendations ----
elif menu == "Recommendations":
    st.header("💡 Recommendations")

    pests = st.session_state.pest_counts
    if pests["whitefly"] > 10:
        st.write("🪰 Apply biological control for whiteflies (e.g., parasitoids).")
    if pests["thrips"] > 5:
        st.write("🪲 Use sticky traps to reduce thrips.")
    if pests["tuta_miner_traces"] > 0:
        st.write("🍅 Inspect tomato leaves for Tuta damage and remove affected leaves.")

    if st.session_state.critical_alerts > 0:
        st.warning("⚠️ Climate stress detected! Add shading, cooling, or adjust irrigation.")

    if sum(pests.values()) == 0 and st.session_state.critical_alerts == 0:
        st.success("✅ No major risks detected.")
