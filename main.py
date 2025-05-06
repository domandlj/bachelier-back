from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, ConfigDict, HttpUrl
from datetime import date, datetime
from typing import List, Dict, Optional
from pymongo.server_api import ServerApi
from bson import ObjectId
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
import time

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List the origins that are allowed to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)



# Load the .env file
load_dotenv()

# Access the MONGO_KEY
MONGO_KEY = os.getenv("MONGO_KEY")

# Connect to MongoDB

# Create a new client and connect to the server
client = MongoClient(MONGO_KEY, server_api=ServerApi('1'))


db = client["modeldb"]
collection = db["models"]
collection_board = db["board"]
reports = db["reports"]
ai = db["ai"]

# Pydantic Model to validate the JSON payload
class IndexedDBData(BaseModel):
    name: str
    code: str
    parameters: Dict[str, str]
    markdown: str
    paramNames: List[str]

# Pydantic Model with an ID field for database retrieval
class Model(BaseModel):
    name: str
    code: str
    parameters: Dict[str, str]
    markdown: str
    paramNames: List[str]
    id: Optional[str] = Field(None, alias="_id")
    
    @classmethod
    def from_mongo(cls, data):
        # Convert ObjectId to string
        data["_id"] = str(data.get("_id", ""))
        return cls(**data)
    
class AI(BaseModel):
    lecaps: str
    hd : str




class Lecap(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    ticker: str 
    fechaVencim: str 
    liqui_secu: Optional[str] = Field(alias='liqui_secu')
    dias: Optional[int] = None
    meses: Optional[float] = Field(alias='Meses', default=None)
    precio: Optional[float] = None
    total: Optional[float] = Field(alias='total', default=None)
    tna: Optional[float] = Field(alias='tna', default=None)
    tem: Optional[float] = None
    tea: Optional[float] = Field(alias='tea', default=None)
    price_var_daily : Optional[float] = Field(alias='price day %', default=None)
    price_var_ytd : Optional[float] = Field(alias='price ytd %', default=None)

class Bond(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    report : List[dict] = Field(alias='report', default=None)
    cf : Dict[str, List[dict]] = Field(alias='cf', default=None)

class Report(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    date: str
    lecaps: List[Lecap] = Field(alias='lecaps', default=None)
    bonares : Bond = Field(alias='bonares', default=None)
    globales : Bond = Field(alias='globales', default=None)
    cer : Bond = Field(alias='cer', default=None)


# POST endpoint to store a model
@app.post("/models/")
async def store_model(model: Model):
    model_dict = model.dict(exclude_unset=True)  # Avoid including fields not set
    model_dict.pop('_id', None)  # Ensure `_id` is not included in the document

    print(f"Model dict to be inserted: {model_dict}")  # Debugging print
    try:
        result = collection.insert_one(model_dict)
        print(f"Insert result: {result}")  # Debugging print
        return {"id": str(result.inserted_id)}  # Return the generated ID
    except Exception as e:
        print(f"Error inserting document: {e}")  # Debugging print
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/models/{id}", response_model=Model)
async def get_model(id: str):
    try:
        # Convert string ID to ObjectId
        object_id = ObjectId(id)
        model = collection.find_one({"_id": object_id})
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        # Convert the model to the Pydantic model
        
        return Model.from_mongo(model)
    except Exception as e:
        print(f"Error retrieving model: {e}")
        raise HTTPException(status_code=400, detail="Invalid ID format")


# GET endpoint to retrieve all models
@app.get("/models/", response_model=List[Model])
async def get_all_models():
    try:
        models = collection_board.find()
        return [Model.from_mongo(model) for model in models]
    except Exception as e:
        print(f"Error retrieving models: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/report", response_model=Report)
async def get_report():
    try:
        today = time.strftime("%Y-%m-%d")
        # Find the document for today's date

        # Find the last inserted document
        document = reports.find_one(
            sort=[("_id", -1)]  # Sort by `_id` in descending order
        )

        if not document:
            raise HTTPException(status_code=404, detail="No report found for today")
        return document
    except Exception as e:
        print(f"Error retrieving models: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/ai", response_model=AI)
async def get_report():
    try:
     
        # Find the last inserted document
        document = ai.find_one(
            sort=[("_id", -1)]  # Sort by `_id` in descending order
        )

        if not document:
            raise HTTPException(status_code=404, detail="No report found for today")
        return document
    except Exception as e:
        print(f"Error retrieving models: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")







class NewsItem(BaseModel):
    title: str
    summary: str
    url: HttpUrl
    source: Optional[str]

NewsData = Dict[str, List[NewsItem]]

# --- Mockup news data ---
mock_news_data: NewsData = {
    "USA": [
        {"title": "Tech Stocks Surge Amid AI Boom", "summary": "Major U.S. tech companies saw a 5% gain today.", "url": "https://news.example.com/tech-ai-boom", "source": "News Example"},
        {"title": "Inflation Eases Slightly", "summary": "Consumer prices rose 0.2% in March.", "url": "https://news.example.com/inflation-march", "source": "News Example"}
    ],
    "FRA": [
        {"title": "Paris Fashion Week Highlights", "summary": "Spring trends take over the runway.", "url": "https://news.example.com/paris-fashion", "source": "News Example"}
    ],
    "JPN": [
        {"title": "Tokyo Olympics Legacy Projects", "summary": "New sports facilities open across Tokyo.", "url": "https://news.example.com/tokyo-legacy", "source": "News Example"},
        {"title": "Sakura Season in Full Bloom", "summary": "Tourists flock to cherry blossom spots.", "url": "https://news.example.com/sakura-season", "source": "News Example"}
    ],
    "ARG": [
        {"title": "A nisman lo mataron", "summary": "a nisman lo mataron", "url": "https://news.example.com/arg-football", "source": "News Example"}
    ]
}


import requests
import xml.etree.ElementTree as ET


def parse_ambito_finanzas_rss(url="https://www.ambito.com/rss/pages/finanzas.xml"):
    # Fetch the RSS feed
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
        'Accept': 'application/rss+xml,application/xml'
    }

    response = requests.get(url, verify=False, headers=headers)
    response.raise_for_status()
    
    # Parse XML content
    root = ET.fromstring(response.content)
    channel = root.find('channel')
    items = channel.findall('item')
    
    # Initialize news data structure
    news_data=[]
    
    for item in items:
        # Extract relevant fields
        title_elem = item.find('title')
        description_elem = item.find('description')
        link_elem = item.find('link')
        
        title_text       = title_elem.text or ""
        summary_text     = description_elem.text or ""
        link_text        = link_elem.text or ""
        article = {
            "title": title_text,
            "summary": summary_text,
            "url": link_text,
            "source": "Ambito"
        }
        
        
        # Add to ARG category (all articles are from Argentinian source)
        news_data.append(article)
    
    return news_data



def parse_wsj_rss(url="https://feeds.content.dowjones.io/public/rss/RSSMarketsMain"):
    # Fetch the RSS feed
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
        'Accept': 'application/rss+xml,application/xml'
    }

    response = requests.get(url, verify=False, headers=headers)
    response.raise_for_status()
    
    # Parse XML content
    root = ET.fromstring(response.content)
    channel = root.find('channel')
    items = channel.findall('item')
    
    # Initialize news data structure
    news_data = []
    
    for item in items:
        # Extract relevant fields
        title_elem = item.find('title')
        description_elem = item.find('description')
        link_elem = item.find('link')
        
        title_text       = title_elem.text or ""
        summary_text     = description_elem.text or ""
        link_text        = link_elem.text or ""
        article = {
            "title": title_text,
            "summary": summary_text,
            "url": link_text,
            "source": "Wall Street Journal"
        }
                
        news_data.append(article)
    
    return news_data

#https://news.google.com/rss/search?q=source:Financial+Times+UK&hl=en-US&gl=US&ceid=US:en


def parse_ft_rss(url="https://news.google.com/rss/search?q=source:Financial+Times+UK&hl=en-US&gl=US&ceid=US:en"):
    # Fetch the RSS feed
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
        'Accept': 'application/rss+xml,application/xml'
    }

    response = requests.get(url, verify=False, headers=headers)
    response.raise_for_status()
    
    # Parse XML content
    root = ET.fromstring(response.content)
    channel = root.find('channel')
    items = channel.findall('item')
    
    # Initialize news data structure
    news_data = []
    
    for item in items:
        # Extract relevant fields
        title_elem = item.find('title')
        #description_elem = item.find('description')
        link_elem = item.find('link')
        
        title_text       = title_elem.text.removesuffix(" - Financial Times") or ""
        #summary_text     = description_elem.text or ""
        link_text        = link_elem.text or ""
        article = {
            "title": title_text,
            "summary": "",
            "url": link_text,
            "source": "Financial Times"
        }
                
        news_data.append(article)
    return news_data

