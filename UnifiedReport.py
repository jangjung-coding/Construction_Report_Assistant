import os
import streamlit as st
from datetime import datetime
import pandas as pd
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import requests

# Load environment variables for API keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Error handling for missing API keys
if not GOOGLE_API_KEY:
    st.error("Gemini API key is missing. Please check your environment variables.")
    raise ValueError("Gemini API key is missing.")
if not WEATHER_API_KEY:
    st.error("Weather API key is missing. Please check your environment variables.")
    raise ValueError("Weather API key is missing.")

# Configure the Gemini AI model using generation_config
genai.configure(api_key=GOOGLE_API_KEY)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

CSV_FILE_PATH = 'captions_records.csv'  # Path to your CSV file

# Function to fetch weather data using OpenWeatherMap API
def fetch_weather_data(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        return {
            "description": data['weather'][0]['description'].capitalize(),
            "temperature": f"{data['main']['temp']}°C",
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s",
            "wind_direction": f"{data['wind']['deg']}°"
        }
    except Exception as e:
        st.error(f"Failed to fetch weather data: {e}")
        return None

# Function to generate a summary using Gemini AI
def generate_summary_with_gemini(summary_prompt):
    contents = [{"role": "user", "parts": [{"text": summary_prompt}]}]
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    response = model.generate_content(contents=contents)
    return response.text.strip()

# Function to generate a summary report based on the selected inspection date
def generate_summary(inspection_date):
    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except Exception as e:
        st.error(f"CSV 파일을 불러오는 중 오류 발생: {e}")
        return
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    df['생성시간'] = pd.to_datetime(df['생성시간'])
    selected_date_str = inspection_date.strftime('%Y-%m-%d')
    selected_data = df[df['생성시간'].dt.strftime('%Y-%m-%d') == selected_date_str]

    if selected_data.empty:
        st.warning(f"{selected_date_str}의 데이터가 없습니다.")
        return

    prompt_data = ""
    for index, row in selected_data.iterrows():
        prompt_data += f"작업자 기록 {index + 1}:\n- 생성시간: {row['생성시간']}\n- 캡셔닝: {row['캡셔닝']}\n- 안전 상태: {row['안전상태']}\n"
        if pd.notna(row['불안전 사유']):
            prompt_data += f"- 불안전 사유: {row['불안전 사유']}\n"
        else:
            prompt_data += "- 불안전 사유: 해당 없음\n"

    summary_prompt = (
        "다음은 하루 동안의 작업 기록입니다. 이 작업 기록을 바탕으로 하루 작업을 6줄 이내로 요약하십시오. "
        "건설 현장 일일 안전 점검 보고서 요약본이므로 공식적인 문체를 사용하세요."
        "날짜 관련 정보는 상단에 표기되므로 내용에 추가하지 마세요."
        "날씨 관련해서 작업에 문제가 있었다면 추가하세요."
        "요약에는 위험 사항이 몇 번 발생했는지, 언제 위험이 자주 발생했는지, 그리고 어떤 안전 수칙이 지켜지지 않았는지 포함하십시오:\n\n"
        + prompt_data
    )

    # Generate the summary and store it in session state
    summary = generate_summary_with_gemini(summary_prompt)
    st.session_state["summary"] = summary

# Function to load captions from CSV file
def load_captions_from_csv(inspection_date):
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        df['생성시간'] = pd.to_datetime(df['생성시간'])
        selected_date_str = inspection_date.strftime('%Y-%m-%d')
        selected_data = df[df['생성시간'].dt.strftime('%Y-%m-%d') == selected_date_str]
        if len(selected_data) >= 4:
            camera_1_images = [
                (selected_data.iloc[0]['캡셔닝'], selected_data.iloc[0]['안전상태'], selected_data.iloc[0].get('불안전 사유', ""), selected_data.iloc[0].get('이미지 경로', "")),
                (selected_data.iloc[1]['캡셔닝'], selected_data.iloc[1]['안전상태'], selected_data.iloc[1].get('불안전 사유', ""), selected_data.iloc[1].get('이미지 경로', ""))
            ]
            camera_2_images = [
                (selected_data.iloc[2]['캡셔닝'], selected_data.iloc[2]['안전상태'], selected_data.iloc[2].get('불안전 사유', ""), selected_data.iloc[2].get('이미지 경로', "")),
                (selected_data.iloc[3]['캡셔닝'], selected_data.iloc[3]['안전상태'], selected_data.iloc[3].get('불안전 사유', ""), selected_data.iloc[3].get('이미지 경로', ""))
            ]
            return camera_1_images, camera_2_images
        else:
            st.error("CSV 파일에 충분한 정보가 없습니다.")
            return None, None
    except Exception as e:
        st.error(f"CSV 파일 로드 중 오류 발생: {e}")
        return None, None

# Main function to run the report creation process
def run_create_report():
    col1, col2 = st.columns(2)
    with col1:
        inspection_date = st.date_input("점검날짜", value=datetime.today())
        inspector_name = st.text_input("작성자", value="홍길동")
        construction_name = st.text_input("공사명", value="공대 2호관 리모델링")
        construction_location = st.text_input("공사장소", value="Gwangju")

    with col2:
        if construction_location:
            weather_data = fetch_weather_data(construction_location)
            if weather_data:
                st.subheader("🌤️ 현재 날씨 정보")
                st.write(f"**날씨:** {weather_data['description']}")
                st.write(f"**온도:** {weather_data['temperature']}")
                st.write(f"**습도:** {weather_data['humidity']}")
                st.write(f"**풍속:** {weather_data['wind_speed']}")
                st.write(f"**풍향:** {weather_data['wind_direction']}")
            else:
                st.error("날씨 정보를 불러오지 못했습니다.")

    st.markdown("---")

    # Show stored summary if available
    if "summary" in st.session_state:
        st.text_area("📊 작업 요약", value=st.session_state["summary"], height=150)

    # Summary 버튼
    if st.button("Summary"):
        generate_summary(inspection_date)

    st.markdown("---")

    # Generate Report 버튼
    if st.button("Generate Report"):
        camera_1_images, camera_2_images = load_captions_from_csv(inspection_date)
        if camera_1_images and camera_2_images:
            st.markdown("### [CAMERA 1]")
            colLeftCam1, colRightCam1 = st.columns(2)
            for i, (caption, safety_status, unsafe_reason, image_path) in enumerate(camera_1_images):
                with (colLeftCam1 if i == 0 else colRightCam1):
                    if image_path and os.path.exists(image_path):
                        img_displayed_cam = Image.open(image_path)
                        st.image(img_displayed_cam.resize((500, 300)))
                    st.text_area(f" ", value=caption, key=f"caption_cam_{i}")
                    st.selectbox(f"안전 상태", ["안전", "불안전"], index=0 if safety_status == "안전" else 1, key=f"safety_status_cam_{i}")
                    if safety_status == "불안전":
                        st.text_area(f"불안전 사유 {i+1}:", value=unsafe_reason, key=f"unsafe_reason_cam_{i}")

            st.markdown("### [CAMERA 2]")
            colLeftCam2, colRightCam2 = st.columns(2)
            for i, (caption, safety_status, unsafe_reason, image_path) in enumerate(camera_2_images):
                with (colLeftCam2 if i == 0 else colRightCam2):
                    if image_path and os.path.exists(image_path):
                        img_displayed_cam = Image.open(image_path)
                        st.image(img_displayed_cam.resize((500, 300)))
                    st.text_area(f" ", value=caption, key=f"caption_cam_{i + 10}")
                    st.selectbox(f"안전 상태", ["안전", "불안전"], index=0 if safety_status == "안전" else 1, key=f"safety_status_cam_{i + 10}")
                    if safety_status == "불안전":
                        st.text_area(f"불안전 사유 {i+1}:", value=unsafe_reason, key=f"unsafe_reason_cam_{i + 10}")

# Unified page for both summary and report generation
def run_unified_page():
    st.title("👷‍♂️ 일일 정기 안전 점검 보고서")
    run_create_report()

if __name__ == "__main__":
    run_unified_page()