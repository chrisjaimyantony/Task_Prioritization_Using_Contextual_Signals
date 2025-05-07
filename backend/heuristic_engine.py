import json
import re
from datetime import datetime, timedelta

# === Load heuristic weights from a JSON file ===
def load_weights(path):
    """
    Reads the heuristic weights from a JSON file.
    Each weight corresponds to a feature-value pair like 'urgency=high'.
    """
    with open(path, "r") as f:
        return json.load(f)

# === Score task using feature weights ===
def score_task(features, weights):
    """
    Adds up the score for each feature based on its weight from the weights file.
    """
    score = 0
    for key, value in features.items():
        feature_key = f"{key}={value}"
        score += weights.get(feature_key, 0)
    return score

# === Extract and validate time if mentioned in task string ===
def extract_and_validate_time(task_text: str) -> (str, bool):
    """
    Checks if the task includes a time (e.g., '5 p.m.') and whether it's in the past.
    Returns (time_string, needs_clarification)
    """
    task_lower = task_text.lower()
    time_match = re.search(r'\b(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)\b', task_lower)

    if time_match:
        hour = int(time_match.group(1))
        meridian = time_match.group(2).replace('.', '')

        # Convert to 24-hour format
        if meridian == "pm" and hour != 12:
            hour += 12
        elif meridian == "am" and hour == 12:
            hour = 0

        now = datetime.now()
        task_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)

        # If the time is in the past, flag for clarification
        if task_time < now:
            return f"{hour:02d}:00", True

        return f"{hour:02d}:00", False

    return None, False

# === Extract features from a task string using rule-based heuristics ===
def extract_features(task: str) -> dict:
    """
    Infers heuristic features from the task string.
    Detects urgency (based on time or keywords), task type, tone, and adds system time.
    Returns a dictionary of features.
    """
    task_lower = task.lower()

    # Default urgency based on keywords
    if any(word in task_lower for word in ["now", "urgent", "immediately", "asap", "tonight", "today"]):
        urgency = "high"
    elif any(word in task_lower for word in ["tomorrow", "soon", "later", "this week"]):
        urgency = "medium"
    else:
        urgency = "low"

    # Check time and boost urgency if within 2 hours
    time_match = re.search(r'\b(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)\b', task_lower)
    if time_match:
        hour = int(time_match.group(1))
        meridian = time_match.group(2).replace('.', '')

        # Convert to 24-hour time
        if meridian == "pm" and hour != 12:
            hour += 12
        elif meridian == "am" and hour == 12:
            hour = 0

        now = datetime.now()
        task_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)

        if timedelta(0) <= (task_time - now) <= timedelta(hours=2):
            urgency = "high"

    # Infer task type
    if any(word in task_lower for word in ["assignment", "submit", "research", "homework"]):
        task_type = "academic"
    elif any(word in task_lower for word in ["meeting", "email", "client", "project"]):
        task_type = "work"
    else:
        task_type = "personal"

    # Infer tone
    if "please" in task_lower or "kindly" in task_lower:
        tone = "formal"
    elif "maybe" in task_lower or "idk" in task_lower:
        tone = "casual"
    else:
        tone = "neutral"

    # Record system time for LLM prompt
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    return {
        "urgency": urgency,
        "task_type": task_type,
        "tone": tone,
        "system_time": current_time
    }
