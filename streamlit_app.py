import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("🦠 Predicting and Mapping Flu Outbreaks in Cauayan City")
st.write("Upload flu and weather datasets to generate predictions and insights.")

# Upload datasets
flu_file = st.file_uploader("📄 Upload Flu Cases CSV", type=["csv"])
weather_file = st.file_uploader("🌦️ Upload Weather Data CSV", type=["csv"])

if flu_file and weather_file:
    flu = pd.read_csv(flu_file)
    weather = pd.read_csv(weather_file)
    
    st.success("✅ Data successfully loaded!")
    st.write("### Flu Data Preview")
    st.dataframe(flu.head())
    st.write("### Weather Data Preview")
    st.dataframe(weather.head())

    # Ensure Date columns are consistent
    flu['Date'] = pd.to_datetime(flu['Date'])
    weather['Date'] = pd.to_datetime(weather['Date'])

    # Merge datasets by Date and Barangay
    merged = pd.merge(flu, weather, on=["Date", "Barangay"], how="inner")

    # --- Simple AI Logic for Prediction ---
    # (This simulates prediction until we train a real model)
    merged['Predicted_Cases'] = (
        merged['Flu_Cases'] +
        0.02 * merged['Rainfall_mm'] +
        0.5 * (merged['Temperature_C'] - 28)
    ).round().astype(int)

    st.write("### 🧠 Predicted Flu Cases")
    st.dataframe(merged[['Date', 'Barangay', 'Flu_Cases', 'Predicted_Cases']])

    # --- Visualization ---
    st.write("### 📊 Trend of Predicted Cases per Barangay")
    barangay = st.selectbox("Select Barangay:", merged['Barangay'].unique())

    barangay_data = merged[merged['Barangay'] == barangay]

    plt.figure(figsize=(8, 4))
    plt.plot(barangay_data['Date'], barangay_data['Flu_Cases'], marker='o', label='Actual')
    plt.plot(barangay_data['Date'], barangay_data['Predicted_Cases'], marker='x', label='Predicted')
    plt.title(f"Flu Trend in {barangay}")
    plt.xlabel("Date")
    plt.ylabel("Number of Cases")
    plt.legend()
    st.pyplot(plt)
else:
    st.info("Please upload both datasets to proceed.")
