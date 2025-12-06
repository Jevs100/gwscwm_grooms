"""This module is the main module"""

from fastapi import FastAPI
# from modules.db.database import engine
# from modules.models.models import Base

app = FastAPI()

# # Create the database tables
# Base.metadata.create_all(bind=engine)

# Include the API router

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to the FastAPI MySQL app!"}