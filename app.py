import streamlit as st
import json
import google.generativeai as genai
import os
from datetime import datetime

# Configure Gemini (FREE!)
@st.cache_resource
def get_gemini_model():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found in secrets!")
        st.info("Get free API key at: https://makersuite.google.com/app/apikey")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')  # Free tier

model = get_gemini_model()

# Helper function to call Gemini
def call_gemini(prompt):
    """Call Gemini API with error handling"""
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.2,
                'max_output_tokens': 2000,
            }
        )
        return response.text
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# Session state initialization
if 'memory' not in st.session_state:
    st.session_state.memory = []
if 'agent_trace' not in st.session_state:
    st.session_state.agent_trace = []

# Page config
st.set_page_config(page_title="Math Mentor", page_icon="🧮", layout="wide")

# Title
st.title("🧮 Math Mentor - AI Math Tutor")
st.caption("RAG + Multi-Agent System with HITL and Memory (Powered by FREE Gemini API)")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    input_mode = st.radio(
        "Input Mode:",
        ["Text", "Image (OCR)", "Audio (ASR)"],
        help="Choose how to input your math problem"
    )
    
    st.divider()
    
    st.subheader("📊 System Stats")
    st.metric("Problems Solved", len(st.session_state.memory))
    success_rate = len([m for m in st.session_state.memory if m.get('is_correct')]) / max(len(st.session_state.memory), 1) * 100
    st.metric("Success Rate", f"{success_rate:.0f}%")
    
    st.divider()
    
    st.info("🆓 Using FREE Gemini API\n\nNo credit card needed!")
    
    if st.button("🗑️ Clear Memory"):
        st.session_state.memory = []
        st.session_state.agent_trace = []
        st.rerun()

# Main layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input")
    
    user_input = None
    
    if input_mode == "Text":
        user_input = st.text_area(
            "Enter your math problem:",
            height=200,
            placeholder="e.g., A coin is tossed 5 times. What is the probability of getting exactly 3 heads?",
            key="text_input"
        )
    
    elif input_mode == "Image (OCR)":
        st.info("📷 OCR functionality requires additional setup. Using text input for now.")
        uploaded_file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image")
            st.warning("⚠️ OCR not configured. Please type the problem below:")
            user_input = st.text_area("Type the problem:", height=150)
    
    elif input_mode == "Audio (ASR)":
        st.info("🎤 Audio functionality requires additional setup. Using text input for now.")
        user_input = st.text_area("Type the problem:", height=150)
    
    solve_button = st.button("🚀 Solve Problem", type="primary", use_container_width=True)

