import os
import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd
import google.generativeai as genai
import time

# Set up Google Gemini-Pro AI model with the prompted configuration
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

def gemini_pro():
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=(
            "당신은 한국의 건설현장 안전관리자 보조입니다.\n"
            "일일 안전 점검 보고서와 안전 교육 보고서를 작성하는데 도움을 줘야합니다.\n"
            "안전 관리자가 건설 현장 이미지를 업로드하면,\n"
            "- 캡셔닝 1 : \"작업자가 어디에서 뭘하고 있고 뭐가 근처에 있는지\"를 이미지를 참고해서 써주고\n"
            "- 캡셔닝 2 : \"작업자가 무슨 작업을 하고 있고 어떤 안전수칙을 잘지키고있는지\"를 이미지를 참고해서 써주면 돼 "
            "작업의 종류는 사다리작업, 고소작업, 비계작업이 있어\n\n"
            "예시) 지금 주는 이미지로\n\n"
            "캡셔닝 1 : \"작업자가 A형사다리 위에서 작업을 하고 있고 드릴이 작업자 근처에 있습니다\"\n"
            "캡셔닝 2 : \"작업자가 사다리 작업을 하고 있고, 안전모 착용상태가 양호합니다\""
        )
    )
    return model

# Define gemini_vision as a wrapper around gemini_pro (fix for NameError)
def gemini_vision():
    return gemini_pro()

# Classify safety status based on captions
def classify_safety(caption1, caption2):
    safe_keywords = ['안전', '양호', '지킴', '문제가 없다']
    unsafe_keywords = ['위험', '문제', '사고', '인명', '안전수칙을 지키지 않음']
    
    if any(keyword in caption1 for keyword in safe_keywords) and \
       any(keyword in caption2 for keyword in safe_keywords):
        return 0  # Safe
    elif any(keyword in caption1 for keyword in unsafe_keywords) or \
         any(keyword in caption2 for keyword in unsafe_keywords):
        return 1  # Unsafe
    return 1  # Default to unsafe if unsure

def determine_unsafe_reason(caption1, caption2):
    unsafe_indicators = {
        '두 명 이상': '두 명 이상의 작업자가 사다리를 동시에 사용하고 있습니다.',
        '안전모': '작업자의 안전모 착용 상태가 불량합니다.',
        '위험한 기계': '위험한 기계가 작업자 근처에 있습니다.',
        '사다리 불안정': '사다리가 안정적으로 설치되지 않았습니다.',
        '보호 장비': '작업자가 보호 장비를 착용하지 않았습니다.',
        '높은 곳': '작업자가 높은 곳에서 작업하고 있으며 추락 위험이 있습니다.'
    }
    
    reasons = []
    
    for keyword, reason in unsafe_indicators.items():
        if keyword in caption1 or keyword in caption2:
            reasons.append(reason)

    return reasons if reasons else ['불안전 판단 이유를 찾을 수 없습니다.']

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d ## %H:%M')

# Retry mechanism to handle cases where 캡셔닝 2 is not generated correctly.
def retry_generate_captions(model, image, max_retries=3, delay=1):
    """Retry generating captions if 캡셔닝 2 is empty or incomplete."""
    
    attempt = 0
    
    while attempt < max_retries:
        attempt += 1
        
        # Generate captions using the AI model.
        caption1, caption2 = gemini_visoin_response(model, image)
        
        # Check if 캡셔닝 2 is valid.
        if caption2 and caption2 != "캡셔닝 2가 생성되지 않았습니다.":
            return caption1, caption2
        
        # If not valid, wait before retrying.
        time.sleep(delay)
    
    # Return the last attempt's result even if it's incomplete.
    return caption1, caption2

def gemini_visoin_response(model, image):
    response = model.generate_content([image])
    
    captions = response.text.split("\n")
    
    if len(captions) >= 2:
        caption1 = captions[0].strip()
        caption2 = captions[1].strip()
    else:
        caption1 = captions[0].strip() if len(captions) > 0 else ""
        caption2 = "캡셔닝 2가 생성되지 않았습니다."

    return caption1, caption2

