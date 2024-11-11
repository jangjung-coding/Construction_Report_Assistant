import os
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Load environment variables for API key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Function to fetch current weather using OpenWeatherMap API (including temperature, humidity, wind direction, and wind speed)
def fetch_weather_data(city="Seoul"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description'].capitalize()
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        wind_direction = data['wind']['deg']
        
        return {
            "description": weather_description,
            "temperature": f"{temperature}°C",
            "humidity": f"{humidity}%",
            "wind_speed": f"{wind_speed} m/s",
            "wind_direction": f"{wind_direction}°"
        }
    else:
        return {
            "description": "Weather data unavailable",
            "temperature": "-",
            "humidity": "-",
            "wind_speed": "-",
            "wind_direction": "-"
        }

# Function to read CSV file and generate report layout
def generate_report(construction_name, inspection_date, inspector_name):
    # Read CSV file containing inspection records
    if os.path.exists('captions_records.csv'):
        df = pd.read_csv('captions_records.csv')
        
        # Display header of report (e.g., construction name, location, date)
        st.title("일일 정기 안전 점검 보고서")
        
        # Display construction name, inspection date, and inspector name
        st.write(f"**공사명:** {construction_name}")
        st.write(f"**점검날짜:** {inspection_date}")
        st.write(f"**작성자:** {inspector_name}")
        
        # Fetch and display current weather data from API (including temperature, humidity, wind speed, and direction)
        weather_data = fetch_weather_data(city="Seoul")
        
        # Display Weather Information in a row format like your image.
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**날씨:** {weather_data['description']}")
        
        with col2:
            st.write(f"**온도:** {weather_data['temperature']}")
        
        with col3:
            st.write(f"**습도:** {weather_data['humidity']}")
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.write(f"**풍속:** {weather_data['wind_speed']}")
        
        with col5:
            st.write(f"**풍향:** {weather_data['wind_direction']}")
        
        st.markdown("---")
        
        # Display each row from the CSV file as part of the report (similar to your image format)
        for index, row in df.iterrows():
            st.subheader(f"[CAMERA{index + 1}] {row['생성시간']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(row['이미지 경로'], width=300)
                st.write(f"<Area{index + 1}> {row['캡셔닝 1']}")
            
            with col2:
                # Assuming a second image is available; otherwise remove this line.
                st.image(row['이미지 경로'], width=300)  
                st.write(f"<Area{index + 1}> {row['캡셔닝 2']}")
            
            st.write(f"**안전 상태:** {row['안전상태']}")
            
            if row['안전상태'] == "불안전":
                st.warning(f"**불안전 판단 이유:** {row['불안전 판단 이유']}")
            
            st.markdown("---")
        
    else:
        st.error("No CSV file found. Please generate captions first.")

# Main function to run the CreateReport page
def run_create_report():
    st.title("📄 Create Safety Inspection Report")
    
    # User inputs for construction name, inspection date, and inspector name
    construction_name = st.text_input("공사명", value="공사명 입력")
    inspection_date = st.date_input("점검날짜", value=datetime.today())
    inspector_name = st.text_input("작성자", value="작성자 이름 입력")
    
    # Generate report button
    if st.button("Generate Report"):
        generate_report(construction_name, inspection_date.strftime('%Y.%m.%d'), inspector_name)