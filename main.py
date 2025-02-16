from fastapi import FastAPI, Query,Path,Body
from pydantic import BaseModel,Field
from enum import Enum
from typing import Annotated, Literal

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/items/")
async def read_item(name: str, price: float):
    return {"name": name, "price": price}


class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return {"name": item.name, "price": item.price}


# //////////////////// Path Parameters////////////////////////

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


# //////////////////// Query Parameters////////////////////////

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/itemsQuery/")
async def read_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.get("/itemsQuery/{item_id}")
async def read_item1(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

@app.get("/itemsQuery1/{item_id}")
async def read_item2(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

# //////////////////// Request Body////////////////////////

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/items_body/")
async def create_item(item: Item):
    return item



@app.put("/items_body1/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


# //////////////////// Validation ////////////////////////

@app.get("/itemsValidation/")
async def read_items(
    q: Annotated[str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/itemsValidation1/")
async def read_items(q: Annotated[list[str] | None, Query()] = None):
    return {"q": q}



# //////////////////// Path Parameters ////////////////////////


@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=1, le=1000)],
    size: Annotated[float, Path(gt=0, lt=10.5)]
):
    return {"item_id": item_id, "size": size}


# //////////////////// Pydantic ////////////////////////



class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}  # 🚨 جلوگیری از ارسال پارامترهای اضافی
    limit: int = Field(100, gt=0, le=100)  # مقدار بین 1 تا 100 باشد
    offset: int = Field(0, ge=0)  # مقدار حداقل 0 باشد
    order_by: Literal["created_at", "updated_at"] = "created_at"  # مقدار ثابت از بین دو مقدار مشخص‌شده
    tags: list[str] = []  # لیستی از رشته‌ها

@app.get("/Pydantic/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query




# //////////////////// Field ////////////////////////

class Item(BaseModel):
    name: str  # نام محصول (اجباری)
    description: str | None = Field(
        default=None, title="توضیحات محصول", max_length=300
    )  # توضیحات اختیاری با حداکثر 300 کاراکتر
    price: float = Field(gt=0, description="قیمت باید بیشتر از صفر باشد")  # قیمت باید بیشتر از 0 باشد
    tax: float | None = None  # مالیات اختیاری

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    return {"item_id": item_id, "item": item}

class User(BaseModel):
    username: str = Field(..., example="john_doe", extra={"role": "admin"})
    age: int = Field(..., gt=0, example=30, extra={"unit": "years"})


# ////////////////////  ////////////////////////
