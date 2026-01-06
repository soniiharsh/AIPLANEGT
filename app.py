import streamlit as st
import json
import os
from datetime import datetime
from groq import Groq

# ----------------------------
# Groq client
# ----------------------------
@st.cache_resource
def get_client():
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("⚠️ GROQ_API_KEY not found in Streamlit secrets!")
        st.stop()
    return Groq(api_key=api_key)

client = get_client()

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Math Mentor", page_icon="🧮", layout="wide")

# ----------------------------
# Session state
# ----------------------------
if "memory" not in st.session_state:
    st.session_state.memory = []

if "agent_trace" not in st.session_state:
    st.session_state.agent_trace = []

# ----------------------------
# Title
# ----------------------------
st.title("🧮 Math Mentor - AI Math Tutor")
st.caption("RAG + Multi-Agent System with HITL and Memory (Groq)")

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    input_mode = st.radio(
        "Input Mode:",
        ["Text", "Image (OCR)", "Audio (ASR)"],
    )

    st.divider()

    solved = len(st.session_state.memory)
    correct = len([m for m in st.session_state.memory if m.get("is_correct")])
    success_rate = (correct / max(solved, 1)) * 100

    st.metric("Problems Solved", solved)
    st.metric("Success Rate", f"{success_rate:.0f}%")

    st.divider()

    if st.button("🗑️ Clear Memory"):
        st.session_state.memory = []
        st.session_state.agent_trace = []
        st.rerun()

# ----------------------------
# Layout
# ----------------------------
col1, col2 = st.columns([1, 1])

# ----------------------------
# Input
# ----------------------------
with col1:
    st.header("📝 Input")

    user_input = None

    if input_mode == "Text":
        user_input = st.text_area(
            "Enter your math problem:",
            height=200,
            placeholder="e.g., A coin is tossed 5 times. What is the probability of getting exactly 3 heads?",
        )

    elif input_mode == "Image (OCR)":
        st.info("OCR disabled in cloud demo.")
        user_input = st.text_area("Type the problem:", height=150)

    elif input_mode == "Audio (ASR)":
        st.info("ASR disabled in cloud demo.")
        user_input = st.text_area("Type the problem:", height=150)

    solve_button = st.button("🚀 Solve Problem", type="primary", use_container_width=True)

# ----------------------------
# Solution
# ----------------------------
with col2:
    st.header("✨ Solution")

    if solve_button and user_input:
        st.session_state.agent_trace = []

        with st.status("🤖 Processing...", expanded=True):

            # ----------------------------
            # 1. Parser Agent
            # ----------------------------
            st.write("🔍 **Parser Agent**")

            parser_prompt = f"""
Parse the following math problem and return ONLY valid JSON.

Problem:
{user_input}

Format:
{{
  "problem_text": "...",
  "topic": "arithmetic/algebra/probability/calculus",
  "variables": [],
  "needs_clarification": false
}}
"""

            parser_response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": parser_prompt}],
                temperature=0
            )

            parsed = json.loads(parser_response.choices[0].message.content)
            st.session_state.agent_trace.append(
                {"agent": "Parser", "status": "complete", "data": parsed}
            )

            # ----------------------------
            # 2. RAG (lightweight demo)
            # ----------------------------
            st.write("📚 **RAG Retrieval**")

            knowledge_context = """
Basic Arithmetic:
Total Cost = Cost per item × Number of items
"""
            st.session_state.agent_trace.append(
                {"agent": "RAG", "status": "complete"}
            )

            # ----------------------------
            # 3. Solver Agent
            # ----------------------------
            st.write("🧮 **Solver Agent**")

            solver_prompt = f"""
Use the context below to solve step-by-step.

Context:
{knowledge_context}

Problem:
{parsed["problem_text"]}

Return:
ANSWER:
STEPS:
"""

            solver_response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": solver_prompt}],
                temperature=0.2
            )

            solution = solver_response.choices[0].message.content
            st.session_state.agent_trace.append(
                {"agent": "Solver", "status": "complete"}
            )

            # ----------------------------
            # 4. Verifier Agent
            # ----------------------------
            st.write("✅ **Verifier Agent**")

            verifier_prompt = f"""
Verify the solution below. Output ONLY valid JSON.

Problem:
{parsed["problem_text"]}

Solution:
{solution}

Format:
{{
  "is_correct": true,
  "confidence": 0.0,
  "issues": [],
  "needs_human_review": false
}}
"""

            verifier_response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": verifier_prompt}],
                temperature=0
            )

            verification = json.loads(
                verifier_response.choices[0].message.content
            )

            st.session_state.agent_trace.append(
                {"agent": "Verifier", "status": "complete", "data": verification}
            )

        # ----------------------------
        # Display
        # ----------------------------
        st.divider()

        with st.expander("🔍 Agent Trace"):
            for trace in st.session_state.agent_trace:
                st.json(trace)

        st.subheader("📊 Solution")

        if verification["is_correct"]:
            st.success(f"✅ Verified ({verification['confidence']:.0%})")
        else:
            st.error("❌ Issues detected")

        st.markdown(solution)

        # ----------------------------
        # HITL
        # ----------------------------
        st.divider()
        st.subheader("💬 Feedback")

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("✅ Correct", use_container_width=True):
                st.session_state.memory.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "input": user_input,
                        "solution": solution,
                        "is_correct": True,
                    }
                )
                st.success("Stored in memory.")

        with col_b:
            if st.button("❌ Incorrect", use_container_width=True):
                feedback = st.text_area("What was wrong?")
                st.session_state.memory.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "input": user_input,
                        "solution": solution,
                        "is_correct": False,
                        "feedback": feedback,
                    }
                )
                st.success("Feedback recorded.")

# ----------------------------
# Memory Viewer
# ----------------------------
if st.session_state.memory:
    st.divider()
    st.subheader("🧠 Solution Memory")

    with st.expander("View past solutions"):
        for mem in reversed(st.session_state.memory):
            st.json(mem)

# ----------------------------
# Footer
# ----------------------------
st.divider()
st.caption("Math Mentor | Groq-powered deployment")
