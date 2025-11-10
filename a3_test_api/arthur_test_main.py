# Arthur Nguyen
# Assignment 3, Exercise 3
# test_main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from your test API!"}

@app.get("/ping")
def ping():
    return {"status": "ok"}