"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (kept for reference)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# App-specific schemas
class Link(BaseModel):
    label: str = Field(..., description="Link label, e.g., Ver en Amazon")
    href: str = Field(..., description="Destination URL (may include affiliate params)")

class Recommendation(BaseModel):
    market: str = Field(..., description="Market code: usa, ar")
    category: str = Field(..., description="Category: beauty, fitness, shoes, etc.")
    name: str = Field(..., description="Item name/title")
    note: Optional[str] = Field(None, description="Short note/description")
    image: Optional[str] = Field(None, description="Image URL or API path e.g. /api/image/{id}")
    alt: Optional[str] = Field(None, description="Alt text for image")
    links: Optional[List[Link]] = Field(default_factory=list, description="List of outbound links")

class Image(BaseModel):
    filename: str
    content_type: str
    data_b64: str = Field(..., description="Base64-encoded image data")
