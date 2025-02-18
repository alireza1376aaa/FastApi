
from fastapi import FastAPI, Query,Path,Body,Cookie,Response,Header,status,Form ,File,UploadFile,HTTPException,Request,Depends,APIRouter
from pydantic import BaseModel,Field,EmailStr
from enum import Enum
from typing import Annotated, Literal
from datetime import datetime, time, timedelta
from typing import Annotated,Union
from uuid import UUID
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import json
app = FastAPI()

# ////////////////////////////////Path Operation Configuration////////////////////////////////////

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()

@app.post("/items1/", response_model=Item, tags=["items"])
async def create_item(item: Item):
    return item

@app.get("/items2/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]

@app.post(
    "/items3/",
    response_model=Item,
    summary="Create an item",
    description="Create an item with all the information, including name, description, price, tax, and tags."
)
async def create_item(item: Item):
    return item

@app.post(
    "/item4/",
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


# /////////////////////jsonable_encoder//////////////////////////

# پایگاه داده‌ی جعلی
fake_db = {}

# تعریف مدل Pydantic
class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None

app = FastAPI()

# مسیر برای به‌روزرسانی آیتم
@app.put("/items5/{id}")
def update_item(id: str, item: Item):
    # تبدیل مدل Pydantic به ساختار سازگار با JSON
    json_compatible_item_data = jsonable_encoder(item)
    x =  json.dumps(json_compatible_item_data)
    # ذخیره‌سازی در پایگاه داده‌ی جعلی
    fake_db[id] = json_compatible_item_data

    return {"message": "Item updated successfully", "item": json_compatible_item_data}


# //////////////////////put path/////////////////////////


class Item23(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []

# دیتابیس جعلی
items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

@app.put("/items8/{item_id}", response_model=Item23)
async def update_item(item_id: str, item: Item23):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded  # جایگزینی کامل داده‌ها
    return update_item_encoded


@app.patch("/items9/{item_id}", response_model=Item23)
async def update_item(item_id: str, item: Item23):
    stored_item_data = items[item_id]  # دریافت داده‌های فعلی
    stored_item_model = Item23(**stored_item_data)  # تبدیل به مدل Pydantic
    update_data = item.model_dump(exclude_unset=True)  # حذف مقادیر `None`
    
    # بروزرسانی داده‌های قدیمی با داده‌های جدید
    updated_item = stored_item_model.model_copy(update=update_data)
    
    # ذخیره‌سازی تغییرات در دیتابیس
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item

# //////////////////////Dependency Injection/////////////////////////

# تابع وابستگی: پردازش پارامترهای عمومی
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

# استفاده از وابستگی در مسیرهای API
@app.get("/items10/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

@app.get("/users11/")
async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

@app.get("/products/")
async def get_products(filters: dict = Depends(common_parameters)):
    return filters

CommonsDep = Annotated[dict, Depends(common_parameters)]

@app.get("/items12/")
async def read_items(commons: CommonsDep):
    return commons


# دیتابیس جعلی
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# تعریف کلاس برای مدیریت پارامترهای جستجو
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

# استفاده از کلاس به عنوان وابستگی
@app.get("/items13/")
async def read_items(commons: Annotated[CommonQueryParams, Depends()]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items13": items})
    return response



# وابستگی اصلی: مقدار q را از Query Parameters استخراج می‌کند
def query_extractor(q: str | None = None):
    return q

# وابستگی جدید که از query_extractor استفاده می‌کند
def query_or_cookie_extractor(
    q: Annotated[str | None, Depends(query_extractor)],  # وابسته به query_extractor
    last_query: Annotated[str | None, Cookie()] = None  # خواندن مقدار قبلی از کوکی
):
    if not q:
        return last_query  # اگر q موجود نبود، مقدار کوکی را برگردان
    return q


@app.get("/items14/")
async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor)]
):
    return {"q_or_cookie": query_or_default}



# تابع بررسی توکن (X-Token)
async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

# تابع بررسی کلید امنیتی (X-Key)
async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")

# استفاده از این وابستگی‌ها در دکوراتور مسیر
@app.get("/items15/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]

# //////////////////////////////////////
router = APIRouter(
    prefix="/secure",
    tags=["secure"],
    dependencies=[Depends(verify_token), Depends(verify_key)]
)

@router.get("/dashboard/")
async def dashboard():
    return {"message": "Welcome to the secure dashboard"}

@router.get("/settings/")
async def settings():
    return {"message": "Secure settings"}


# ///////////////////////// Dependencies with yield////////////////////////////////
# شبیه‌سازی یک کلاس پایگاه داده
class DBSession:
    def __init__(self):
        print("✅ Database session started")
    
    def close(self):
        print("🛑 Database session closed")

# وابستگی برای مدیریت اتصال به دیتابیس
async def get_db():
    db = DBSession()  # ایجاد اتصال
    try:
        yield db  # ارائه اتصال به مسیر API
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()  # بستن اتصال پس از اتمام درخواست

# استفاده از `get_db` در مسیر API
@app.get("/items16/")
async def read_items(db: DBSession = Depends(get_db)):
    return {"message": "Database connection is active"}




# وابستگی اول: اتصال به دیتابیس
async def dependency_a():
    print("✅ Dependency A started")
    yield "A"
    print("🛑 Dependency A closed")

# وابستگی دوم که به `dependency_a` نیاز دارد
async def dependency_b(dep_a: str = Depends(dependency_a)):
    print(f"✅ Dependency B started, using {dep_a}")
    yield "B"
    print(f"🛑 Dependency B closed, releasing {dep_a}")

# وابستگی سوم که به `dependency_b` نیاز دارد
async def dependency_c(dep_b: str = Depends(dependency_b)):
    print(f"✅ Dependency C started, using {dep_b}")
    yield "C"
    print(f"🛑 Dependency C closed, releasing {dep_b}")

# مسیر API که وابستگی `dependency_c` را دارد
@app.get("/sub-dependencies/")
async def sub_dependencies(data: str = Depends(dependency_c)):
    return {"message": f"Using dependency: {data}"}



data = {
    "plumbus": {"owner": "Morty"},
    "portal-gun": {"owner": "Rick"},
}

async def get_username():
    try:
        yield "Rick"  # مقدار ثابت به عنوان نام کاربر
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")

@app.get("/items17/{item_id}")
async def get_item(item_id: str, username: str = Depends(get_username)):
    if item_id not in data:
        raise HTTPException(status_code=404, detail="Item not found")
    if data[item_id]["owner"] != username:
        raise HTTPException(status_code=403, detail="Access denied")
    return data[item_id]


# /////////////////////////////////////////////////////////
