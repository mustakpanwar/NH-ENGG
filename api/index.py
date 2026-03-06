import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app, init_db
    init_db()
except Exception as e:
    import traceback
    from flask import Flask, jsonify
    app = Flask(__name__)
    error_detail = traceback.format_exc()

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return f"<pre>STARTUP ERROR:\n{error_detail}</pre>", 500