# Save data to CSV file (now includes image path)
def save_to_csv(timestamp, safety_status, caption1, caption2, unsafe_reasons, image_path):
    record = {
        '생성시간': timestamp,
        '이미지 경로': image_path,
        '안전상태': safety_status,
        '캡셔닝 1': caption1,
        '캡셔닝 2': caption2,
        '불안전 판단 이유': ', '.join(unsafe_reasons)
    }
    
    try:
        # Check if the file exists; if not, create it with appropriate columns.
        if os.path.exists('captions_records.csv'):
            df = pd.read_csv('captions_records.csv')
        else:
            df = pd.DataFrame(columns=record.keys())

        # Append the new record using pd.concat.
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)

        # Save back to CSV.
        df.to_csv('captions_records.csv', index=False)
        
        return True

    except Exception as e:
        st.error(f"Error saving to CSV: {e}")
        return False

def run_image_captioning():
   st.title("🖼️ Image Captioning")

   # Specify the folder containing images
   image_folder_path = "/Users/computer/Desktop/capstone2/IMG/"

   # Check if the directory exists and list images
   if os.path.exists(image_folder_path):  
       image_files = [f for f in os.listdir(image_folder_path) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
       
       if len(image_files) == 0:
           st.error("No images found in the folder.")
           return

       # Allow user to select an image from the list of available images
       selected_image_file = st.selectbox("Select an image:", image_files)

       # Full path of the selected image file
       selected_image_path = os.path.join(image_folder_path, selected_image_file)

       colLeft, colRight = st.columns(2)

       # Display the selected image on the left column
       with colLeft:
           load_image = Image.open(selected_image_path)
           st.image(load_image.resize((800, 500)))

       # Add a button to generate captions after selecting an image.
       if st.button("Generate Caption"):
           model = gemini_vision()

           # Use retry mechanism to handle cases where 캡셔닝 2 is not generated correctly.
           caption1, caption2 = retry_generate_captions(model, load_image)

           # Store generated data into session state so it persists across interactions.
           st.session_state["caption1"] = caption1
           st.session_state["caption2"] = caption2
           st.session_state["safety_status_value"] = classify_safety(caption1, caption2)
           st.session_state["timestamp"] = get_current_timestamp()
           st.session_state["unsafe_reasons_list"] = determine_unsafe_reason(caption1, caption2) \
               if st.session_state["safety_status_value"] == 1 else []

       # Check if captions have been generated and stored in session state.
       if "caption1" in st.session_state and "caption2" in st.session_state:

           # Allow editing of captions and safety status before saving.
           edited_caption1 = st.text_area("Edit 캡셔닝 1:", value=st.session_state["caption1"])
           edited_caption2 = st.text_area("Edit 캡셔닝 2:", value=st.session_state["caption2"])
           edited_safety_status_text = st.selectbox(
               "Edit 안전 상태:", ["안전", "불안전"], index=st.session_state["safety_status_value"]
           )

           # Display the edited results along with safety status and timestamp.
           with colRight:
               st.info(f"**캡셔닝 1:** {edited_caption1}")
               st.info(f"**캡셔닝 2:** {edited_caption2}")
               st.info(f"**안전 상태:** {edited_safety_status_text}")
               st.info(f"**생성 시간:** {st.session_state['timestamp']}")

               # If unsafe, show reasons why it's considered unsafe.
               if edited_safety_status_text == "불안전":
                   st.warning(f"**불안전 판단 이유:** {', '.join(st.session_state['unsafe_reasons_list'])}")

           # Step to save data into CSV when Save button is clicked 
           if st.button("Save"):
               success = save_to_csv(
                   timestamp=st.session_state['timestamp'],
                   safety_status=edited_safety_status_text,
                   caption1=edited_caption1,
                   caption2=edited_caption2,
                   unsafe_reasons=st.session_state['unsafe_reasons_list'],
                   image_path=selected_image_path
               )
               if success:
                   st.success(f"Data saved successfully!")
               else:
                   st.error(f"Failed to save data.")
   else:
       st.error(f"Image folder not found at path: {image_folder_path}")