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
# ---- Dashboard ----
if menu == "Dashboard":
    st.title("🌿 GreenGuard Dashboard")
    st.caption("Monitor your greenhouse in real-time")

    # --- Climate Fetch ---
    try:
        #forecast_resp = requests.get(f"{BACKEND}/forecast?hours=1").json()
        with st.spinner("⏳ Fetching latest climate data..."):
            forecast_resp = requests.get(f"{BACKEND}/forecast?hours=1").json()
        if "hourly" in forecast_resp and "hourly" in forecast_resp["hourly"]:
            hourly_data = forecast_resp["hourly"]["hourly"]

            # Capture current values
            st.session_state.last_temp = forecast_resp["hourly"].get("current_temp")
            st.session_state.last_rh = hourly_data[0].get("rh_pct")

            # Run risk analysis
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
        else:
            st.info("⚠️ Forecast data format unexpected. Showing last known values.")
    except Exception as e:
        st.warning(f"⚠️ Climate data unavailable ({e})")

    # --- Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_pests = sum(st.session_state.pest_counts.values())
        st.metric("🪰 Pest Detections", total_pests)
    with col2:
        temp_val = f"{st.session_state.last_temp}°C" if st.session_state.last_temp else "--"
        st.metric("🌡 Temperature", temp_val)
    with col3:
        st.metric("⚠️ Critical Alerts", st.session_state.critical_alerts)
    with col4:
        st.metric("📋 Active Tasks", st.session_state.active_tasks)

    # --- System Status ---
    st.subheader("System Status")
    status_cols = st.columns(3)
    with status_cols[0]:
        st.success("🪰 AI Pest Detection: Active")
    with status_cols[1]:
        st.success("🌡 Climate Monitoring: Active")
    with status_cols[2]:
        if st.session_state.critical_alerts > 0:
            st.warning("⚠️ Alert System: Attention Needed")
        else:
            st.success("🔔 Alert System: Active")

# ---- Pest Detection ----
elif menu == "Pest Detection":
    st.header("🪰 Pest Detection")
    st.write("Capture sticky trap image via webcam or upload an image")

    col1, col2 = st.columns(2)

    with col1:
        img_camera = st.camera_input("📷 Take Photo")

    with col2:
        img_file = st.file_uploader("📂 Upload Image", type=["jpg", "jpeg", "png"])

    # Pick whichever input is provided
    img = img_camera or img_file

    if img:
        files = {"file": ("frame.jpg", img.getvalue(), "image/jpeg")}
        resp = requests.post(f"{BACKEND}/pests", files=files).json()
        counts = resp.get("counts", {})

        # Save to session state
        st.session_state.pest_counts = counts
        # Save annotated image
        #st.session_state.last_annotated_image = resp.get("annotated_image")

        st.subheader("Detection Results")
        #st.json(counts)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div style="padding:15px; border-radius:12px; background-color:#fce4ec; text-align:center;">
                    <h3>🪰 Whiteflies</h3>
                    <p style="font-size:24px; font-weight:bold;">{counts.get("whitefly", 0)}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style="padding:15px; border-radius:12px; background-color:#e3f2fd; text-align:center;">
                    <h3>🪲 Thrips</h3>
                    <p style="font-size:24px; font-weight:bold;">{counts.get("thrips", 0)}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div style="padding:15px; border-radius:12px; background-color:#e8f5e9; text-align:center;">
                    <h3>🍅 Tuta Miner</h3>
                    <p style="font-size:24px; font-weight:bold;">{counts.get("tuta_miner_traces", 0)}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.session_state.pest_counts["whitefly"] > 5:
            st.session_state.critical_alerts += 1
            st.session_state.active_tasks += 1
        
        # # Button to view annotated image
        # if st.session_state.last_annotated_image:
        #     st.image(st.session_state.last_annotated_image, caption="Detected Pests", use_container_width=True)

# ---- Climate Monitor ----
# ---- Climate Monitor ----
# elif menu == "Climate Monitor":
#     st.header("🌡 Climate Monitor")

#     if st.button("Get Latest Forecast"):
#         try:
#             resp = requests.get(f"{BACKEND}/forecast?hours=6").json()
#             #st.write("DEBUG Climate Monitor response:", resp)  # <-- debug output

#             if "hourly" in resp and "hourly" in resp["hourly"]:
#                 hourly_data = resp["hourly"]["hourly"]
#                 st.session_state.last_temp = resp["hourly"].get("current_temp")
#                 st.session_state.last_rh = hourly_data[0].get("rh_pct")

#                 # Build dataframe
#                 df = pd.DataFrame(hourly_data)  # <-- use nested hourly

#                 # Fake dust index for demo
#                 import random
#                 df["dust_index"] = [round(random.uniform(0, 1), 2) for _ in range(len(df))]

#                 # Charts
#                 st.subheader("Forecast (Next 6 Hours)")
#                 col1, col2, col3 = st.columns(3)
#                 with col1:
#                     st.line_chart(df, x="time", y="temp_c")
#                 with col2:
#                     st.line_chart(df, x="time", y="rh_pct")
#                 with col3:
#                     st.bar_chart(df, x="time", y="dust_index")

