from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from urllib.parse import unquote
import subprocess
import uuid
import os

app = FastAPI()

# CORS for frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static .zip files for download
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

class PlaylistRequest(BaseModel):
    playlistUrl: str

@app.post("/api/download")
async def download_playlist(data: PlaylistRequest):
    # Decode encoded URL from frontend
    playlist_url = unquote(data.playlistUrl)

    # Directories
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{uuid.uuid4()}.zip"
    temp_dir = f"temp_{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Download playlist using yt-dlp
        result = subprocess.run([
            "yt-dlp",
            "-o", f"{temp_dir}/%(title)s.%(ext)s",
            "--yes-playlist",
            playlist_url
        ], capture_output=True, text=True, check=True)

        # Zip downloaded videos
        subprocess.run(["zip", "-r", f"{output_dir}/{output_filename}", temp_dir], check=True)

        # Clean temp folder
        subprocess.run(["rm", "-rf", temp_dir])

        return {
            "downloadLink": f"https://backedyt.onrender.com/downloads/{output_filename}"
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": f"Download failed: {e.stderr}"
        }