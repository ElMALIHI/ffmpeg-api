from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import uuid
import subprocess
from fastapi.responses import FileResponse
import os

app = FastAPI()

class AudioRequest(BaseModel):
    data: str  # base64-encoded PCM
    output_format: str = "wav"  # wav or mp3

@app.post("/convert")
def convert_audio(req: AudioRequest):
    if req.output_format not in ("wav", "mp3"):
        raise HTTPException(status_code=400, detail="Invalid output format")

    # Create unique filenames
    audio_id = str(uuid.uuid4())
    input_path = f"/tmp/{audio_id}.pcm"
    output_path = f"/tmp/{audio_id}.{req.output_format}"

    try:
        # Decode base64 and save to file
        with open(input_path, "wb") as f:
            f.write(base64.b64decode(req.data))

        # FFmpeg command to convert PCM to wav/mp3
        subprocess.run([
            "ffmpeg",
            "-f", "s16le",
            "-ar", "24000",
            "-ac", "1",
            "-i", input_path,
            output_path
        ], check=True)

        return FileResponse(
            output_path,
            filename=f"converted.{req.output_format}",
            media_type=f"audio/{req.output_format}"
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg error: {e}")
    finally:
        # Optional: clean up files after response
        pass
