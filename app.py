import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import tempfile
import os

st.title("🎥 Urdu Text Video Editor")

uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
urdu_text = st.text_input("Enter Urdu text to display (bottom-right):")

if uploaded_video and urdu_text:
    if st.button("Add Text to Video"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
            tmp_input.write(uploaded_video.read())
            tmp_input_path = tmp_input.name

        clip = VideoFileClip(tmp_input_path)

        # Create Urdu text clip
        txt_clip = TextClip(urdu_text, fontsize=40, color='white', font='Arial-Unicode-MS')
        txt_clip = txt_clip.set_position(("right", "bottom")).set_duration(clip.duration)

        # Composite the video with the text
        final_clip = CompositeVideoClip([clip, txt_clip])

        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

        st.video(output_path)
        with open(output_path, "rb") as f:
            st.download_button("Download Edited Video", f, file_name="edited_video.mp4")

        # Clean up temp files
        os.unlink(tmp_input_path)
        os.unlink(output_path)
