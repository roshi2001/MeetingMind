import pytest
import requests

BASE = "http://127.0.0.1:8000"
SAMPLE = """
John (CEO): Good morning everyone. Let's start the Q1 planning meeting.
Sarah (Product): Thanks John. The team has done a great job this quarter.
Mike (Engineering): We shipped 3 major features in Q4. All live in production.
John (CEO): Great work Mike. Sarah please update the product spec by Thursday.
Mike (Engineering): I will have the demo environment ready by January 10th.
Rachel (HR): I will set up the recruiting agency by end of this week.
"""

# ── Health ──
def test_health():
    res = requests.get(f"{BASE}/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

# ── Root ──
def test_root():
    res = requests.get(f"{BASE}/")
    assert res.status_code == 200
    assert "MeetingMind" in res.json()["message"]

# ── Summarize ──
def test_summarize_success():
    res = requests.post(f"{BASE}/summarize", json={"transcript": SAMPLE})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "summary" in data
    assert "action_items" in data
    assert len(data["summary"]) > 0
    assert len(data["action_items"]) > 0

def test_summarize_empty_transcript():
    res = requests.post(f"{BASE}/summarize", json={"transcript": ""})
    assert res.status_code == 400

# ── Analyze ──
def test_analyze_success():
    res = requests.post(f"{BASE}/analyze", json={"transcript": SAMPLE})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "overall_sentiment" in data
    assert "speakers" in data
    assert "topics" in data
    assert "sentiment_timeline" in data

def test_analyze_sentiment_values():
    res = requests.post(f"{BASE}/analyze", json={"transcript": SAMPLE})
    assert res.status_code == 200
    sentiment = res.json()["overall_sentiment"]
    assert sentiment in ["positive", "negative", "neutral"]

# ── Score ──
def test_score_success():
    res = requests.post(f"{BASE}/score", json={"transcript": SAMPLE})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "score" in data
    assert 1 <= data["score"] <= 10
    assert "decisions_made" in data
    assert "risks" in data

# ── Ask ──
def test_ask_success():
    requests.post(f"{BASE}/summarize", json={"transcript": SAMPLE})
    res = requests.post(f"{BASE}/ask", json={"question": "Who is in the meeting?"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "answer" in data
    assert len(data["answer"]) > 0

def test_ask_empty_question():
    res = requests.post(f"{BASE}/ask", json={"question": ""})
    assert res.status_code == 400

# ── Email ──
def test_email_success():
    res = requests.post(f"{BASE}/email", json={
        "summary": "This was a productive Q1 planning meeting.",
        "action_items": "- [Sarah]: Update product spec by Thursday\n- [Mike]: Demo ready by Jan 10",
        "sender_name": "John Smith",
        "sender_role": "CEO",
        "recipients": "All Meeting Attendees",
        "tone": "Professional"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "email" in data
    assert len(data["email"]) > 0