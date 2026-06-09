import streamlit as st
import os
import time
import json
import urllib.request
import urllib.parse
from pypinyin import pinyin, Style

# Direct link to your custom Imgflip GIF background
BACKGROUND_GIF_URL = "https://i.imgflip.com/ato4on.gif"

# Native translation function
def native_translate(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=zh-CN&tl=en&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            return "".join([sentence[0] for sentence in res[0]])
    except Exception:
        return "Translation temporarily unavailable"

# Advanced function to parse pinyin and inject vibrant HTML colors based on tone marks
def color_code_pinyin(text):
    words = text.split(" ")
    colored_words = []
    
    tone_1 = ['ā', 'ē', 'ī', 'ō', 'ū', 'ǖ', 'Ā', 'Ē', 'Ī', 'Ō', 'Ū', 'Ǖ']
    tone_2 = ['á', 'é', 'í', 'ó', 'ú', 'ǘ', 'Á', 'É', 'Í', 'Ó', 'Ú', 'Ǘ']
    tone_3 = ['ǎ', 'ě', 'ǐ', 'ǒ', 'ǔ', 'ǚ', 'Ǎ', 'Ě', 'Ǐ', 'Ǒ', 'Ǔ', 'Ǚ']
    tone_4 = ['à', 'è', 'ì', 'ò', 'ù', 'ǜ', 'À', 'È', 'Ì', 'Ò', 'Ù', 'Ǜ']
    
    for word in words:
        if any(char in tone_1 for char in word):
            color = "#FF4B4B"  # Vibrant Red
        elif any(char in tone_2 for char in word):
            color = "#29B6F6"  # Electric Blue
        elif any(char in tone_3 for char in word):
            color = "#00E676"  # Bright Green
        elif any(char in tone_4 for char in word):
            color = "#E040FB"  # Neon Purple
        else:
            color = "#FFFFFF"  # Neutral White
            
        # FIXED: Font-family switched to Montserrat/Sans-Serif to ensure perfect alignment of 3rd tone marks
        colored_words.append(f'<span style="color:{color}; font-weight:600; font-family:\'Montserrat\', sans-serif; font-size:1.2rem; margin-right:4px;">{word}</span>')
    
    return "".join(colored_words)

# Initialize persistent page memory states
if "transcript_result" not in st.session_state:
    st.session_state.transcript_result = ""

st.set_page_config(layout="wide", page_title="Studio Lyric Decoder")

# Style configurations
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Montserrat:wght@300;400;600&display=swap');
    
    .stApp {{
        background-image: url("{BACKGROUND_GIF_URL}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        font-family: 'Montserrat', sans-serif !important;
    }}
    
    h1, h2, h3, h4 {{
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
    }}
    
    .glass-card {{
        background-color: rgba(20, 20, 30, 0.9) !important;
        backdrop-filter: blur(12px) !important;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        min-height: 350px;
        margin-bottom: 15px;
        color: white !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Custom styled header dashboard
st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(43,88,118,0.95), rgba(78,67,118,0.95)); backdrop-filter: blur(5px); padding: 25px; border-radius: 12px; margin-bottom: 25px; border: 1px solid rgba(255,255,255,0.1);">
        <h1 style="margin:0; color:white; font-family:'Playfair Display', serif;">Pro Studio Chinese Lyric Decoder</h1>
        <p style="margin:5px 0 0 0; color:#e0e0e0; font-size:1.1rem; font-family:'Montserrat', sans-serif; font-weight:300;">Cinematic background workspace with fixed layout alignment vectors.</p>
    </div>
""", unsafe_allow_html=True)

# Layout Setup
with st.sidebar:
    st.header("Audio Input Panel")
    
    user_api_key = st.text_input("Enter AssemblyAI API Key", type="password", help="Paste your active AssemblyAI key here to process audio streams.")
    
    # FIXED: Clean, professional instructions built right into the interface
    with st.expander("Get a Free API Key"):
        st.markdown("""
        <div style="font-size:0.85rem; color:#d1d1e6; font-family:'Montserrat', sans-serif; line-height:1.4;">
            1. Go to <a href="https://www.assemblyai.com" target="_blank" style="color:#29B6F6; text-decoration:none; font-weight:600;">assemblyai.com</a> and sign up for a free account.<br><br>
            2. Log into your dashboard to instantly find your free trial <b>API Key</b> on the main page.<br><br>
            3. Paste it here to run custom track transcriptions completely for free.
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    uploaded_file = st.file_uploader("Upload Audio Capture", type=["wav"])
    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")
    st.divider()
    
    st.markdown("""
        <div style="background-color: rgba(30, 30, 47, 0.95); padding:15px; border-radius:8px; border: 1px solid rgba(255,255,255,0.1); font-family:'Montserrat', sans-serif;">
            <h4 style="margin-top:0; color:#fff; font-family:'Playfair Display', serif;">Tone Guide Legend</h4>
            <p style="margin:5px 0; color:#FF4B4B;">■ <b>1st Tone:</b> Red</p>
            <p style="margin:5px 0; color:#29B6F6;">■ <b>2nd Tone:</b> Blue</p>
            <p style="margin:5px 0; color:#00E676;">■ <b>3rd Tone:</b> Green</p>
            <p style="margin:5px 0; color:#E040FB;">■ <b>4th Tone:</b> Purple</p>
        </div>
    """, unsafe_allow_html=True)

# Processing Trigger Action
if uploaded_file is not None:
    if st.sidebar.button("Run Universal-3 Pro Cloud Transcribe", use_container_width=True):
        if not user_api_key or user_api_key.strip() == "":
            st.error("Please enter a valid AssemblyAI API key in the sidebar password box to proceed.")
        else:
            try:
                headers = {"authorization": user_api_key, "content-type": "application/json"}
                
                with st.spinner("Streaming audio track to secure repository cloud..."):
                    upload_url = "https://api.assemblyai.com/v2/upload"
                    req_upload = urllib.request.Request(upload_url, data=uploaded_file.getvalue(), headers=headers, method="POST")
                    with urllib.request.urlopen(req_upload) as res_upload:
                        audio_url = json.loads(res_upload.read().decode('utf-8'))["upload_url"]
                
                transcript_url = "https://api.assemblyai.com/v2/transcript"
                payload = json.dumps({
                    "audio_url": audio_url, 
                    "language_code": "zh",
                    "speech_models": ["universal-3-pro"]
                })
                req_trans = urllib.request.Request(transcript_url, data=payload.encode('utf-8'), headers=headers, method="POST")
                with urllib.request.urlopen(req_trans) as res_trans:
                    transcript_id = json.loads(res_trans.read().decode('utf-8'))["id"]
                
                status_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
                status_container = st.empty()
                while True:
                    req_status = urllib.request.Request(status_url, headers={"authorization": user_api_key})
                    with urllib.request.urlopen(req_status) as res_status:
                        current_data = json.loads(res_status.read().decode('utf-8'))
                        if current_data["status"] == "completed":
                            st.session_state.transcript_result = current_data["text"]
                            status_container.empty()
                            break
                        elif current_data["status"] == "failed":
                            raise Exception("Cloud structural analysis failed.")
                    status_container.info("Cloud neural network clusters are processing audio patterns...")
                    time.sleep(2)
                    
                st.success("Initial Transcription Loaded into Dashboard Workspace!")
            except Exception as e:
                st.error(f"Processing Error Profile: {e}")

# The Main Display Workspace Matrix
if st.session_state.transcript_result:
    
    # Interactive Workspace Editor Container
    with st.container(border=True):
        st.subheader("Workspace Editor & Playback Highlighter")
        st.caption("Fix any missing words below, then use the slider to highlight characters during playback:")
        
        edited_text = st.text_area("Live Lyrics Input Box", value=st.session_state.transcript_result, height=80, label_visibility="collapsed")
        
        if st.button("Update Study Guide Matrix", use_container_width=True, type="primary"):
            st.session_state.transcript_result = edited_text
            st.toast("Dashboard layout metrics synchronized!")
            
        # Clean segment separation logic
        text_segments = [seg.strip() for seg in edited_text.replace('，', ' ').replace('。', ' ').replace('\n', ' ').split(' ') if seg.strip()]
        
        highlight_index = 0
        selected_segment = ""
        
        if len(text_segments) > 1:
            highlight_index = st.slider("Audio Sync Scrubber (Slide to highlight words as you listen)", min_value=0, max_value=len(text_segments)-1, value=0, step=1)
            selected_segment = text_segments[highlight_index]
        elif len(text_segments) == 1:
            selected_segment = text_segments[0]
            
    st.divider()
    
    # Process display outputs cleanly
    working_text = st.session_state.transcript_result
    
    # 1. Chinese Highlight block
    highlighted_chinese = ""
    for segment in text_segments:
        if segment == selected_segment and selected_segment != "":
            highlighted_chinese += f'<mark style="background-color: #ffd600; color: #000000; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-family:\'Kaiti\', \'STKaiti\', \'Microsoft YaHei\', serif; font-size: 1.6rem;">{segment}</mark> '
        else:
            highlighted_chinese += f'<span style="opacity: 0.5; font-family:\'Kaiti\', \'STKaiti\', \'Microsoft YaHei\', serif; font-size: 1.5rem; color: #ffffff;">{segment}</span> '
            
    # 2. Pinyin Highlight Block
    highlighted_pinyin_html = ""
    for segment in text_segments:
        seg_pinyin_list = pinyin(segment, style=Style.TONE)
        seg_pinyin = " ".join([word[0] for word in seg_pinyin_list])
        colored_seg_pinyin = color_code_pinyin(seg_pinyin)
        
        if segment == selected_segment and selected_segment != "":
            # FIXED: Kept Montserrat font style for perfect diacritic accent mark tracking
            highlighted_pinyin_html += f'<span style="background-color: rgba(255,255,255,0.25); padding: 2px 6px; border-radius: 4px; display: inline-block; border: 1px solid #fff; font-family:\'Montserrat\', sans-serif;">{colored_seg_pinyin}</span> '
        else:
            highlighted_pinyin_html += f'<span style="opacity: 0.4; display: inline-block; padding: 2px 6px; font-family:\'Montserrat\', sans-serif;">{colored_seg_pinyin}</span> '
            
    # 3. Build Translation Block
    english_translation = native_translate(working_text)
    
    # Display columns matching custom glassmorphic panels
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""<div class="glass-card" style="border-left: 5px solid #9c27b0;"><h3>Chinese Characters</h3><p style="line-height:2.2; letter-spacing:1px;">{highlighted_chinese}</p></div>""", unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="glass-card" style="border-left: 5px solid #00e676;">
                <h3>Highlighted Pinyin</h3>
                <p style="line-height: 2.2; word-break: break-word; white-space: normal; display: block; width: 100%;">
                    {highlighted_pinyin_html}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""<div class="glass-card" style="border-left: 5px solid #29b6f6;"><h3>English Meaning</h3><p style="font-size:1.2rem; line-height:1.7; font-family:\'Georgia\', serif; color:#e0e0e0;">{english_translation}</p></div>""", unsafe_allow_html=True)
else:
    st.info("Upload a WAV track file in the left sidebar menu to populate your stylized workspace.")