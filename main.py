import os
from backend.llm_interface import extract_priority_from_llm
from backend.heuristic_engine import (
    load_weights,
    extract_features,
    score_task,
    extract_and_validate_time
)
from backend.feedback_logger import log_feedback, log_task_entry

# === 0) Define absolute path to the weights file ===
BASE_DIR = os.path.dirname(__file__)
WEIGHTS_PATH = os.path.join(BASE_DIR, "backend", "heuristic_weights.json")

# === 1) Get task from user ===
task_input = input("Enter your task: ").strip()

# === 1.5) Check if task includes a past time ===
task_time, needs_clarification = extract_and_validate_time(task_input)

if needs_clarification:
    print(f"You mentioned a time in the past ({task_time}).")
    print("Did you mean a different day or a future time?")
    clarified_input = input("Please clarify your task: ").strip()

    # Replace original task input with clarified version
    task_input = clarified_input

# === 2) Log task only after clarification is complete ===
log_task_entry(task_input)

# === 3) Extract features from task ===
features = extract_features(task_input)
print("Extracted features:", features)

# === 4) Load heuristic weights ===
weights = load_weights(WEIGHTS_PATH)

# === 5) Score the task using weights ===
heuristic_score = score_task(features, weights)
print("Heuristic Scores:", heuristic_score)

# === 6) Extract current system time (used by LLM) ===
current_time = features.pop("system_time")

# === 7) Ask LLM to prioritize based on context ===
priority, thought = extract_priority_from_llm(task_input, heuristic_score, current_time)
print("Predicted Priority:", priority)
print("Reasoning:", thought)


# === 8) Ask user to verify the prediction ===
feedback = input("Is this correct? (y/n): ").strip().lower()

if feedback == "n":
    corrected_priority = input("What should it be? (HIGH / MEDIUM / LOW): ").strip().upper()

    # Log corrected feedback
    log_feedback(
    task=task_input,
    heuristics=features,
    llm_prediction=priority,
    user_correction=corrected_priority,
    reason=thought
)

    print("Feedback saved.")
else:
    print("No correction needed.")
