from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.summarizer import summarize_transcript, generate_followup_email, score_meeting
from app.rag import build_vector_store, answer_question
from app.monitor import log_request
from app.sentiment import analyze_sentiment
import mlflow

app = FastAPI(
    title="MeetingMind API",
    description="AI-powered meeting intelligence system",
    version="1.0.0"
)

mlflow.set_experiment("meetingmind")

class TranscriptRequest(BaseModel):
    transcript: str

class QuestionRequest(BaseModel):
    question: str

class EmailRequest(BaseModel):
    summary: str
    action_items: str
    sender_name: str
    sender_role: str
    recipients: str
    tone: str

@app.get("/")
def root():
    return {"message": "Welcome to MeetingMind API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/summarize")
def summarize(request: TranscriptRequest):
    if not request.transcript or not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    try:
        build_vector_store(request.transcript)
        result = summarize_transcript(request.transcript)
        log_request(
            endpoint="/summarize",
            input_length=len(request.transcript),
            output_length=len(result["summary"])
        )
        return {
            "status": "success",
            "summary": result["summary"],
            "action_items": result["action_items"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
def ask(request: QuestionRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        answer = answer_question(request.question)
        log_request(
            endpoint="/ask",
            input_length=len(request.question),
            output_length=len(answer)
        )
        return {
            "status": "success",
            "question": request.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze(request: TranscriptRequest):
    if not request.transcript or not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    try:
        result = analyze_sentiment(request.transcript)
        log_request(
            endpoint="/analyze",
            input_length=len(request.transcript),
            output_length=100
        )
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/score")
def meeting_score(request: TranscriptRequest):
    if not request.transcript or not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
    try:
        result = score_meeting(request.transcript)
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/email")
def followup_email(request: EmailRequest):
    try:
        email = generate_followup_email(
            summary=request.summary,
            action_items=request.action_items,
            sender_name=request.sender_name,
            sender_role=request.sender_role,
            recipients=request.recipients,
            tone=request.tone
        )
        return {"status": "success", "email": email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))