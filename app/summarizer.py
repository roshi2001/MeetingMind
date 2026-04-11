from dotenv import load_dotenv
import os

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import mlflow

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

summary_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="""
    You are an expert meeting assistant.
    Given the following meeting transcript, provide a SHORT summary in maximum 4 sentences.
    Focus only on the most important outcomes and decisions.
    Do not repeat details from the transcript.

    Transcript:
    {transcript}

    Summary (4 sentences max):
    """
)

action_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="""
    Extract only the top 5 most important action items from this meeting transcript.
    Be very brief - one line per action item maximum.
    Format as:
    - [Owner]: Action

    Transcript:
    {transcript}

    Top 5 Action Items only:
    """
)

email_prompt = PromptTemplate(
    input_variables=["summary", "action_items", "sender_name", "sender_role", "recipients", "tone"],
    template="""
    Write a {tone} follow-up email for a meeting.

    From: {sender_name} ({sender_role})
    To: {recipients}

    Meeting Summary: {summary}
    Action Items: {action_items}

    Write a complete email with:
    - Subject line
    - Greeting addressing {recipients}
    - Brief recap of meeting (2-3 sentences max)
    - Clear action items section
    - Professional sign-off from {sender_name}, {sender_role}

    Keep it concise and professional. Max 200 words.
    """
)

score_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="""
    Rate this meeting out of 10 and return ONLY a valid JSON object.
    {{
        "score": number between 1 and 10,
        "reason": "one sentence explanation",
        "decisions_made": number of clear decisions made,
        "risks": ["risk 1", "risk 2"] (max 3 short risks or blockers mentioned)
    }}

    Transcript:
    {transcript}
    """
)

def summarize_transcript(transcript: str) -> dict:
    """Generate meeting summary and action items."""
    with mlflow.start_run(run_name="summarization"):
        mlflow.log_param("transcript_length", len(transcript))

        summary_chain = summary_prompt | llm
        action_chain = action_prompt | llm

        summary = summary_chain.invoke({"transcript": transcript}).content
        action_items = action_chain.invoke({"transcript": transcript}).content

        mlflow.log_metric("summary_length", len(summary))
        mlflow.log_metric("action_items_length", len(action_items))

        return {
            "summary": summary,
            "action_items": action_items
        }

def generate_followup_email(summary: str, action_items: str, sender_name: str, sender_role: str, recipients: str, tone: str) -> str:
    """Generate a follow up email."""
    chain = email_prompt | llm
    return chain.invoke({
        "summary": summary,
        "action_items": action_items,
        "sender_name": sender_name,
        "sender_role": sender_role,
        "recipients": recipients,
        "tone": tone
    }).content

def score_meeting(transcript: str) -> dict:
    """Score the meeting and extract risks."""
    import json
    chain = score_prompt | llm
    response = chain.invoke({"transcript": transcript}).content
    response = response.strip()
    if "```json" in response:
        response = response.split("```json")[1].split("```")[0].strip()
    elif "```" in response:
        response = response.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(response)
    except:
        return {
            "score": 7,
            "reason": "Could not parse score",
            "decisions_made": 0,
            "risks": []
        }