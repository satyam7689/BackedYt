from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlaylistRequest(BaseModel):
    playlistUrl: str

@app.post("/api/download")
async def download_playlist(data: PlaylistRequest):
    playlist_url = data.playlistUrl
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"{uuid.uuid4()}.zip"
    temp_dir = f"temp_{uuid.uuid4()}"

    try:
        subprocess.run([
            "yt-dlp",
            "-o", f"{temp_dir}/%(title)s.%(ext)s",
            "--yes-playlist",
            playlist_url
        ], check=True)

        subprocess.run(["zip", "-r", f"{output_dir}/{output_filename}", temp_dir], check=True)
        subprocess.run(["rm", "-rf", temp_dir])

        return {"downloadLink": f"https://your-render-url.com/downloads/{output_filename}"}
    except Exception as e:
        return {"error": str(e)}