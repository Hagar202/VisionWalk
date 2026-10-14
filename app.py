"""VisionWalk Streamlit app. Run with:  streamlit run app.py"""

import streamlit as st
import os
import time
import uuid
from yolov8_inference import detect_image, detect_video, LiveCamProcessor
from streamlit_webrtc import webrtc_streamer
import base64

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Set page config with modern theme and logo
st.set_page_config(
    page_title="VisionWalk",
    layout="centered",
    page_icon="Logo.png" # Make sure to have Logo.png in your directory
)

# Function to encode image to base64
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Function to set background image
def set_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpg;base64,{encoded_string});
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            background-blur: 2px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background image (replace with your actual image path)
background_image_path = "Background.png"
if os.path.exists(background_image_path):
    set_background(background_image_path)

# Custom CSS for the modern, youthful design
st.markdown(
    """
    <style>
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    :root {
        --primary: #ff9ff3;
        --secondary: #a55eea;
        --dark: #341f97;
        --light: #fef6e4;
    }
    
    body {
        background-image: url('Background.png');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 0;
    }
    
    .stApp {
        background-color: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(4px);
        min-height: 100vh;
    }
    
    .logo-container {
        position: absolute;
        top:-30px;
        left:-10px;
        z-index: 1000;
        animation: float 6s ease-in-out infinite;
    }
    
    .logo {
        width: 80px;
        height: auto;
        border-radius: 50%;
        box-shadow: 0 10px 30px rgba(165, 94, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .logo:hover {
        transform: scale(1.05) rotate(5deg);
        box-shadow: 0 15px 40px rgba(165, 94, 234, 0.6);
    }
    
    .title {
        text-align: center;
        font-size: 2.8em;
        background: white;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-bottom: 0.3em;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: float 4s ease-in-out infinite;
    }
    
    .section-title {
        background: rgba(255, 255, 255, 0.7);
        padding: 12px 20px;
        border-radius: 20px;
        background: linear-gradient(to right, #ffd6e7, #e2c1ff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-top: 1.5em;
        font-size: 1.4em;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #a55eea;
        transition: all 0.3s ease;
        margin-bottom: 1em;
    }
    
    .section-title:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stRadio > div {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin-bottom: 1.5em;
    }
    
    .stRadio > div:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stFileUploader {
        background: rgba(255, 255, 255, 0.7);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin-bottom: 1.5em;
    }
    
    .stFileUploader:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stButton>button {
        background: linear-gradient(to right, #a55eea, #ff9ff3);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(165, 94, 234, 0.3);
        margin-bottom: 1.5em;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(165, 94, 234, 0.4);
        background: linear-gradient(to right, #ff9ff3, #a55eea);
    }
    
    .stSpinner>div {
        color: #a55eea;
    }
    
    .stAlert {
        border-radius: 15px;
        transition: all 0.3s ease;
        margin-bottom: 1.5em;
        background: rgba(255, 255, 255, 0.7);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stAlert:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stVideo {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        margin-bottom: 1.5em;
    }
    
    .stVideo:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
    }
    
    .stImage {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        margin-bottom: 1.5em;
    }
    
    .stImage:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
    }
    
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    .text-content {
        color: white;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    .gradient-text {
        background: linear-gradient(to right, #ff9ff3, #a55eea);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Logo in top-left corner
logo_path = "Logo1.png"
if os.path.exists(logo_path):
    logo_base64 = get_image_base64(logo_path)
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" class="logo" alt="VisionWalk Logo">
        </div>
        """, 
        unsafe_allow_html=True
    )

# Header
st.markdown(
    """
    <div class="title">
        <span style="font-size: 1.2em;">✨</span> VisionWalk AI 
        <span style="font-size: 1.2em;">🚶</span><br>
        <span style="font-size: 0.6em; display: block; margin-top: 5px;">
        Real-time Person Detection with YOLOv8
        </span>
    </div>
    """, 
    unsafe_allow_html=True
)

