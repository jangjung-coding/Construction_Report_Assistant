# import os
# import streamlit as st
# from PIL import Image
# from datetime import datetime
# import pandas as pd
# import google.generativeai as genai
# from io import BytesIO
# import json
# from dotenv import load_dotenv

# # Load environment variables for the API key
# load_dotenv()
# GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GOOGLE_API_KEY:
#     st.error("Gemini API key is missing. Please check your environment variables.")
#     raise ValueError("Gemini API key is missing.")

# # Configure the Gemini AI model using generation_config
# genai.configure(api_key=GOOGLE_API_KEY)
# generation_config = {
#     "temperature": 0.7,
#     "top_p": 0.95,
#     "top_k": 40,
#     "max_output_tokens": 8192,
# }

# system_instruction_caption = (
#     "당신은 한국 건설현장의 안전관리자 보조입니다. "
#     "안전 관리자가 건설 현장 이미지를 업로드하면, 작업자의 행동을 분석하고 다음 항목을 중심으로 캡션을 작성하세요:\n"
#     "1. 작업 종류\n"
#     "2. 작업자\n"
#     "3. 안전장비 착용 여부\n"
#     "4. 작업에 따른 안전 규칙 준수 여부\n\n"
# )

# def gemini_flash():
#     """Sets up the Gemini AI model."""
#     model = genai.GenerativeModel(
#         model_name="gemini-1.5-flash", 
#         generation_config=generation_config
#     )
#     return model

# def gemini_vision():
#     """Wrapper for initializing the Gemini AI model."""
#     return gemini_flash()

# def parse_json_data(json_data):
#     """Parses the JSON data and handles cases where the format is not standard."""
    
#     extracted_info = []
    
#     try:
#         if isinstance(json_data, list):
#             for item in json_data:
#                 if isinstance(item, dict):
#                     frame_id = item.get("frame_id", "Unknown frame_id")
#                     filename = item.get("filename", "Unknown filename")
#                     objects = item.get("objects", [])
                    
#                     for obj in objects:
#                         class_id = obj.get("class_id", "Unknown class_id")
#                         name = obj.get("name", "Unknown name")
#                         confidence = obj.get("confidence", "Unknown confidence")
#                         extracted_info.append(f"Frame ID: {frame_id}, Filename: {filename}, Object: {name}, Confidence: {confidence}")
                        
#         elif isinstance(json_data, dict):
#             for key, value in json_data.items():
#                 extracted_info.append(f"{key}: {value}")
                
#         return extracted_info
    
#     except Exception as e:
#         st.error(f"Error parsing JSON: {e}")
#         return []

# def generate_caption(model, image, json_data=None):
#     """Generates a caption using the Gemini AI model."""
    
#     # Convert PIL image to bytes and specify MIME type (e.g., image/jpeg)
#     img_byte_arr = BytesIO()
#     image.save(img_byte_arr, format='JPEG')
#     img_bytes = img_byte_arr.getvalue()

#     json_info = ""
    
#     if json_data:
#         extracted_info = parse_json_data(json_data)
#         if extracted_info:
#             json_info = f"\n추가 정보: {', '.join(extracted_info)}"

#     prompt = (
#         system_instruction_caption + json_info + 
#         "\n작업자의 작업 내용과 안전 장비 착용 여부를 구체적으로 설명하세요."
#         "\n작업 환경의 위험 요소가 있는지 확인하세요."
#         "\n작업자가 헬멧이나 보호 장비를 착용하고 있는지 여부도 포함하세요."
#         "\n캡션은 한글로 45자 내외로 공식적인 문서 형식으로 작성해야 합니다."
#     )

#     contents = [
#         {
#             "role": "user",
#             "parts": [
#                 {"text": prompt},
#                 {"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}}
#             ]
#         }
#     ]

#     response = model.generate_content(contents=contents)
    
#     captions = response.text.split("\n")
    
#     if len(captions) > 0:
#         caption = captions[0].strip()
#         return caption
    
#     return "캡셔닝이 생성되지 않았습니다."

# def get_current_timestamp():
#     """Returns the current timestamp."""
#     return datetime.now().strftime('%Y-%m-%d %H:%M')

# def save_to_csv(csv_file_path, timestamp, caption, image_path):
#     """Saves the generated data to a CSV file."""
    
#     record = {
#         '생성시간': timestamp,
#         '이미지 경로': image_path,
#         '캡셔닝': caption,
#     }

#     try:
#         # Check if the file exists; if not, create it with appropriate columns.
#         if os.path.exists(csv_file_path):
#             try:
#                 df = pd.read_csv(csv_file_path)
#             except pd.errors.EmptyDataError:
#                 df = pd.DataFrame(columns=record.keys())
#         else:
#             df = pd.DataFrame(columns=record.keys())

