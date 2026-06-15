"""
Local VLM (Scene Captioning) Module
===================================
Uses a local Vision-Language Model running via Ollama (e.g. moondream or llava)
to generate descriptions for images and keyframes of videos.
"""

import os
import base64
import json
import requests
from PIL import Image

OLLAMA_API_URL = "http://localhost:11434/api/generate"
VLM_MODEL = "moondream"

def generate_caption(image_path: str) -> str:
    """Generate a caption for a single image using Ollama."""
    if not os.path.isfile(image_path):
        return ""
    
    try:
        # Read image and convert to base64
        with open(image_path, "rb") as img_file:
            img_b64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        prompt = "Describe what is shown in this image in detail."
        
        payload = {
            "model": VLM_MODEL,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            print(f"  [VLM Error] Ollama API returned status {response.status_code}: {response.text}")
            return ""
            
    except requests.exceptions.ConnectionError:
        print("  [VLM Error] Could not connect to Ollama. Is it running on localhost:11434?")
    except Exception as e:
        print(f"  [VLM Error] Failed to caption image: {e}")
        
    return ""

def process_video_frames(video_path: str, interval_seconds: int = 10) -> list:
    """Extract frames from a video at a given interval and caption them."""
    if not os.path.isfile(video_path):
        return []
    
    try:
        from moviepy import VideoFileClip
    except ImportError:
        try:
            from moviepy.editor import VideoFileClip
        except ImportError:
            print("  [VLM Error] moviepy not installed.")
            return []
        
    captions = []
    temp_dir = "temp_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        
        for t in range(0, int(duration), interval_seconds):
            frame_path = os.path.join(temp_dir, f"frame_{t}.jpg")
            clip.save_frame(frame_path, t=t)
            
            caption = generate_caption(frame_path)
            if caption:
                captions.append(f"[Time: {t}s] Scene Description: {caption}")
                
            os.remove(frame_path)
    except Exception as e:
        print(f"  [VLM Error] Failed to process video frames: {e}")
        
    return captions
