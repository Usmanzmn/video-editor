import streamlit as st
import subprocess
import tempfile
import os
import shutil

APP_TITLE = "🎥 Urdu Bottom-Right Caption"
DEFAULT_FONT = "Arial Unicode MS"  # Built-in font that supports Urdu

st.set_page_config(page_title="Urdu Caption", page_icon="🎥", layout="centered")
st.title(APP_TITLE)
st.caption("Upload a video and burn a single-line Urdu caption at the bottom-right.")

# --- Helpers ---
def ensure_ffmpeg() -> bool:
    """Return True if ffmpeg is available."""
    return shutil.which("ffmpeg") is not None

def make_ass_file(text: str, fontsize: int, margin_r: int, margin_v: int, fontname: str, ass_path: str):
    """Create a minimal .ass subtitle file with a bottom-right style (Alignment=3)."""
    clean_text = text.replace(",", "\\,").replace("\n", " ")
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: UrduBR,{fontname},{fontsize},&H00FFFFFF,&H000000FF,&H96000000,&H96000000,0,0,0,0,100,100,0,0,1,3,0,3,20,{margin_r},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,9:59:59.00,UrduBR,,0,0,0,,{clean_text}
"""
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass)

# --- UI Controls ---
uploaded_video = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "mkv"]) 
urdu_text = st.text_input("Urdu text (single line):", value="میرا پہلا کیپشن")
col1, col2 = st.columns(2)
with col1:
    fontsize = st.slider("Font size", 24, 96, 48)
with col2:
    margin = st.slider("Bottom/Right margin (px)", 10, 120, 40)

process_btn = st.button("🔥 Burn Text")

# --- Process ---
if process_btn:
    if not uploaded_video:
        st.error("Please upload a video first.")
        st.stop()

    if not ensure_ffmpeg():
        st.error("FFmpeg not found on server. Please enable FFmpeg.")
        st.stop()

    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, "input_video")
        suffix = os.path.splitext(uploaded_video.name)[1] or ".mp4"
        in_path += suffix
        with open(in_path, "wb") as f:
            f.write(uploaded_video.read())

        # Create ASS file
        ass_path = os.path.join(tmpdir, "captions.ass")
        make_ass_file(
            text=urdu_text.strip(),
            fontsize=fontsize,
            margin_r=margin,
            margin_v=margin,
            fontname=DEFAULT_FONT,
            ass_path=ass_path,
        )

        out_path = os.path.join(tmpdir, "output.mp4")

        cmd = [
            "ffmpeg",
            "-y",
            "-i", in_path,
            "-vf", f"subtitles={ass_path}",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "veryfast",
            "-c:a", "copy",
            out_path,
        ]

        with st.status("Rendering… This may take a moment."):
            try:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except Exception as e:
                st.error(f"FFmpeg failed to run: {e}")
                st.stop()

        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            st.code(proc.stderr[-2000:])
            st.error("Rendering failed. See FFmpeg log above.")
            st.stop()

        st.success("Done! Preview below and download.")
        st.video(out_path)
        with open(out_path, "rb") as f:
            st.download_button("⬇️ Download Edited Video", f, file_name="edited_urdu_caption.mp4")
