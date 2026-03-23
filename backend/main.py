"""
FastAPI Entry Point

Initializes the API, middleware, and routes.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import interview routes
from routes.interview import router as interview_router

# ---------------------------
# App Initialization
# ---------------------------

app = FastAPI(
    title="AI Interviewer API",
    description="Backend for AI-powered interview system",
    version="1.0.0"
)

# ---------------------------
# CORS Configuration
# ---------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------
# Exception Handler
# ---------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions and return proper JSON error response."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) if str(exc) else "An unexpected error occurred"}
    )

# ---------------------------
# Base Routes (health/debug)
# ---------------------------

@app.get("/")
async def root():
    return {"message": "AI Interviewer API is running"}

@app.get("/api/data")
async def get_data():
    return {"data": "Backend connected successfully"}

# ---------------------------
# Interview Routes
# ---------------------------

app.include_router(interview_router)

# Optional: prefix versioning
# app.include_router(interview_router, prefix="/api")