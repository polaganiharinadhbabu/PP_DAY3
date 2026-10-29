
from typing import Annotated

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(
    title="PP_DAY3 - HTTP & FastAPI Basics",
    description="Day 3 assignment covering HTTP methods, validation, "
                "response models, error handling, and file uploads.",
    version="1.0.0",
)


# Pydantic request model
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Item name cannot be empty")
        return value


# Model for partial updates
class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Item name cannot be empty")
        return value


# Response model
class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float


# In-memory storage for practice
items: dict[int, ItemOut] = {}
next_item_id = 1


@app.get("/")
def home():
    return {
        "message": "PP_DAY3 FastAPI application is running",
        "docs": "/docs",
    }


# GET: Retrieve all items
@app.get("/items", response_model=list[ItemOut])
def list_items(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return list(items.values())[:limit]


# GET: Retrieve one item
@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int):
    if item_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Item ID must be positive",
        )

    item = items.get(item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    return item


# POST: Create an item
@app.post(
    "/items",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
)
def create_item(payload: ItemCreate):
    global next_item_id

    item = ItemOut(
        id=next_item_id,
        name=payload.name,
        price=payload.price,
    )

    items[next_item_id] = item
    next_item_id += 1

    return item


# PUT: Replace an existing item
@app.put("/items/{item_id}", response_model=ItemOut)
def replace_item(item_id: int, payload: ItemCreate):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    item = ItemOut(
        id=item_id,
        name=payload.name,
        price=payload.price,
    )

    items[item_id] = item
    return item


# PATCH: Update selected fields
@app.patch("/items/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate):
    existing = items.get(item_id)

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    changes = payload.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update",
        )

    updated = existing.model_copy(update=changes)
    items[item_id] = updated

    return updated


# DELETE: Remove an item
@app.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    del items[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# File upload: validate file type and size
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    allowed_types = {
        "text/plain",
        "application/pdf",
        "image/png",
        "image/jpeg",
    }
    max_size = 5 * 1024 * 1024  # 5 MB

    try:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type. Upload TXT, PDF, PNG, or JPEG.",
            )

        content = await file.read(max_size + 1)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 5 MB limit",
            )

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(content),
            "message": "File validated successfully. File is not saved.",
        }

    finally:
        await file.close()
