import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

token = os.environ.get("AIPROXY_TOKEN", "") or os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=token)
if "AIPROXY_TOKEN" in os.environ:
    client.base_url = "https://aiproxy.sanand.workers.dev/openai/v1"

class CommentRequest(BaseModel):
    comment: str

class SentimentResponse(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    rating: int

@app.post("/comment", response_model=SentimentResponse)
def analyze_comment(req: CommentRequest):
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a customer feedback analysis system. Classify the overall sentiment of the provided comment as strictly 'positive', 'negative', or 'neutral'. Also, assign a rating from 1 to 5 representing the sentiment intensity (5=highly positive, 1=highly negative)."
                },
                {
                    "role": "user",
                    "content": req.comment
                }
            ],
            response_format=SentimentResponse,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
