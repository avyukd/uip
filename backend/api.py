from fastapi import FastAPI, Query, Depends, HTTPException, File, UploadFile
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from loader import load_all_options, load_all_stocks, save_scenario, load_scenario
from model import Model
import json
import shutil
from utils import delete_scenario, get_scenarios
import pandas as pd

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_portfolio")
def upload_portfolio(portfolio_csv_wrapper: UploadFile, name: str):
    portfolio_csv = portfolio_csv.file
    file_location = f"tmp/{name}_{portfolio_csv_wrapper.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(portfolio_csv, file_object) 
        
    

@app.post("/save_scenario")
def save_scenario_endpoint(model: Model, name: str):
    save_scenario(model.dict(), name)
    return {"status": "success"}

@app.get("/load_scenario/{name}")
def load_scenario_endpoint(name: str):
    try:
        return load_scenario(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Scenario not found.")

@app.get("/load_all_scenarios")
def load_all_scenarios():
    return {"scenarios": get_scenarios()}

@app.delete("/delete_scenario/{name}")
def delete_scenario_endpoint(name: str):
    try:
        delete_scenario(name)
        return {"status": "success"} 
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Scenario not found.")

@app.post("/load_options")
def load_options(model: Model):
    options = load_all_options(user_input=model.dict())
    options.sort(key=lambda x: x["upside"], reverse=True)
    return {"options": options}

@app.post("/load_stocks")
def load_stocks(model: Model):
    # want to sort by upside
    stocks = load_all_stocks(user_input = model.dict())
    stocks.sort(key=lambda x: x["upside"], reverse=True)
    return {"stocks": stocks}

@app.get("/get_defaults")
def get_defaults():
    defaults = json.load(open("defaults.json"))
    return defaults

@app.get("/get_writeup/{ticker}")
def get_writeup(ticker: str):
    try:
        writeup = open("markdown/" + ticker + ".md").read()
        return {"writeup": writeup}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No writeup found for " + ticker)
