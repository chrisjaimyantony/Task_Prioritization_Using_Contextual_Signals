import json
import requests

def query_mistral(prompt: str) -> str:
    """
    Sends the prompt to Mistral via Ollama's API and returns the raw text response.
    """
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
        }
    )
    return response.json().get("response", "")

def extract_priority_from_llm(task_input, heuristic_score, current_time):
    import ollama

    prompt = f"""
You are a reasoning assistant that assigns priority levels (HIGH, MEDIUM, LOW) to tasks.

# Task Information:
- Task: "{task_input}"
- Heuristic score: {heuristic_score}
- System time: {current_time}

# Instructions:
First, explain your reasoning in 1–3 sentences.
Then write the priority as a final line using this exact format:
Priority: <HIGH / MEDIUM / LOW>

Example output:
Thought: This task is urgent and due soon. The heuristic score is high, and it's work-related.
Priority: HIGH
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    full_response = response["message"]["content"]

    # Split to extract Thought and Priority
    lines = full_response.strip().splitlines()
    thought = ""
    priority = "MEDIUM"  # fallback if nothing found

    for line in lines:
        if line.lower().startswith("thought:"):
            thought = line.split(":", 1)[1].strip()
        elif "priority:" in line.lower():
            priority = line.split(":")[1].strip().upper()

    return priority, thought