#         # Append the new record using pd.concat.
#         df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)

#         # Save back to CSV.
#         df.to_csv(csv_file_path, index=False)
        
#         return True
    
#     except Exception as e:
#         st.error(f"Error saving to CSV: {e}")
#         return False

# def reset_session_state():
#     """Resets session state for generating new captions."""
#     st.session_state["caption"] = None
#     st.session_state["timestamp"] = None

# def run_image_captioning():
#     """Main function to run the image captioning process."""
    
#     st.title("🖼️ Image Captioning with JSON")

#     csv_file_path = 'captions_records.csv'

#     colLeft, colRight = st.columns(2)

#     with colLeft:
#         uploaded_image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

#     with colRight:
#         uploaded_json_file = st.file_uploader("Upload JSON File", type=["json"])

#     if uploaded_image_file is not None:

#         load_image = Image.open(uploaded_image_file)

#         # Display uploaded image on left side
#         st.image(load_image.resize((800, 500)))

#         # Parse JSON file (if provided)
#         json_data = None

#         if uploaded_json_file is not None:
#             try:
#                 json_data = json.load(uploaded_json_file)
#                 st.json(json_data)  # Display parsed JSON data on right side
#             except Exception as e:
#                 st.error(f"Error loading JSON file: {e}")

#         # Generate caption after selecting an image and (optionally) a JSON file.
#         if st.button("Generate Caption"):
#             reset_session_state()  # Reset session state before generating a new caption.
#             model = gemini_vision()

#             # Generate caption only (no safety status)
#             caption_result = generate_caption(model, load_image, json_data=json_data)

#             # Store generated data into session state so it persists across interactions.
#             st.session_state["caption"] = caption_result
#             st.session_state["timestamp"] = get_current_timestamp()

#             # Display the results along with timestamp below the JSON data.
#             st.info(f"**캡셔닝:** {st.session_state['caption']}")
#             st.info(f"**생성 시간:** {st.session_state['timestamp']}")

#         # Step to save data into CSV when Save button is clicked
#         if st.button("Save"):
#             success = save_to_csv(
#                 csv_file_path=csv_file_path,
#                 timestamp=st.session_state['timestamp'],
#                 caption=st.session_state["caption"],
#                 image_path=uploaded_image_file.name
#             )

#             if success:
#                 st.success(f"Data saved successfully!")
#             else:
#                 st.error(f"Failed to save data.")

#################################################

import os
import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd
import google.generativeai as genai
from io import BytesIO
import json
from dotenv import load_dotenv
import time  # 딜레이를 위한 모듈

# Load environment variables for the API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Gemini API key is missing. Please check your environment variables.")
    raise ValueError("Gemini API key is missing.")

# Configure the Gemini AI model using generation_config
genai.configure(api_key=GOOGLE_API_KEY)
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# 3. 역할 및 지침 정의
role_instruction = (
    "**역할**: 당신은 한국 건설 현장의 안전관리자 보조입니다. "
    "이미지를 분석하여 '작업 종류', '작업자 명수', '안전장비 착용 여부', '안전 수칙 준수 여부'를 바탕으로 캡셔닝을 작성합니다."
)

work_guidelines = (
    "### 작업 지침\n"
    "- **작업 분석**:\n"
    "  - 사다리의 2인 1조 작업의 경우, 2명 이상이 감지된 경우에는 해당 안전수칙을 제외합니다.\n"
    "  - 1명만 감지된 경우에는 2인 1조 작업에 대해 반드시 포함합니다.\n"
    "  - UA-19 코드가 포함된 경우, '사다리에 2명 이상 올라가는 행위'가 우선 언급됩니다."
)

safety_rules_summary = (
    "- **사다리 작업 안전수칙**:\n"
    "  - 120~200cm: 2인 1조, 최상부 발판 작업 금지\n"
    "  - 200~350cm: 2인 1조, 안전대 필수\n"
    "  - 350cm 초과: 발판 사용 금지\n"
    "  - 모든 작업 시 안전모 착용 필수\n"
    "- **고소작업대 안전수칙**:\n"
    "  - 안전모, 안전대 착용\n"
    "  - 발끝막이판 설치\n"
    "  - 작업구역 통제 필수\n"
    "  - 경사지 작업 시 고임목 설치"
)

