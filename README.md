# Document Intake Assistant

A modern, trust-aware AI assistant designed to help users draft a **Personal Wishes Document** step-by-step. Built with a fast Python backend (FastAPI, Pydantic, Groq/Gemini) and a beautiful React frontend (Tailwind CSS, Horizon UI).

##  Features

- **Conversational Interface**: Chat naturally with the AI to provide details for your document.
- **Trust-Aware Extraction Engine**: Uses a strict Pydantic state model that enforces logical consistency (e.g., catching contradictions like "no children" but naming a "son" as an executor).
- **Real-Time Progress Dashboard**: A 4-panel ultra-wide UI displaying Chat, Live Progress, State Summary, and a complete Activity Timeline.
- **Live Document Preview**: Watch your final markdown document build itself dynamically beneath your state cards as you answer questions.
- **Conflict Resolution UI**: Automatically pauses when contradictory or confusing information is detected and clearly displays the reason so you can provide corrections.

##  Tech Stack

### Frontend
- **React 18** (Vite)
- **Tailwind CSS** (Custom Horizon UI styling)
- **Lucide React** (Icons)
- **React Markdown** (Live document rendering)

### Backend
- **FastAPI** (Python web framework)
- **Pydantic v2** (Strict data validation and schema enforcement)
- **Groq API / Gemini API** (High-speed LLM inference for state extraction)

##  Quick Start

### 1. Setup Backend

Navigate to the backend directory and install dependencies:
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your API keys:
```env
LLM_PROVIDER=universal
LLM_API_KEY=your_llm_api_key
LLM_MODEL_NAME=your_llm_model_name
```

Start the backend server:
```bash
uvicorn app.main:app --reload
```

### 2. Setup Frontend

Navigate to the frontend directory and install dependencies:
```bash
cd frontend
npm install
```

Start the frontend development server:
```bash
npm run dev
```

The application will be running at `http://localhost:5173`.

##  Screenshots

Here is a look at the application in action during different activities:

### Final Dashboard (4-Panel View & Live Preview)
The completed UI features a 4-column layout perfectly fitting modern widescreen monitors, showing real-time chat, progress rings, and a live rendering of the legal document.

<img width="1889" height="1016" alt="image" src="https://github.com/user-attachments/assets/2c3c584a-ebd6-4388-b354-64b088f9f2b9" />


### Document Preview 

<img width="1911" height="1025" alt="image" src="https://github.com/user-attachments/assets/75ba75a4-a40c-439f-9b9b-b34040f06d13" />


### Strict Conflict Resolution
When the backend detects a logical contradiction (e.g., claiming no children but naming a son as an executor), the system safely intercepts it and demands user confirmation, explicitly displaying the conflict reason.

<img width="1915" height="1023" alt="image" src="https://github.com/user-attachments/assets/b8f96e39-97fc-4ed5-a5f0-d6cb8bdafda0" />

## A short explanation of how the mock would be replaced by a real provider

How it works: The application backend is built using the Dependency Injection and Strategy design patterns. We defined a base LLMProvider interface that dictates how the system talks to an AI (e.g., methods for extract_state and generate_response).

Both the MockProvider (used for testing) and the real providers (GroqProvider, GeminiProvider) implement this exact same interface. Because the application only relies on the abstract interface, swapping the mock out for a real AI requires zero code changes to the core application logic.

How to replace it: The provider selection is dynamically routed at runtime via the get_llm_provider() factory function based on your environment variables.

To replace the mock with a real provider, you only need to "give" the project two things in your .env file:

1.The Provider Flag: Tell the system which engine to use by setting LLM_PROVIDER (e.g., LLM_PROVIDER=groq).
2.The API Key: Provide the authenticating secret key for that specific service.

Example .env configuration:

Give the project the required API Key

LLM_API_KEY=your_real_api_key_here

Give the project the required model name

LLM_MODEL_NAME=your_model_name
