# Day 3 — HTTP & FastAPI Basics

**Name:** Polagani Harinadh Babu
**Date:** 28 October 2026
**Topic:** HTTP, FastAPI, Pydantic v2, Validation, Response Models, Error Handling and File Uploads

## 1. HTTP Methods and Status Codes

HTTP is an application-layer protocol that allows clients and servers to communicate through requests and responses.

| Method | Purpose                     | Use case                           | Example status code |
| ------ | --------------------------- | ---------------------------------- | ------------------- |
| GET    | Retrieve data               | Fetch an item by ID                | 200 OK              |
| POST   | Create or process data      | Create a new item                  | 201 Created         |
| PUT    | Replace a resource          | Replace an existing item's details | 200 OK              |
| PATCH  | Partially update a resource | Update only an item's price        | 200 OK              |
| DELETE | Remove a resource           | Delete an item                     | 204 No Content      |

### Common HTTP status codes

- **200 OK:** The request was successful.
- **201 Created:** A resource was successfully created.
- **204 No Content:** The operation succeeded without a response body.
- **400 Bad Request:** The request contains invalid input.
- **401 Unauthorized:** Authentication is missing or invalid.
- **403 Forbidden:** The user does not have permission.
- **404 Not Found:** The requested resource does not exist.
- **409 Conflict:** The request conflicts with existing data.
- **422 Unprocessable Content:** Request validation failed.
- **500 Internal Server Error:** An unexpected server-side error occurred.

### Idempotency and safety

A safe method is intended not to change server state. GET is the standard example.

An idempotent operation has the same intended effect when repeated with the same request. PUT and DELETE are defined as idempotent in HTTP semantics. POST is not guaranteed to be idempotent.

## 2. FastAPI Routes and Parameter Types

FastAPI is a Python framework for building APIs. It uses Python type hints to parse and validate inputs and generates API documentation automatically.

### Path parameters

Path parameters identify a particular resource.

Example:

`GET /items/1`

Here, `1` is the item ID.

### Query parameters

Query parameters commonly filter or paginate a collection.

Example:

`GET /items?limit=10`

Here, `limit` specifies the maximum number of items requested.

### Request body

A request body contains data sent by the client, commonly as JSON when creating a resource.

Example:

```json
{
  "name": "Notebook",
  "price": 50
}
```

### Automatic documentation

FastAPI provides:

- `/docs` — Interactive Swagger UI documentation.
- `/redoc` — ReDoc API documentation.

These endpoints are generated from the application's routes, types and models by default.

## 3. Pydantic v2 Request Model and Validation

Pydantic validates incoming data against a declared model and its constraints.

For this assignment, the item model requires:

- `name`: a non-empty string.
- `price`: a number greater than zero.

Example:

```python
from pydantic import BaseModel, Field, field_validator

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Item name must not be blank")
        return value
```

`Field` defines validation constraints, while `field_validator` performs custom validation. The validator strips surrounding whitespace and rejects names containing only whitespace.

Invalid request data normally produces a `422 Unprocessable Content` response before the route's business logic completes.

## 4. Response Model and Error Handling

A response model defines the expected shape of the API output.

For example:

```python
from pydantic import BaseModel

class ItemOut(BaseModel):
    id: int
    name: str
    price: float
```

Using `response_model=ItemOut` documents and validates the output structure and helps filter fields that are not part of the public response model.

### Error handling

FastAPI's `HTTPException` allows a route to return a deliberate HTTP error.

Example:

```python
from fastapi import HTTPException

raise HTTPException(
    status_code=404,
    detail="Item not found"
)
```

### Status code choices

- `200 OK` is used when an item is retrieved successfully.
- `201 Created` is used when a new item is created.
- `404 Not Found` is used when the requested item does not exist.
- `422 Unprocessable Content` is used for request validation failures.
- `400 Bad Request` can be used for a request that violates a route-level rule.
- `204 No Content` is suitable for a successful operation that returns no body.

Using appropriate status codes makes API behavior clearer to clients.

## 5. File Upload Safety Notes

FastAPI supports uploaded files through `UploadFile` and `File`.

The upload endpoint in this assignment returns the uploaded filename and declared content type as demonstration metadata.

Before deploying a file upload endpoint to production, I would add these safeguards:

