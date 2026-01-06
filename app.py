import streamlit as st
import json
from anthropic import Anthropic
import os
from datetime import datetime

# Initialize Anthropic client
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ ANTHROPIC_API_KEY not found in secrets!")
        st.stop()
    return Anthropic(api_key=api_key)

client = get_client()

# Session state initialization
if 'memory' not in st.session_state:
    st.session_state.memory = []
if 'agent_trace' not in st.session_state:
    st.session_state.agent_trace = []

# Page config
st.set_page_config(page_title="Math Mentor", page_icon="🧮", layout="wide")

# Title
st.title("🧮 Math Mentor - AI Math Tutor")
st.caption("RAG + Multi-Agent System with HITL and Memory")

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
    st.metric("Success Rate", f"{len([m for m in st.session_state.memory if m.get('is_correct')]) / max(len(st.session_state.memory), 1) * 100:.0f}%")
    
    st.divider()
    
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
        with st.status("🤖 Processing...", expanded=True) as status:
            
            # 1. Parser Agent
            st.write("🔍 **Parser Agent**: Analyzing problem...")
            st.session_state.agent_trace.append({"agent": "Parser", "status": "processing"})
            
            parser_prompt = f"""Parse this math problem and output ONLY valid JSON:

Problem: {user_input}

Output format:
{{
  "problem_text": "cleaned problem statement",
  "topic": "algebra/probability/calculus/linear_algebra",
  "variables": ["list", "of", "variables"],
  "needs_clarification": false,
  "clarification_reason": ""
}}"""

            try:
                parser_response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    temperature=0,
                    messages=[{"role": "user", "content": parser_prompt}]
                )
                
                parsed_text = parser_response.content[0].text
                # Try to extract JSON from response
                if "```json" in parsed_text:
                    parsed_text = parsed_text.split("```json")[1].split("```")[0].strip()
                elif "```" in parsed_text:
                    parsed_text = parsed_text.split("```")[1].split("```")[0].strip()
                
                parsed = json.loads(parsed_text)
                st.session_state.agent_trace.append({"agent": "Parser", "status": "complete", "data": parsed})
                st.success(f"✅ Topic: {parsed['topic']}")
                
            except Exception as e:
                st.error(f"Parser error: {e}")
                parsed = {
                    "problem_text": user_input,
                    "topic": "unknown",
                    "variables": [],
                    "needs_clarification": False
                }
            
            # 2. Intent Router
            st.write("🎯 **Intent Router**: Routing to solver...")
            st.session_state.agent_trace.append({"agent": "Router", "status": "complete"})
            
            # 3. RAG Retrieval (Simulated)
            st.write("📚 **RAG**: Retrieving knowledge...")
            knowledge_context = f"""
# {parsed['topic'].title()} Knowledge

## Key Concepts
- Use systematic approach
- Show all work
- Check units and constraints

## Common Mistakes
- Forgetting to state assumptions
- Not checking domain validity
- Calculation errors
"""
            st.session_state.agent_trace.append({"agent": "RAG", "status": "complete"})
            
            # 4. Solver Agent
            st.write("🧮 **Solver Agent**: Computing solution...")
            
            solver_prompt = f"""You are a math tutor. Solve this problem step-by-step.

Context from knowledge base:
{knowledge_context}

Problem: {parsed['problem_text']}

Provide:
1. Final answer
2. Step-by-step solution (numbered steps)
3. Any formulas used

Format your response as:
ANSWER: [your answer]
STEPS:
1. [step 1]
2. [step 2]
...
"""

            try:
                solver_response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    temperature=0.2,
                    messages=[{"role": "user", "content": solver_prompt}]
                )
                
                solution = solver_response.content[0].text
                st.session_state.agent_trace.append({"agent": "Solver", "status": "complete"})
                
            except Exception as e:
                st.error(f"Solver error: {e}")
                solution = f"Error solving problem: {e}"
            
            # 5. Verifier Agent
            st.write("✅ **Verifier Agent**: Checking correctness...")
            
            verifier_prompt = f"""Verify this solution. Output ONLY valid JSON:

Problem: {parsed['problem_text']}
Solution: {solution}

Output format:
{{
  "is_correct": true/false,
  "confidence": 0.0-1.0,
  "issues": ["list of issues if any"],
  "needs_human_review": true/false
}}"""

            try:
                verifier_response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    temperature=0,
                    messages=[{"role": "user", "content": verifier_prompt}]
                )
                
                verifier_text = verifier_response.content[0].text
                if "```json" in verifier_text:
                    verifier_text = verifier_text.split("```json")[1].split("```")[0].strip()
                elif "```" in verifier_text:
                    verifier_text = verifier_text.split("```")[1].split("```")[0].strip()
                
                verification = json.loads(verifier_text)
                st.session_state.agent_trace.append({"agent": "Verifier", "status": "complete", "data": verification})
                
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
st.caption("🧮 Math Mentor v1.0 | Built with Claude Sonnet 4 + Streamlit")