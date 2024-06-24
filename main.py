from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from moviepy.editor import VideoFileClip
from openai import OpenAI

from database import SessionLocal, engine
import models
from models import VideoInsight, SubjectEnum, LevelEnum

models.Base.metadata.create_all(bind=engine)
client = OpenAI()

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def video_to_mp3(video_file, output_mp3_file):
    try:
        video_clip = VideoFileClip(video_file)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_mp3_file, codec='mp3')
        video_clip.close()
        audio_clip.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting video to audio: {e}")

def transcribe_audio_to_text(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcription
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {e}")

@app.post("/upload-video/")
async def upload_video(
    file: UploadFile = File(...),
    subjects: List[SubjectEnum] = Form(...),
    levels: List[LevelEnum] = Form(...),
    db: Session = Depends(get_db)
):
    video_file_path = f"temp_{file.filename}"
    output_mp3_path = "output_audio.mp3"

    # Save uploaded video file
    with open(video_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Convert video to audio
        video_to_mp3(video_file_path, output_mp3_path)

        # Transcribe audio to text
        transcription = transcribe_audio_to_text(output_mp3_path)

        # Delete the audio file
        os.remove(output_mp3_path)

        # Save transcription to a text file
        transcription_text_path = f"{video_file_path}.txt"
        with open(transcription_text_path, "w") as text_file:
            text_file.write(transcription)

        # Store the response in the database
        db_video_insight = VideoInsight(
            transcription=transcription,
            video_file_saved=video_file_path,
            transcription_file_saved=transcription_text_path,
            subjects=subjects[0],  # assuming one subject for simplicity
            levels=levels[0],  # assuming one level for simplicity
            tags=""
        )
        db.add(db_video_insight)
        db.commit()
        db.refresh(db_video_insight)

        # Return the transcription and confirm video file saved along with tags
        return JSONResponse(content={
            "transcription": transcription,
            "video_file_saved": video_file_path,
            "transcription_file_saved": transcription_text_path,
            "subjects": [subject.value for subject in subjects],
            "levels": [level.value for level in levels]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/videos/")
def get_videos(
    db: Session = Depends(get_db),
    subject: Optional[SubjectEnum] = Query(None),
    level: Optional[LevelEnum] = Query(None),
    search: Optional[str] = Query(None)
):
    query = db.query(VideoInsight)

    if subject:
        query = query.filter(VideoInsight.subjects == subject)
    if level:
        query = query.filter(VideoInsight.levels == level)
    if search:
        query = query.filter(VideoInsight.transcription.contains(search))

    return query.all()

@app.put("/videos/{video_id}/tags/")
def update_tags(video_id: int, tags: List[str], db: Session = Depends(get_db)):
    video = db.query(VideoInsight).filter(VideoInsight.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    video.tags = ", ".join(tags)
    db.commit()
    db.refresh(video)
    return video

@app.get("/search/")
def search_videos(subject: Optional[SubjectEnum] = None, level: Optional[LevelEnum] = None, tag: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(VideoInsight)
    if subject:
        query = query.filter(VideoInsight.subjects == subject)
    if level:
        query = query.filter(VideoInsight.levels == level)
    if tag:
        query = query.filter(VideoInsight.tags.contains(tag))
    videos = query.all()
    return videos

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0", port=8000)
