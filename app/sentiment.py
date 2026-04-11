from dotenv import load_dotenv
import os
import json

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

sentiment_prompt = PromptTemplate(
    input_variables=["transcript"],
    template="""
    Analyze this meeting transcript and return ONLY a valid JSON object with no extra text.

    Transcript:
    {transcript}

    Return exactly this JSON structure:
    {{
        "overall_sentiment": "positive" or "negative" or "neutral",
        "sentiment_score": a number between 0 and 100,
        "speakers": [
            {{
                "name": "speaker name",
                "lines": number of lines they spoke,
                "sentiment": "positive" or "negative" or "neutral"
            }}
        ],
        "topics": [
            {{
                "topic": "topic name",
                "mentions": number of times mentioned
            }}
        ],
        "sentiment_timeline": [
            {{"segment": "Early", "sentiment_score": number between 0 and 100}},
            {{"segment": "Middle", "sentiment_score": number between 0 and 100}},
            {{"segment": "Late", "sentiment_score": number between 0 and 100}}
        ]
    }}
    """
)

def parse_speakers(transcript: str) -> dict:
    lines = transcript.strip().split('\n')
    speaker_lines = {}
    for line in lines:
        if ':' in line:
            speaker = line.split(':')[0].strip()
            if speaker:
                speaker_lines[speaker] = speaker_lines.get(speaker, 0) + 1
    return speaker_lines

def analyze_sentiment(transcript: str) -> dict:
    try:
        chain = sentiment_prompt | llm
        response = chain.invoke({"transcript": transcript}).content
        response = response.strip()
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        result = json.loads(response)

        actual_speakers = parse_speakers(transcript)
        for speaker in result.get("speakers", []):
            name = speaker.get("name", "")
            if name in actual_speakers:
                speaker["lines"] = actual_speakers[name]

        return result

    except json.JSONDecodeError:
        actual_speakers = parse_speakers(transcript)
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 50,
            "speakers": [
                {"name": k, "lines": v, "sentiment": "neutral"}
                for k, v in actual_speakers.items()
            ],
            "topics": [],
            "sentiment_timeline": [
                {"segment": "Early", "sentiment_score": 50},
                {"segment": "Middle", "sentiment_score": 50},
                {"segment": "Late", "sentiment_score": 50}
            ]
        }