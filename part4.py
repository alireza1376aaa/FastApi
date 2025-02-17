
from fastapi import FastAPI, Query,Path,Body,Cookie,Response,Header,status,Form ,File,UploadFile,HTTPException,Request
from pydantic import BaseModel,Field,EmailStr
from enum import Enum
from typing import Annotated, Literal
from datetime import datetime, time, timedelta
from typing import Annotated,Union
from uuid import UUID
from fastapi.responses import JSONResponse
app = FastAPI()

# ////////////////////////////////Path Operation Configuration////////////////////////////////////

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()

@app.post("/items/", response_model=Item, tags=["items"])
async def create_item(item: Item):
    return item

@app.get("/items/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]

@app.post(
    "/items/",
    response_model=Item,
    summary="Create an item",
    description="Create an item with all the information, including name, description, price, tax, and tags."
)
async def create_item(item: Item):
    return item

@app.post(
    "/items/",
    response_model=Item,
    summary="Create an item",
    response_description="The created item"
)
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: Each item must have a name.
    - **description**: A long description.
    - **price**: Required.
    - **tax**: If the item doesn’t have a tax, you can omit this.
    - **tags**: A set of unique tag strings for this item.
    """
    return item

@app.get("/elements/", tags=["items"], deprecated=True)
async def read_elements():
    return [{"item_id": "Foo"}]