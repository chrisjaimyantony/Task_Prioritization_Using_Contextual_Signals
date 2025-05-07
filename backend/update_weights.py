import json
from collections import defaultdict
import os

# Paths to your files
LOG_PATH = os.path.join(os.path.dirname(__file__), "feedback_log.json")
WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "heuristic_weights.json")

def load_json(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def priority_to_score(priority):
    """Convert HIGH/MEDIUM/LOW to numerical values for easier comparison."""
    mapping = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    return mapping.get(priority.upper(), 2)

def update_weights():
    feedback_log = load_json(LOG_PATH)
    weights = load_json(WEIGHTS_PATH)

    # Track how often each feature is wrong
    feature_adjustments = defaultdict(int)

    for entry in feedback_log:
        predicted = entry["llm_prediction"]
        corrected = entry["user_correction"]
        features = entry["heuristics"]

        # Compare numeric values of predicted and corrected
        delta = priority_to_score(corrected) - priority_to_score(predicted)

        if delta == 0:
            continue  # No need to update if prediction was already correct

        # Adjust weights of each feature
        for key, value in features.items():
            feature_key = f"{key}={value}"
            # If the model under-prioritized (e.g. said LOW, user said HIGH), increase
            # If over-prioritized, decrease
            feature_adjustments[feature_key] += delta

    # Apply adjustments
    for feature, change in feature_adjustments.items():
        old_weight = weights.get(feature, 0)
        new_weight = max(0, min(5, old_weight + change))  # clamp between 0–5
        weights[feature] = new_weight
        print(f"{feature}: {old_weight} → {new_weight} (Δ {change})")

    save_json(weights, WEIGHTS_PATH)
    print("Weights updated and saved.")

# Run the update if script is executed directly
if __name__ == "__main__":
    update_weights()
