"""
Job Posting Data Extraction with Schema Validation
Uses LLM (GPT-4o-mini via OpenRouter) to extract structured data from unstructured text.
Includes JSON Schema validation, retry logic, and confidence scoring.
"""

import json
import os
from openai import OpenAI

# --- Configuration ---
API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjEwMDMxNDlAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.dNTWplTlAxzlj5_dhbcQlcHUsMkvlnj7DFDPV1LRNHU"
MODEL = "gpt-4o-mini"
MAX_RETRIES = 2

# --- Schema Definition ---
SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Job title"},
        "company": {"type": "string", "description": "Company name"},
        "location": {"type": "string", "description": "Job location"},
        "salary": {"type": "string", "description": "Salary range or amount"},
        "requirements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of job requirements",
        },
    },
    "required": ["title", "company", "location", "salary"],
}

SAMPLE_TEXT = (
    "Senior Software Engineer at Google in Mountain View, CA. "
    "Salary: $150k-$200k. "
    "Requirements: 5+ years Python, distributed systems"
)


def build_extraction_prompt(text: str, errors: list[str] | None = None) -> str:
    """Build the LLM prompt, optionally including previous validation errors."""
    base = (
        "Extract the following information from the text and return as JSON:\n\n"
        "Required fields:\n"
        "- title: The job title (string)\n"
        "- company: The company name (string)\n"
        "- location: The job location including city and state (string)\n"
        "- salary: The salary or salary range (string)\n\n"
        "Optional fields:\n"
        "- requirements: A JSON array of individual requirement strings\n\n"
        f'Text: "{text}"\n\n'
        "Return ONLY valid JSON matching this structure. No markdown, no explanation."
    )
    if errors:
        base += (
            "\n\nPrevious extraction had these validation errors — please fix them:\n"
            + "\n".join(f"- {e}" for e in errors)
        )
    return base


def validate_extraction(data: dict) -> tuple[bool, list[str], float]:
    """
    Validate extracted data against the schema.
    Returns (is_valid, error_list, confidence_score).
    """
    errors: list[str] = []
    confidence = 1.0

    # Check required fields
    for field in SCHEMA["required"]:
        if field not in data:
            errors.append(f"Missing required field: {field}")
            confidence -= 0.25
        elif not isinstance(data[field], str):
            errors.append(f"Field '{field}' must be a string, got {type(data[field]).__name__}")
            confidence -= 0.1
        elif not data[field].strip():
            errors.append(f"Field '{field}' is empty")
            confidence -= 0.15

    # Check optional 'requirements' field type if present
    if "requirements" in data:
        if not isinstance(data["requirements"], list):
            errors.append("Field 'requirements' must be an array")
            confidence -= 0.1
        elif not all(isinstance(r, str) for r in data["requirements"]):
            errors.append("All items in 'requirements' must be strings")
            confidence -= 0.05
    else:
        # Missing optional field lowers confidence slightly
        confidence -= 0.05

    # Clamp
    confidence = round(max(0.0, min(1.0, confidence)), 2)
    return len(errors) == 0, errors, confidence


def extract_with_llm(text: str, previous_errors: list[str] | None = None) -> dict:
    """Call the LLM and return parsed JSON."""
    client = OpenAI(
        base_url="https://aipipe.org/openai/v1",
        api_key=API_KEY,
    )

    prompt = build_extraction_prompt(text, previous_errors)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise data extraction assistant. "
                    "Always respond with valid JSON only."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def run_extraction(text: str) -> dict:
    """
    Full extraction pipeline:
      1. Call LLM
      2. Validate
      3. Retry up to MAX_RETRIES on failure
      4. Return final result envelope
    """
    errors: list[str] = []
    extracted: dict = {}
    validated = False
    confidence = 0.0
    retry_count = 0

    for attempt in range(1 + MAX_RETRIES):
        try:
            extracted = extract_with_llm(text, errors if attempt > 0 else None)
            validated, errors, confidence = validate_extraction(extracted)

            if validated:
                break

            retry_count = attempt + 1
            print(f"[Attempt {attempt + 1}] Validation failed: {errors}")

        except Exception as exc:
            errors = [f"Extraction error: {exc}"]
            confidence = 0.0
            retry_count = attempt + 1
            print(f"[Attempt {attempt + 1}] Exception: {exc}")

    # Build response envelope
    result = {
        "schema": SCHEMA,
        "extracted": extracted,
        "validated": validated,
        "confidence": confidence,
        "errors": errors,
        "retryCount": retry_count,
        "model": MODEL,
    }
    return result


if __name__ == "__main__":
    result = run_extraction(SAMPLE_TEXT)
    print(json.dumps(result, indent=2))
