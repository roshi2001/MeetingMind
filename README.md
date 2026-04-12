# 🧠 MeetingMind — AI-Powered Meeting Intelligence

> Turn every meeting transcript into actionable insights, analytics, and follow-ups — instantly powered by AI.

---

## 🔍 The Problem

Professionals spend over 31 hours per month in meetings. Yet after most meetings:

- Notes are incomplete or never written
- Action items get forgotten or misattributed
- Key decisions are not documented
- Follow-up emails take 20-30 minutes to write manually
- People who missed the meeting have no way to catch up quickly

Existing tools like Otter.ai and Fireflies only transcribe — they do not extract insights, score meetings, analyze sentiment, or give participants personal analytics.

---

## ✅ The Solution

MeetingMind is an end-to-end AI meeting intelligence platform that:

- Automatically summarizes meetings in 4 sentences
- Extracts and assigns action items
- Analyzes sentiment and meeting health
- Scores the meeting and flags risks
- Gives each participant personal insights
- Generates role-based follow-up emails
- Answers questions about the meeting via RAG

---

## 🎯 Objective

Build a production-ready AI application that transforms raw meeting transcripts into structured, actionable intelligence — reducing post-meeting work from 30 minutes to under 30 seconds.

---

## ⚙️ Methodology

| Feature | Approach |
|---|---|
| Summarization | LLM prompt engineering with Groq (llama-3.3-70b-versatile) |
| Action Extraction | Structured LLM output parsing |
| Q&A | RAG pipeline using FAISS + LangChain |
| Sentiment Analysis | LLM-based JSON structured output |
| Meeting Scoring | Multi-criteria LLM evaluation |
| Speaker Analytics | Regex parsing + LLM classification |
| Experiment Tracking | MLflow logging for all runs |
| API Layer | FastAPI with Pydantic validation |
| Frontend | Streamlit multi-page application |



## 📋 Features

| Feature | Description |
|---|---|
| 📋 Smart Summary | 4-sentence AI summary of any meeting |
| ✅ Action Items | Top 5 action items extracted automatically |
| 📊 Analytics Dashboard | Speaker breakdown, topic trends, sentiment timeline |
| 💬 Ask Questions | RAG-powered Q&A on your transcript |
| 🟢 Meeting Score | AI scores meeting out of 10 with risk flags |
| 👤 My Insights | Personal talk time, tasks, and report card |
| ✉️ Email Generator | Role-based follow-up email in one click |
| 📥 Export | Download PDF reports and CSV action items |

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/meetingmind.git
cd meetingmind
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free API key at [console.groq.com](https://console.groq.com)

### 5. Start the FastAPI backend
```bash
python -m uvicorn app.main:app --reload
```
API will run at `http://127.0.0.1:8000`

### 6. Start the Streamlit frontend
Open a new terminal and run:
```bash
streamlit run frontend.py
```
App will open at `http://localhost:8501`

---

## 📁 Project Structure

```
meetingmind/
├── app/
│   ├── main.py           # FastAPI routes
│   ├── summarizer.py     # LLM summarization + scoring
│   ├── rag.py            # FAISS RAG pipeline
│   ├── sentiment.py      # Sentiment analysis
│   └── monitor.py        # MLflow logging
├── data/
│   └── sample_transcript.txt   # Sample transcript for testing
├── models/               # Runtime model artifacts
├── tests/
│   └── test_api.py       # API tests
├── frontend.py           # Streamlit app
├── requirements.txt      # Dependencies
├── .env                  # API keys (not committed)
└── README.md
```

---

## 🧪 Testing

Make sure the FastAPI server is running, then:
```bash
pytest tests/test_api.py -v
```

---

## 📊 MLflow Tracking

To view experiment tracking dashboard:
```bash
mlflow ui
```
Open `http://127.0.0.1:5000` in your browser.

---

## 💡 Example Usage

1. Open the app at `http://localhost:8501`
2. Navigate to **📋 Analyze Meeting**
3. Paste a meeting transcript (use `data/sample_transcript.txt` as an example)
4. Click **✨ Analyze Meeting**
5. Explore **📊 Analytics Dashboard** for charts and insights
6. Go to **👤 My Insights** and type your name to see personal stats
7. Use **✉️ Email Generator** to create a follow-up email
8. Export results via **📥 Export**

---

## 👩‍💻 Author

**Roshitha Tiruveedhula**
MS Data Science — Northeastern University, Boston MA

---

## 📄 License

MIT License — feel free to use and build on this project."# MeetingMind" 
