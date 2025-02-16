from fastapi import FastAPI
import time
import asyncio

app = FastAPI()



class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    
item = Item(name="Laptop", price=1500.0, description="Powerful laptop", tax=100.0)
print(item.dict())
