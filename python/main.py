import os
import logging
import pathlib
import json
import sqlite3
import hashlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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


#Function to add a single item to DB
def AddItemDB(name, category, image_name):
    conn = sqlite3.connect('mercari.sqlite3')
    c = conn.cursor()
    c.execute("SELECT id FROM categories WHERE name = ?", (category,))
    category_id = c.fetchone()[0]
    c.execute("INSERT INTO items (name, category_id, image_filename) VALUES (?, ?, ?)", (name, category_id, image_filename))
    conn.commit()
    conn.close()

def ShowDB():
    conn = sqlite3.connect('mercari.sqlite3')
    c = conn.cursor()
    c.execute("""SELECT items.id, items.name, categories.name AS category_name, items.image_filename
                FROM items
                JOIN categories ON items.category_id = categories.id;
                """)
    listOfItems = c.fetchall()
    items = [{'id': item[0], 'name': item[1], 'category_name': item[2], 'image_filename': item[3]} for item in listOfItems]

    conn.commit()
    conn.close()
    return items

def SearchDB(keyword):
    conn = sqlite3.connect('mercari.sqlite3')
    c = conn.cursor()
    c.execute("SELECT * from items WHERE name = (?)", (keyword,))
    listOfItems = c.fetchall()
    conn.commit()
    conn.close()
    return listOfItems



def hashingImage(image: UploadFile = File(...)):
    content = image.file.read()
    sha256 = hashlib.sha256()
    sha256.update(content)
    return sha256.hexdigest()


@app.get("/items")
def list_items():
    return ShowDB()


@app.get("/search")
async def search_item(keyword: str = Query(...)):
    return SearchDB(keyword)



@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):

    logger.info(f"Receive item, name: {name}, category: {category}")

    hashedImage = hashingImage(image)

    AddItemDB(name, category, hashedImage)

    image_path = images / hashedImage
    with open(image_path, "wb") as file:
        file.write(image.file.read())

    return {"message": f"item received with name: {name}, category: {category}, image: {hashedImage}"}


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