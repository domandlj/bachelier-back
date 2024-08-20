from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from pymongo.server_api import ServerApi
from bson import ObjectId
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os


app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # List the origins that are allowed to make requests
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


if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="0.0.0.0", port=8000)
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

