import streamlit as st
from helpers.InstagramAPI import InstagramAPI
import time

def run(operation):
    
        # Initialize InstagramAPI instance
    try:
        api = InstagramAPI()
        st.success("Initialized Instagram API successfully.")
    except Exception as e:
        st.error(f"Failed to initialize Instagram API: {e}")



    
        
    # Check if Instagram API was successfully initialized before proceeding
    if api and api.access_token:
        
        # --- GET ACCOUNT INFO ---
        if operation == "Get Account Info":
            st.header("Instagram Account Information")
            
            try:
                account_info = api.get_account_info()
                st.write("Account Information:")
                st.json(account_info)
                
                # Display profile picture if available
                if "profile_picture_url" in account_info:
                    st.image(account_info["profile_picture_url"], caption=account_info.get("username", "Instagram Profile"))
            
            except Exception as e:
                st.error(f"Error fetching account information: {e}")
        
        # --- PUBLISH POST ---
        elif operation == "Publish Post":
            st.header("Create and Publish an Instagram Post")
            
            # Input for the image URL and caption
            image_url = st.text_input("Image URL", "")
            caption = st.text_area("Caption", "")
            
            if st.button("Publish Post"):
                try:
                    # Step 1: Create a media container and get the creation ID
                    result = api.create_post(image_url, caption)
                    
                    if result and 'id' in result:
                        media_id = result['id']
                        st.success(f"Post created successfully! Media ID: {media_id}")
                        
                        # Step 2: Retrieve the media details to get the permalink
                        # Give Instagram some time to process the post
                        time.sleep(5)
                        media_details = api._make_request('GET', media_id, params={'fields': 'permalink'})
                        
                        if media_details and "permalink" in media_details:
                            post_url = media_details["permalink"]
                            # Display a clickable link to view the new post on Instagram
                            st.markdown(f"[View New Post on Instagram]({post_url})", unsafe_allow_html=True)
                        else:
                            st.error("Failed to retrieve the permalink for the new post.")
                    else:
                        st.error("Failed to create post. Please check the image URL and your permissions.")
                except Exception as e:
                    st.error(f"Error publishing post: {e}")
        
        # --- GET MEDIA LIST ---
        elif operation == "Get Media List":
            st.header("Recent Instagram Media Posts")
            
            # Input for the number of media items to fetch
            limit = st.number_input("Number of media posts to display", min_value=1, max_value=25, value=5)
            
            if st.button("Get Media List"):
                try:
                    media_list = api.get_media_list(limit=limit)
                    if "data" in media_list:
                        for media in media_list["data"]:
                            st.subheader(f"Post ID: {media['id']}")
                            st.write(f"Caption: {media.get('caption', 'No caption')}")
                            st.write(f"Media Type: {media.get('media_type')}")
                            st.write(f"Posted on: {media.get('timestamp')}")
                            
                            # Display image if it's a photo or a thumbnail for videos
                            if media.get("media_type") in ["IMAGE", "CAROUSEL_ALBUM"]:
                                st.image(media["media_url"], use_column_width=True)
                            elif media.get("media_type") == "VIDEO":
                                if "thumbnail_url" in media:
                                    st.image(media["thumbnail_url"], caption="Video Thumbnail", use_column_width=True)
                            
                            # Link to the post on Instagram
                            st.markdown(f"[View on Instagram]({media['permalink']})", unsafe_allow_html=True)
                            st.write("---")
                    else:
                        st.error("No media found or an error occurred.")
                except Exception as e:
                    st.error(f"Error fetching media list: {e}")
    else:
        st.warning("Instagram API not initialized. Check your credentials and .env file.")
