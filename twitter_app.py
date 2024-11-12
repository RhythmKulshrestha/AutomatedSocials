import streamlit as st
from helpers.TwitterManager import TwitterManager
import tweepy
import time

def handle_rate_limit(sleep_time):
    """Display a message when rate limit is exceeded and show remaining time."""
    st.warning(f"Twitter API rate limit exceeded. Sleeping for {sleep_time} seconds.")
    st.info("Twitter’s API rate limits refresh every 15 minutes. Please wait until limit resets.")
    # Sleep in smaller increments to allow Streamlit to update the UI
    for i in range(sleep_time, 0, -5):
        time.sleep(5)
        st.write(f"Resuming in {i} seconds...")

def run(operation):
    # Attempt to initialize TwitterManager instance with rate limit handling
    try:
        twitter = TwitterManager()
        # Verify initialization and display success if no issues
        st.success("Twitter API initialized successfully!")
    except tweepy.TooManyRequests as e:
        # Display rate limit message if initialization hits rate limit
        sleep_time = int(e.response.headers.get("x-rate-limit-reset", 15*60))  # Defaults to 15 minutes
        handle_rate_limit(sleep_time)
        return  # Exit to prevent further attempts
    except Exception as e:
        # Catch any other exceptions and display the error message
        st.error(f"Failed to initialize Twitter API: {e}")
        return  # Exit to prevent further attempts

    # Check if Twitter API was successfully initialized before proceeding
    if twitter:
        try:
            # --- CREATE TWEET ---
            if operation == "Create Tweet":
                st.header("Create a New Tweet")
                tweet_text = st.text_area("Tweet Content", "")
                
                if st.button("Create Tweet"):
                    response = twitter.create_tweet(tweet_text)
                    if response and 'id' in response:
                        tweet_id = response['id']
                        st.success(f"Tweet created successfully! Tweet ID: {tweet_id}")
                        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                        st.markdown(f"[View Tweet on Twitter]({tweet_url})", unsafe_allow_html=True)
                    else:
                        st.error("Failed to create tweet.")

            # --- READ TWEET ---
            elif operation == "Read Tweet":
                st.header("Read a Specific Tweet")
                tweet_id = st.text_input("Tweet ID", "")
                
                if st.button("Read Tweet"):
                    tweet_content = twitter.get_tweet(tweet_id)
                    if tweet_content:
                        st.write("Tweet Content:")
                        st.write(f"Text: {tweet_content.get('text', 'No content found')}")
                        st.write(f"Created At: {tweet_content.get('created_at')}")
                        st.write(f"Public Metrics: {tweet_content.get('public_metrics', {})}")
                        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                        st.markdown(f"[View Tweet on Twitter]({tweet_url})", unsafe_allow_html=True)
                    else:
                        st.error("Tweet not found. Please check the Tweet ID.")

            # --- GET RECENT TWEETS ---
            elif operation == "Get Recent Tweets":
                st.header("Get Recent Tweets")
                max_results = st.number_input("Number of tweets to fetch", min_value=1, max_value=10, value=5)
                
                if st.button("Get Recent Tweets"):
                    recent_tweets = twitter.get_my_tweets(max_results=max_results)
                    if recent_tweets:
                        for tweet in recent_tweets:
                            st.subheader(f"Tweet ID: {tweet.id}")
                            st.write(f"Text: {tweet.text}")
                            st.write(f"Created At: {tweet.created_at}")
                            tweet_url = f"https://twitter.com/user/status/{tweet.id}"
                            st.markdown(f"[View on Twitter]({tweet_url})", unsafe_allow_html=True)
                            st.write("---")
                    else:
                        st.error("No recent tweets found.")

            # --- DELETE TWEET ---
            elif operation == "Delete Tweet":
                st.header("Delete a Specific Tweet")
                tweet_id = st.text_input("Tweet ID to Delete", "")
                
                if st.button("Delete Tweet"):
                    delete_success = twitter.delete_tweet(tweet_id)
                    if delete_success:
                        st.success("Tweet deleted successfully!")
                    else:
                        st.error("Failed to delete tweet. Check the Tweet ID.")

        except tweepy.TooManyRequests as e:
            # Handle rate limit error across all operations
            sleep_time = int(e.response.headers.get("x-rate-limit-reset", 15*60))
            handle_rate_limit(sleep_time)
        except Exception as e:
            # Handle any other general exceptions
            st.error(f"Error occurred: {e}")

    else:
        st.warning("Twitter API not initialized. Check your credentials and .env file.")
