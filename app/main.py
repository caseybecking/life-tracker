from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from .database import engine
from . import models
from .routers import finance, general

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Life Tracker",
    description="A comprehensive life tracking application with flexible EAV data model",
    version="1.0.0"
)

# Include routers
app.include_router(finance.router)
app.include_router(general.router)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/static/templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main landing page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/finance", response_class=HTMLResponse)
async def finance_page(request: Request):
    """Finance tracking page"""
    return templates.TemplateResponse("finance.html", {"request": request})

@app.get("/track", response_class=HTMLResponse)
async def track_page(request: Request):
    """General tracking page"""
    return templates.TemplateResponse("track.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Life Tracker is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 