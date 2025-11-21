import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path

from database import db, create_document, get_documents
from schemas import Recommendation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# -------------------------
# Content management endpoints
# -------------------------

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Accept an uploaded image and store it in uploads/; return a public URL path."""
    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Ensure unique filename
    safe_name = file.filename.replace(" ", "_")
    target = UPLOAD_DIR / safe_name
    # If exists, add suffix counter
    counter = 1
    while target.exists():
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        target = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
        counter += 1

    data = await file.read()
    with open(target, "wb") as f:
        f.write(data)

    return {"path": f"/uploads/{target.name}"}

@app.get("/uploads/{filename}")
async def get_uploaded_image(filename: str):
    path = UPLOAD_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)

class RecommendationIn(BaseModel):
    market: str
    category: str
    name: str
    note: Optional[str] = None
    image: Optional[str] = None  # can be external URL or /uploads/xxx
    alt: Optional[str] = None
    links: Optional[List[dict]] = []

@app.post("/api/recommendations")
async def create_recommendation(payload: RecommendationIn):
    # validate market/category minimal
    payload.market = payload.market.lower()
    payload.category = payload.category.lower()

    # Save to DB
    rec = Recommendation(**payload.model_dump())
    rec_id = create_document("recommendation", rec)
    return {"id": rec_id}

@app.get("/api/recommendations")
async def list_recommendations(market: Optional[str] = None, category: Optional[str] = None, limit: int = 100):
    filt = {}
    if market:
        filt["market"] = market.lower()
    if category:
        filt["category"] = category.lower()
    docs = get_documents("recommendation", filt, limit)

    # Normalize _id to string
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
