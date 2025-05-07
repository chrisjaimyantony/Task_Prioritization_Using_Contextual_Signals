import json
import os
from datetime import datetime

# Path to the feedback log inside this same folder
FEEDBACK_LOG_PATH = os.path.join(os.path.dirname(__file__), "feedback_log.json")

def log_feedback(task, heuristics, llm_prediction, user_correction, reason=None):
    """
    Save the user feedback to a JSON file.
    - task: the original task string
    - heuristics: a dict of feature:value pairs
    - llm_prediction: what the model predicted (HIGH/MEDIUM/LOW)
    - user_correction: what the user corrected it to (HIGH/MEDIUM/LOW)
    
    Ensures the folder & file exist, and only logs if heuristics is a dict.
    """

    # 1. Validate heuristics
    if not isinstance(heuristics, dict):
        print("⚠️  Heuristics must be a dict. Feedback not logged.")
        return

    # 2. Build the single feedback entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "heuristics": heuristics,
        "llm_prediction": llm_prediction,
        "user_correction": user_correction,
        "llm_reasoning": reason
    }

    # 3. Ensure the backend folder exists
    os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)

    # 4. Load existing feedback (if any)
    if os.path.exists(FEEDBACK_LOG_PATH):
        try:
            with open(FEEDBACK_LOG_PATH, "r") as f:
                feedback_list = json.load(f)
                if not isinstance(feedback_list, list):
                    # If the file is corrupted or not a list, reset it
                    feedback_list = []
        except json.JSONDecodeError:
            feedback_list = []
    else:
        feedback_list = []

    # 5. Append the new entry
    feedback_list.append(entry)

    # 6. Write back to disk
    with open(FEEDBACK_LOG_PATH, "w") as f:
        json.dump(feedback_list, f, indent=2)

    print("Feedback saved successfully.")

TASK_HISTORY_PATH = os.path.join(os.path.dirname(__file__), "task_history.json")

def log_task_entry(task: str):
    """
    Logs every task entered by the user to a task history file.
    Each entry includes a timestamp and the task string.
    """
    from datetime import datetime

    entry = {
        "timestamp": datetime.now().isoformat(),
        "task": task
    }

    # Load existing history
    if os.path.exists(TASK_HISTORY_PATH):
        with open(TASK_HISTORY_PATH, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    else:
        history = []

    history.append(entry)

    with open(TASK_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

    print("📚 Task history updated.")

