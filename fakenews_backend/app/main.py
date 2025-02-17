from flask import Flask
from flask_restx import Api
from app.api.News import news_ns
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    api = Api(app, doc='/docs')
    api.add_namespace(news_ns)

    return app
