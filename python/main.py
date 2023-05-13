import os
import logging
import pathlib
import json
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [os.environ.get('FRONT_URL', 'http://localhost:3000')]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


inventory = {}


def RetrieveItems(filename):
    with open(filename, "r") as f:
        try:
            data = json.load(f)
            if "items" in data:
                inventory = data
            else:
                inventory = {'items': []}
        except:
            inventory = {'items': []}
    return inventory


def hashingImage(image: UploadFile = File(...)):
    content = image.file.read()
    sha256 = hashlib.sha256()
    sha256.update(content)
    return sha256.hexdigest()


@app.get("/")
def root():
    value = RetrieveItems("items.json")
    return value


@app.get("/items")
def list_items():
    inventory = RetrieveItems("items.json")
    return inventory


@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):

    logger.info(f"Receive item, name: {name}, category: {category}")

    hashedImage = hashingImage(image)

    newItem = {
        'name': name,
        'category': category,
        'image': hashedImage
    }

    inventory = RetrieveItems("items.json")

    inventory["items"].append(newItem)

    with open("items.json", "w") as file:
        json.dump(inventory, file)

    image_path = images / hashedImage
    with open(image_path, "wb") as file:
        file.write(image.file.read())

    return {"message": f"item received with name: {name}, category: {category}, image: {hashedImage}"}


@app.get("/items/{item_id}")
async def get_item_id(item_id: int):
    inventory = RetrieveItems("items.json")

    item_id -= 1

    if item_id >= len(inventory["items"]) or item_id == -1:
        raise HTTPException(status_code=404, detail="Item Id does not exist")

    specificItem = inventory["items"][item_id]
    return specificItem, item_id

@app.get("/image/{image_filename}")
async def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.info(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)