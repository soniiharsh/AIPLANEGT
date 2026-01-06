import streamlit as st
from multimodal.ocr_processor import OCRProcessor
from multimodal.asr_processor import ASRProcessor
from agents.parser_agent import ParserAgent
from agents.solver_agent import SolverAgent
from agents.verifier_agent import VerifierAgent
from rag.knowledge_base import KnowledgeBase
from memory.solution_memory import SolutionMemory
from config.settings import Config

# Initialize
st.set_page_config(page_title="Math Mentor", page_icon="🧮", layout="wide")

@st.cache_resource
def init_system():
    """Initialize all components"""
    config = Config()
    
    # RAG
    kb = KnowledgeBase(
        config.KNOWLEDGE_BASE_PATH,
        config.EMBEDDING_MODEL
    )
    kb.build()
    
    # Memory
    memory = SolutionMemory(config.MEMORY_DB_PATH)
    
    # Processors
    ocr = OCRProcessor()
    asr = ASRProcessor()
    
    return config, kb, memory, ocr, asr

config, kb, memory, ocr, asr = init_system()

# UI
st.title("🧮 Math Mentor")
st.caption("Multimodal AI Math Tutor with RAG + Agents + HITL")

# Sidebar
with st.sidebar:
    st.header("Input Mode")
    input_mode = st.radio(
        "Choose input type:",
        ["Text", "Image", "Audio"]
    )

# Main area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input")
    
    if input_mode == "Text":
        user_input = st.text_area(
            "Enter math problem:",
            height=150,
            placeholder="e.g., A coin is tossed 5 times..."
        )
        
    elif input_mode == "Image":
        uploaded_file = st.file_uploader(
            "Upload image", 
            type=["jpg", "png"]
        )
        if uploaded_file:
            st.image(uploaded_file)
            if st.button("Extract Text"):
                with st.spinner("Processing OCR..."):
                    result = ocr.process_image(uploaded_file)
                    st.session_state.extracted = result
                    
                    if result["needs_review"]:
                        st.warning(
                            f"Low confidence ({result['confidence']:.2f}). "
                            "Please review extracted text."
                        )
                    
                    user_input = st.text_area(
                        "Extracted text (edit if needed):",
                        value=result["text"],
                        height=150
                    )
    
    elif input_mode == "Audio":
        audio_file = st.file_uploader(
            "Upload audio", 
            type=["mp3", "wav", "m4a"]
        )
        if audio_file and st.button("Transcribe"):
            with st.spinner("Transcribing..."):
                result = asr.process_audio(audio_file)
                user_input = st.text_area(
                    "Transcript:",
                    value=result["text"],
                    height=150
                )
    
    if st.button("Solve", type="primary"):
        if 'user_input' in locals() and user_input:
            st.session_state.solving = True

with col2:
    st.header("Solution")
    
    if st.session_state.get("solving"):
        # Agent execution trace
        with st.status("Processing...", expanded=True) as status:
            # Parser
            st.write("🔍 Parser Agent: Structuring problem...")
            parser = ParserAgent(config.ANTHROPIC_API_KEY, config.LLM_MODEL)
            parsed = parser.parse(user_input)
            st.json(parsed)
            
            if parsed["needs_clarification"]:
                st.error(f"⚠️ Needs clarification: {parsed['clarification_reason']}")
                status.update(label="Needs clarification", state="error")
                st.stop()
            
            # Solver
            st.write("🧮 Solver Agent: Computing solution...")
            solver = SolverAgent(client, config.LLM_MODEL, kb)
            solution = solver.solve(parsed)
            
            # Verifier
            st.write("✅ Verifier Agent: Checking correctness...")
            verifier = VerifierAgent(client, config.LLM_MODEL)
            verification = verifier.verify(parsed, solution)
            
            status.update(label="Complete!", state="complete")
        
        # Display results
        st.subheader("Answer")
        st.success(solution["solution"])
        
        st.subheader("Retrieved Context")
        for doc in solution["context_used"]:
            with st.expander(f"📄 {doc['source']}"):
                st.text(doc["content"])
        
        st.subheader("Verification")
        if verification["is_correct"]:
            st.success(f"✅ Verified (Confidence: {verification['confidence']:.2%})")
        else:
            st.error("❌ Issues detected:")
            for issue in verification["issues"]:
                st.write(f"- {issue}")
        
        # HITL
        if verification["needs_human_review"]:
            st.warning("🔍 This solution needs human review")
            feedback = st.text_area("Provide corrections:")
            if st.button("Submit Feedback"):
                memory.store({
                    "input_type": input_mode.lower(),
                    "raw_input": user_input,
                    "parsed_problem": parsed,
                    "solution": solution,
                    "verification": verification,
                    "user_feedback": feedback,
                    "is_correct": False
                })
                st.success("Feedback stored!")
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Correct"):
                    memory.store({
                        "input_type": input_mode.lower(),
                        "raw_input": user_input,
                        "parsed_problem": parsed,
                        "solution": solution,
                        "verification": verification,
                        "is_correct": True
                    })
                    st.success("Thanks for the feedback!")
            
            with col_b:
                if st.button("❌ Incorrect"):
                    st.session_state.needs_feedback = True