json_code_explanation = (
    "### JSON 코드 해석\n"
    "- **작업자 관련 코드**:\n"
    "  - WO-01=작업자\n"
    "  - WO-02=수신원\n"
    "  - WO-03=이동식 비계\n"
    "  - WO-04=안전모 미착용\n"
    "  - WO-05=안전벨트 미착용\n"
    "  - WO-06=안전고리 미착용\n"
    "  - WO-07=안전화 미착용\n"
    "- **장비/도구 코드**:\n"
    "  - WO-08=고소작업차(렌탈차)\n"
    "  - WO-09=스카이차\n"
    "  - SO-01=안전 난간\n"
    "  - SO-02=안전 발판\n"
    "  - SO-03=A형 사다리\n"
    "  - SO-04=내부 비계 전도방지대 미설치\n"
    "  - SO-05=과상승방지봉 미설치\n"
    "  - SO-06=로프\n"
    "  - SO-07=고임목 미설치\n"
    "  - SO-08=안전 덮개\n"
    "  - SO-09=코킹건\n"
    "  - SO-10=헤라\n"
    "  - SO-11=커터칼\n"
    "  - SO-12=망치\n"
    "  - SO-14=드릴\n"
    "  - SO-15=렌치\n"
    "  - SO-18=니퍼\n"
    "  - SO-19=와이퍼\n"
    "  - SO-20=착기\n"
    "  - SO-22=테이프 류\n"
    "  - SO-24=고대\n"
    "  - SO-25=조명기구\n"
    "  - SO-26=벽돌\n"
    "  - SO-27=레미탈\n"
    "  - SO-29=콘크리트 벽돌\n"
    "- **불안전 상황 코드**:\n"
    "  - UA-01=안전고리 미체결\n"
    "  - UA-02=안전벨트 미착용\n"
    "  - UA-03=안전화 미착용\n"
    "  - UA-04=안전모 미착용\n"
    "  - UA-05=안전 난간에 오르는 행위\n"
    "  - UA-06=안전 난간 밖으로 몸을 기울이는 행위\n"
    "  - UA-07=안전 발판 위 2명 이상 오르는 행위\n"
    "  - UA-08=안전 발판 끝단에서 작업하는 행위\n"
    "  - UA-09=적재물 위에서 근로자 작업\n"
    "  - UA-10=적재물을 안전 난간 밖으로 던지는 행위\n"
    "  - UA-11=안전 난간에 오르는 행위\n"
    "  - UA-12=안전 난간 밖으로 몸을 기울이는 행위\n"
    "  - UA-13=안전 발판 위 2명 이상 오르는 행위\n"
    "  - UA-14=안전 발판 끝단에서 작업하는 행위\n"
    "  - UA-15=적재물 위에서 근로자 작업\n"
    "  - UA-16=적재물을 안전 난간 밖으로 던지는 행위\n"
    "  - UA-17=사다리를 등지고 기대서 작업하는 행위\n"
    "  - UA-18=보조지지자 미동행\n"
    "  - UA-19=사다리에 2명 이상 오르는 행위\n"
    "  - UA-20=사다리 끝단에서 작업하는 행위\n"
    "  - UA-21=자재 및 공구를 사다리 위에 놓는 행위\n"
    "  - UA-22=자재 및 공구를 사다리 밑으로 던지는 행위\n"
    "  - UA-23=안전 난간에 오르는 행위\n"
    "  - UA-24=안전 난간 밖으로 몸을 기울이는 행위\n"
    "  - UA-25=안전 발판 위 2명 이상 오르는 행위\n"
    "  - UA-26=안전 발판 끝단에서 작업하는 행위\n"
    "  - UA-27=적재물 위에서 근로자 작업\n"
    "  - UA-28=적재물을 안전 난간 밖으로 던지는 행위\n"
    "  - UA-30=작업자가 출입문을 여는 행위\n"
    "  - UC-01=안전 난간 미설치\n"
    "  - UC-02=안전 발판 미설치\n"
    "  - UC-03=안전 난간 위 발판 설치\n"
    "  - UC-04=안전 난간 미설치\n"
    "  - UC-05=전도방지대 미설치\n"
    "  - UC-06=안전 난간 위 발판 설치\n"
    "  - UC-07=적재물 위에 사다리 설치\n"
    "  - UC-08=전도방지대 미설치\n"
    "  - UC-09=고임목 미설치\n"
    "  - UC-10=과상승방지봉 미설치\n"
    "  - UC-11=렌탈차량 통행로 미확보\n"
    "  - UC-12=전도방지대 미설치"
)

captioning_rules = (
    "### 캡셔닝 규칙\n"
    "1. **한글 30자 이상 40자 이하 내로 작성**\n"
    "2. 불안전 상황이 있으면: \"~ 중, 조치 필요\"로 작성.\n"
    "3. 위험 상황이 없으면: \"~ 중, 준수\"로 작성.\n"
    "4. 작업자가 없으면: \"작업자는 인식되지 않음\"으로 시작.\n"
    "5. JSON 코드는 정의만 반영 (예: WO-01 대신 '작업자')."
)

