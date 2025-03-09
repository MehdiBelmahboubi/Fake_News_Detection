import os
import json
import fitz  # PyMuPDF for PDF processing
import numpy as np
from flask import request
from flask_restx import Namespace, Resource, reqparse
from dotenv import load_dotenv
from newsapi import NewsApiClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

load_dotenv()

news_api_key = os.getenv("NEWS_API_KEY")
if not news_api_key:
    raise ValueError("Missing NEWS_API_KEY in environment variables")

api = NewsApiClient(api_key=news_api_key)

news_ns = Namespace("News", description="News related operations")

parser = reqparse.RequestParser()
parser.add_argument("query", type=str, required=True, help="Query is required to search news")

bert_classifier = pipeline("text-classification", model="roberta-base-openai-detector")

def load_news_articles(file_path="Fake_News.json"):
    """Loads news articles from a JSON file and extracts content."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return [article.get("content", "").strip() for article in data.get("articles", []) if article.get("content")]
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def check_fake_news_similarity(user_text, threshold=0.3):
    """Checks similarity between user text and existing news articles using TF-IDF."""
    news_articles = load_news_articles()

    if not news_articles:
        return {"message": "Not enough news data available to compare.", "similarity": None, "result": "Fake", "confidence": 0.0}

    all_texts = news_articles + [user_text]

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
    except ValueError:
        return {"message": "Not enough text data to perform comparison.", "similarity": None, "result": "Fake", "confidence": 0.0}

    similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
    max_similarity = float(np.max(similarity_scores)) if len(similarity_scores) > 0 else 0.0

    is_true = max_similarity > threshold
    return {
        "message": "The news is likely TRUE based on similarity." if is_true else "The news is NOT strongly supported by existing sources.",
        "similarity": round(max_similarity, 2),
        "result": "Réel" if is_true else "Fake",
        "confidence": round(max_similarity, 2)
    }

def check_fake_news_bert(user_text, confidence_threshold=0.5):
    """Uses BERT model to classify user text as FAKE or REAL news"""
    result = bert_classifier(user_text)
    label = result[0]['label'].upper()
    score = float(result[0]['score'])

    is_true = "REAL" in label or label == "LABEL_1"

    return {
        "message": "AI suggests the news is likely TRUE." if is_true else "AI suggests the news is questionable.",
        "confidence": round(score, 2),
        "result": "Réel" if is_true else "Fake"
    }

@news_ns.route("/getAll")
class getAllNews(Resource):
    def get(self):
        try:
            headlines = api.get_top_headlines()
            if not headlines or headlines.get("status") != "ok":
                return {"error": "Failed to fetch news"}, 500
            return headlines, 200
        except Exception as e:
            return {"error": str(e)}, 500

@news_ns.route("/checkNews")
class getNewsByQuery(Resource):
    @news_ns.expect(parser)
    def get(self):
        try:
            args = parser.parse_args()
            query = args.get("query")

            if not query:
                return {"error": "Query parameter is missing"}, 400

            search_results = api.get_everything(q=query, page_size=100, language="en")
            if not search_results or search_results.get("status") != "ok":
                return {"error": "Failed to fetch news"}, 500

            with open("Fake_News.json", "w", encoding="utf-8") as file:
                json.dump(search_results, file, ensure_ascii=False, indent=4)

            similarity_result = check_fake_news_similarity(query)
            bert_result = check_fake_news_bert(query)

            # Determine final result: Fake if either method classifies it as Fake
            final_result = "Fake" if similarity_result["result"] == "Fake" or bert_result["result"] == "Fake" else "Réel"
            final_confidence = max(similarity_result["confidence"], bert_result["confidence"])

            return {
                "similarity_check": similarity_result,
                "bert_check": bert_result,
                "result": final_result,
                "confidence": final_confidence
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {str(e)}"

@news_ns.route("/checkPdf")
class CheckNewsFromPDF(Resource):
    def post(self):
        """Handles file upload and checks if the news in the PDF is fake or real."""
        if "file" not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files["file"]
        if file.filename == "":
            return {"error": "Empty filename"}, 400

        # Save the uploaded PDF temporarily
        temp_path = "temp_uploaded.pdf"
        file.save(temp_path)

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(temp_path)
        if "Error" in extracted_text:
            return {"error": extracted_text}, 500

        # Delete the temporary file
        os.remove(temp_path)

        # Analyze the extracted text
        similarity_result = check_fake_news_similarity(extracted_text)
        bert_result = check_fake_news_bert(extracted_text)

        # Determine final result: Fake if either method classifies it as Fake
        final_result = "Fake" if similarity_result["result"] == "Fake" or bert_result["result"] == "Fake" else "Réel"
        final_confidence = max(similarity_result["confidence"], bert_result["confidence"])

        return {
            "similarity_check": similarity_result,
            "bert_check": bert_result,
            "result": final_result,
            "confidence": final_confidence
        }, 200
