import streamlit as st
import pandas as pd
import ollama
from utils.pdf_reader import extract_text

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="StudyMate AI Pro",
    page_icon="📚",
    layout="wide"
)

# =========================
# SESSION STATE
# =========================
if "user" not in st.session_state:
    st.session_state.user = None

if "history" not in st.session_state:
    st.session_state.history = {}

if "chat" not in st.session_state:
    st.session_state.chat = []

# =========================
# LOGIN
# =========================
def login():
    st.title("🔐 StudyMate AI Login")

    username = st.text_input("Enter your name")

    if st.button("Login"):
        if username:
            st.session_state.user = username

            if username not in st.session_state.history:
                st.session_state.history[username] = []

            st.rerun()

if not st.session_state.user:
    login()
    st.stop()

user = st.session_state.user

# =========================
# STYLING
# =========================
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

.glass {
    background: rgba(255,255,255,0.08);
    border-radius: 15px;
    padding: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    font-weight: bold;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#4f46e5,#7c3aed);
}
</style>
""", unsafe_allow_html=True)

# =========================
# AI CORE
# =========================
def call_ai(system_prompt, user_prompt):
    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


def ai_summary(text):
    return call_ai(
        "Summarize these notes into concise exam-focused bullet points.",
        text[:4000]
    )


def ai_tutor(text, question):
    return call_ai(
        "Answer only from the provided notes. If the answer is not present, reply 'Not in notes'.",
        f"NOTES:\n{text[:4000]}\n\nQUESTION:\n{question}"
    )


def ai_quiz(text):
    return call_ai(
        "Generate 5 multiple-choice questions with 4 options and provide the correct answer for each.",
        text[:4000]
    )

# =========================
# HEADER
# =========================
st.title("📚 StudyMate AI Pro")
st.caption(f"Welcome {user} 👋 | AI Learning Assistant")

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.title("⚙️ Control Panel")

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

# =========================
# PDF UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "Upload your PDF Notes",
    type=["pdf"]
)

if uploaded_file:

    text = extract_text(uploaded_file)

    st.success("PDF Loaded Successfully 🚀")

    st.write("Characters extracted:", len(text))

    # =========================
    # ANALYTICS
    # =========================
    st.markdown("## 📊 Smart Analytics")

    word_count = len(text.split())
    reading_time = max(1, word_count // 200)

    col1, col2, col3 = st.columns(3)

    col1.metric("Words", word_count)
    col2.metric("Reading Time", f"{reading_time} min")
    col3.metric(
        "Status",
        "🔥 High Quality" if word_count > 1200 else "📘 Medium"
    )

    df = pd.DataFrame({
        "Skill": [
            "Reading",
            "Understanding",
            "Practice",
            "Revision"
        ],
        "Score": [
            85,
            70,
            60,
            90
        ]
    })

    st.bar_chart(df.set_index("Skill"))

    # =========================
    # TABS
    # =========================
    tab1, tab2, tab3 = st.tabs(
        ["📝 Summary", "🎓 Tutor Chat", "❓ Quiz"]
    )

    # =========================
    # SUMMARY
    # =========================
    with tab1:

        st.markdown("### AI Summary")

        if st.button("Generate Summary"):

            with st.spinner("Generating summary..."):

                summary = ai_summary(text)

            st.session_state.history[user].append(
                ("summary", summary)
            )

            st.markdown(
                f"<div class='glass'>{summary}</div>",
                unsafe_allow_html=True
            )

    # =========================
    # TUTOR CHAT
    # =========================
    with tab2:

        st.markdown("### AI Tutor Chat")

        q = st.text_input("Ask your question")

        if st.button("Ask") and q:

            with st.spinner("Thinking..."):

                ans = ai_tutor(text, q)

            st.session_state.chat.append(
                ("user", q)
            )

            st.session_state.chat.append(
                ("ai", ans)
            )

            st.session_state.history[user].append(
                ("chat", q)
            )

        if len(st.session_state.chat) > 20:
            st.session_state.chat = st.session_state.chat[-20:]

        for role, msg in st.session_state.chat:

            if role == "user":

                st.markdown(
                    f"<div class='glass'>🧑‍🎓 {msg}</div>",
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"<div class='glass'>🤖 {msg}</div>",
                    unsafe_allow_html=True
                )

    # =========================
    # QUIZ
    # =========================
    with tab3:

        st.markdown("### AI Quiz Generator")

        if st.button("Generate Quiz"):

            with st.spinner("Generating quiz..."):

                quiz = ai_quiz(text)

            st.markdown(
                f"<div class='glass'>{quiz}</div>",
                unsafe_allow_html=True
            )

else:
    st.info("Upload a PDF to start learning 🚀")

# =========================
# HISTORY
# =========================
st.markdown("---")
st.markdown("## 🧠 User Learning History")

if st.session_state.history.get(user):

    for item in st.session_state.history[user]:
        st.write(item)

else:
    st.write("No history yet — start learning 🚀")

# =========================
# DEMO FLOW
# =========================
st.markdown("---")
st.markdown("## 🏆 Hackathon Demo Flow")

st.code("""
1. Login user
2. Upload PDF
3. Analytics dashboard
4. AI summary
5. Tutor chat
6. Quiz generation
7. History tracking
""")
