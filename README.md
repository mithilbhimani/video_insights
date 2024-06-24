# Video Insight Dashboard

This project is a web-based dashboard for uploading, transcribing, and managing video files. The dashboard allows instructors to easily upload videos, view and manage their uploaded videos, and add or edit tags as needed. The dashboard also includes search and filter functionality, allowing users to find videos based on specific criteria or tags.

## Features

- **Upload Videos**: Instructors can upload multiple video files at once.
- **View Transcriptions**: Uploaded videos are transcribed and the transcriptions are displayed.
- **Manage Tags**: Add or edit tags for each video.
- **Search and Filter**: Search transcriptions and filter videos by subject and level.
- **Progress Feedback**: Real-time progress bars indicating the upload status of each video.

## Technologies Used

- **FastAPI**: Backend API for video upload, transcription, and tag management.
- **Gradio**: Frontend interface for interacting with the application.
- **SQLAlchemy**: ORM for database interactions.
- **PostgreSQL**: Database for storing video metadata and transcriptions.
- **MoviePy**: Library for handling video to audio conversion.
- **OpenAI API**: Used for transcribing audio to text.

## Setup Instructions

### Prerequisites

- Python 3.7+
- PostgreSQL database

### Install Dependencies

1. Clone the repository:
   ```sh
   git clone <Git URL>
   cd video-insight
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

### Database Setup

1. Create a PostgreSQL database:
   ```sh
   createdb video_insight_db
   ```

2. Update the `DATABASE_URL` in `database.py` to match your database credentials:
   ```python
   DATABASE_URL = "postgresql://username:password@localhost:5432/video_insight_db"
   ```

3. Create the database tables:
   ```sh
   python create_tables.py
   ```

### Run the Application

1. Start the FastAPI server:
   ```sh
   uvicorn main:app --reload
   ```

2. Start the Gradio interface:
   ```sh
   python ui.py
   ```

3. Open your browser and go to `http://127.0.0.1:7860` to access the Gradio interface.

## API Endpoints

- **POST `/upload-video/`**: Upload a video file and get its transcription.
- **GET `/videos/`**: Fetch all videos with optional search and filter parameters.
- **PUT `/videos/{video_id}/tags/`**: Update tags for a specific video.

## Project Structure

```
video-insight/
├── database.py          # Database setup and connection
├── models.py            # SQLAlchemy models
├── main.py              # FastAPI application
├── ui.py                # Gradio interface
├── create_tables.py     # Script to create database tables
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```