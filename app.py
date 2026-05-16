import streamlit as st
from groq import Groq

# ✅ Page config
st.set_page_config(page_title="AI Study Buddy", page_icon="🤖")

# ✅ App title
st.title("🤖 AI Study Buddy")
st.caption("Your personal AI-powered learning companion!")

# ✅ Sidebar - API key input
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter your Groq API Key", type="password")
    st.markdown("Get your free key at [console.groq.com](https://console.groq.com)")
    st.divider()
    st.metric("✅ Correct", st.session_state.get("correct", 0))
    st.metric("❌ Wrong", st.session_state.get("wrong", 0))

# ✅ Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """You are a friendly AI Study Buddy.
When a user gives you a topic:
1. Explain it simply like they're 15 years old
2. Give a real-life example
3. Then offer a quiz

When quizzing:
- Ask ONE multiple choice question (A/B/C/D)
- Check the answer and say if Correct! or Incorrect!
- Keep score encouraging!"""}
    ]
if "correct" not in st.session_state:
    st.session_state.correct = 0
if "wrong" not in st.session_state:
    st.session_state.wrong = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ✅ Chat input
if prompt := st.chat_input("Ask me any topic or say YES for a quiz!"):
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar!")
        st.stop()

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get AI response
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=st.session_state.messages
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # ✅ Auto score tracking
    if any(w in reply.lower() for w in ["correct!", "that's right", "well done", "great job"]):
        st.session_state.correct += 1
    elif any(w in reply.lower() for w in ["incorrect", "not quite", "wrong", "actually"]):
        st.session_state.wrong += 1

    # Show AI response
    with st.chat_message("assistant"):
        st.markdown(reply)


