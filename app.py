import streamlit as st
import subprocess
import tempfile
import os
import sys
import shutil
import time
from pathlib import Path

APP_TITLE = "🎥 Urdu Bottom-Right Caption"
FONT_DIR = Path(__file__).parent / "fonts"
FONT_PATH = FONT_DIR / "NotoNastaliqUrdu-Regular.ttf"
# Google Fonts (Apache 2.0) direct link to Noto Nastaliq Urdu
FONT_URL = (
    "https://github.com/notofonts/nastaliq-urdu/raw/main/fonts/ttf/NotoNastaliqUrdu-Regular.ttf"
)


st.set_page_config(page_title="Urdu Caption", page_icon="🎥", layout="centered")
st.title(APP_TITLE)
st.caption("Upload a video and burn a single-line Urdu caption at the bottom-right.")

# --- Helpers ---
def ensure_ffmpeg() -> bool:
    """Return True if ffmpeg is available."""
    return shutil.which("ffmpeg") is not None

@st.cache_data(show_spinner=False)
def download_font(url: str, dest: Path) -> str:
    import urllib.request
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        urllib.request.urlretrieve(url, dest)
    return str(dest)

def ensure_font() -> str:
    """Ensure an Urdu-capable font exists locally; download if missing."""
    try:
        if not FONT_PATH.exists():
            download_font(FONT_URL, FONT_PATH)
        return str(FONT_PATH)
    except Exception as e:
        st.warning(f"Could not auto-download font: {e}\nYou can manually upload a .ttf into the fonts/ folder.")
        return ""

def make_ass_file(text: str, fontsize: int, margin_r: int, margin_v: int, fontname: str, ass_path: str):
    """Create a minimal .ass subtitle file with a bottom-right style (Alignment=3)."""
    # Escape commas in ASS dialogue text
    clean_text = text.replace(",", "\\,").replace("\n", " ")

    ass = f"""[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: UrduBR,{fontname},{fontsize},&H00FFFFFF,&H000000FF,&H96000000,&H96000000,0,0,0,0,100,100,0,0,1,3,0,3,20,{margin_r},{margin_v},1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\nDialogue: 0,0:00:00.00,9:59:59.00,UrduBR,,0,0,0,,{clean_text}\n"""
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

    # Ensure font exists (download if needed)
    font_file = ensure_font()
    if not font_file:
        st.error("No Urdu-capable font available. Add a .ttf in fonts/ or re-run.")
        st.stop()

    # Save input video to a temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, "input_video")
        # keep original extension if possible
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
            fontname="Noto Nastaliq Urdu",
            ass_path=ass_path,
        )

        # Output path
        out_path = os.path.join(tmpdir, "output.mp4")

        # Build FFmpeg command using libass subtitles with fontsdir so our local font is discovered
        # -vf "subtitles=captions.ass:fontsdir=fonts"
        cmd = [
            "ffmpeg",
            "-y",
            "-i", in_path,
            "-vf", f"subtitles={ass_path}:fontsdir={FONT_DIR}",
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
