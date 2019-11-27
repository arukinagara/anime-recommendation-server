import os

from flask import Flask, jsonify
from flask_cors import CORS

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = os.urandom(24),
    )

    # enable CORS
    CORS(app, resources={r'/*': {'origins': '*'}})

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # sanity check route
    @app.route('/ping', methods=['GET'])
    def hello():
        return jsonify('Hello, World!!')

    from . import recommendation
    app.register_blueprint(recommendation.bp)

    return app