1. **File-size limits:** Reject files that exceed the allowed size.
2. **File type validation:** Allow only permitted file types and validate the actual content instead of trusting the extension or declared MIME type.
3. **Safe filenames:** Generate a server-side storage name instead of trusting the filename provided by the client.
4. **Safe storage:** Store files in an appropriately restricted location and prevent path traversal.
5. **Access control:** Require appropriate authorization for sensitive uploads.
6. **Clear error responses:** Reject invalid uploads with appropriate status codes and messages.

Sensitive information, passwords and internal exception details should not be exposed in responses or logs.

## 6. Setup Instructions

### Requirements

- Python 3.10 or later
- pip
- A terminal or command prompt

### Step 1: Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### Step 2: Install dependencies

```bash
pip install fastapi uvicorn python-multipart
```

`python-multipart` is required for handling form data and file uploads.

### Step 3: Run the application

Save the application code in `main.py` and execute:

```bash
uvicorn main:app --reload
```

### Step 4: Open the API documentation

- API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc documentation: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 7. Example Requests and Responses

### Create an item

**Request:** `POST /items`

```json
{
  "name": "Notebook",
  "price": 50
}
```

**Expected response:** `201 Created`

```json
{
  "id": 1,
  "name": "Notebook",
  "price": 50.0
}
```

### Get an item by ID

**Request:** `GET /items/1`

**Expected response:** `200 OK`

```json
{
  "id": 1,
  "name": "Notebook",
  "price": 50.0
}
```

### List items

**Request:** `GET /items?limit=10`

**Expected response:** `200 OK`

```json
[
  {
    "id": 1,
    "name": "Notebook",
    "price": 50.0
  }
]
```

### Request a missing item

**Request:** `GET /items/999`

**Expected response:** `404 Not Found`

```json
{
  "detail": "Item not found"
}
```

### Submit an invalid price

**Request:** `POST /items`

```json
{
  "name": "Notebook",
  "price": -10
}
```

**Expected response:** `422 Unprocessable Content`

The response contains validation details explaining why the price is invalid.

### Upload a file

**Request:** `POST /upload`

Select a file using the Swagger UI file input.

**Expected response:** `200 OK`

```json
{
  "filename": "sample.pdf",
  "content_type": "application/pdf"
}
```

The returned filename and content type depend on the uploaded file. The upload endpoint demonstrates metadata handling; it does not permanently save the file.

## 8. Edge Cases Tested

| Test case                                           | Expected result           |
| --------------------------------------------------- | ------------------------- |
| Create an item with a valid name and positive price | 201 Created               |
| Omit the required name                              | 422 Unprocessable Content |
| Omit the required price                             | 422 Unprocessable Content |
| Send a negative price or zero price                 | 422 Unprocessable Content |
| Send a blank or whitespace-only name                | 422 Unprocessable Content |
| Request an existing item                            | 200 OK                    |
| Request an item that does not exist                 | 404 Not Found             |
| Use a non-integer item ID                           | 422 Unprocessable Content |
| Set `limit=0` or `limit=101`                        | 422 Unprocessable Content |
| Upload a file through `/upload`                     | 200 OK with file metadata |

**Testing note:** These are the expected results from the implementation and constraints. Run the requests in `/docs` and record the actual results before claiming that all tests have passed.

## 9. Reflection — What I Learned

Through this assignment, I learned how HTTP methods and status codes are used to design clear APIs. I practiced creating GET and POST endpoints in FastAPI, handling path and query parameters, validating incoming JSON using Pydantic v2, and defining response models.

I also learned how to raise `HTTPException` for missing resources and how to accept uploaded files using `UploadFile`. Finally, I understood the importance of validating inputs, protecting internal information, selecting appropriate status codes and adding file upload safeguards before production.

**Lesson learned:** Input validation, clear response models and meaningful HTTP status codes make APIs easier to understand, safer and more reliable.

## 10. GitHub Repository

Suggested folder structure:

```text
your-repository/
└── Day-3/
    ├── README.md
    └── main.py
```

### Git commands

From the root of your existing repository:

```bash
git add Day-3/
git commit -m "Complete Day 3 HTTP and FastAPI assignment"
git push
```

**GitHub repository / assignment link:** Add your actual repository URL after pushing the files.

**Screenshots:** Capture your running Swagger UI and successful/failed API responses from your own environment and add them to the repository if required by your submission process.
