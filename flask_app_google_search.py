from flask_cors import CORS
import os
import requests
import re
from bs4 import BeautifulSoup
from openai import OpenAI
from flask import Flask, request, jsonify
from dotenv import load_dotenv
# from pymongo import MongoClient
from datetime import datetime, timezone
from connect_db import get_qs_data, get_video_data, insert_video_data  # Import functions
from flask import Blueprint

from flask import Blueprint, request, jsonify


# Load environment variables
load_dotenv(override=True)
# load_dotenv()

flask_app_google_search = Blueprint('flask_app_google_search', __name__)
# app = Flask(__name__)
# FRONTEND RUNS ON PORT 3000
CORS(flask_app_google_search, origins=["http://localhost:3000"])

# Get API keys from environment variables
API_KEY = os.getenv('API_KEY')
CSE_ID = os.getenv('CSE_ID')
OPENAI_API_KEY = os.getenv('openAI_key')

# MongoDB configuration
# mongo_client = MongoClient(os.getenv("MONGO_URI"))
# db = mongo_client['youtube_data']
# videos_collection = db['videos']


def google_search(query, num_results=10):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': CSE_ID,
        'q': query,
        'num': num_results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get('items', [])
        links = [item['link'] for item in results]  # Extract links
        print("extracted links from google - > ", links)
        return links[0:10]
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500  # Return error as JSON


def fetch_text_from_url(url):
    try:
        # Set a timeout of 5 seconds for the request
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        visible_text = extract_visible_text(response.text)
        # Return cleaned text and no error
        return clean_text(visible_text), None
    except requests.Timeout:
        return "", {"error": f"Request to {url} timed out."}  # Timeout error
    except requests.RequestException as e:
        return "", {"error": str(e)}  # Return error as JSON


def clean_text(text):
    # Remove non-alphabetic characters
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text)
    cleaned_text = ' '.join(cleaned_text.split())  # Normalize whitespace
    return cleaned_text


def extract_visible_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    visible_text = soup.get_text(separator=' ', strip=True)
    return visible_text


@flask_app_google_search.route('/search', methods=['POST'])
def search():
    data = request.json
    search_query = data.get('query', '')

    if not search_query:
        return jsonify({"error": "No query provided"}), 400

#    # Check if video data exists in MongoDB
#     qs_data = videos_collection.find_one({"search_query": search_query})
#     if qs_data:
#         print('qs found in mongodb database')
#         print(qs_data)

#         # Remove the '_id' field from the video_data dictionary
#         # The second argument prevents KeyError if '_id' doesn't exist
#         qs_data.pop('_id', None)

#         return jsonify(qs_data), 200  # Return data from MongoDB

    # Check if video data exists in MongoDB
    print('search_query - > ', search_query)
    qs_data = get_qs_data(search_query)
    if qs_data:
        print('qs found in mongodb database')
        print(qs_data)

        # Remove the '_id' field from the video_data dictionary
        # The second argument prevents KeyError if '_id' doesn't exist
        qs_data.pop('_id', None)
        return jsonify(qs_data), 200  # Return data from MongoDB

    # Get the first 10 links
    results = google_search(search_query)

    if isinstance(results, tuple):  # Check if an error occurred
        return results  # Return the error response

    largest_text = ''
    largest_text_url = ''
    largest_text_token_count = 0
    url_text_data = {}  # Dictionary to hold text data for each URL
    errors = []  # List to hold errors for any URL processing

    for url in results:
        text, error = fetch_text_from_url(url)

        if error:  # Check if an error occurred
            errors.append(error)  # Collect errors but continue processing

        url_text_data[url] = text  # Store text for each URL

        # Split the text into tokens based on spaces
        tokens = text.split()
        token_count = len(tokens)

        # Check if this text has more tokens than the current largest
        if token_count > largest_text_token_count:
            largest_text = text
            largest_text_url = url
            largest_text_token_count = token_count

    if largest_text_token_count > 100000 // 3:
        largest_text = ' '.join(largest_text.split()[:100000 // 3])

    client = OpenAI(api_key=OPENAI_API_KEY)

    MODEL = "gpt-4o"
    sys_prompt = "you are an expert who can teach more about any topic if given some context from google"
    user_prompt = f"this is the google search that user did: {search_query} and this is the extracted text from the internet for your support: {largest_text}. Can you teach me more about this topic because I have no time to read the whole website? Make sure you provide enough details so that I can use that material to teach in my course. Also explain the definition of the subject, why it is introduced, and a little history about it, if there is any. always make sure that the summary that you are providing is always in markdown format"

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    # Prepare the response
    response_data = {
        "search_query": search_query,
        "url": largest_text_url,
        "google_search_summary": completion.choices[0].message.content,
        "extracted_links": results,  # Include the extracted links
        "errors": errors,  # Include any errors encountered during processing
        "created_at": datetime.now(timezone.utc)

    }

    # videos_collection.insert_one(response_data)
    insert_video_data(response_data)

    return jsonify(response_data)


# if __name__ == "__main__":
#     flask_app_google_search.run(debug=True, port=5000)  # Run the app on port 8000
