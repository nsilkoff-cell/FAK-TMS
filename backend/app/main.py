"""
FAK-TMS Backend - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FAK-TMS API",
    description="Freight & Accounting Kit - Transportation Management System",
    version="0.1.0"
)

# CORS configuration (allow localhost for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to FAK-TMS API",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# TODO: Import and include routers
# from app.routes import loads, carriers, invoices
# app.include_router(loads.router)
# app.include_router(carriers.router)
# app.include_router(invoices.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)