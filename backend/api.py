from flask import Flask, request, jsonify
from flask_cors import CORS
from heuristic_engine import extract_features, load_weights, score_task
from llm_interface import extract_priority_from_llm
from feedback_logger import log_feedback

import os

app = Flask(__name__)
CORS(app)  # Allows frontend to call backend from browser

# Define weights path
BASE_DIR = os.path.dirname(__file__)
WEIGHTS_PATH = os.path.join(BASE_DIR, "heuristic_weights.json")


@app.route("/process-task", methods=["POST"])
def process_task():
    data = request.get_json()
    task = data.get("task")

    features = extract_features(task)
    score = score_task(features, load_weights(WEIGHTS_PATH))
    current_time = features.pop("system_time")

    priority, reasoning = extract_priority_from_llm(task, score, current_time)

    return jsonify({
        "priority": priority,
        "reasoning": reasoning
    })


@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    task = data.get("task")
    corrected = data.get("corrected_priority")

    features = extract_features(task)
    current_time = features.pop("system_time")

    _, reasoning = extract_priority_from_llm(task, score_task(features, load_weights(WEIGHTS_PATH)), current_time)

    log_feedback(task, features, "UNKNOWN", corrected, reason=reasoning)
    return jsonify({"status": "Feedback saved"})


if __name__ == "__main__":
    app.run(debug=True)