# Short description
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 30px; color: white; font-size: 1.1em;" class="text-content">
    Detect people in images, videos, or live camera feed using cutting-edge AI technology
    </div>
    """,
    unsafe_allow_html=True
)

# --- Section Selector ---
st.markdown('<div class="section-title">📲 Choose Your Detection Method</div>', unsafe_allow_html=True)
option = st.radio(
    "Select input type:", 
    ["Upload Image", "Upload Video", "Use Live Camera"], 
    horizontal=True,
    label_visibility="collapsed"
)

# Divider with style
st.markdown("---")

# --- Uploaded Image ---
if option == "Upload Image":
    st.markdown('<div class="section-title">📸 Image Detection</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="text-content" style="margin-bottom: 20px;">
    Upload an image to detect people using our AI model
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader(
        "Choose an image...", 
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
    
    if uploaded_image:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**<span class='gradient-text'>Original Image</span>**", unsafe_allow_html=True)
            st.image(uploaded_image, use_container_width =True)
        
        with st.spinner("🔍 AI is analyzing your image..."):
            input_path = os.path.join("uploads", uploaded_image.name)
            with open(input_path, "wb") as f:
                f.write(uploaded_image.read())
            
            output_path = os.path.join("outputs", "detected_image.jpg")
            result = detect_image(input_path, output_path)
            
            with col2:
                st.markdown("**<span class='gradient-text'>Detected People</span>**", unsafe_allow_html=True)
                st.image(result, use_container_width =True)
        
        st.success("Detection completed!")

# --- Uploaded Video ---
elif option == "Upload Video":
    st.markdown('<div class="section-title">🎥 Video Detection</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="text-content" style="margin-bottom: 20px;">
    Upload a video to detect people in motion
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_video = st.file_uploader(
        "Choose a video...", 
        type=["mp4", "avi", "mov", "webm"],
        label_visibility="collapsed"
    )
    
    if uploaded_video:
        st.markdown("**<span class='gradient-text'>Original Video</span>**", unsafe_allow_html=True)
        st.video(uploaded_video)
        
        unique_name = f"detected_{uuid.uuid4().hex}.webm"
        output_path = os.path.join("outputs", unique_name)
        
        with st.spinner("🎬 Processing video with AI (this may take a while)..."):
            input_path = os.path.join("uploads", uploaded_video.name)
            with open(input_path, "wb") as f:
                f.write(uploaded_video.read())
            
            result_path = detect_video(input_path, output_path)
        
        # Wait for file to be ready
        wait_time = 0
        while (not os.path.exists(result_path) or os.path.getsize(result_path) < 1000 and wait_time < 5):
            time.sleep(0.5)
            wait_time += 0.5
        
        if os.path.exists(result_path):
            st.success("✅ Detection completed! Here's the result:")
            st.markdown("**<span class='gradient-text'>Processed Video</span>**", unsafe_allow_html=True)
            with open(result_path, "rb") as video_file:
                video_bytes = video_file.read()
                st.video(video_bytes)
        else:
            st.error("❌ Something went wrong. Please try again.")

# --- Live Camera ---
elif option == "Use Live Camera":
    st.markdown('<div class="section-title">📡 Live Camera Detection</div>', unsafe_allow_html=True)
    
    st.info("""
    **ℹ️ How to use:**  
    - Click 'Start' to begin camera detection  
    - Make sure to allow camera access in your browser  
    - Click 'Stop' when finished  
    """, icon="💡")
    
    # Camera visualization with glassmorphism effect
    st.markdown(
        """
        <style>
        .camera-container {
            background: rgba(255, 255, 255, 0.3);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(165, 94, 234, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .camera-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(165, 94, 234, 0.3);
        }
        </style>
        
        <div class="camera-container floating">
        """,
        unsafe_allow_html=True
    )
    
    webrtc_streamer(
        key="live",
        video_processor_factory=LiveCamProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    st.markdown("</div>", unsafe_allow_html=True)