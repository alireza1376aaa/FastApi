
from fastapi import FastAPI, Query,Path,Body,Cookie,Response,Header
from pydantic import BaseModel,Field
from enum import Enum
from typing import Annotated, Literal
from datetime import datetime, time, timedelta
from typing import Annotated,Union
from uuid import UUID


app = FastAPI()

    
# //////////////////// set defult  ////////////////////////

class Item1(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2
                }
            ]
        }
    }


@app.put("/items1/{item_id}")
async def update_item(item_id: int, item: Item1):
    return {"item_id": item_id, "item": item}


class Item2(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(default=None, examples=["A very nice Item"])
    price: float = Field(examples=[35.4])
    tax: float | None = Field(default=None, examples=[3.2])

@app.put("/items2/{item_id}")
async def update_item(item_id: int, item: Item2):
    return {"item_id": item_id, "item": item}



class Item3(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.put("/items3/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[
        Item3,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2
                }
            ]
        )
    ]
):
    return {"item_id": item_id, "item": item}


@app.put("/items4/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[
        Item3,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2
                },
                {
                    "name": "Bar",
                    "price": 20.0
                },
                {
                    "name": "Baz",
                    "price": "thirty five point four"
                }
            ]
        )
    ]
):
    return {"item_id": item_id, "item": item}


@app.put("/items5/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[
        Item3,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2
                    }
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4"
                    }
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four"
                    }
                }
            }
        )
    ]
):
    return {"item_id": item_id, "item": item}



# //////////////////Extra Data Types///////////////////////


@app.put("/items6/{item_id}")
async def read_items(
    item_id: UUID,  # شناسه یکتا برای آیتم
    start_datetime: Annotated[datetime, Body()],  # زمان شروع پردازش
    end_datetime: Annotated[datetime, Body()],  # زمان پایان پردازش
    process_after: Annotated[timedelta, Body()],  # پردازش بعد از مدت مشخص
    repeat_at: Annotated[time | None, Body()] = None,  # اجرای مجدد در یک ساعت خاص
):
    start_process = start_datetime + process_after  # محاسبه زمان شروع پردازش
    duration = end_datetime - start_process  # مدت زمان پردازش

    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }


# //////////////////Cookie///////////////////////

@app.get("/items7/")
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    return {"ads_id": ads_id}


@app.get("/set-coocc/")
async def set_cookie(response: Response):
    response.set_cookie(key="session_id", value="ABC123XYZ", httponly=True, max_age=3600)
    return {"message": "Cookie has been set!"}

@app.get("/getcooc/")
async def get_user(session_id: Annotated[str | None, Cookie()] = None):
    return {"session_id": session_id}


# 🎯 مدل کوکی با جلوگیری از دریافت مقادیر اضافه
class Cookies(BaseModel):
    model_config = {"extra": "forbid"}  # جلوگیری از دریافت کوکی‌های اضافی
    session_id: str
    fatebook_tracker: Union[str, None] = None
    googall_tracker: Union[str, None] = None

@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies

# //////////////////Header///////////////////////

@app.get("/items8/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}


@app.get("/secure-data/")
async def secure_data(x_token: Annotated[str | None, Header()] = None):
    if x_token != "my_secret_token":
        return {"error": "Invalid Token!"}
    return {"message": "Access Granted"}


# 🎯 مدل هدر با جلوگیری از دریافت مقادیر اضافه
class CommonHeaders(BaseModel):
    # model_config = {"extra": "forbid"}  # جلوگیری از دریافت هدرهای اضافی
    host: str
    save_data: bool = False  # مقدار پیش‌فرض به `False` تغییر یافت    
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []

@app.get("/items9/")
async def read_items(headers: Annotated[CommonHeaders, Header()]):
    return headers

@app.get("/set-headers/")
async def set_headers(response: Response):
    response.headers["X-Request-ID"] = "abc123"
    response.headers["Cache-Control"] = "no-cache"
    return {"message": "Headers have been set!"}

@app.get("/get-headers/")
async def get_headers(headers: Annotated[CommonHeaders, Header()]):
    return headers