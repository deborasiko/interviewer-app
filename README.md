# Python React FastAPI App

This project consists of a Python backend using FastAPI and a React frontend that communicate via API. The application uses GitHub Models (Azure AI Inference) for LLM capabilities.

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- GitHub Personal Access Token (PAT) for GitHub Models

## GitHub Token Setup

The application requires a GitHub Personal Access Token to access GitHub Models:

1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token" → "Generate new token (classic)"
3. Give your token a descriptive name (e.g., "Interviewer App")
4. Select the required scopes (no specific scopes needed for GitHub Models)
5. Click "Generate token" and copy the token

### Setting the GitHub Token

**Windows (Command Prompt):**
```cmd
set GITHUB_TOKEN=your_github_token_here
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="your_github_token_here"
```

**Linux/macOS:**
```bash
export GITHUB_TOKEN=your_github_token_here
```

**Note:** The token needs to be set in each terminal session, or you can add it to your system environment variables for persistence.

## Backend

The backend is located in the [`backend/`](backend/) directory and uses FastAPI with Azure AI Inference for LLM integration.

### Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your GitHub token (see [GitHub Token Setup](#github-token-setup) above)

4. Run the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The API will be available at http://localhost:8000

### API Documentation

Once the backend is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend

The frontend is located in the [`frontend/`](frontend/) directory and is built with React.

### Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The app will be available at http://localhost:3000

## Running Both Servers

### Option 1: Using VS Code Tasks (Recommended)

This project includes VS Code tasks for easy development:

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "Tasks: Run Task"
3. Select either:
   - **"Run Backend"** - Starts the FastAPI backend server
   - **"Run Frontend"** - Starts the React development server

**Note:** Make sure to set the `GITHUB_TOKEN` environment variable in your terminal before running the backend task, or the backend will fail to start.

You can run both tasks simultaneously in separate terminal panels.

### Option 2: Using Terminal Commands

**Terminal 1 (Backend):**
```bash
# Set GitHub token first
set GITHUB_TOKEN=your_github_token_here  # Windows CMD
# OR
$env:GITHUB_TOKEN="your_github_token_here"  # Windows PowerShell
# OR
export GITHUB_TOKEN=your_github_token_here  # Linux/macOS

# Run backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

## Project Structure

```
Interviewer-app/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application entry point
│   ├── requirements.txt # Python dependencies
│   ├── models/          # Data models and schemas
│   ├── routes/          # API route handlers
│   ├── services/        # Business logic and LLM integration
│   ├── prompts/         # LLM prompt templates
│   └── data/            # Interview data and transcripts
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.js      # Main React component
│   │   └── components/ # React components
│   ├── public/         # Static assets
│   └── package.json    # Node dependencies
└── .vscode/
    └── tasks.json      # VS Code task definitions
```

## Troubleshooting

### Backend Issues

- **"GITHUB_TOKEN environment variable not set"**: Make sure you've set the GitHub token in your terminal session before starting the backend.
- **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
- **Port already in use**: Change the port in the uvicorn command (e.g., `--port 8001`)

### Frontend Issues

- **Port 3000 already in use**: The React dev server will prompt you to use a different port automatically.
- **Module not found errors**: Run `npm install` to ensure all dependencies are installed.
- **API connection errors**: Verify the backend is running on http://localhost:8000

## Docker Deployment

The project includes Docker support for easy deployment and development.

### Prerequisites

- Docker and Docker Compose installed on your system
- GitHub Personal Access Token (same as for local development)

### Quick Start with Docker

1. **Set your GitHub token environment variable:**
   ```powershell
   # Windows (PowerShell)
   $env:GITHUB_TOKEN="your_github_token_here"
   
   # Windows (CMD)
   set GITHUB_TOKEN=your_github_token_here
   
   # Linux/macOS
   export GITHUB_TOKEN=your_github_token_here
   ```

2. **Build and run the containers:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Commands

**Build images:**
```bash
docker-compose build
```

**Start services:**
```bash
docker-compose up
```

**Start services in detached mode:**
```bash
docker-compose up -d
```

**Stop services:**
```bash
docker-compose down
```

**Stop services and remove volumes (clean slate):**
```bash
docker-compose down -v
```

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Environment Variables

The Docker setup uses the following environment variables:

- `GITHUB_TOKEN`: Required for the backend LLM service (Azure AI Inference)
- `REACT_APP_API_URL`: Frontend API URL (set to `http://backend:8000` in docker-compose)

**Setting GITHUB_TOKEN for Docker Compose:**

For PowerShell:
```powershell
$env:GITHUB_TOKEN="your_github_token_here"
docker-compose up
```

For CMD:
```cmd
set GITHUB_TOKEN=your_github_token_here
docker-compose up
```

For Linux/macOS:
```bash
export GITHUB_TOKEN=your_github_token_here
docker-compose up
```

### Development with Docker

For development, you can use the development frontend configuration by uncommenting the `frontend-dev` service in [`docker-compose.yml`](docker-compose.yml) and commenting out the production frontend service.

### Docker Files

- [`backend/Dockerfile`](backend/Dockerfile) - Backend Python FastAPI container
- [`frontend/Dockerfile`](frontend/Dockerfile) - Frontend React container with multi-stage build
- [`frontend/nginx.conf`](frontend/nginx.conf) - Nginx configuration for production frontend
- [`docker-compose.yml`](docker-compose.yml) - Docker Compose orchestration

### Container Architecture

```
┌─────────────────────────────────┐
│      interviewer-network        │
│  ┌───────────────────────────┐   │
│  │   interviewer-backend    │   │
│  │   (FastAPI - Port 8000)  │   │
│  └───────────────────────────┘   │
│  ┌───────────────────────────┐   │
│  │   interviewer-frontend   │   │
│  │   (Nginx - Port 80)       │   │
│  └───────────────────────────┘   │
└─────────────────────────────────┘
         │              │
         │              │
    Port 8000        Port 3000
    (Backend)       (Frontend)
```