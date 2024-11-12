import streamlit as st
from helpers.YouTubeOperations import YouTubeOperations
import os

def run(operation):
    yt = YouTubeOperations()
    # Authenticate only once, if not already authenticated
    if not yt.credentials or not yt.youtube:
        try:
            yt.authenticate()
            st.success("YouTube authenticated successfully!")
        except Exception as e:
            st.error(f"Failed to authenticate YouTube: {e}")
    
    # --- CREATE VIDEO ---
    if operation == "Create Video":
        st.header("Upload a New Video to YouTube")
        
        # Get user inputs for video creation
        title = st.text_input("Video Title", "")
        description = st.text_area("Video Description", "")
        privacy_status = st.selectbox("Privacy Status", ["public", "unlisted", "private"])
        
        # File uploader for video file
        video_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
        
        if st.button("Upload Video"):
            if video_file is not None:
                try:
                    # Save file temporarily and upload it
                    with open("temp_video.mp4", "wb") as f:
                        f.write(video_file.read())
                    
                    # Call the create_video method with the path to the temp file
                    response = yt.create_video(title, description, privacy_status, "temp_video.mp4")
                    
                    if response:
                        video_id = response['id']
                        st.success(f"Video uploaded successfully! Video ID: {video_id}")
                        st.markdown(f"[View Video on YouTube](https://www.youtube.com/watch?v={video_id})")
                except Exception as e:
                    st.error(f"Error uploading video: {e}")
                finally:
                    # Cleanup temporary file
                    os.remove("temp_video.mp4")
            else:
                st.warning("Please upload a video file before clicking 'Upload Video'")    

    # --- READ VIDEO ---
    elif operation == "Read Video":
        st.header("Get Video Details")
        
        # List user's recent videos to choose one to read details
        try:
            videos = yt.list_my_videos(max_results=5)
            video_options = {}
            
            if videos.get('items'):
                for item in videos['items']:
                    title = item['snippet']['title']
                    video_id = item['id']['videoId']
                    video_options[title] = video_id
                
                if video_options:
                    selected_title = st.selectbox("Choose a Video to Read", options=list(video_options.keys()))
                    video_id = video_options[selected_title]
                    
                    if st.button("Fetch Video Details"):
                        try:
                            video_info = yt.read_video(video_id)
                            st.write("Video details:")
                            st.write(video_info)
                        except Exception as e:
                            st.error(f"Failed to fetch video details: {e}")
            else:
                st.warning("No videos found in your channel.")
                
        except Exception as e:
            st.error(f"Failed to fetch videos: {e}")

    # --- UPDATE VIDEO ---
    elif operation == "Update Video":
        st.header("Update Video Details")
        
        # List user's recent videos to help choose one for updating
        try:
            videos = yt.list_my_videos(max_results=5)
            video_options = {}
            
            if videos.get('items'):
                for item in videos['items']:
                    title = item['snippet']['title']
                    video_id = item['id']['videoId']
                    video_options[title] = video_id
                
                if video_options:
                    selected_title = st.selectbox("Choose a Video to Update", options=list(video_options.keys()))
                    video_id = video_options[selected_title]
                    
                    # Get current video details to show in the form
                    current_video = yt.youtube.videos().list(
                        part="snippet",
                        id=video_id
                    ).execute()
                    
                    if current_video['items']:
                        current_snippet = current_video['items'][0]['snippet']
                        new_title = st.text_input("New Title", value=current_snippet['title'])
                        new_description = st.text_area("New Description", value=current_snippet['description'])
                        
                        if st.button("Update Video"):
                            try:
                                updated_video = yt.update_video(
                                    video_id=video_id,
                                    title=new_title,
                                    description=new_description
                                )
                                st.success("Video updated successfully!")
                                st.markdown(f"[View Updated Video on YouTube](https://www.youtube.com/watch?v={video_id})")
                            except Exception as e:
                                st.error(f"Failed to update video: {e}")
            else:
                st.warning("No videos found in your channel.")
                
        except Exception as e:
            st.error(f"Failed to fetch videos: {e}")

    # --- DELETE VIDEO ---
    elif operation == "Delete Video":
        st.header("Delete a Video")
        
        # List user's recent videos to help choose one for deletion
        try:
            videos = yt.list_my_videos(max_results=5)
            video_options = {}
            
            if videos.get('items'):
                for item in videos['items']:
                    title = item['snippet']['title']
                    video_id = item['id']['videoId']
                    video_options[title] = video_id
                
                if video_options:
                    selected_title = st.selectbox("Choose a Video to Delete", options=list(video_options.keys()))
                    video_id = video_options[selected_title]
                    
                    # Show video details before deletion
                    st.warning(f"You are about to delete: {selected_title}")
                    st.markdown(f"Video ID: `{video_id}`")
                    
                    confirm = st.checkbox("I understand that this action cannot be undone")
                    if st.button("Delete Video") and confirm:
                        try:
                            yt.delete_video(video_id)
                            st.success("Video deleted successfully!")
                            # Add a rerun button to refresh the video list
                            if st.button("Refresh Video List"):
                                st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Failed to delete video: {e}")
                else:
                    st.warning("No videos found in your channel.")
            else:
                st.warning("No videos found in your channel.")
                
        except Exception as e:
            st.error(f"Failed to fetch videos: {e}")
