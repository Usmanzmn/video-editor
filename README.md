# 🎥 Streamlit Urdu Bottom-Right Caption

Add a single-line Urdu caption at the bottom-right of any uploaded video. Fast, crisp text using FFmpeg + libass (supports RTL shaping).

## Features
- Upload MP4/MOV/AVI/MKV
- One-line Urdu text, burned into video
- Bottom-right placement with adjustable margins
- Font auto-download (Noto Nastaliq Urdu)
- Download the edited MP4

## Deploy (Streamlit Community Cloud)
1. Fork or upload this repo to GitHub.
2. Go to https://share.streamlit.io → **New app** → select repo, branch, `app.py`.
3. Click **Deploy**.

## Local Run
```bash
pip install -r requirements.txt
# Ensure ffmpeg is installed and on PATH
# macOS (brew): brew install ffmpeg
# Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y ffmpeg
streamlit run app.py
