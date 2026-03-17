Internal Idea Hub: Architecture & Step-by-Step Plan

1. System Architecture Overview

Frontend: React.js (Single Page Application) with Tailwind CSS for a clean, modern, Reddit-like interface.

Backend: FastAPI (Python). It is lightweight, fast, and handles async operations perfectly, making it ideal for LLM API calls.

AI Engine: Google Gemini API.

Summarization: gemini-2.5-flash for fast, cost-effective summarization of long comment threads.

Semantic Search: text-embedding-004 to convert ideas and summaries into vector embeddings for natural language search.

Database (Production Recommendation): PostgreSQL with the pgvector extension (to store idea data and their vector embeddings). Note: The provided prototype uses an in-memory vector store for immediate local testing.

Deployment: Google Cloud Run (Direct source-based deployment from GitHub).

2. Step-by-Step Implementation Plan

Phase 1: Data Modeling & Core API (Completed in Prototype)

Define Schemas: Create Pydantic models for Idea, Comment, User, and Tag.

ID Generation: Implement a unique, human-readable ID generator (e.g., IDEA-A7F2) for easy reference in meetings.

CRUD Endpoints: Build FastAPI routes to Create, Read, Update, and Delete ideas and comments.

Phase 2: AI Integration (Completed in Prototype)

Summarization Trigger: Create an endpoint /api/ideas/{id}/summarize. When clicked, it pulls the idea description and all comments, sends them to gemini-2.5-flash, and saves the summary.

Embedding Generation: Whenever an idea is created or summarized, pass the text to the Gemini embedding model to generate a numerical vector representing the semantic meaning of the idea.

Semantic Search Engine: Build a /api/search endpoint.

If the user searches an exact ID (e.g., "IDEA-123"), return it directly.

Otherwise, convert the search query into an embedding and perform a Cosine Similarity mathematical calculation against all stored idea embeddings to return the most contextually relevant results.

Phase 3: Frontend Development (Completed in Prototype)

Layout: Create a top navigation bar (About, Contribute, Contact, Search) and a main feed.

Feed (Reddit-style): Display ideas as cards with upvotes, tags, status badges, and comment counts.

Detail View: A dedicated pane for an idea showing the full thread, tagged employees, and the "Summarize Conversation" button.

Contribute Form: A clean form to submit new ideas, attach categories (Process Improvement, New Product, etc.), and tag colleagues.

Phase 4: Production Readiness (Next Steps for your team)

Authentication: Integrate your company's SSO (e.g., Google Workspace, Microsoft Entra ID) using OAuth2 in FastAPI.

Database Migration: Replace the in-memory Python dictionaries with SQLAlchemy and a real PostgreSQL/pgvector database.

Mentions/Notifications: Enhance the frontend to support dynamic @username autocomplete in the text area, and trigger email/Slack notifications via the backend when someone is tagged.

Phase 5: Deployment (Direct from GitHub)

Version Control: Push your main.py, index.html, and a requirements.txt file to a GitHub repository. (Optionally include a Procfile containing web: uvicorn main:app --host 0.0.0.0 --port $PORT to explicitly tell Cloud Run how to start the app).

Cloud Run Setup: In the Google Cloud Console, create a new Cloud Run service and choose "Continuously deploy new revisions from a source repository".

Connect GitHub: Link your repository and branch. Cloud Run uses Google Cloud Buildpacks to automatically detect Python, install dependencies, and build the container in the background.

Environment Variables: During setup, ensure the GEMINI_API_KEY environment variable is securely injected (preferably via Google Secret Manager) and the standard container port is mapped properly.