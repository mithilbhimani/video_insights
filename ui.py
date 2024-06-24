import gradio as gr
import requests
import pandas as pd

# Function to upload video files via the FastAPI endpoint
def upload_videos(files, subjects, levels):
    results = []
    for file in files:
        with open(file.name, "rb") as f:
            files = {'file': (file.name, f, 'video/mp4')}
            response = requests.post(
                "http://localhost:8000/upload-video/",
                files=files,
                data={
                    "subjects": subjects,
                    "levels": levels
                }
            )
            results.append(response.json())
    return results

# Function to search videos from the FastAPI endpoint
def search_videos(subject=None, level=None, search=None):
    params = {}
    if subject:
        params['subject'] = subject
    if level:
        params['level'] = level
    if search:
        params['search'] = search

    response = requests.get("http://localhost:8000/search/", params=params)
    return response.json()

# Function to update video tags via the FastAPI endpoint
def update_video_tags(video_id, tags):
    response = requests.put(f"http://localhost:8000/videos/{video_id}/tags/", json= tags)
    return response.json()

# Define Gradio interface
def gradio_interface():
    with gr.Blocks() as demo:
        with gr.Tab("Upload"):
            subjects = gr.Dropdown(choices=["math", "science", "history", "art", "music"], label="Subjects", multiselect=True)
            levels = gr.Dropdown(choices=["beginner", "intermediate", "advanced"], label="Levels", multiselect=True)
            files = gr.File(label="Upload Videos", file_count="multiple", file_types=["video"])

            with gr.Row():
                upload_button = gr.Button("Upload Videos")
                progress = gr.Progress()

            output = gr.Dataframe(label="Results")

            def upload_with_progress(files, subjects, levels):
                if files is None:
                    return pd.DataFrame({"Error": ["No files uploaded"]})
                if not subjects:
                    return pd.DataFrame({"Error": ["No subjects selected"]})
                if not levels:
                    return pd.DataFrame({"Error": ["No levels selected"]})

                progress(0, "Starting upload...")
                results = []
                for i, file in enumerate(files):
                    progress((i+1)/len(files), f"Uploading {file.name}...")
                    result = upload_videos([file], subjects, levels)
                    results.extend(result)
                progress(1, "Upload complete!")

                data = []
                for res in results:
                    if isinstance(res, dict) and 'transcription' in res:
                        data.append([
                            res['transcription'],
                            res['video_file_saved'],
                            res['transcription_file_saved'],
                            ", ".join(res['subjects']),
                            ", ".join(res['levels'])
                        ])
                    else:
                        data.append(["Error in processing", "", "", "", ""])
                
                df = pd.DataFrame(data, columns=["Transcription", "Video File", "Transcription File", "Subjects", "Levels"])
                return df

            upload_button.click(upload_with_progress, inputs=[files, subjects, levels], outputs=output)

        with gr.Tab("Dashboard"):
            with gr.Row():
                search_input = gr.Textbox(label="Search Transcriptions", placeholder="Search...")
                subject_filter = gr.Dropdown(choices=["", "math", "science", "history", "art", "music"], label="Filter by Subject")
                level_filter = gr.Dropdown(choices=["", "beginner", "intermediate", "advanced"], label="Filter by Level")
                filter_button = gr.Button("Apply Filters")

            video_df = gr.Dataframe(label="Uploaded Videos")
            refresh_button = gr.Button("Refresh")

            def refresh_videos(search_input, subject_filter, level_filter):
                videos = search_videos(subject_filter, level_filter, search_input)
                data = []
                for video in videos:
                    data.append([
                        video['id'],
                        video['transcription'],
                        video['video_file_saved'],
                        video['transcription_file_saved'],
                        video['subjects'],
                        video['levels'],
                        video.get('tags', "")
                    ])
                df = pd.DataFrame(data, columns=["ID", "Transcription", "Video File", "Transcription File", "Subjects", "Levels", "Tags"])
                return df

            filter_button.click(refresh_videos, inputs=[search_input, subject_filter, level_filter], outputs=video_df)
            refresh_button.click(lambda: refresh_videos("", "", ""), outputs=video_df)

            video_id = gr.Textbox(label="Video ID")
            new_tags = gr.Textbox(label="New Tags (comma-separated)")
            update_tags_button = gr.Button("Update Tags")

            def handle_update_tags(video_id, new_tags):
                tags = [tag.strip() for tag in new_tags.split(",")]
                response = update_video_tags(video_id, tags)
                if 'id' in response:  # Check if the response is valid
                    return f"Tags updated for video ID {video_id}"
                else:
                    return f"Failed to update tags for video ID {video_id}: {response.get('detail', 'Unknown error')}"

            update_result = gr.Textbox(label="Update Result")

            update_tags_button.click(handle_update_tags, inputs=[video_id, new_tags], outputs=update_result)

            # Initially load all videos
            demo.load(lambda: refresh_videos("", "", ""), outputs=video_df)

    return demo

if __name__ == "__main__":
    interface = gradio_interface()
    interface.launch()
