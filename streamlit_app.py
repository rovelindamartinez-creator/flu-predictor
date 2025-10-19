# streamlit_app.py
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flu + Live Weather", layout="wide")
st.title("Flu Prediction Dashboard with Live Weather Data 🌦️")

# upload
flu_file = st.file_uploader("Upload your flu dataset (CSV) — must contain a date and a cases column", type="csv")
if flu_file:
    flu_df = pd.read_csv(flu_file)
    st.write("🔎 Uploaded flu file columns:")
    st.write(list(flu_df.columns))

    # Try to find the date column and the cases column automatically
    # Common column name options:
    possible_date_cols = ['Date', 'date', 'DATE']
    possible_case_cols = ['Flu_Cases', 'FluCases', 'Cases', 'cases', 'Dengue_Cases', 'dengue_cases', 'Count']

    # detect date column
    date_col = None
    for c in possible_date_cols:
        if c in flu_df.columns:
            date_col = c
            break
    if date_col is None:
        st.error("Could not find a Date column in your flu CSV. Please ensure there is a 'Date' column.")
        st.stop()

    # detect cases column
    case_col = None
    for c in possible_case_cols:
        if c in flu_df.columns:
            case_col = c
            break
    if case_col is None:
        st.error(f"Could not find a flu/cases column. Expected one of: {possible_case_cols}. Please rename your flu column.")
        st.stop()

    # normalize column names for downstream code
    flu_df = flu_df.rename(columns={date_col: 'Date', case_col: 'Cases'})
    # ensure types
    flu_df['Date'] = pd.to_datetime(flu_df['Date'], errors='coerce')
    # drop rows with invalid dates
    flu_df = flu_df.dropna(subset=['Date']).reset_index(drop=True)
    # convert Cases to numeric (coerce errors -> NaN -> fill 0)
    flu_df['Cases'] = pd.to_numeric(flu_df['Cases'], errors='coerce').fillna(0).astype(int)

    st.success("✅ Flu CSV loaded and columns mapped.")
    st.write("Sample of processed flu data:")
    st.dataframe(flu_df.head())

    # fetch weather data automatically for Cauayan City using Open-Meteo archive API
    st.write("🌤 Fetching weather data (Open-Meteo) for the same date range...")
    start_date = flu_df['Date'].min().strftime("%Y-%m-%d")
    end_date = flu_df['Date'].max().strftime("%Y-%m-%d")

    # Cauayan coordinates approx (lat, lon)
    lat, lon = 16.93, 121.77
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia/Manila"
    )

    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        j = resp.json()
        # build weather dataframe
        weather_df = pd.DataFrame({
            'Date': pd.to_datetime(j['daily']['time']),
            'Temp_Max': j['daily'].get('temperature_2m_max', []),
            'Temp_Min': j['daily'].get('temperature_2m_min', []),
            'Rainfall': j['daily'].get('precipitation_sum', [])
        })
        st.success("✅ Weather data fetched.")
        st.write("Sample weather data:")
        st.dataframe(weather_df.head())
    except Exception as e:
        st.error(f"Failed to fetch weather data: {e}")
        st.stop()

    # merge by Date
    combined = pd.merge(flu_df, weather_df, on='Date', how='inner')
    if combined.empty:
        st.warning("Merged dataset is empty — check that the date ranges overlap and formats are correct.")
    st.write("🧩 Combined data (sample):")
    st.dataframe(combined.head())

    # --- Simple example prediction (replace with real model later) ---
    # Predicted cases = actual cases + small effect of rainfall and temperature
    combined['Predicted_Cases'] = (
        combined['Cases']
        + (0.02 * combined['Rainfall']).round()
        + (0.5 * (combined['Temp_Max'] - 28)).round()
    ).astype(int).clip(lower=0)

    st.write("### 🧠 Predicted Cases (example rule-based)")
    st.dataframe(combined[['Date', 'Cases', 'Temp_Max', 'Rainfall', 'Predicted_Cases']].head(30))

    # Plot: user selects metric to plot
    st.write("### 📊 Flu Cases vs Temperature")
    st.write("If the plot fails, check the 'Manage app' -> Logs on Streamlit Cloud for full error details.")

    # allow the user to choose barangay if the uploaded data had Barangay column
    if 'Barangay' in flu_df.columns:
        barangay_list = sorted(flu_df['Barangay'].unique())
        selected_barangay = st.selectbox("Select Barangay (optional)", ['All'] + barangay_list)
        if selected_barangay != 'All':
            plot_df = combined[combined['Barangay'] == selected_barangay]
        else:
            plot_df = combined.copy()
    else:
        plot_df = combined.copy()

    if plot_df.empty:
        st.warning("No rows to plot for the selected barangay/date range.")
    else:
        fig, ax1 = plt.subplots(figsize=(10,4))
        ax1.plot(plot_df['Date'], plot_df['Cases'], color='red', marker='o', label='Actual Cases')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Cases', color='red')
        ax2 = ax1.twinx()
        ax2.plot(plot_df['Date'], plot_df['Temp_Max'], color='blue', marker='x', label='Max Temp (°C)')
        ax2.set_ylabel('Temp Max (°C)', color='blue')
        # combine legends
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc='upper left')
        st.pyplot(fig)
else:
    st.info("Please upload a flu dataset CSV to begin.")
