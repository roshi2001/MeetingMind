import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import csv

st.set_page_config(
    page_title="MeetingMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

with st.sidebar:
    st.title("🧠 MeetingMind")
    st.caption("AI-powered meeting intelligence")
    st.divider()
    page = st.radio("", [
        "🏠 Home",
        "📋 Analyze Meeting",
        "📊 Analytics Dashboard",
        "💬 Ask Questions",
        "📥 Export",
        "✉️ Email Generator",
        "👤 My Insights"
    ])
    st.divider()
    if st.session_state.get("transcript_loaded"):
        st.success("✅ Meeting loaded")
    else:
        st.info("No meeting analyzed yet")

def generate_pdf(summary, action_items):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("MeetingMind Report", styles['Title']),
        Spacer(1, 20),
        Paragraph("Summary", styles['Heading1']),
        Paragraph(summary.replace('\n', '<br/>'), styles['Normal']),
        Spacer(1, 20),
        Paragraph("Action Items", styles['Heading1']),
        Paragraph(action_items.replace('\n', '<br/>'), styles['Normal']),
    ]
    doc.build(story)
    buf.seek(0)
    return buf

def generate_csv(action_items):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Action Item"])
    for line in action_items.strip().split('\n'):
        if line.strip():
            w.writerow([line.strip()])
    return out.getvalue()

