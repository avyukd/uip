from fastapi import FastAPI, Query, Depends, HTTPException
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from loader import load_all_stocks
from model import Model

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/load_stocks")
def load_stocks(model: Model):
    # want to sort by upside
    stocks = load_all_stocks(user_input = model.dict())
    stocks.sort(key=lambda x: x["upside"], reverse=True)
    return {"stocks": stocks}