import os
import time
import requests
import base64
import tempfile
import logging
from dotenv import load_dotenv

load_dotenv()
DID_API_KEY = os.getenv("DID_API_KEY", "").strip()
DID_API_URL = "https://api.d-id.com/talks"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Soft check for API Key - no raising exception
if not DID_API_KEY:
    logging.warning("D-ID API Key is missing! Avatar generation will not work properly.")

# ✅ Set up headers using Basic or Bearer auth
if ":" in DID_API_KEY:
    encoded_auth = base64.b64encode(DID_API_KEY.encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }
else:
    headers = {
        "Authorization": f"Bearer {DID_API_KEY}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

def create_avatar_video(text_content):
    """
    Create an avatar video from text using D-ID API.
    
    Args:
        text_content (str): The text that the avatar will speak
        
    Returns:
        dict: Contains status and video_url or error
    """
    if not DID_API_KEY:
        return {
            "status": "error",
            "error": "D-ID API Key is missing. Please add it to your .env file."
        }
        
    print("🔹 Using Headers:", headers)
    print(f"💰 About to charge D-ID credits for text: '{text_content[:50]}...'")

    # Build payload using the text content as the input for the avatar's script
    payload = {
        "source_url": "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg",
        "script": {
            "type": "text",
            "provider": {"type": "microsoft", "voice_id": "Sara"},
            "input": text_content,
            "ssml": "false"
        },
        "config": {"fluent": "false"}
    }    # Step 1: Send request to generate video
    response = requests.post(DID_API_URL, json=payload, headers=headers)
    if response.status_code != 201:
        return {
            "status": "error",
            "error": f"API request failed: {response.status_code} - {response.text}"
        }

    # Extract the talk ID from the response
    response_data = response.json()
    talk_id = response_data.get("id")
    print(f"✅ Video processing started! Talk ID: {talk_id} (Credits charged)")

    # Step 2: Poll for video status
    status_url = f"{DID_API_URL}/{talk_id}"
    video_url = None

    print("⏳ Waiting for video to be ready...")

    # Poll up to 90 times (approx. 4.5 minutes) - increased to ensure we don't waste credits
    for attempt in range(90):
        status_response = requests.get(status_url, headers=headers)
        if status_response.status_code != 200:
            return {
                "status": "error",
                "error": f"Error checking status: {status_response.text}"
            }

        status_data = status_response.json()
        status = status_data.get("status")

        print(f"🔄 Attempt {attempt + 1}/90 - Status: {status}")

        if status == "done":
            video_url = status_data.get("result_url")
            print(f"✅ Video is ready: {video_url}")
            break
        elif status == "failed":
            return {
                "status": "error",
                "error": "Video processing failed! Credits were charged but video failed."
            }

        # Wait 3 seconds between checks (total max wait time: 4.5 minutes)
        time.sleep(3)

    if not video_url:
        return {
            "status": "error", 
            "error": "Video is still processing after 4.5 minutes. Credits were charged. Contact D-ID support if video doesn't appear."
        }

    # Step 3: Download the video from the API
    try:
        video_response = requests.get(video_url)
        if video_response.status_code == 200:
            return {
                "status": "success",
                "video_url": video_url,
                "video_data": video_response.content
            }
        else:
            return {
                "status": "error",
                "error": "Error downloading video from D-ID API!"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error downloading video: {e}"
        }
