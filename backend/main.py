import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import uuid
import json
import subprocess
import platform

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

jobs = {}

class OverlayMetadata(BaseModel):
    type: str
    content: Optional[str] = None
    x: int
    y: int
    scale: Optional[float] = 1.0
    start_time: float
    end_time: float
    fontsize: Optional[int] = 40
    color: Optional[str] = '#E0FFD6'
    filter: Optional[str] = 'none'
    font: Optional[str] = 'Impact'

def get_font_path(font_name):
    """
    Robust font path finder for Windows/Mac/Linux
    """
    system = platform.system()
    
    # Map our App's font names to actual filenames on the computer
    font_map = {
        'Impact': ['impact.ttf', 'Impact.ttf'],
        'Arial': ['arial.ttf', 'Arial.ttf'],
        'Courier': ['cour.ttf', 'Courier New.ttf'],
        'Georgia': ['georgia.ttf', 'Georgia.ttf'],
        'Verdana': ['verdana.ttf', 'Verdana.ttf'],
    }
    
    potential_files = font_map.get(font_name, ['arial.ttf'])
    
    if system == 'Windows':
        base_path = "C:/Windows/Fonts/"
        for filename in potential_files:
            full_path = os.path.join(base_path, filename)
            if os.path.exists(full_path):
                return full_path.replace(":", "\\:")
        return "C\:/Windows/Fonts/arial.ttf" # Fallback
        
    elif system == 'Darwin': # Mac
        base_paths = ["/Library/Fonts/", "/System/Library/Fonts/"]
        for base in base_paths:
            for filename in potential_files:
                full_path = os.path.join(base, filename)
                if os.path.exists(full_path):
                    return full_path
        return "/System/Library/Fonts/Helvetica.ttc"
    
    else: # Linux
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def process_video(job_id: str, main_video_path: str, overlays: List[dict], overlay_files: dict):
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp4")
    jobs[job_id]["status"] = "processing"
    
    try:
        inputs = [f'-i "{main_video_path}"']
        filter_complex = []
        current_stream = "[0:v]"
        input_idx = 1
        
        for i, ov in enumerate(overlays):
            ov_type = ov['type']
            x = int(float(ov['x']))
            y = int(float(ov['y']))
            scale = float(ov.get('scale', 1.0))
            start = ov['start_time']
            end = ov['end_time']
            ov_filter = ov.get('filter', 'none')
            ov_font = ov.get('font', 'Impact')
            
            next_stream = f"[v{i}]"
            
            if ov_type == 'text':
                text_content = ov['content'].replace(":", "\\:").replace("'", "")
                base_fontsize = ov.get('fontsize', 40)
                final_fontsize = int(base_fontsize * scale)
                font_color = ov.get('color', 'white')
                
                font_path = get_font_path(ov_font)
                font_str = f"fontfile='{font_path}':" if font_path else ""
                
                filter_cmd = (
                    f"{current_stream}drawtext=text='{text_content}':"
                    f"{font_str}" 
                    f"x={x}:y={y}:fontsize={final_fontsize}:fontcolor={font_color}:"
                    f"enable='between(t,{start},{end})'{next_stream}"
                )
                filter_complex.append(filter_cmd)
                current_stream = next_stream

            elif ov_type in ['image', 'video']:
                filename = ov['content']
                if filename in overlay_files:
                    file_path = overlay_files[filename].replace("\\", "/")
                    inputs.append(f'-i "{file_path}"')
                    
                    source_node = f"[{input_idx}:v]"
                    scaled_node = f"[scaled_{i}]"
                    filtered_node = f"[filtered_{i}]"
                    
                    filter_complex.append(f"{source_node}scale=iw*{scale}:-1{scaled_node}")
                    
                    filter_cmd_str = "null"
                    if ov_filter == 'grayscale': filter_cmd_str = "hue=s=0"
                    elif ov_filter == 'sepia': filter_cmd_str = "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131"
                    elif ov_filter == 'invert': filter_cmd_str = "negate"

                    filter_complex.append(f"{scaled_node}{filter_cmd_str}{filtered_node}")
                    
                    overlay_cmd = (
                        f"{current_stream}{filtered_node}overlay={x}:{y}:"
                        f"enable='between(t,{start},{end})'{next_stream}"
                    )
                    filter_complex.append(overlay_cmd)
                    
                    current_stream = next_stream
                    input_idx += 1

        cmd_inputs = " ".join(inputs)
        
        if filter_complex:
            cmd_filter = f'-filter_complex "{";".join(filter_complex)}"'
            cmd_map = f'-map "{current_stream}" -map 0:a?' 
        else:
            cmd_filter = ""
            cmd_map = "-map 0:v -map 0:a?"

        full_command = (
            f'ffmpeg -y {cmd_inputs} {cmd_filter} {cmd_map} '
            f'-c:v libx264 -pix_fmt yuv420p -preset ultrafast "{output_path}"'
        )
        
        print(f"Executing: {full_command}")
        
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(result.stderr)
            raise Exception("FFmpeg failed.")
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["output_file"] = output_path
        
    except Exception as e:
        print(f"Job Failed: {str(e)}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    metadata: str = Form(...),
    assets: List[UploadFile] = File(None)
):
    job_id = str(uuid.uuid4())
    video_path = os.path.abspath(os.path.join(UPLOAD_DIR, f"{job_id}_{video.filename}"))
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    video_path = video_path.replace("\\", "/")

    try:
        overlays_data = json.loads(metadata)
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    saved_assets = {}
    if assets:
        for asset in assets:
            asset_path = os.path.abspath(os.path.join(UPLOAD_DIR, f"{job_id}_{asset.filename}"))
            with open(asset_path, "wb") as buffer:
                shutil.copyfileobj(asset.file, buffer)
            saved_assets[asset.filename] = asset_path.replace("\\", "/")
            
    jobs[job_id] = {"status": "pending"}
    background_tasks.add_task(process_video, job_id, video_path, overlays_data, saved_assets)
    return {"job_id": job_id, "status": "processing_started"}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})

@app.get("/result/{job_id}")
def get_result(job_id: str):
    job = jobs.get(job_id)
    if not job or job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not ready")
    return FileResponse(job["output_file"], media_type="video/mp4", filename="rendered.mp4")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)