#                 # Current metrics
#                 st.metric("Current Temperature", f"{st.session_state.last_temp}°C")
#                 st.metric("Current Humidity", f"{st.session_state.last_rh}%")
#                 st.metric("Dust Storm Risk", df['dust_index'].iloc[0])
#             else:
#                 st.warning("No forecast data available (unexpected structure).")
#         except Exception as e:
#             st.error(f"Failed to fetch forecast: {e}")

# ---- Climate Monitor ----
# ---- Climate Monitor ----
elif menu == "Climate Monitor":
    st.header("🌡 Climate Monitor")

    if st.button("Get Latest Forecast"):
        try:
            resp = requests.get(f"{BACKEND}/forecast?hours=24").json()
            if "hourly" in resp and "hourly" in resp["hourly"]:
                df = pd.DataFrame(resp["hourly"]["hourly"])

                # Smoothing (rolling average 3-hour window)
                df["temp_c_smooth"] = df["temp_c"].rolling(window=3, min_periods=1).mean()
                df["rh_pct_smooth"] = df["rh_pct"].rolling(window=3, min_periods=1).mean()

                import matplotlib.pyplot as plt
                import random

                # Simulated dust index
                df["dust_index"] = [round(random.uniform(0, 1), 2) for _ in range(len(df))]

                # Latest values
                latest_temp = df["temp_c"].iloc[0]
                latest_rh = df["rh_pct"].iloc[0]
                latest_dust = df["dust_index"].iloc[0]

                # Thresholds
                temp_min, temp_max = 18, 28
                rh_min, rh_max = 60, 80
                dust_threshold = 0.7

                # Layout
                col1, col2, col3 = st.columns(3)

                # --- Temperature card ---
                with col1:
                    delta_temp = "🟢 OK" if temp_min <= latest_temp <= temp_max else "🔴 Risk"
                    st.metric("🌡 Temperature", f"{latest_temp}°C", delta=delta_temp)
                    fig, ax = plt.subplots()
                    ax.plot(df["time"], df["temp_c_smooth"], label="Temp (°C)", color="orange")
                    ax.fill_between(df["time"], temp_min, temp_max, color="green", alpha=0.2, label="Optimal Zone")
                    ax.fill_between(df["time"], temp_max, df["temp_c_smooth"].max()+5, color="red", alpha=0.1)
                    ax.fill_between(df["time"], df["temp_c_smooth"].min()-5, temp_min, color="blue", alpha=0.1)
                    ax.set_ylabel("°C")
                    ax.tick_params(axis='x', rotation=45)
                    ax.legend(fontsize=6)
                    st.pyplot(fig)

                # --- Humidity card ---
                with col2:
                    delta_rh = "🟢 OK" if rh_min <= latest_rh <= rh_max else "🔴 Risk"
                    st.metric("💧 Humidity", f"{latest_rh}%", delta=delta_rh)
                    fig2, ax2 = plt.subplots()
                    ax2.plot(df["time"], df["rh_pct_smooth"], label="Humidity (%)", color="blue")
                    ax2.fill_between(df["time"], rh_min, rh_max, color="green", alpha=0.2, label="Optimal Zone")
                    ax2.fill_between(df["time"], rh_max, 100, color="red", alpha=0.1)
                    ax2.fill_between(df["time"], 0, rh_min, color="yellow", alpha=0.1)
                    ax2.set_ylabel("%RH")
                    ax2.tick_params(axis='x', rotation=45)
                    ax2.legend(fontsize=6)
                    st.pyplot(fig2)

                # --- Dust card ---
                with col3:
                    delta_dust = "🟢 OK" if latest_dust < dust_threshold else "🔴 High"
                    st.metric("🌪 Dust Risk", latest_dust, delta=delta_dust)
                    st.bar_chart(df, x="time", y="dust_index")

            else:
                st.warning("No forecast data available.")
        except Exception as e:
            st.error(f"Failed to fetch forecast: {e}")


# ---- Alerts ----
elif menu == "Alerts":
    st.header("⚠ Alerts")
    st.write(f"Critical alerts: {st.session_state.critical_alerts}")
    if st.session_state.critical_alerts > 0:
        st.warning("Immediate action required! Check pest counts and climate risks.")
        #resp = requests.get(f"{BACKEND}/sendsms?smstext='Immediate action required!'").json()

    else:
        st.success("No critical alerts at this time.")

# ---- Recommendations ----
elif menu == "Recommendations":
    st.header("💡 Recommendations")

    pests = st.session_state.pest_counts

    if pests["whitefly"] > 5:
        st.write(f"🪰 {pests['whitefly']} whiteflies detected, apply biological control (e.g., parasitoids).")
    elif pests["whitefly"] > 0:
        st.write(f"🪰 {pests['whitefly']} whiteflies detected, monitor and take preventive measures.")

    if pests["thrips"] > 5:
        st.write(f"🪲 {pests['thrips']} thrips detected, use sticky traps to reduce them.")
    elif pests["thrips"] > 0:
        st.write(f"🪲 {pests['thrips']} thrips detected, keep monitoring.")

    if pests["tuta_miner_traces"] > 0:
        st.write(f"🍅 {pests['tuta_miner_traces']} tomato leaves with Tuta miner damage, inspect and remove affected leaves.")

    if st.session_state.critical_alerts > 0:
        st.warning("⚠ Climate stress detected! Add shading, cooling, or adjust irrigation.")

    if sum(pests.values()) == 0 and st.session_state.critical_alerts == 0:
        st.success("✅ No major risks detected.")