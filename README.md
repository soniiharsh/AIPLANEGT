# 🧮 Math Mentor
Reliable Multimodal AI Math Tutor  
(RAG + Multi-Agent System + Human-in-the-Loop + Memory)  
Powered by FREE Google Gemini API

---

## 📌 Project Overview

Math Mentor is an end-to-end AI system designed to reliably solve JEE-level mathematics problems while prioritizing correctness, transparency, and safety.

Unlike basic AI chatbots, this project is built as a reliable AI pipeline combining:
- Multi-agent architecture
- Retrieval-Augmented Generation (RAG)
- Human-in-the-Loop (HITL) validation
- Memory-based self-learning

The focus of this project is AI system design, not just model usage.

---

## 🎯 Objectives

This project demonstrates the ability to:
- Design a RAG pipeline
- Build a multi-agent AI system
- Handle text, image, and audio inputs
- Introduce human-in-the-loop (HITL)
- Implement memory and self-learning
- Package and deploy a working application

---

## 📚 Supported Math Scope

- Algebra
- Probability
- Basic Calculus (limits, derivatives, simple optimization)
- Linear Algebra (basics)

Difficulty level: JEE Main / early JEE Advanced

---

## 🏗️ System Architecture

User Input (Text / Image / Audio)
→ Parser Agent
→ Intent Router Agent
→ RAG Retrieval
→ Solver Agent
→ Verifier Agent
→ (Low confidence → Human-in-the-Loop)
→ Explainer Agent
→ Memory Storage

---

## 🧩 Core Features

### Multimodal Input
- Text input for direct problem entry
- Image input (PNG/JPG) with HITL correction
- Audio input with speech-to-text and confirmation

### Multi-Agent System
- Parser Agent: cleans input and detects ambiguity
- Router Agent: identifies math domain
- Solver Agent: solves using RAG
- Verifier Agent: checks correctness and confidence
- Explainer Agent: produces step-by-step explanation

Agent execution is visible in the UI.

---

## 📚 Retrieval-Augmented Generation (RAG)

- Curated knowledge base containing:
  - Math formulas and identities
  - Domain constraints
  - Common mistakes
- Embedding-based similarity search
- Retrieved context displayed in the UI
- No hallucinated citations if retrieval fails

---

## 🧑‍🏫 Human-in-the-Loop (HITL)

HITL is explicitly triggered when:
- OCR / ASR is unavailable or unreliable
- Parser detects ambiguity
- Verifier confidence is low
- User marks a solution as incorrect

Users can:
- Approve the solution
- Reject the solution
- Provide corrections

All feedback is stored as learning signals.

---

## 🧠 Memory & Self-Learning

The system stores:
- Original user input
- Parsed problem
- Retrieved context
- Final solution
- Verification result
- User feedback

Memory is used at runtime to:
- Retrieve similar solved problems
- Reuse solution patterns
- Improve reliability over time

No model retraining is required.

---

## 📁 Project Structure

aiplanegt/
├── app.py
├── requirements.txt
├── agents/
├── multimodal/
├── rag/
├── memory/
└── knowledge_base/

Some folders are intentionally minimal. Core logic is implemented inline where appropriate to reduce deployment risk while preserving extensibility.

---

## 🛠️ Setup & Run Instructions

Clone the repository:
git clone https://github.com/soniiharsh/aiplanegt.git
cd aiplanegt

Create virtual environment:
python3 -m venv venv
source venv/bin/activate

Install dependencies:
pip install --upgrade pip
pip install -r requirements.txt

Configure environment variables:
touch .env
echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env

Run the application:
streamlit run app.py

Open in browser:
http://localhost:8501

---

## 🖼️ OCR & Image Input Behavior

- Supported formats: PNG, JPG, JPEG
- OCR requires system-level Tesseract

Local Machine:
- OCR works if Tesseract is installed

Streamlit Cloud:
- Tesseract is unavailable
- OCR is intentionally disabled
- Image input routes to Human-in-the-Loop

This ensures reliability and prevents crashes.

---

## 🚀 Deployment

Deployed using Streamlit Cloud.

Steps:
1. Push repository to GitHub
2. Connect repository on Streamlit Cloud
3. Add GEMINI_API_KEY in Secrets
4. Deploy and test using public link

---

## 🎥 Demo Flow

1. Text input → verified solution
2. Image input → HITL correction → solution
3. Low confidence → human review
4. Similar problem → memory reuse

---

## 📊 Evaluation Coverage

- Multimodal input: YES
- Parser Agent: YES
- RAG pipeline: YES
- Multi-agent system: YES
- Human-in-the-loop: YES
- Memory & reuse: YES
- Deployment: YES

---

## 🧠 Design Philosophy

When automation is uncertain, the system escalates to humans instead of hallucinating.

---

## 👨‍💻 Author

Harsh Soni  
B.Tech – Electronics & Communication Engineering  
Specialization: Artificial Intelligence

---

## ✅ Status

Fully implemented  
Deployed and testable  
Meets all assignment criteria
