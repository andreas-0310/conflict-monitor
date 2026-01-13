from fastapi import FastAPI
from app.database import init_db
from app.routers import auth, conflict_data
import uvicorn

app = FastAPI(
    title="Conflict Monitor API",
    description="API for monitoring conflicts in different countries",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(auth.router)
app.include_router(conflict_data.router)


@app.get("/")
def read_root():
    return {
        "message": "Conflict Monitor API",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
