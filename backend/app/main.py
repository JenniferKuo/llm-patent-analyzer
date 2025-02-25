from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import analysis, search, reports
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Patent Infringement Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router)
app.include_router(search.router)
app.include_router(reports.router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}