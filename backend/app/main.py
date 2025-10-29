"""This is the main FastAPI application Module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from modules.databases.mysql_manager import MysqlManager
import uvicorn
import os

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost/dbname")
database = MysqlManager.from_env()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: connect the database manager
    await database.startup()
    app.state.database = database
    try:
        yield
    finally:
        # shutdown: disconnect the database manager
        await database.shutdown()

app = FastAPI(title="Simple FastAPI App", version="0.1.0", lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/josh")
async def read_josh():
    return {"message": "Hello Josh"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)