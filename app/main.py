import os,shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils.bengaliasr import convert_bengali_audio_to_text
from fastapi.responses import StreamingResponse
from moviepy.editor import VideoFileClip
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,    
    allow_origins=origins,    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# this endpoint takes Bengali video file and converts it to Text
def convert_video_to_audio(video_path, audio_dir):
    try:
        # Load the video clip
        video_clip = VideoFileClip(video_path)
        
        # Extract audio from the video
        audio_clip = video_clip.audio
        
        # Save the audio using the video's filename
        filename_without_extension = os.path.splitext(os.path.basename(video_path))[0]
        audio_filename = f"{filename_without_extension}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)
        audio_clip.write_audiofile(audio_path)
        
        return audio_path
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/video_to_text/")
async def upload_file(file: UploadFile = File(...)):
    try:
        video_dir = "./data/video"
        audio_dir = "./data/audio"
        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        
        video_path = os.path.join(video_dir, file.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        audio_path = convert_video_to_audio(video_path, audio_dir)
        transcription = convert_bengali_audio_to_text(audio_path)
        return {"transcription": transcription}       
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})    
