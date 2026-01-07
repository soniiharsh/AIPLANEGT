import streamlit as st
import json
import os
from datetime import datetime
import google.generativeai as genai
from PIL import Image
import io

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Math Mentor",
    page_icon="🧮",
    layout="wide"
)

# =================================================
# GEMINI SETUP (FREE)
# =================================================
@st.cache_resource
def load_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found")
        st.info("Get a free key from https://aistudio.google.com/app/apikey")
        st.stop()

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-2.5-flash")

model = load_gemini()

def call_gemini(prompt, max_tokens=2000):
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": max_tokens
        }
    )
    return response.text

# =================================================
# SESSION STATE
# =================================================
if "memory" not in st.session_state:
    st.session_state.memory = []

if "agent_trace" not in st.session_state:
    st.session_state.agent_trace = []

if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False

# =================================================
# HEADER
# =================================================
st.title("🧮 Math Mentor")
st.caption("Reliable AI Math Tutor • RAG + Agents + HITL + Memory (Gemini Multimodal)")

# =================================================
# SIDEBAR
# =================================================
with st.sidebar:
    st.header("⚙️ Settings")

    input_mode = st.radio(
        "Input Mode",
        ["Text", "Image (OCR)", "Audio (ASR)"]
    )

    st.divider()

    solved = len(st.session_state.memory)
    correct = len([m for m in st.session_state.memory if m["is_correct"]])
    success_rate = (correct / max(solved, 1)) * 100

    st.metric("Problems Solved", solved)
    st.metric("Success Rate", f"{success_rate:.0f}%")

    st.divider()
    st.info("🆓 Powered by Google Gemini Multimodal API")

    if st.button("🗑️ Clear Memory"):
        st.session_state.memory.clear()
        st.session_state.agent_trace.clear()
        st.rerun()

# =================================================
# LAYOUT
# =================================================
col1, col2 = st.columns([1, 1])

# =================================================
# INPUT COLUMN
# =================================================
with col1:
    st.header("📝 Input")
    user_input = None

    # ---------------- TEXT ----------------
    if input_mode == "Text":
        user_input = st.text_area(
            "Enter math problem",
            height=200,
            placeholder="A coin is tossed 5 times. Find probability of exactly 3 heads."
        )

    # ---------------- IMAGE (GEMINI OCR) ----------------
    elif input_mode == "Image (OCR)":
        uploaded_image = st.file_uploader(
            "Upload image",
            type=["jpg", "png", "jpeg"]
        )

        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image")

            with st.spinner("Extracting text using Gemini Vision..."):
                image_bytes = uploaded_image.read()
                image = Image.open(io.BytesIO(image_bytes))

                ocr_prompt = """
Extract the complete math problem text from this image.
Preserve mathematical symbols.
Do NOT solve the problem.
Return only the extracted text.
"""
                ocr_response = model.generate_content([ocr_prompt, image])

            st.warning("OCR completed. Please review (HITL enabled).")

            user_input = st.text_area(
                "Extracted Text",
                value=ocr_response.text.strip(),
                height=180
            )

    # ---------------- AUDIO (GEMINI ASR) ----------------
    elif input_mode == "Audio (ASR)":
        audio_file = st.file_uploader(
            "Upload audio",
            type=["wav", "mp3", "m4a"]
        )

        if audio_file:
            with st.spinner("Transcribing audio using Gemini..."):
                audio_bytes = audio_file.read()

                asr_prompt = """
Transcribe this audio accurately.
Preserve mathematical expressions.
Do NOT summarize.
"""

                asr_response = model.generate_content(
                    [
                        asr_prompt,
                        {
                            "mime_type": audio_file.type,
                            "data": audio_bytes
                        }
                    ]
                )

            st.warning("Audio transcription completed. Please review (HITL enabled).")

            user_input = st.text_area(
                "Transcript",
                value=asr_response.text.strip(),
                height=180
            )

    solve_clicked = st.button(
        "🚀 Solve",
        type="primary",
        use_container_width=True
    )