# ══════════════════════════════════════════
# PAGE 0 — Home
# ══════════════════════════════════════════
if page == "🏠 Home":
    st.markdown("""
    <div style="text-align:center; padding:40px 0 20px;">
        <div style="font-size:72px; margin-bottom:16px;">🧠</div>
        <h1 style="font-size:52px; font-weight:800; letter-spacing:-2px; background:linear-gradient(135deg,#534AB7,#1D9E75); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">MeetingMind</h1>
        <p style="font-size:18px; color:gray; margin:16px auto; max-width:480px; line-height:1.7;">Turn every meeting transcript into actionable insights, analytics, and follow-ups — instantly powered by AI.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("📋 **Smart Summary**\n\nAI-powered 4-sentence summaries that capture only what matters")
    with c2:
        st.info("📊 **Analytics Dashboard**\n\nSpeaker breakdown, topic trends and sentiment timeline")
    with c3:
        st.info("💬 **Ask Questions**\n\nRAG-powered chat to query your transcript instantly")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("👤 **My Insights**\n\nPersonal talk time, tasks assigned and your report card")
    with c2:
        st.info("✉️ **Email Generator**\n\nRole-based follow up emails ready in one click")
    with c3:
        st.info("📥 **Export**\n\nDownload PDF reports and CSV action items instantly")

    st.divider()

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div style="text-align:center; padding:20px; background:linear-gradient(135deg,rgba(83,74,183,0.1),rgba(29,158,117,0.1)); border-radius:12px; border:0.5px solid rgba(83,74,183,0.3);">
            <p style="font-size:16px; margin-bottom:8px;">👈 Select <b>📋 Analyze Meeting</b> from the sidebar to get started!</p>
            <p style="font-size:12px; color:gray;">Paste any meeting transcript and get insights in seconds</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:32px; color:gray; font-size:11px;">
        Built with LangChain · Groq · FAISS · FastAPI · MLflow · Streamlit
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
# PAGE 1 — Analyze Meeting
# ══════════════════════════════════════════
elif page == "📋 Analyze Meeting":
    st.title("📋 Analyze Your Meeting")
    st.caption("Paste a transcript and get instant AI-powered insights")
    st.divider()

    transcript = st.text_area(
        "Meeting Transcript",
        placeholder="Paste your meeting transcript here...",
        height=300
    )

    if st.button("✨ Analyze Meeting", type="primary", use_container_width=True):
        if not transcript.strip():
            st.error("Please paste a transcript first!")
        else:
            with st.spinner("Analyzing your meeting... this may take 15-20 seconds"):
                try:
                    r1 = requests.post(f"{API_URL}/summarize", json={"transcript": transcript})
                    r2 = requests.post(f"{API_URL}/analyze", json={"transcript": transcript})
                    r3 = requests.post(f"{API_URL}/score", json={"transcript": transcript})

                    if r1.status_code == 200:
                        d = r1.json()
                        st.session_state["summary"] = d["summary"]
                        st.session_state["action_items"] = d["action_items"]
                        st.session_state["transcript"] = transcript
                        st.session_state["transcript_loaded"] = True
                    if r2.status_code == 200:
                        st.session_state["analytics"] = r2.json()
                    if r3.status_code == 200:
                        st.session_state["score"] = r3.json()

                    st.success("✅ Meeting analyzed successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Could not connect to API: {e}")

    if st.session_state.get("transcript_loaded"):
        st.divider()

        if "score" in st.session_state:
            s = st.session_state["score"]
            score = s.get("score", 0)
            emoji = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
            col1, col2, col3 = st.columns(3)
            col1.metric("Meeting Score", f"{emoji} {score}/10")
            col2.metric("Decisions Made", s.get("decisions_made", 0))
            col3.metric("Overall Sentiment",
                st.session_state.get("analytics", {}).get("overall_sentiment", "N/A").capitalize())
            st.caption(f"**Verdict:** {s.get('reason', '')}")

            risks = s.get("risks", [])
            if risks:
                with st.expander("⚠️ Risks & Blockers"):
                    for r in risks:
                        st.warning(r)

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📝 Summary")
            st.write(st.session_state.get("summary", ""))

        with col2:
            st.subheader("✅ Action Items")
            items = st.session_state.get("action_items", "")
            for line in items.strip().split('\n'):
                if line.strip():
                    st.checkbox(line.strip(), key=f"cb_{line[:30]}")

# ══════════════════════════════════════════
# PAGE 2 — Analytics Dashboard
# ══════════════════════════════════════════
elif page == "📊 Analytics Dashboard":
    st.title("📊 Analytics Dashboard")
    st.divider()

    if "analytics" not in st.session_state:
        st.warning("Please analyze a meeting first.")
    else:
        a = st.session_state["analytics"]
        speakers = a.get("speakers", [])
        topics = a.get("topics", [])
        timeline = a.get("sentiment_timeline", [])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Sentiment", a.get("overall_sentiment", "").capitalize())
        c2.metric("Score", f"{a.get('sentiment_score', 0)}/100")
        c3.metric("Speakers", len(speakers))
        c4.metric("Topics", len(topics))

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if speakers:
                df = pd.DataFrame(speakers)
                fig = px.pie(df, values="lines", names="name",
                    title="🎤 Talk Time by Speaker",
                    color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if topics:
                df2 = pd.DataFrame(topics)
                fig2 = px.bar(df2, x="mentions", y="topic",
                    orientation='h', title="💡 Key Topics",
                    color="mentions", color_continuous_scale="Blues")
                st.plotly_chart(fig2, use_container_width=True)

        if timeline:
            df3 = pd.DataFrame(timeline)
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df3["segment"], y=df3["sentiment_score"],
                mode='lines+markers',
                line=dict(color='#4A90E2', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(74,144,226,0.1)'
            ))
            fig3.update_layout(
                title="📈 Sentiment Timeline",
                yaxis_title="Sentiment Score",
                yaxis_range=[0, 100]
            )
            st.plotly_chart(fig3, use_container_width=True)

        if speakers:
            st.subheader("👥 Speaker Details")
            df4 = pd.DataFrame(speakers)
            df4.columns = ["Speaker", "Lines", "Sentiment"]
            st.dataframe(df4, use_container_width=True)

# ══════════════════════════════════════════
# PAGE 3 — Ask Questions
# ══════════════════════════════════════════
elif page == "💬 Ask Questions":
    st.title("💬 Ask Questions")
    st.divider()

    if not st.session_state.get("transcript_loaded"):
        st.warning("Please analyze a meeting first.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        for chat in st.session_state["chat_history"]:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])

        question = st.chat_input("Ask anything about the meeting...")
        if question:
            with st.spinner("Finding answer..."):
                try:
                    res = requests.post(f"{API_URL}/ask", json={"question": question})
                    if res.status_code == 200:
                        answer = res.json()["answer"]
                        st.session_state["chat_history"].append({
                            "question": question, "answer": answer
                        })
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ══════════════════════════════════════════
# PAGE 4 — Export
# ══════════════════════════════════════════
elif page == "📥 Export":
    st.title("📥 Export Results")
    st.divider()

    if not st.session_state.get("transcript_loaded"):
        st.warning("Please analyze a meeting first.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📄 PDF Report")
            pdf = generate_pdf(
                st.session_state.get("summary", ""),
                st.session_state.get("action_items", "")
            )
            st.download_button("⬇️ Download PDF", data=pdf,
                file_name="meeting_summary.pdf", mime="application/pdf",
                use_container_width=True)

        with col2:
            st.subheader("📊 CSV Action Items")
            csv_data = generate_csv(st.session_state.get("action_items", ""))
            st.download_button("⬇️ Download CSV", data=csv_data,
                file_name="action_items.csv", mime="text/csv",
                use_container_width=True)

        with col3:
            st.subheader("✉️ Follow Up Email")
            st.caption("Generate in the Email Generator tab →")

# ══════════════════════════════════════════
# PAGE 5 — Email Generator
# ══════════════════════════════════════════
elif page == "✉️ Email Generator":
    st.title("✉️ Follow Up Email Generator")
    st.caption("Generate a professional follow up email from your meeting")
    st.divider()

    if not st.session_state.get("transcript_loaded"):
        st.warning("Please analyze a meeting first.")
    else:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("⚙️ Email Settings")
            sender_name = st.text_input("Your Name", placeholder="e.g. John Smith")
            sender_role = st.text_input("Your Role", placeholder="e.g. CEO, Engineering Lead")
            recipients = st.text_input("Recipients", placeholder="e.g. All Meeting Attendees")
            tone = st.selectbox("Email Tone", [
                "Professional", "Friendly", "Formal", "Concise"
            ])

            st.divider()
            st.caption("📋 Email will be based on:")
            st.caption("✅ Meeting summary already analyzed")
            st.caption("✅ Action items already extracted")

            if st.button("✉️ Generate Email", type="primary", use_container_width=True):
                if not sender_name.strip():
                    st.error("Please enter your name!")
                else:
                    with st.spinner("Writing your email..."):
                        try:
                            res = requests.post(
                                f"{API_URL}/email",
                                json={
                                    "summary": st.session_state.get("summary", ""),
                                    "action_items": st.session_state.get("action_items", ""),
                                    "sender_name": sender_name,
                                    "sender_role": sender_role or "Team Member",
                                    "recipients": recipients or "Team",
                                    "tone": tone
                                }
                            )
                            if res.status_code == 200:
                                st.session_state["email"] = res.json()["email"]
                                st.success("✅ Email generated!")
                            else:
                                st.error(f"Error: {res.text}")
                        except Exception as e:
                            st.error(f"Could not connect to API: {e}")

        with col2:
            st.subheader("📧 Generated Email")
            if "email" in st.session_state:
                st.text_area(
                    "Email Content",
                    value=st.session_state["email"],
                    height=400,
                    label_visibility="collapsed"
                )
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        "⬇️ Download Email",
                        data=st.session_state["email"],
                        file_name="followup_email.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col_b:
                    if st.button("🗑️ Clear", use_container_width=True):
                        del st.session_state["email"]
                        st.rerun()
            else:
                st.info("Your generated email will appear here.")

# ══════════════════════════════════════════
# PAGE 6 — My Insights
# ══════════════════════════════════════════
elif page == "👤 My Insights":
    st.title("👤 My Meeting Insights")
    st.caption("Enter your name to see your personal meeting analytics")
    st.divider()

    if not st.session_state.get("transcript_loaded"):
        st.warning("Please analyze a meeting first.")
    else:
        user_name = st.text_input(
            "Your Name",
            placeholder="e.g. John, Sarah, Mike...",
            help="Enter your first name as it appears in the transcript"
        )

        if user_name.strip():
            transcript = st.session_state.get("transcript", "")
            lines = transcript.strip().split('\n')

            user_lines = []
            for line in lines:
                if ':' in line:
                    speaker = line.split(':')[0].strip().lower()
                    if user_name.lower() in speaker:
                        content = ':'.join(line.split(':')[1:]).strip()
                        if content:
                            user_lines.append(content)

            total_lines = sum(1 for l in lines if ':' in l and l.split(':')[1].strip())

            if not user_lines:
                st.error(f"Couldn't find '{user_name}' in the transcript. Check your name matches.")
            else:
                talk_pct = round(len(user_lines) / total_lines * 100) if total_lines > 0 else 0
                questions = sum(1 for l in user_lines if '?' in l)

                analytics = st.session_state.get("analytics", {})
                speakers = analytics.get("speakers", [])
                user_sentiment = "neutral"
                for s in speakers:
                    if user_name.lower() in s.get("name", "").lower():
                        user_sentiment = s.get("sentiment", "neutral")
                        break

                sentiment_emoji = "🟢" if user_sentiment == "positive" else "🔴" if user_sentiment == "negative" else "🟡"

                action_items = st.session_state.get("action_items", "")
                user_tasks = [
                    line.strip() for line in action_items.split('\n')
                    if line.strip() and user_name.lower() in line.lower()
                ]

                st.divider()

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Lines Spoken", len(user_lines))
                c2.metric("Talk Time", f"{talk_pct}%")
                c3.metric("Questions Asked", questions)
                c4.metric("Tasks Assigned", len(user_tasks))

                st.divider()
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("😊 Your Sentiment")
                    st.markdown(f"**{sentiment_emoji} {user_sentiment.capitalize()}**")
                    st.caption("Based on your contributions during the meeting")

                    st.subheader("🎤 Your Talk Time")
                    fig = px.pie(
                        values=[talk_pct, 100 - talk_pct],
                        names=[user_name, "Others"],
                        color_discrete_sequence=["#4A90E2", "#E8E8E8"]
                    )
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("✅ Your Action Items")
                    if user_tasks:
                        for task in user_tasks:
                            st.checkbox(task, key=f"my_task_{task[:20]}")
                    else:
                        st.info("No action items assigned to you.")

                    st.subheader("🏆 Your Report Card")
                    if talk_pct > 30:
                        participation = "🌟 Highly Active"
                    elif talk_pct > 15:
                        participation = "✅ Active Participant"
                    elif talk_pct > 5:
                        participation = "👀 Moderate Participant"
                    else:
                        participation = "🤫 Low Participation"

                    st.markdown(f"**Participation:** {participation}")
                    st.markdown(f"**Sentiment:** {sentiment_emoji} {user_sentiment.capitalize()}")
                    st.markdown(f"**Questions Asked:** {'🙋 Engaged' if questions > 1 else '📝 Listener'}")
                    st.markdown(f"**Tasks Assigned:** {'📋 Accountable' if user_tasks else '🆓 No Tasks'}")

                st.divider()
                st.subheader("💬 Your Contributions")
                for i, line in enumerate(user_lines[:5]):
                    st.markdown(f"> {line}")
                if len(user_lines) > 5:
                    with st.expander(f"Show {len(user_lines) - 5} more..."):
                        for line in user_lines[5:]:
                            st.markdown(f"> {line}")