def parse_jpn_rss(url="https://www.japantimes.co.jp/feed/"):
    # Fetch the RSS feed
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36',
        'Accept': 'application/rss+xml,application/xml'
    }

    response = requests.get(url, verify=False, headers=headers)
    response.raise_for_status()
    
    # Parse XML content
    root = ET.fromstring(response.content)
    channel = root.find('channel')
    items = channel.findall('item')
    
    # Initialize news data structure
    news_data = []
    
    for item in items:
        if item.find('category').text != "BUSINESS":
            continue

        title_elem = item.find('title')
        description_elem = item.find('description')
        link_elem = item.find('link')
        
        title_text       = title_elem.text or ""
        summary_text     = description_elem.text or ""
        link_text        = link_elem.text or ""
        article = {
            "title": title_text,
            "summary": summary_text,
            "url": link_text,
            "source": "The Japan Times"
        }
                
        news_data.append(article)
    return news_data

# GET endpoint for news data
@app.get("/news", response_model=NewsData)
async def get_news():
    """
    Retrieve mock news data per country.
    Response format: { ISO_A3: [NewsItem, ...], ... }
    """
    news_data: NewsData = {
        "USA": parse_wsj_rss(),
        "FRA": [],
        "JPN": parse_jpn_rss(),
        "GBR": parse_ft_rss(),
        "ARG": parse_ambito_finanzas_rss()
    }
    return news_data



if __name__ == "__main__":
    import uvicorn
     #uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
