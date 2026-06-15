"""
Local Audio Transcription Module
================================
Uses Whisper to transcribe audio files.
"""

import os

# Dynamically add the ffmpeg binary from imageio_ffmpeg to the system PATH
# This prevents "[WinError 2] The system cannot find the file specified" on Windows
try:
    import imageio_ffmpeg
    ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
    os.environ["PATH"] += os.pathsep + ffmpeg_dir
except ImportError:
    pass

_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        import torch
        print("  [Whisper] Loading local transcription model (base)...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _whisper_model = whisper.load_model("base", device=device)
    return _whisper_model

def transcribe_audio(file_path: str) -> dict:
    """Transcribe an audio or video file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    model = get_whisper_model()
    
    # Check if the file is a video, and if so, extract audio first using ffmpeg
    import subprocess
    import tempfile
    
    is_video = file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.flv'))
    target_path = file_path
    temp_audio_file = None
    
    try:
        if is_video:
            print("  [Whisper] Video detected. Extracting audio using ffmpeg...")
            temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            # ffmpeg -i video.mp4 -vn audio.wav
            cmd = ["ffmpeg", "-y", "-i", file_path, "-vn", temp_audio_file]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            target_path = temp_audio_file
            
        import torch
        use_fp16 = torch.cuda.is_available()
        result = model.transcribe(target_path, fp16=use_fp16)
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "extractor": "Whisper (base)"
        }
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}")
    finally:
        if temp_audio_file and os.path.exists(temp_audio_file):
            try:
                os.remove(temp_audio_file)
            except OSError:
                pass
