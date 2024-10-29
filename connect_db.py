# from pymongo import MongoClient
# from pymongo.mongo_client import MongoClient

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import os
from dotenv import load_dotenv

# for checking if the database is connected or not
load_dotenv()

# MongoDB configuration

# mongo_client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))

mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client['youtube_data']
videos_collection = db['videos']


# def get_db():
#     mongo_client = MongoClient(os.getenv("MONGO_URI"))
#     db = mongo_client['youtube_data']
#     return db


def get_video_data(video_id):
    return videos_collection.find_one({"video_id": video_id})


def get_qs_data(video_id):
    return videos_collection.find_one({"search_query": video_id})


def insert_video_data(video_data):
    videos_collection.insert_one(video_data)
