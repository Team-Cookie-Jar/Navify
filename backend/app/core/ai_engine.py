# app/core/ai_engine.py

import random

def analyze_document(doc: dict) -> dict:
    # Placeholder AI Logic - replace with actual model
    issues = []

    if "expiration_date" in doc and doc["expiration_date"] < "2025-01-01":
        issues.append("Document is expired")

    if "name" not in doc:
        issues.append("missing required field: name.")

    confidence = round(random.uniform(0.7, 0.99), 2)

    return {
        "issues": issues,
        "confidence": confidence
    }

def simulate_what_if(original_doc: dict, scenario: dict) -> dict:
    # Modify the document with the scenario
    simulate_doc = original_doc.copy()
    simulate_doc.update(scenario)

    return analyze_document(simulate_doc)

