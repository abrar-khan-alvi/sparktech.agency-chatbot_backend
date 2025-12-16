# AI Chatbot Backend (RAG Pipeline)

## Project Overview
This project is a production-ready backend service for an AI chatbot. It acts as the "Brain" and "Memory" of a support system. Instead of relying solely on an AI model's training data, I implemented a **Retrieval-Augmented Generation (RAG)** pipeline to answer questions based on specific company documents.

**Key Features:**
1.  **Secure Auth:** JWT-based Signup and Login.
2.  **RAG AI:** Uses FAISS and Google Gemini to answer questions using a local Knowledge Base.
3.  **Chat History:** Stores all conversations in PostgreSQL.
4.  **Background Tasks:** Handles both **scheduled maintenance** (cleanup) and **asynchronous events** (emails).

---

## Technologies Used
*   **Backend Framework:** Python (Django REST Framework)
*   **Database:** PostgreSQL (Production-grade relational DB)
*   **Authentication:** JWT (via `simplejwt`)
*   **AI Model:** Google Gemini 2.5 Flash
*   **Vector Search:** FAISS (Facebook AI Similarity Search)
*   **Task Management:** APScheduler (for Cron jobs) & Python Threading (for Async tasks)

---

## API Documentation

You can test these endpoints using the `chatbot_api_collection.json` file included in this repository.

### 1. User Registration
*   **Endpoint:** `POST /api/signup/`
*   **Body:** `{"username": "user", "email": "test@test.com", "password": "123"}`
*   **Background Action:** Creates the user and immediately triggers a background thread to send a welcome email (printed to console).

### 2. User Login
*   **Endpoint:** `POST /api/login/`
*   **Body:** `{"username": "user", "password": "123"}`
*   **Response:** Returns `access` and `refresh` tokens.

### 3. Chat with AI (Protected)
*   **Endpoint:** `POST /api/chat/`
*   **Headers:** `Authorization: Bearer <YOUR_ACCESS_TOKEN>`
*   **Body:** `{"message": "What is your return policy?"}`
*   **Response:** AI answer based on the knowledge base.

### 4. View History (Protected)
*   **Endpoint:** `GET /api/chat-history/`
*   **Headers:** `Authorization: Bearer <YOUR_ACCESS_TOKEN>`
*   **Response:** JSON list of past conversations.

---

## Setup Instructions

### 1. Clone and Install
```bash
git clone <YOUR_REPO_URL>
cd chatbot_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory.
*(Note: I configured the email backend to print to the console for testing).*

```ini
SECRET_KEY=django-insecure-key-dev
# Database
DB_NAME=chatbot_db
DB_USER=chatbot_user
DB_PASSWORD=securepassword123
DB_HOST=localhost

# Google AI Key (Required for RAG)
GEMINI_API_KEY=AIzaSy... (Paste your key here)
```

### 3. Initialize Database
```bash
python manage.py migrate
```

### 4. Run the Server
```bash
python manage.py runserver
```

---

## Background Task Implementation

I implemented **two** types of background tasks in `chatbot_api/tasks.py`:

**1. Scheduled Task (The Janitor):**
*   **Purpose:** Deletes chat history older than 30 days.
*   **Tool:** `APScheduler`.
*   **Frequency:** Runs automatically every 24 hours.
*   **Verification:** You will see `Background Scheduler Started ()!` in the terminal when the server starts.

**2. Async Task (The Mailman):**
*   **Purpose:** Sends a welcome email after signup.
*   **Tool:** Python `threading`.
*   **Trigger:** Fires immediately when `POST /signup/` is called.
*   **Verification:** Check your terminal after signup to see the simulated email output.

---

## Answers to Technical Questions

### 1. How did you integrate the RAG pipeline?
I built a custom utility that loads the knowledge base text file. I used `google-generativeai` to create embeddings (`gemini-embedding-001`) and stored them in a **FAISS** index.
When a user asks a question:
1.  The question is converted to a vector.
2.  FAISS finds the closest matching paragraph.
3.  That paragraph is injected into the Gemini prompt as "Context".
4.  Gemini generates the answer based *only* on that context.

### 2. What database and model structure did you use?
I used **PostgreSQL** because it is robust and handles concurrent writes better than SQLite. The `ChatHistory` model links to the `User` model via a ForeignKey. It stores the input, output, and timestamp, allowing efficient retrieval per user.

### 3. How did you implement user authentication?
I used `simplejwt` for stateless authentication.
*   **Security:** Passwords are hashed using PBKDF2.
*   **Tokens:** Users receive a short-lived Access Token (1 hour) and a long-lived Refresh Token (24 hours). This ensures security without forcing frequent logins.

### 4. How does the chatbot generate responses?
It uses **Context-Aware Prompting**. I instruct the AI: *"You are a helpful customer support assistant.Use the following Context to answer the User's Question.If the answer is not in the Context, say "I don't have that information."* This prevents the AI from "hallucinating" or making up facts that aren't in the document.

### 5. How did you schedule background tasks?
I used two different strategies to demonstrate flexibility:
*   **For Cleanup:** I used `APScheduler` because it needs to run on a fixed interval (Cron job style).
*   **For Emails:** I used `threading` because it needs to happen *immediately* after a user action (Event-driven), ensuring the API remains fast and non-blocking.

### 6. What testing strategies did you use?
*   **Unit Testing:** I tested the `generate_rag_response` function in the Django Shell to ensure the Vector Search was finding the correct documents.
*   **Integration Testing:** I used Postman (exported as `chatbot_api_collection.json`) to test the full Signup -> Login -> Chat flow.

### 7. What external services did you integrate?
*   **Google Gemini API:** Selected for its speed (`gemini-2.5-flash`) and free tier.
*   **FAISS:** Selected for local vector storage, removing the need for external services like Pinecone during development.

### 8. How would you expand this?
*   **Dynamic Knowledge Base:** I would move the text data into a Database Table so admins can update facts via the Admin Panel without restarting the server.
*   **Dockerization:** I would add a `Dockerfile` and `docker-compose.yml` to spin up the Django app and PostgreSQL container with one command.