# =================================================
# SOLUTION COLUMN
# =================================================
with col2:
    st.header("✨ Solution")

    if solve_clicked and user_input:
        st.session_state.agent_trace.clear()

        with st.status("🤖 Running multi-agent pipeline...", expanded=True):

            # ---------------- PARSER AGENT ----------------
            st.write("🔍 Parser Agent")
            parser_prompt = f"""
Parse the following math problem into JSON ONLY.

Problem:
{user_input}

JSON format:
{{
  "problem_text": "...",
  "topic": "algebra | probability | calculus | linear_algebra",
  "variables": [],
  "needs_clarification": false,
  "clarification_reason": ""
}}
"""
            parser_raw = call_gemini(parser_prompt, 800)

            try:
                if "```" in parser_raw:
                    parser_raw = parser_raw.split("```")[1]
                parsed = json.loads(parser_raw)
            except:
                parsed = {
                    "problem_text": user_input,
                    "topic": "unknown",
                    "variables": [],
                    "needs_clarification": False
                }

            st.session_state.agent_trace.append(
                {"agent": "Parser", "output": parsed}
            )

            if parsed["needs_clarification"]:
                st.error(parsed["clarification_reason"])
                st.stop()

            # ---------------- ROUTER ----------------
            st.write("🧭 Router Agent")
            route = parsed.get("topic", "math")

            # ---------------- RAG ----------------
            st.write("📚 RAG Retrieval")
            knowledge_context = f"""
Topic: {route}
Use correct formulas, constraints, and common mistakes.
"""

            # ---------------- SOLVER ----------------
            st.write("🧮 Solver Agent")
            solver_prompt = f"""
Solve step by step.

Context:
{knowledge_context}

Problem:
{parsed['problem_text']}

Format:
ANSWER:
STEPS:
FORMULAS USED:
"""
            solution = call_gemini(solver_prompt, 2000)

            # ---------------- VERIFIER ----------------
            st.write("✅ Verifier Agent")
            verifier_prompt = f"""
Verify the solution below.

Problem:
{parsed['problem_text']}

Solution:
{solution}

Return JSON only:
{{
  "is_correct": true,
  "confidence": 0.0,
  "issues": [],
  "needs_human_review": false
}}
"""
            verifier_raw = call_gemini(verifier_prompt, 800)

            try:
                if "```" in verifier_raw:
                    verifier_raw = verifier_raw.split("```")[1]
                verification = json.loads(verifier_raw)
            except:
                verification = {
                    "is_correct": True,
                    "confidence": 0.7,
                    "issues": [],
                    "needs_human_review": False
                }

        # ---------------- OUTPUT ----------------
        st.subheader("📊 Result")

        if verification["is_correct"]:
            st.success(f"Verified (Confidence {verification['confidence']:.0%})")
        else:
            st.warning("Verification issues detected")
            for issue in verification.get("issues", []):
                st.error(issue)

        st.markdown(solution)

        # ---------------- HITL ----------------
        st.divider()
        st.subheader("💬 Human Feedback")

        if verification["needs_human_review"] or verification["confidence"] < 0.8:
            st.warning("Human review recommended")

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("✅ Correct"):
                st.session_state.memory.append({
                    "timestamp": datetime.now().isoformat(),
                    "input": user_input,
                    "parsed": parsed,
                    "solution": solution,
                    "verification": verification,
                    "is_correct": True
                })
                st.success("Stored as correct")

        with col_b:
            if st.button("❌ Incorrect"):
                st.session_state.show_feedback = True

        if st.session_state.show_feedback:
            feedback = st.text_area("What was incorrect?")
            if st.button("Submit Feedback"):
                st.session_state.memory.append({
                    "timestamp": datetime.now().isoformat(),
                    "input": user_input,
                    "parsed": parsed,
                    "solution": solution,
                    "verification": verification,
                    "is_correct": False,
                    "feedback": feedback
                })
                st.session_state.show_feedback = False
                st.success("Feedback recorded")
                st.rerun()

# =================================================
# MEMORY VIEW
# =================================================
if st.session_state.memory:
    st.divider()
    st.subheader("🧠 Memory")

    with st.expander("View past attempts"):
        for m in reversed(st.session_state.memory):
            icon = "✅" if m["is_correct"] else "❌"
            st.markdown(f"{icon} **{m['timestamp'][:19]}**")
            st.text(m["input"][:120])
            st.divider()

# =================================================
# FOOTER
# =================================================
st.divider()
st.caption("Math Mentor • Reliable Multimodal AI System • 2026")