# 4. 시스템 지침 통합
system_instruction = (
    role_instruction + "\n\n"
    + work_guidelines + "\n"
    + safety_rules_summary + "\n\n"
    + json_code_explanation + "\n\n"
    + captioning_rules
)

def gemini_flash():
    """Sets up the Gemini AI model."""
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        generation_config=generation_config
    )
    return model

def gemini_vision():
    """Wrapper for initializing the Gemini AI model."""
    return gemini_flash()

def parse_json_data(json_data):
    """Parses the JSON data and handles cases where the format is not standard."""
    extracted_info = []
    try:
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                extracted_info.append(f"{key}: {value}")
        elif isinstance(json_data, list):
            for item in json_data:
                if isinstance(item, dict):
                    extracted_info.append(json.dumps(item, ensure_ascii=False))
        return extracted_info
    except Exception as e:
        st.error(f"Error parsing JSON: {e}")
        return []

def generate_captions(model, image, json_data=None, num_captions=20):
    """Generates multiple captions using the Gemini AI model."""
    # Convert PIL image to bytes
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()

    json_info = ""
    if json_data:
        extracted_info = parse_json_data(json_data)
        if extracted_info:
            json_info = f"\n추가 정보: {', '.join(extracted_info)}"

    prompt = (
        system_instruction + json_info + 
            "### 캡셔닝 예시\n"
            "- '작업자가 사다리 위에서 드릴 작업 중, 안전모 미착용으로 조치 필요'\n"
            "- '작업자가 사다리 위에서 작업 중, 안전모 착용 및 2인 1조 작업을 준수'\n"
            "- '작업자는 인식되지 않음, 고임목 미설치 확인 조치 필요'"
    )

    captions = []
    for i in range(num_captions):
        contents = [
            {
                "role": "user",
                "parts": [
                    {"text": f"캡셔닝 {i+1}: {prompt}"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}}
                ]
            }
        ]
        response = model.generate_content(contents=contents)
        caption = response.text.strip()
        captions.append(caption)
    
    return captions

def get_current_timestamp():
    """Returns the current timestamp."""
    return datetime.now().strftime('%Y-%m-%d %H:%M')

def save_to_csv(csv_file_path, records):
    """Saves multiple records to a CSV file."""
    try:
        # Check if the file exists; if not, create it with appropriate columns.
        if os.path.exists(csv_file_path):
            try:
                df = pd.read_csv(csv_file_path)
            except pd.errors.EmptyDataError:
                df = pd.DataFrame(columns=records[0].keys())
        else:
            df = pd.DataFrame(columns=records[0].keys())

        # Append the new records using pd.concat.
        df = pd.concat([df, pd.DataFrame(records)], ignore_index=True)

        # Save back to CSV.
        df.to_csv(csv_file_path, index=False)
        
        return True
    except Exception as e:
        st.error(f"Error saving to CSV: {e}")
        return False

def run_image_captioning():
    """Main function to run the image captioning process."""
    st.title("🖼️ Image Captioning with JSON (1000 Captions)")

    csv_file_path = '/Users/computer/Desktop/capstone2/captions_records_1000.csv'

    colLeft, colRight = st.columns(2)
    with colLeft:
        uploaded_image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    with colRight:
        uploaded_json_file = st.file_uploader("Upload JSON File", type=["json"])

    if uploaded_image_file is not None:
        load_image = Image.open(uploaded_image_file)
        st.image(load_image.resize((800, 500)), caption="Uploaded Image", use_column_width=True)

        json_data = None
        if uploaded_json_file is not None:
            try:
                json_data = json.load(uploaded_json_file)
                st.json(json_data)
            except Exception as e:
                st.error(f"Error loading JSON file: {e}")

        if st.button("Generate and Save 100 Captions"):
            model = gemini_vision()
            all_captions = []
            for batch in range(20):
                st.info(f"Generating captions batch {batch + 1}...")
                generated_captions = generate_captions(model, load_image, json_data=json_data, num_captions= 5)
                all_captions.extend(generated_captions)
                timestamp = get_current_timestamp()

                # Prepare records for saving
                records = [
                    {
                        '생성시간': timestamp,
                        '이미지 경로': uploaded_image_file.name,
                        '캡셔닝': caption
                    }
                    for caption in generated_captions
                ]

                # Save to CSV after each batch
                save_to_csv(csv_file_path, records)
                st.success(f"Batch {batch + 1} saved to CSV.")
                time.sleep(10)  # 딜레이 추가 (API Rate 제한 방지)

            st.success(f"Total 100 captions saved to {csv_file_path}")
            st.download_button("📥 Download CSV", data=pd.DataFrame(all_captions).to_csv(index=False), file_name="captions_records_1000.csv", mime="text/csv")