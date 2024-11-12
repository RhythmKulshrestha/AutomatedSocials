import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import tweepy
from time import time, sleep
from datetime import datetime

# Load environment variables
load_dotenv()

class TwitterManager:
    def __init__(self):
        """
        Initialize Twitter API credentials from environment variables
        """
        client_id = os.getenv('TWITTER_CLIENT_ID')
        client_secret = os.getenv('TWITTER_CLIENT_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        # Verify credentials are present
        if not all([client_id, client_secret, bearer_token, access_token, access_token_secret]):
            raise ValueError("Missing required Twitter API credentials in .env file")

        # Initialize Twitter API v2 client with rate limit auto-sleep
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=client_id,
            consumer_secret=client_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True  # Automatically handles rate limits by sleeping
        )

        # Verify credentials
        try:
            self.client.get_me()
            print("Twitter API v2 authentication successful!")
        except tweepy.TweepyException as e:
            print(f"Error authenticating with Twitter: {str(e)}")
            raise

    def check_rate_limit_status(self, endpoint: str = "/statuses/user_timeline"):
        """
        Checks rate limit for a specific endpoint and returns time to reset if limit is exceeded.
        """
        try:
            rate_limit_status = self.client.get_rate_limit_status()
            limit_data = rate_limit_status['resources']['statuses'][endpoint]

            remaining_requests = limit_data['remaining']
            reset_time = limit_data['reset']

            if remaining_requests == 0:
                reset_time_formatted = datetime.fromtimestamp(reset_time).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Rate limit exceeded. Please wait until {reset_time_formatted} before retrying.")
                return reset_time  # Return reset time in seconds
            return None  # Rate limit has not been exceeded
        except tweepy.TweepyException as e:
            print(f"Error checking rate limit status: {str(e)}")
            raise

    # CREATE
    def create_tweet(self, text: str) -> Dict[str, Any]:
        """
        Create a new tweet
        """
        reset_time = self.check_rate_limit_status()
        if reset_time:
            print(f"Rate limit exceeded. Please wait until {datetime.fromtimestamp(reset_time)}.")
            return

        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data['id']
            print(f"Tweet created successfully! Tweet ID: {tweet_id}")
            return response.data
        except tweepy.TweepyException as e:
            print(f"Error creating tweet: {str(e)}")
            raise

    # READ
    def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get a specific tweet by its ID
        """
        reset_time = self.check_rate_limit_status()
        if reset_time:
            print(f"Rate limit exceeded. Please wait until {datetime.fromtimestamp(reset_time)}.")
            return

        try:
            response = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=['created_at', 'public_metrics']
            )
            if response.data:
                print(f"Tweet fetched successfully! Content: {response.data['text']}")
            return response.data
        except tweepy.TweepyException as e:
            print(f"Error fetching tweet: {str(e)}")
            raise

    # GET RECENT TWEETS
    def get_my_tweets(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get your own tweets
        """
        reset_time = self.check_rate_limit_status()
        if reset_time:
            print(f"Rate limit exceeded. Please wait until {datetime.fromtimestamp(reset_time)}.")
            return []

        try:
            me = self.client.get_me()
            user_id = me.data.id
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at']
            )
            if response.data:
                print(f"Retrieved {len(response.data)} tweets")
                for tweet in response.data:
                    print(f"Tweet ID: {tweet.id}")
                    print(f"Content: {tweet.text}")
                    print("---")
            return response.data if response.data else []
        except tweepy.TweepyException as e:
            print(f"Error fetching tweets: {str(e)}")
            raise

    # UPDATE (Note: Twitter API v2 doesn't support direct tweet updates, but you can delete and recreate)
    def update_tweet(self, tweet_id: str, new_text: str) -> Dict[str, Any]:
        """
        Update a tweet by deleting and recreating it
        """
        reset_time = self.check_rate_limit_status()
        if reset_time:
            print(f"Rate limit exceeded. Please wait until {datetime.fromtimestamp(reset_time)}.")
            return

        try:
            # Delete the old tweet
            self.delete_tweet(tweet_id)
            # Create new tweet
            return self.create_tweet(new_text)
        except tweepy.TweepyException as e:
            print(f"Error updating tweet: {str(e)}")
            raise

    # DELETE
    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet
        """
        reset_time = self.check_rate_limit_status()
        if reset_time:
            print(f"Rate limit exceeded. Please wait until {datetime.fromtimestamp(reset_time)}.")
            return False

        try:
            self.client.delete_tweet(tweet_id)
            print(f"Tweet deleted successfully!")
            return True
        except tweepy.TweepyException as e:
            print(f"Error deleting tweet: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    try:
        # Initialize Twitter manager
        twitter = TwitterManager()

        # Example to create a tweet
        print("\n1. Creating a tweet...")
        new_tweet = twitter.create_tweet("Hello Twitter. This is a new test tweet using API v2.")
        tweet_id = new_tweet['id'] if new_tweet else None
        
        # Read the tweet
        if tweet_id:
            print("\n2. Reading the tweet...")
            twitter.get_tweet(tweet_id)
        
        # Get recent tweets
        print("\n3. Getting recent tweets...")
        twitter.get_my_tweets(max_results=3)

        # Update the tweet (delete and recreate)
        if tweet_id:
            print("\n4. Updating the tweet...")
            twitter.update_tweet(tweet_id, "Updated test tweet using Twitter API v2!")
        
        # Delete the tweet
        if tweet_id:
            print("\n5. Deleting the tweet...")
            twitter.delete_tweet(tweet_id)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
