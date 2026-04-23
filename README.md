# AI-First Healthcare CRM Module

An advanced, AI-driven Customer Relationship Management (CRM) module tailored for Healthcare Professionals (HCPs). This application utilizes a LangGraph-powered conversational agent to intelligently capture, format, and log interaction data directly into the database through natural language. 

The project is structured as a modern full-stack web application with a clear separation of concerns between the client interface and the API server.

---

## 🌟 Key Application Features

- **Conversational Data Entry**: Simply tell the AI about a meeting with a Healthcare Professional, and it will automatically extract the details, format them, and log the interaction.
- **Agentic Workflows**: The backend AI agent operates autonomously via a set of specific tools, allowing it to read database schemas and write records dynamically.
- **Secure Authentication**: End-to-end secure access managed via HTTP-only JWT cookies (sign-up, log-in, refresh).
- **Responsive UI/UX**: A highly polished, dynamic user interface crafted with Tailwind CSS v4 for a seamless user experience.

---

## 🚀 Getting Started

To run the full application locally, you will need to start both the backend API server and the frontend development server concurrently.

### 1. Database & Environment Setup
Before starting the servers, ensure you have a PostgreSQL database available.

Navigate to the `backend` directory and create a `.env` file based on the following example:

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

### 2. Start the Backend
Open a terminal and start the backend service:

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```
*The API will be running at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.*

### 3. Start the Frontend
Open a **new** terminal window/tab and start the frontend development server:

```bash
cd frontend

# Install dependencies
npm install

# Start the application
npm run dev
```
*The web interface will be accessible at `http://localhost:5173`.*

---

## 💻 Frontend Architecture

The frontend is a modern, responsive React web application providing a split-screen interface. One side displays the interaction logging form and data, while the other features an interactive AI Chat Assistant. 

### Frontend Features
- **AI-Driven Chat Assistant**: Split-screen design with a conversational AI panel that seamlessly manages data entry.
- **Dynamic Interaction Logging**: Real-time form population based on natural language inputs.
- **Authentication**: Secure sign-up, sign-in, and session management using httpOnly cookies.
- **Modern UI/UX**: Designed using Tailwind CSS v4 for a highly responsive, clean, and intuitive interface.
- **State Management**: Centralized application state handling with Redux Toolkit.
- **Client-Side Routing**: Smooth navigation with React Router DOM.

### Frontend Tech Stack
- **Framework**: [React](https://react.dev/) 19 (via [Vite](https://vitejs.dev/))
- **State Management**: [Redux Toolkit](https://redux-toolkit.js.org/) (`react-redux`)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Routing**: [React Router DOM](https://reactrouter.com/) v7
- **HTTP Client**: [Axios](https://axios-http.com/) *(Note: API calls utilize `withCredentials: true` to handle automatic cookie-based session management securely).*

### Frontend Project Structure
- `frontend/src/`
  - `components/`: Reusable UI components.
  - `features/`: Feature-specific modules (e.g., `agent`, `auth`, `interactions`).
  - `services/`: Axios instance configuration (`api.js`) and API request logic.
  - `store/`: Redux store configuration and slices.
  - `App.jsx`: Main application routing and layout setup.
  - `main.jsx`: React root mounting and context providers.

### Building for Production
To create an optimized production build, run:
```bash
cd frontend
npm run build
npm run preview
```

---

## ⚙️ Backend Architecture

A high-performance FastAPI application that handles secure user authentication, database operations, and orchestrates the LangGraph AI agent.

### Backend Features
- **AI-Driven Data Extraction**: Uses a LangGraph agent powered by Groq (Gemma2-9b) to intelligently extract and format data from chat conversations.
- **Robust Authentication**: Full JWT-based auth flow (sign-up, sign-in, token refresh, and logout) with securely hashed passwords and HTTP-only cookies.
- **Asynchronous Database Access**: Integrates with PostgreSQL using `asyncpg` and SQLAlchemy for high-performance, non-blocking database queries.
- **Tool-Calling Agent**: The AI agent has access to multiple tools (`log_interaction`, `edit_interaction`, etc.) allowing it to read schemas and directly create records in the database.
- **Thread-Safe AI Execution**: Heavy synchronous AI agent invocations are offloaded to background threads to ensure the FastAPI event loop remains unblocked and responsive.

### Backend Tech Stack
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) & [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **AI / LLM Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) & [LangChain](https://python.langchain.com/)
- **LLM Provider**: [Groq](https://console.groq.com/) API
- **Authentication**: JWT (JSON Web Tokens), Passlib for hashing.

### Backend Architecture & Directory Flow
- `backend/app/`
  - `agent/`: Contains the LangGraph configuration, node logic, state definitions, and custom tools (`tools.py`) that the LLM uses to interact with the database.
  - `core/`: Core configurations (e.g., loading environment variables, database engine setup).
  - `dependencies/`: FastAPI dependencies (e.g., getting a database session, fetching the current authenticated user).
  - `models/`: SQLAlchemy ORM definitions for tables like `User`, `Interaction`, and `HCP`.
  - `routes/`: API endpoint definitions separated by domain (`auth_route.py`, `chat_route.py`, etc.).
  - `schemas/`: Pydantic models used for input validation and API serialization.
  - `services/`: Business logic, such as password hashing and token generation.
  - `utils/`: Helper scripts and utility functions.
  - `main.py`: The entry point for the FastAPI application, where all routers and middlewares (like CORS) are registered.

### Core Data Flow Example: Chat Routing
1. The frontend posts a message to `/api/v1/chat/invoke`.
2. The route extracts the `session_id` and the message text.
3. FastAPI passes the input to the LangGraph agent in a separate thread (using `asyncio.to_thread()`) to prevent blocking the async event loop.
4. The Agent accesses conversational memory from SQLite, processes the input via the Groq LLM, and decides whether to respond naturally or call an internal Tool (e.g., "log_interaction").
5. The response, including any structured data or tool-call payloads, is returned to the frontend.
