from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import os
import re
from openai import OpenAI
from flask_cors import CORS  # Import CORS
import json
import re
from dotenv import load_dotenv
from pymongo import MongoClient

from datetime import datetime, timezone

from connect_db import get_video_data, insert_video_data  # Import functions

from flask import Blueprint, request, jsonify

flask_app = Blueprint('flask_app', __name__)
# app = Flask(__name__)
load_dotenv(override=True)

# FRONTEND RUNS ON PORT 3000
CORS(flask_app, origins=["http://localhost:3000"])

# Initialize OpenAI client
# client = OpenAI(api_key=os.getenv("openAI_key"))


# Load environment variables from .env file
# load the newest key with the same value
# Access the API key
client = OpenAI(api_key=os.getenv("openAI_key"))


MODEL = "gpt-4o"

# MongoDB configuration
# mongo_client = MongoClient(os.getenv("MONGO_URI"))
# db = mongo_client['youtube_data']
# videos_collection = db['videos']

# Function to extract video ID from the URL


def get_video_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([A-Za-z0-9_-]{11})'
    match = re.match(pattern, url)
    return match.group(1) if match else None

# Function to get captions for a video


def get_captions(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        captions_text = ' '.join([item['text'] for item in transcript])
        return captions_text
    except Exception as e:
        return f"Error retrieving captions for video {video_id}: {str(e)}"


@flask_app.route('/extract-captions', methods=['POST'])
def extract_captions():
    data = request.json
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({"error": "Video URL is required"}), 400

    video_id = get_video_id(video_url)

    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

      # Check if video data exists in MongoDB
    # video_data = videos_collection.find_one({"video_id": video_id})
    # if video_data:
    #     print('found in mongodb database')
    #     print(video_data)
    #     # Remove the '_id' field from the video_data dictionary
    #     # The second argument prevents KeyError if '_id' doesn't exist
    #     video_data.pop('_id', None)
    #     return jsonify(video_data), 200  # Return data from MongoDB

  # Check if video data exists in MongoDB
    video_data = get_video_data(video_id)
    if video_data:
        print('found in mongodb database')
        video_data.pop('_id', None)
        return jsonify(video_data), 200  # Return data from MongoDB

    captions_text = get_captions(video_id)

    if "Error" in captions_text:
        return jsonify({"error": captions_text}), 500

    # Read system and user prompts
    sys_prompt = ""
    user_prompt = ""
    try:
        with open('video_summary_sys_prompt.txt', 'r', encoding='utf-8') as file:
            sys_prompt = file.read()

        with open('video_summary_user_prompt.txt', 'r', encoding='utf-8') as file:
            user_prompt = file.read() + captions_text

        # Make request to OpenAI API
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        assistant_response = completion.choices[0].message.content

        match = re.search(r'```json\n(.*?)\n```',
                          assistant_response, re.DOTALL)
        if match:
            # Extract JSON text inside ```json```
            json_content = match.group(1)

            # Convert to JSON
            try:
                parsed_data = json.loads(json_content)

                # Accessing the keys
                summary = parsed_data["summary"]
                google_search_ideas = parsed_data["google_search_ideas"]
                main_keywords = parsed_data["main_keywords"]

                print(google_search_ideas)
                print(main_keywords)
                # print("Summary:", summary)
                # print("Google Search Ideas:", google_search_ideas)
                # print("Main Keywords:", main_keywords)

                # Structure data to save in MongoDB
                video_data = {
                    "video_id": video_id,
                    "video_url": video_url,
                    "captions": captions_text,
                    "summary": summary,
                    "google_search_ideas": google_search_ideas,
                    "main_keywords": main_keywords,
                    "created_at": datetime.now(timezone.utc)
                }

                # Insert data into MongoDB
                # videos_collection.insert_one(video_data)

                insert_video_data(video_data)

                # Return response
                return jsonify(video_data), 201

            except json.JSONDecodeError as e:
                return jsonify({"Failed to decode JSON": str(e)}), 500

            except Exception as e:
                return jsonify({"error": str(e)}), 500

                # print("Failed to decode JSON:", e)
        else:
            return jsonify({"error": "no json output found"}), 500

        # return jsonify({"captions": captions_text, "assistant_response": assistant_response})

        # return jsonify({"captions": captions_text, "summary": summary, "google_search_ideas": google_search_ideas, "main_keywords": main_keywords})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# if __name__ == '__main__':
#     # RUNS BY DEFAULT ON PORT 5000
#     flask_app.run(debug=True)
