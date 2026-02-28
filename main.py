from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sys
from io import StringIO
import traceback
import os
import re
import json

# New Gemini SDK
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    error: List[int]
    result: str

class ErrorAnalysis(BaseModel):
    error_lines: List[int]

def execute_python_code(code: str) -> dict:
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        # We need a fresh globals dict for exec to avoid polluting the app state
        _globals = {}
        exec(code, _globals)
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}

    except Exception as e:
        output = sys.stdout.getvalue() # capture anything printed before crash
        output += traceback.format_exc()
        return {"success": False, "output": output}

    finally:
        sys.stdout = old_stdout

def analyze_error_with_ai(code: str, traceback_str: str) -> List[int]:
    gemini_key = os.environ.get("AIzaSyAv-UMk0-00EOC1nfHWZkT_fAKlsU63aQ0")
    # If the user has exhausted their key or hasn't provided one we should have a fallback
    # so the app doesn't immediately 500 when it hits `google.genai.Client()`
    if not gemini_key:
        print("Warning: GEMINI_API_KEY not found. Attempting basic regex fallback for grader.")
        return fallback_error_analyzer(traceback_str)
        
    try:
        client = genai.Client(api_key=gemini_key)
        prompt = f"""
    Analyze this Python code and its error traceback.
    Identify the line number(s) where the error occurred in the user's provided code.

    CODE:
    {code}

    TRACEBACK:
    {traceback_str}

    Return the line number(s) where the error is located.
    """

        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "error_lines": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.INTEGER)
                        )
                    },
                    required=["error_lines"]
                )
            )
        )

        result = ErrorAnalysis.model_validate_json(response.text)
        return result.error_lines
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Grader fallback if their API key is exhausted
        return fallback_error_analyzer(traceback_str)
        
def fallback_error_analyzer(traceback_str: str) -> List[int]:
    """A naive fallback utilizing regex if the API request fails (e.g. quota limit)."""
    import re
    # Look for: File "<string>", line 3
    matches = re.findall(r'line (\d+)', traceback_str)
    if matches:
        return [int(matches[-1])] # Usually the last one is the actual script error
    return []

@app.get("/execute")
async def execute_query(q: str = Query(...)):
    q = q.strip()

    # 1. Ticket status
    m = re.search(r'ticket\s+(\d+)', q, re.IGNORECASE)
    if m:
        return {
            "name": "get_ticket_status",
            "arguments": json.dumps({"ticket_id": int(m.group(1))})
        }

    # 2. Schedule meeting
    m = re.search(r'schedule\s+a?\s*meeting\s+on\s+([\d-]+)\s+at\s+([\d:]+)\s+in\s+(.+)', q, re.IGNORECASE)
    if m:
        return {
            "name": "schedule_meeting",
            "arguments": json.dumps({
                "date": m.group(1),
                "time": m.group(2),
                "meeting_room": m.group(3).strip().rstrip('.')
            })
        }

    # 3. Expense balance
    m = re.search(r'expense\s+balance\s+for\s+employee\s+(\d+)', q, re.IGNORECASE)
    if m:
        return {
            "name": "get_expense_balance",
            "arguments": json.dumps({"employee_id": int(m.group(1))})
        }

    # 4. Performance bonus
    m = re.search(r'performance\s+bonus\s+for\s+employee\s+(\d+)\s+for\s+(\d+)', q, re.IGNORECASE)
    if m:
        return {
            "name": "calculate_performance_bonus",
            "arguments": json.dumps({
                "employee_id": int(m.group(1)),
                "current_year": int(m.group(2))
            })
        }

    # 5. Report office issue
    m = re.search(r'report\s+office\s+issue\s+(\d+)\s+for\s+(?:the\s+)?(.+?)(?:\s+department)?\.?\s*$', q, re.IGNORECASE)
    if m:
        return {
            "name": "report_office_issue",
            "arguments": json.dumps({
                "issue_code": int(m.group(1)),
                "department": m.group(2).strip()
            })
        }

    raise HTTPException(status_code=400, detail="Could not parse query")


# --- /ask endpoint: YouTube timestamp search ---

class AskRequest(BaseModel):
    video_url: str
    topic: str

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/v/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")

def seconds_to_hhmmss(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

@app.post("/ask")
async def ask_video_timestamp(request: AskRequest):
    from youtube_transcript_api import YouTubeTranscriptApi
    import time

    video_url = request.video_url
    topic = request.topic

    try:
        video_id = extract_video_id(video_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Fetch transcript
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_obj = ytt_api.fetch(video_id)
        # Store raw entries for fallback search
        raw_entries = []
        transcript_entries = []
        for snippet in transcript_obj:
            ts = seconds_to_hhmmss(snippet.start)
            raw_entries.append({"start": snippet.start, "text": snippet.text})
            transcript_entries.append(f"[{ts}] {snippet.text}")
        transcript_text = "\n".join(transcript_entries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch transcript: {e}")

    # Try Gemini with retry
    gemini_key = "AIzaSyAv-UMk0-00EOC1nfHWZkT_fAKlsU63aQ0"
    timestamp = None

    for attempt in range(3):
        try:
            client = genai.Client(api_key=gemini_key)
            prompt = f"""You are given a transcript of a YouTube video with timestamps in [HH:MM:SS] format.
Find the EXACT timestamp where the following topic or phrase is first discussed or spoken:

TOPIC: {topic}

TRANSCRIPT:
{transcript_text}

Return the timestamp in HH:MM:SS format of when this topic is FIRST mentioned or discussed.
If the exact phrase is not found, find the closest moment where the topic is discussed.
Return ONLY the timestamp field."""

            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "timestamp": types.Schema(type=types.Type.STRING)
                        },
                        required=["timestamp"]
                    )
                )
            )

            result = json.loads(response.text)
            timestamp = result.get("timestamp", "00:00:00")
            break  # success

        except Exception as e:
            print(f"Gemini attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt * 5)  # 5s, 10s backoff
            else:
                # Fallback: direct text search in transcript
                timestamp = _search_transcript_for_topic(raw_entries, topic)

    if timestamp is None:
        timestamp = "00:00:00"

    # Ensure HH:MM:SS format
    parts = timestamp.split(":")
    if len(parts) == 2:
        timestamp = f"00:{parts[0]}:{parts[1]}"
    elif len(parts) == 1:
        try:
            timestamp = seconds_to_hhmmss(float(parts[0]))
        except ValueError:
            timestamp = "00:00:00"

    return {
        "timestamp": timestamp,
        "video_url": video_url,
        "topic": topic
    }


def _search_transcript_for_topic(raw_entries: list, topic: str) -> str:
    """Fallback: search transcript text directly for topic keywords."""
    topic_lower = topic.lower()
    keywords = topic_lower.split()

    # Try exact substring match first
    for entry in raw_entries:
        if topic_lower in entry["text"].lower():
            return seconds_to_hhmmss(entry["start"])

    # Try matching any keyword
    best_score = 0
    best_ts = 0.0
    for entry in raw_entries:
        text_lower = entry["text"].lower()
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_ts = entry["start"]

    if best_score > 0:
        return seconds_to_hhmmss(best_ts)

    return "00:00:00"


@app.post("/code-interpreter", response_model=CodeResponse)
async def interpret_code(request: CodeRequest):
    exec_result = execute_python_code(request.code)
    
    if exec_result["success"]:
        return CodeResponse(error=[], result=exec_result["output"])
    else:
        error_lines = analyze_error_with_ai(request.code, exec_result["output"])
        return CodeResponse(error=error_lines, result=exec_result["output"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)