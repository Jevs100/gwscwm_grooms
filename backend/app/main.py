"""This is the main FastAPI application Module."""

from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Simple FastAPI App", version="0.1.0")


@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)