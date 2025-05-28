import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables from .env file
load_dotenv()

# Configure Google Generative AI API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API Key is missing. Please set it in a .env file as GOOGLE_API_KEY.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/text-bison-001')

# Prompt template
prompt = """You are a YouTube video summarizer. Summarize the given transcript text
into concise bullet points or short paragraphs, all within 250 words."""

# Extract video ID from YouTube URL
def extract_video_id(youtube_url):
    try:
        if "v=" in youtube_url:
            return youtube_url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            return youtube_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format.")
    except Exception as e:
        st.error(f"Error extracting video ID: {e}")
        return None

# Fetch transcript text from video
def extract_transcript_details(youtube_url):
    try:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            return None
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry["text"] for entry in transcript_list])
        return transcript_text
    except Exception as e:
        st.error(f"Transcript not available: {e}")
        return None

# Generate summary from transcript
def generate_summary(transcript_text):
    try:
        response = model.generate_content(prompt + "\n\n" + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Streamlit app layout
st.set_page_config(page_title="YouTube Video Summarizer", layout="centered")
st.title("🎥 YouTube Transcript Summarizer")

youtube_link = st.text_input("Paste YouTube Video URL:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Summarize Video"):
    if youtube_link:
        with st.spinner("Fetching transcript..."):
            transcript = extract_transcript_details(youtube_link)
        if transcript:
            with st.spinner("Generating summary..."):
                summary = generate_summary(transcript)
            if summary:
                st.markdown("## 📝 Summary:")
                st.write(summary)
            else:
                st.error("Failed to generate summary.")
        else:
            st.warning("Could not retrieve transcript for this video.")
