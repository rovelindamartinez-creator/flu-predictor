import streamlit as st
import pandas as pd
import requests
import datetime
import matplotlib.pyplot as plt

st.title("Flu Prediction Dashboard with Live Weather Data 🌦️")

# Step 1: Upload flu data
flu_file = st.file_uploader("Upload your flu dataset (CSV)", type="csv")

if flu_file:
    flu_data = pd.read_csv(flu_file)
    flu_data['Date'] = pd.to_datetime(flu_data['Date'])
    st.write("📅 Flu Data Preview:")
    st.dataframe(flu_data.head())

    # Step 2: Get weather data automatically
    st.write("🌤 Fetching weather data for Cauayan City, Isabela...")

    start_date = flu_data['Date'].min().strftime("%Y-%m-%d")
    end_date = flu_data['Date'].max().strftime("%Y-%m-%d")

    url = f"https://archive-api.open-meteo.com/v1/archive?latitude=16.93&longitude=121.77&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia/Manila"

    response = requests.get(url)
    if response.status_code == 200:
        weather_json = response.json()
        weather_data = pd.DataFrame({
            "Date": weather_json["daily"]["time"],
            "Temp_Max": weather_json["daily"]["temperature_2m_max"],
            "Temp_Min": weather_json["daily"]["temperature_2m_min"],
            "Rainfall": weather_json["daily"]["precipitation_sum"]
        })
        weather_data["Date"] = pd.to_datetime(weather_data["Date"])

        # Step 3: Merge both datasets
        combined = pd.merge(flu_data, weather_data, on="Date", how="inner")

        st.write("🧩 Combined Data:")
        st.dataframe(combined.head())

        # Step 4: Visualization
        st.write("📊 Flu Cases vs Temperature")
        fig, ax1 = plt.subplots()
        ax1.plot(combined["Date"], combined["Cases"], color="red", label="Flu Cases")
        ax2 = ax1.twinx()
        ax2.plot(combined["Date"], combined["Temp_Max"], color="blue", label="Max Temp (°C)")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Flu Cases", color="red")
        ax2.set_ylabel("Temperature (°C)", color="blue")
        st.pyplot(fig)
    else:
        st.error("Failed to fetch weather data. Try again later.")
else:
    st.info("Please upload a flu dataset to begin.")
