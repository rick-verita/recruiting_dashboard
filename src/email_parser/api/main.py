"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from email_parser.api.routers import applications, statistics, positions

app = FastAPI(
    title="Recruiting Dashboard API",
    description="API for managing job applications",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["statistics"])
app.include_router(positions.router, prefix="/api/positions", tags=["positions"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
