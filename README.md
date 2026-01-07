🧮 Math Mentor
Reliable Multimodal AI-Powered Math Tutor

(RAG + Multi-Agent System + Human-in-the-Loop + Memory)

📌 Project Overview

Math Mentor is an end-to-end AI system designed to reliably solve JEE-style mathematics problems while prioritizing correctness, transparency, and safety.
The application supports multimodal inputs (text, image, and audio), uses a multi-agent architecture, grounds reasoning through Retrieval-Augmented Generation (RAG), incorporates human-in-the-loop (HITL) validation, and improves over time using a memory layer.

Unlike simple AI demos, this project focuses on reliable AI system design, explicitly handling uncertainty instead of hallucinating answers.

🎯 Objectives

This project was built to demonstrate the ability to:

Design a RAG pipeline

Build a multi-agent AI system

Handle text, image, and audio inputs

Introduce human-in-the-loop (HITL) mechanisms

Implement memory and self-learning

Package, deploy, and demonstrate a working AI application

📚 Supported Math Scope

Algebra

Probability

Basic Calculus (limits, derivatives, simple optimization)

Linear Algebra (basics)

Difficulty level: JEE-style, not olympiad-level.

🏗️ System Architecture
graph TD
    A[User Input] --> B{Input Type}
    B -->|Text| C[Parser Agent]
    B -->|Image| D[HITL OCR Flow]
    B -->|Audio| E[ASR + Confirmation]

    C --> F[Intent Router Agent]
    F --> G[RAG Retrieval]
    G --> H[Solver Agent]
    H --> I[Verifier Agent]

    I -->|Low Confidence| J[Human-in-the-Loop]
    I -->|High Confidence| K[Explainer Agent]

    J --> K
    K --> L[Memory Storage]

🧩 Core Features
✅ Multimodal Input

Text: Direct typed input

Image: PNG/JPG upload with HITL fallback

Audio: Speech-to-text with transcript confirmation

🤖 Multi-Agent System

Parser Agent – cleans input and detects ambiguity

Intent Router Agent – identifies problem domain

Solver Agent – generates step-by-step solution using RAG

Verifier Agent – checks correctness and confidence

Explainer Agent – produces student-friendly explanations

📚 Retrieval-Augmented Generation (RAG)

Curated knowledge base:

Formulas and identities

Domain constraints

Common mistakes

Embeddings + vector search

Retrieved context shown explicitly in the UI

No hallucinated citations when retrieval fails

🧑‍🏫 Human-in-the-Loop (HITL)

HITL is triggered when:

OCR / ASR is unavailable or unreliable

Parser detects ambiguity

Verifier confidence is low

User explicitly marks a solution as incorrect

Users can:

Approve

Edit

Reject solutions
Corrections are stored as learning signals.

🧠 Memory & Self-Learning

The system stores:

Original input

Parsed problem

Retrieved context

Final solution

Verification outcome

User feedback

Memory is used at runtime to:

Retrieve similar past problems

Reuse solution patterns

Improve future reliability
(No model retraining required.)

📁 Project Structure
aiplanegt/
├── app.py                      # Streamlit application
├── requirements.txt
├── README.md
├── multimodal/
│   ├── ocr_processor.py        # Cloud-safe OCR with HITL fallback
│   └── asr_processor.py        # Audio transcription
├── rag/
│   ├── embeddings.py           # Embedding generation
│   └── retriever.py            # Vector similarity search
├── memory/
│   └── solution_memory.py      # SQLite-based memory
├── agents/
│   ├── parser_agent.py
│   ├── router_agent.py
│   ├── solver_agent.py
│   ├── verifier_agent.py
│   └── explainer_agent.py
└── knowledge_base/
    ├── algebra_formulas.md
    ├── calculus_basics.md
    ├── probability_guide.md
    └── common_mistakes.txt


Some folders are intentionally minimal. Core logic is implemented inline where appropriate to reduce deployment risk while preserving extensibility.

🛠️ Setup & Run Instructions
1️⃣ Clone the Repository
git clone https://github.com/soniiharsh/aiplanegt.git
cd aiplanegt

2️⃣ Create Virtual Environment
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

3️⃣ Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

4️⃣ Configure Environment Variables
touch .env
echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env


Get a free API key from:
https://aistudio.google.com/app/apikey

5️⃣ Run the Application
streamlit run app.py


Open:

http://localhost:8501

🖼️ OCR & Image Input Behavior (Important)

Image formats supported: PNG, JPG, JPEG

OCR depends on system-level Tesseract binaries

Local Machine

OCR can work if Tesseract is installed

Streamlit Cloud / Cloud Environments

Tesseract binaries are not available

OCR is intentionally disabled

Image input routes directly to HITL manual correction

This design prevents crashes and ensures correctness.

🚀 Deployment

The application is deployed using Streamlit Cloud.

Steps:

Push code to GitHub

Connect repository on Streamlit Cloud

Add GEMINI_API_KEY in Secrets

Deploy and test via public link

🎥 Demo (Suggested Flow)

Text input → solved and verified

Image upload → HITL correction → solution

Low confidence case → human review

Similar problem → memory reuse

📊 Evaluation Coverage Summary
Requirement	Status
Multimodal input	✅
Parser agent	✅
RAG pipeline	✅
Multi-agent system	✅
Human-in-the-loop	✅
Memory & reuse	✅
Deployment	✅
🧠 Design Philosophy

When automation is uncertain, the system escalates to humans instead of hallucinating.

This project emphasizes trustworthy AI system engineering, not just model usage.

👨‍💻 Author

Harsh Soni
B.Tech – Electronics & Communication Engineering (AI Specialization)