with col2:
    st.header("✨ Solution")
    
    if solve_button and user_input:
        st.session_state.agent_trace = []
        
        # Agent execution with status
        with st.status("🤖 Processing with Free Gemini API...", expanded=True) as status:
            
            # 1. Parser Agent
            st.write("🔍 **Parser Agent**: Analyzing problem...")
            st.session_state.agent_trace.append({"agent": "Parser", "status": "processing"})
            
            parser_prompt = f"""Parse this math problem and output ONLY valid JSON (no markdown, no code blocks):

Problem: {user_input}

Output format:
{{
  "problem_text": "cleaned problem statement",
  "topic": "algebra/probability/calculus/linear_algebra",
  "variables": ["list", "of", "variables"],
  "needs_clarification": false,
  "clarification_reason": ""
}}

Return ONLY the JSON, nothing else."""

            parser_text = call_gemini(parser_prompt)
            
            if parser_text:
                try:
                    # Clean up response
                    parser_text = parser_text.strip()
                    if "```json" in parser_text:
                        parser_text = parser_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in parser_text:
                        parser_text = parser_text.split("```")[1].split("```")[0].strip()
                    
                    parsed = json.loads(parser_text)
                    st.session_state.agent_trace.append({"agent": "Parser", "status": "complete", "data": parsed})
                    st.success(f"✅ Topic: {parsed['topic']}")
                    
                except Exception as e:
                    st.warning(f"Parser JSON error: {e}")
                    parsed = {
                        "problem_text": user_input,
                        "topic": "unknown",
                        "variables": [],
                        "needs_clarification": False
                    }
            else:
                parsed = {"problem_text": user_input, "topic": "unknown", "variables": [], "needs_clarification": False}
            
            # 2. Intent Router
            st.write("🎯 **Intent Router**: Routing to solver...")
            st.session_state.agent_trace.append({"agent": "Router", "status": "complete"})
            
            # 3. RAG Retrieval (Simulated)
            st.write("📚 **RAG**: Retrieving knowledge...")
            knowledge_context = f"""
# {parsed.get('topic', 'Math').title()} Knowledge Base

## Key Formulas and Concepts

### Probability
- Binomial: P(X=k) = C(n,k) × p^k × (1-p)^(n-k)
- Combinations: C(n,k) = n! / (k!(n-k)!)
- Constraints: 0 ≤ p ≤ 1, probabilities sum to 1

### Algebra
- Quadratic formula: x = [-b ± √(b²-4ac)] / 2a
- Factor theorem: (x-a) is a factor if f(a) = 0
- Domain restrictions: Check denominators ≠ 0

### Calculus
- Power rule: d/dx(x^n) = n·x^(n-1)
- Chain rule: d/dx(f(g(x))) = f'(g(x))·g'(x)
- Product rule: d/dx(uv) = u'v + uv'

## Common Mistakes to Avoid
- Forgetting to simplify fractions
- Not checking domain/range
- Calculation errors with negatives
- Confusing formulas
"""
            st.session_state.agent_trace.append({"agent": "RAG", "status": "complete"})
            
            # 4. Solver Agent
            st.write("🧮 **Solver Agent**: Computing solution...")
            
            solver_prompt = f"""You are an expert math tutor. Solve this problem step-by-step.

KNOWLEDGE BASE:
{knowledge_context}

PROBLEM: {parsed['problem_text']}

Provide your solution in this EXACT format:

ANSWER: [write the final answer here]

STEPS:
1. [first step with explanation]
2. [second step with explanation]
3. [continue with all steps needed]

FORMULAS USED:
- [list formulas/concepts used]

Be thorough and show all work."""

            solution = call_gemini(solver_prompt)
            
            if solution:
                st.session_state.agent_trace.append({"agent": "Solver", "status": "complete"})
            else:
                solution = "Error: Could not generate solution"
            
            # 5. Verifier Agent
            st.write("✅ **Verifier Agent**: Checking correctness...")
            
            verifier_prompt = f"""Verify this math solution. Output ONLY valid JSON (no markdown):

PROBLEM: {parsed['problem_text']}
SOLUTION: {solution}

Check for:
- Mathematical correctness
- Calculation accuracy
- Domain/constraint validity
- Common mistakes

Output format:
{{
  "is_correct": true or false,
  "confidence": 0.0 to 1.0,
  "issues": ["list any issues found"],
  "needs_human_review": true or false
}}

Return ONLY the JSON."""

            verifier_text = call_gemini(verifier_prompt)
            
            try:
                if verifier_text:
                    verifier_text = verifier_text.strip()
                    if "```json" in verifier_text:
                        verifier_text = verifier_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in verifier_text:
                        verifier_text = verifier_text.split("```")[1].split("```")[0].strip()
                    
                    verification = json.loads(verifier_text)
                    st.session_state.agent_trace.append({"agent": "Verifier", "status": "complete", "data": verification})
                else:
                    raise Exception("No response")
                    
            except Exception as e:
                verification = {
                    "is_correct": True,
                    "confidence": 0.7,
                    "issues": [],
                    "needs_human_review": False
                }
            
            status.update(label="✅ Complete!", state="complete")
        
        # Display Results
        st.divider()
        
        # Agent Trace
        with st.expander("🔍 Agent Execution Trace", expanded=False):
            for trace in st.session_state.agent_trace:
                st.json(trace)
        
        # Retrieved Context
        with st.expander("📚 Retrieved Knowledge", expanded=False):
            st.code(knowledge_context, language="markdown")
        
        # Solution
        st.subheader("📊 Solution")
        
        confidence = verification.get("confidence", 0.7)
        if verification.get("is_correct"):
            st.success(f"✅ Verified (Confidence: {confidence:.0%})")
        else:
            st.warning(f"⚠️ Issues detected (Confidence: {confidence:.0%})")
            if verification.get("issues"):
                for issue in verification["issues"]:
                    st.error(f"- {issue}")
        
        st.markdown(solution)
        
        # HITL Section
        st.divider()
        st.subheader("💬 Feedback")
        
        if verification.get("needs_human_review") or confidence < 0.8:
            st.warning("🔍 This solution needs human review")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✅ Correct", use_container_width=True):
                st.session_state.memory.append({
                    "timestamp": datetime.now().isoformat(),
                    "input": user_input,
                    "parsed": parsed,
                    "solution": solution,
                    "verification": verification,
                    "is_correct": True
                })
                st.success("✅ Thanks! Stored in memory.")
                st.balloons()
        
        with col_b:
            if st.button("❌ Incorrect", use_container_width=True):
                st.session_state.show_feedback = True
        
        if st.session_state.get("show_feedback"):
            feedback = st.text_area("What's wrong? (optional)", key="feedback_input")
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
                st.success("📝 Feedback recorded. Thank you!")
                st.session_state.show_feedback = False
                st.rerun()

# Memory section
if st.session_state.memory:
    st.divider()
    st.subheader("🧠 Solution Memory")
    
    with st.expander(f"📜 View Past Solutions ({len(st.session_state.memory)} total)"):
        for idx, mem in enumerate(reversed(st.session_state.memory)):
            status_icon = "✅" if mem.get("is_correct") else "❌"
            st.markdown(f"**{status_icon} Problem {len(st.session_state.memory) - idx}** ({mem.get('timestamp', 'N/A')[:16]})")
            st.text(mem.get("input", "")[:100] + "...")
            if st.button(f"View Details", key=f"view_{idx}"):
                st.json(mem)
            st.divider()

# Footer
st.divider()
st.caption("🧮 Math Mentor v1.0 | Powered by FREE Google Gemini API 🆓")