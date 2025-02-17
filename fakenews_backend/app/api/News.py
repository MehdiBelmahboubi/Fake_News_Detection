import os
import http.client
from flask import jsonify
from flask_restx import Namespace, Resource
from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()

news_api_key = os.getenv('NEWS_API_KEY')
if not news_api_key:
    raise ValueError("Missing NEWS_API_KEY in environment variables")

api = NewsApiClient(api_key=news_api_key)

news_ns = Namespace('News', description='News related operations')

@news_ns.route('/')
class News(Resource):
    def get(self):
        try:
            headlines = api.get_top_headlines()

            # Check if response contains articles
            if not headlines or headlines.get("status") != "ok":
                return jsonify({"error": "Failed to fetch news"}), 500

            return jsonify(headlines)

        except Exception as e:
            return jsonify({"error": str(e)}), 500
