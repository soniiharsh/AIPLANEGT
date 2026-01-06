import streamlit as st
import json
from datetime import datetime

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
st.caption("RAG + Multi-Agent System with HITL and Memory (API-free demo mode)")

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

    st.subheader("📊 System Stats")
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
# Input column
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
        st.info("OCR disabled in demo mode.")
        user_input = st.text_area("Type the problem:", height=150)

    elif input_mode == "Audio (ASR)":
        st.info("ASR disabled in demo mode.")
        user_input = st.text_area("Type the problem:", height=150)

    solve_button = st.button("🚀 Solve Problem", type="primary", use_container_width=True)

# ----------------------------
# Solution column
# ----------------------------
with col2:
    st.header("✨ Solution")

    if solve_button and user_input:
        st.session_state.agent_trace = []

        with st.status("🤖 Processing...", expanded=True):

            # ----------------------------
            # 1. Parser Agent (rule-based)
            # ----------------------------
            st.write("🔍 **Parser Agent**")
            parsed = {
                "problem_text": user_input.strip(),
                "topic": "probability" if "probability" in user_input.lower() else "general",
                "variables": [],
                "needs_clarification": False,
            }
            st.session_state.agent_trace.append(
                {"agent": "Parser", "status": "complete", "data": parsed}
            )

            # ----------------------------
            # 2. Router
            # ----------------------------
            st.write("🎯 **Intent Router**")
            st.session_state.agent_trace.append(
                {"agent": "Router", "status": "complete"}
            )

            # ----------------------------
            # 3. RAG (static demo context)
            # ----------------------------
            st.write("📚 **RAG Retrieval**")
            knowledge_context = """
### Probability Reminder
P(X = k) = C(n, k) · p^k · (1 − p)^(n − k)

Common mistakes:
- Wrong combination formula
- Using incorrect p
"""
            st.session_state.agent_trace.append(
                {"agent": "RAG", "status": "complete"}
            )

            # ----------------------------
            # 4. Solver Agent (deterministic placeholder)
            # ----------------------------
            st.write("🧮 **Solver Agent**")

            solution = f"""
ANSWER:
This is a demo solution.

STEPS:
1. Identify the type of problem.
2. Apply the relevant formula.
3. Substitute values.
4. Compute final result.

NOTE:
This deployment runs without external LLM APIs.
"""

            st.session_state.agent_trace.append(
                {"agent": "Solver", "status": "complete"}
            )

            # ----------------------------
            # 5. Verifier Agent (heuristic)
            # ----------------------------
            st.write("✅ **Verifier Agent**")
            verification = {
                "is_correct": True,
                "confidence": 0.85,
                "issues": [],
                "needs_human_review": False,
            }
            st.session_state.agent_trace.append(
                {"agent": "Verifier", "status": "complete", "data": verification}
            )

        # ----------------------------
        # Output
        # ----------------------------
        st.divider()

        with st.expander("🔍 Agent Execution Trace"):
            for trace in st.session_state.agent_trace:
                st.json(trace)

        with st.expander("📚 Retrieved Knowledge"):
            st.markdown(knowledge_context)

        st.subheader("📊 Solution")
        st.success(f"✅ Verified (Confidence: {verification['confidence']:.0%})")
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
st.caption("Math Mentor | API-free demo mode")
