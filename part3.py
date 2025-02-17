
from fastapi import FastAPI, Query,Path,Body,Cookie,Response,Header,status,Form ,File,UploadFile,HTTPException,Request
from pydantic import BaseModel,Field,EmailStr
from enum import Enum
from typing import Annotated, Literal
from datetime import datetime, time, timedelta
from typing import Annotated,Union
from uuid import UUID
from fastapi.responses import JSONResponse


app = FastAPI()


# //////////////////// response_model  ////////////////////////

class UserIn(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    username: str
    email: str

@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user  # ✅ رمز عبور از پاسخ حذف می‌شود!

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

@app.get("/items/{item_id}", response_model=Item,response_model_include={"price"},)
async def read_item(item_id: str):
    return items[item_id]


# //////////////////// Extra Models //////////////////// 


# مدل ورودی (شامل رمز عبور)
class UserIn1(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None

# مدل خروجی (بدون رمز عبور)
class UserOut1(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

# مدل ذخیره‌سازی در پایگاه داده (رمز عبور هش شده)
class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: str | None = None

# تابع هش کردن رمز عبور (نمونه اولیه، غیرقابل استفاده در محیط واقعی)
def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password

# تابع ذخیره‌سازی کاربر (رمز عبور هش می‌شود)
def fake_save_user(user_in: UserIn1):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db

# مسیر ایجاد کاربر - خروجی نباید رمز عبور داشته باشد
@app.post("/user/", response_model=UserOut1)
async def create_user(user_in: UserIn1):
    user_saved = fake_save_user(user_in)
    return user_saved



# مدل آیتم
class Item3(BaseModel):
    name: str
    description: str

# لیست داده‌ها
items = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]

# مسیر دریافت لیست آیتم‌ها
@app.get("/items/", response_model=list[Item3])
async def read_items():
    print('ssssssssssssssssssssssss')
    return items

# //////////////////// Response Status Codes //////////////////// 

@app.post("/users207/", status_code=status.HTTP_207_MULTI_STATUS)
async def create_user():
    return {"message": "User created successfully"}


# //////////////////// form data //////////////////// 


@app.post("/login/")
async def login(
    username: Annotated[str, Form()], 
    password: Annotated[str, Form()]
):
    return {"username": username}


@app.post("/register/")
async def register(
    username: str = Form( min_length=3, max_length=15, description="نام کاربری"),
    password: str = Form( min_length=6, description="رمز عبور باید حداقل ۶ کاراکتر باشد"),
    email: str = Form(alias="user-email", description="ایمیل کاربر",default='not-provided@example.com'),
):
    return {"username": username, "email": email}

class FormData(BaseModel):
    username: str
    password: str

@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):  # داده‌های فرم به مدل Pydantic منتقل می‌شوند
    return data

# //////////////////// file //////////////////// 


@app.post('/file/',status_code=status.HTTP_201_CREATED)
async def file_add(file : Annotated[bytes,File()]):
    return('file add seccssusfully')

@app.post('/fileupload/',status_code=status.HTTP_201_CREATED)
async def file_upload(file : UploadFile):
    print('sadasdasd')
    x = await file.read()
    y=await file.write(b"\nNew line added!")
    file_data = {
        'file.filename':file.filename,
        'file.content_type':file.content_type,
        'await file.read(size)':x,
    }
    await file.close()
    return (file_data)

# //////////////////// file form //////////////////// 

@app.post("/upload/")
async def upload_file_with_form(
    file: Annotated[UploadFile, File()],
    description: Annotated[str, Form()]
):
    return {
        "filename": file.filename,
        "description": description
    }


# //////////////////// file form //////////////////// 

items = {"foo": "The Foo Wrestlers"}

async def read_item_header(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

app = FastAPI()

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )

@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}




