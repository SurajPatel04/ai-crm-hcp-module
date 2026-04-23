# AI Healthcare CRM - Frontend

The frontend for the AI Healthcare CRM application. Built with modern web technologies, this interface allows healthcare professionals to securely log in, interact with an AI agent to populate and log interactions, and review HCP details.

## 🚀 Features

- **AI-Driven Chat Assistant**: Split-screen design with a conversational AI panel that seamlessly manages data entry.
- **Dynamic Interaction Logging**: Real-time form population based on natural language inputs.
- **Authentication**: Secure sign-up, sign-in, and session management using httpOnly cookies.
- **Modern UI/UX**: Designed using Tailwind CSS v4 for a highly responsive, clean, and intuitive interface.
- **State Management**: Centralized application state handling with Redux Toolkit.
- **Client-Side Routing**: Smooth navigation with React Router DOM.

## 🛠️ Tech Stack

- **Framework**: [React](https://react.dev/) 19 (via [Vite](https://vitejs.dev/))
- **State Management**: [Redux Toolkit](https://redux-toolkit.js.org/) (`react-redux`)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Routing**: [React Router DOM](https://reactrouter.com/) v7
- **HTTP Client**: [Axios](https://axios-http.com/)

## ⚙️ Setup & Installation

Follow these steps to set up the frontend on your local machine:

### 1. Prerequisites

- **Node.js** (v18 or higher recommended)
- **npm** (comes with Node.js)

### 2. Install Dependencies

Navigate to the `frontend` directory and install the necessary dependencies:

```bash
cd frontend
npm install
```

### 3. Start the Development Server

Run the following command to start the Vite development server:

```bash
npm run dev
```

The application will be accessible at: `http://localhost:5173` (or the port specified by Vite in the terminal output).

### Note on API Connection
The frontend is configured to communicate with the backend running on `http://localhost:8000/api/v1`. Ensure that your backend server is up and running. API calls utilize `withCredentials: true` to handle automatic cookie-based session management securely.

## 📁 Project Structure

- `src/`
  - `components/`: Reusable UI components.
  - `features/`: Feature-specific modules (e.g., `agent`, `auth`, `interactions`).
  - `services/`: Axios instance configuration (`api.js`) and API request logic.
  - `store/`: Redux store configuration and slices.
  - `App.jsx`: Main application routing and layout setup.
  - `main.jsx`: React root mounting and context providers.

## 🏗️ Building for Production

To create an optimized production build, run:

```bash
npm run build
```

This will generate static assets in the `dist/` directory, ready to be served. You can preview the production build locally using:

```bash
npm run preview
```
