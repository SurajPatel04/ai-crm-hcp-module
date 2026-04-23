# AI Healthcare CRM - Backend

The backend for the AI Healthcare CRM application. Built with FastAPI, PostgreSQL, and LangGraph, this service manages authentication, handles interaction logging, and provides an AI agent capable of extracting and acting on conversational data.

## 🚀 Features

- **AI-Driven Data Extraction**: Uses a LangGraph agent powered by Groq (Gemma2-9b) to intelligently extract and format data from chat conversations.
- **Robust Authentication**: Full JWT-based auth flow (sign-up, sign-in, token refresh, and logout) with securely hashed passwords and HTTP-only cookies.
- **Asynchronous Database Access**: Integrates with PostgreSQL using `asyncpg` and SQLAlchemy for high-performance, non-blocking database queries.
- **Tool-Calling Agent**: The AI agent has access to multiple tools (`log_interaction`, `edit_interaction`, etc.) allowing it to read schemas and directly create records in the database.
- **Thread-Safe AI Execution**: Heavy synchronous AI agent invocations are offloaded to background threads to ensure the FastAPI event loop remains unblocked and responsive.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) & [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **AI / LLM Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) & [LangChain](https://python.langchain.com/)
- **LLM Provider**: [Groq](https://console.groq.com/) API
- **Authentication**: JWT (JSON Web Tokens), Passlib for hashing.

## ⚙️ Setup & Installation

### 1. Prerequisites

- Python 3.10+
- PostgreSQL database (local or cloud-hosted)

### 2. Install Dependencies

Create a virtual environment, activate it, and install the required packages:

```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the root of the `backend` directory based on the following example:

```env
# Database configuration (Use asyncpg for async SQLALchemy)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname?sslmode=require

# Authentication configuration
SECRET_KEY=your_super_secret_key_here
REFRESH_TOKEN_SECRET_KEY=your_super_secret_refresh_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_TIME=30 # In minutes
REFRESH_TOKEN_EXPIRE_TIME=7 # In days

# AI/LLM Provider configuration
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Run the Server

Start the FastAPI application using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. You can view the interactive Swagger API documentation at `http://localhost:8000/docs`.

## 📁 Architecture & Directory Flow

- `app/`
  - `agent/`: Contains the LangGraph configuration, node logic, state definitions, and custom tools (`tools.py`) that the LLM uses to interact with the database.
  - `core/`: Core configurations (e.g., loading environment variables, database engine setup).
  - `dependencies/`: FastAPI dependencies (e.g., getting a database session, fetching the current authenticated user).
  - `models/`: SQLAlchemy ORM definitions for tables like `User`, `Interaction`, and `HCP`.
  - `routes/`: API endpoint definitions separated by domain (`auth_route.py`, `chat_route.py`, etc.).
  - `schemas/`: Pydantic models used for input validation and API serialization.
  - `services/`: Business logic, such as password hashing and token generation.
  - `utils/`: Helper scripts and utility functions.
  - `main.py`: The entry point for the FastAPI application, where all routers and middlewares (like CORS) are registered.

## 🔄 Core Data Flow Example: Chat Routing

1. The frontend posts a message to `/api/v1/chat/invoke`.
2. The route extracts the `session_id` and the message text.
3. FastAPI passes the input to the LangGraph agent in a separate thread (using `asyncio.to_thread()`) to prevent blocking the async event loop.
4. The Agent accesses conversational memory from SQLite, processes the input via the Groq LLM, and decides whether to respond naturally or call an internal Tool (e.g., "log_interaction").
5. The response, including any structured data or tool-call payloads, is returned to the frontend.
