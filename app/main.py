from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import events_api
from app.db.mongodb import create_mongodb_connection, close_mongodb_connection

app = FastAPI(
    title="Events management API",
    description="A FastAPI app to manage events using MongoDB database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup():
    await create_mongodb_connection()

@app.on_event("shutdown")
async def shutdown():
    await close_mongodb_connection()

app.include_router(events_api.router, prefix="/events", tags=["Events"])
