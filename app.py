import streamlit as st
from groq import Groq
import PyPDF2
import io

# ✅ Page config
st.set_page_config(page_title="AI Study Buddy", page_icon="🤖", layout="wide")

# ✅ Custom CSS for better UI
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; margin: 5px 0; }
    .stSidebar { background-color: #1a1a2e; }
    h1 { color: #00d4ff; }
</style>
""", unsafe_allow_html=True)

# ✅ App title
st.title("🤖 AI Study Buddy")
st.caption("Your personal AI-powered learning companion!")

# ✅ Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.secrets.get("GROQ_API_KEY", None)
    st.divider()
    st.markdown("---")
    st.markdown("👩‍💻 **Made by Khushi Pal**")

    # 🌐 Language selector
    language = st.selectbox("🌐 Response Language", 
        ["English", "Hindi", "Hinglish", "Spanish", "French"])
    st.divider()

    # 📁 PDF Upload
    st.subheader("📁 Upload Your Notes")
    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
    if uploaded_file:
        st.success("✅ Notes uploaded!")
    st.divider()

    # 📊 Score
    st.subheader("📊 Your Score")
    st.metric("✅ Correct", st.session_state.get("correct", 0))
    st.metric("❌ Wrong", st.session_state.get("wrong", 0))
    st.divider()

    # 📜 Topic History
    st.subheader("📜 Topics Studied")
    if "topics" in st.session_state and st.session_state.topics:
        for topic in st.session_state.topics[-5:]:
            st.write(f"• {topic}")
    else:
        st.write("No topics yet!")

    if st.button("🔄 Reset Everything"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ✅ Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "correct" not in st.session_state:
    st.session_state.correct = 0
if "wrong" not in st.session_state:
    st.session_state.wrong = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "topics" not in st.session_state:
    st.session_state.topics = []
if "note_content" not in st.session_state:
    st.session_state.note_content = ""

# ✅ Extract text from uploaded file
if uploaded_file and not st.session_state.note_content:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        st.session_state.note_content = text[:3000]  # limit to 3000 chars
    else:
        st.session_state.note_content = uploaded_file.read().decode("utf-8")[:3000]

# ✅ System prompt with language + notes context
def get_system_prompt():
    note_context = ""
    if st.session_state.note_content:
        note_context = f"\n\nThe student has uploaded these notes — use them to answer and quiz:\n{st.session_state.note_content}"

    return f"""You are a friendly AI Study Buddy. Always respond in {language}.
When a user gives you a topic:
1. Explain it simply like they're 15 years old
2. Give a real-life example  
3. Offer a quiz

When quizzing:
- Ask ONE multiple choice question (A/B/C/D)
- Check the answer, say Correct! or Incorrect! with explanation
- Be encouraging!
{note_context}"""

# ✅ Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ✅ Chat input
if prompt := st.chat_input("Ask me any topic, upload notes, or say YES for a quiz!"):
    if not api_key:
        st.warning("⚠️ API key not configured. Please contact the app owner!")
        st.stop()

    # Track topics
    if len(prompt) > 5 and "yes" not in prompt.lower():
        st.session_state.topics.append(prompt[:30])

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Build messages with system prompt
    all_messages = [{"role": "system", "content": get_system_prompt()}] + \
                   st.session_state.chat_history

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=all_messages
    )
    reply = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # ✅ Auto score tracking
    if any(w in reply.lower() for w in ["correct!", "that's right", "well done", "great job"]):
        st.session_state.correct += 1
    elif any(w in reply.lower() for w in ["incorrect", "not quite", "wrong", "actually"]):
        st.session_state.wrong += 1

    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()
st.markdown("---")
st.markdown("<center>👩‍💻 Made by <b>Khushi Pal</b></center>", unsafe_allow_html=True)