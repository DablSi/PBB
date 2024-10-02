from fastapi import FastAPI, HTTPException
import os
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

memes = {}

MONGO_URI = os.getenv("MONGO_URI", default="mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

db = client.pbb
collection = db['memes']


@app.get("/memes/{id}")
async def get_meme(id: str):
    meme = collection.find_one({"_id": ObjectId(id)})

    if meme is None:
        raise HTTPException(status_code=404)
    
    return {
        "id": id,
        "text": meme["text"]
    }


@app.post("/memes")
async def create_meme(text: str):
    return str(collection.insert_one({"text": text}).inserted_id)


@app.delete("/memes/{id}")
async def delete_meme(id: str):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404)

    return {"message": "OK"}


@app.put("/memes/{id}")
async def update_meme(id: str, text: str):
    old_text = collection.find_one({"_id": ObjectId(id)})["text"]

    if old_text is None:
        raise HTTPException(status_code=404)

    update_result = collection.update_one(
        {"_id": ObjectId(id)}, {"$set": {"text": text}})
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404)
    

    return {
        "old": {
            "id": id,
            "text": old_text
        },
        "new": {
            "id": id,
            "text": text
        }
    }


@app.get("/memes")
async def get_all_memes():
    return [
        {
            "id": str(meme["_id"]),
            "text": meme["text"]
        }
        for meme in collection.find()
    ]