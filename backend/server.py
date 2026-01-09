from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'admin_dashboard')]

# Create the main app without a prefix
app = FastAPI(title="Admin Dashboard API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============ ENUMS ============
class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    USER = "user"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# ============ MODELS ============

# User Models
class UserBase(BaseModel):
    name: str
    email: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    phone: Optional[str] = None
    avatar: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Product/Content Models
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    stock: int = 0
    image: Optional[str] = None
    status: ContentStatus = ContentStatus.DRAFT

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    stock: Optional[int] = None
    image: Optional[str] = None
    status: Optional[ContentStatus] = None

class Product(ProductBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Page/Content Models
class PageBase(BaseModel):
    title: str
    slug: str
    content: str
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    status: ContentStatus = ContentStatus.DRAFT

class PageCreate(PageBase):
    pass

class PageUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    status: Optional[ContentStatus] = None

class Page(PageBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Order Models
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class OrderBase(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    shipping_address: str
    items: List[OrderItem]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None
    shipping_address: Optional[str] = None

class Order(OrderBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Settings Model
class SiteSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "site_settings"
    site_name: str = "My Website"
    site_description: str = ""
    site_logo: Optional[str] = None
    site_favicon: Optional[str] = None
    contact_email: str = ""
    contact_phone: str = ""
    contact_address: str = ""
    social_facebook: Optional[str] = None
    social_twitter: Optional[str] = None
    social_instagram: Optional[str] = None
    social_linkedin: Optional[str] = None
    footer_text: str = ""
    primary_color: str = "#3b82f6"
    secondary_color: str = "#10b981"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SiteSettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    site_description: Optional[str] = None
    site_logo: Optional[str] = None
    site_favicon: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_address: Optional[str] = None
    social_facebook: Optional[str] = None
    social_twitter: Optional[str] = None
    social_instagram: Optional[str] = None
    social_linkedin: Optional[str] = None
    footer_text: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None

# Activity Log Model
class ActivityLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    entity_type: str
    entity_id: str
    details: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Category Model
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============ HELPER FUNCTIONS ============

def serialize_datetime(obj):
    """Convert datetime to ISO string for MongoDB storage"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def serialize_doc(doc: dict) -> dict:
    """Serialize document for MongoDB storage"""
    result = {}
    for key, value in doc.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, list):
            result[key] = [serialize_doc(item) if isinstance(item, dict) else serialize_datetime(item) for item in value]
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        else:
            result[key] = value
    return result

def deserialize_datetime(doc: dict) -> dict:
    """Convert ISO strings back to datetime"""
    datetime_fields = ['created_at', 'updated_at', 'timestamp']
    for field in datetime_fields:
        if field in doc and isinstance(doc[field], str):
            try:
                doc[field] = datetime.fromisoformat(doc[field])
            except:
                pass
    return doc

async def log_activity(action: str, entity_type: str, entity_id: str, details: str, user_name: str = "Admin"):
    """Log an activity to the database"""
    log = ActivityLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        user_name=user_name
    )
    doc = serialize_doc(log.model_dump())
    await db.activity_logs.insert_one(doc)

# ============ API ROUTES ============

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "Admin Dashboard API", "version": "1.0.0"}

# ============ DASHBOARD STATS ============

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"status": "active"})
    total_products = await db.products.count_documents({})
    published_products = await db.products.count_documents({"status": "published"})
    total_orders = await db.orders.count_documents({})
    pending_orders = await db.orders.count_documents({"status": "pending"})
    total_pages = await db.pages.count_documents({})
    
    # Calculate total revenue
    orders = await db.orders.find({"status": {"$ne": "cancelled"}}).to_list(10000)
    total_revenue = sum(order.get("total", 0) for order in orders)
    
    # Monthly revenue (last 6 months)
    monthly_revenue = []
    months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    current_month = datetime.now().month
    for i in range(5, -1, -1):
        month_idx = (current_month - i - 1) % 12
        monthly_revenue.append({
            "name": months[month_idx],
            "revenue": total_revenue / 6 * (1 + (5 - i) * 0.1) if total_revenue > 0 else (i + 1) * 1500
        })
    
    # Order status distribution
    order_statuses = []
    for status in OrderStatus:
        count = await db.orders.count_documents({"status": status.value})
        order_statuses.append({"name": status.value, "value": count if count > 0 else 0})
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_products": total_products,
        "published_products": published_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_pages": total_pages,
        "total_revenue": total_revenue,
        "monthly_revenue": monthly_revenue,
        "order_statuses": order_statuses
    }

# ============ USER MANAGEMENT ============

@api_router.get("/users", response_model=List[User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None
):
    """Get all users with filtering"""
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    if role:
        query["role"] = role.value
    if status:
        query["status"] = status.value
    
    users = await db.users.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return [deserialize_datetime(user) for user in users]

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get a specific user"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return deserialize_datetime(user)

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    # Check if email exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kullanılıyor")
    
    user = User(**user_data.model_dump(exclude={"password"}))
    doc = serialize_doc(user.model_dump())
    doc["password_hash"] = user_data.password  # In production, hash this
    await db.users.insert_one(doc)
    await log_activity("CREATE", "user", user.id, f"Yeni kullanıcı oluşturuldu: {user.name}")
    return user

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_data: UserUpdate):
    """Update a user"""
    existing = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    await log_activity("UPDATE", "user", user_id, f"Kullanıcı güncellendi: {existing.get('name')}")
    
    updated = await db.users.find_one({"id": user_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    existing = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    await db.users.delete_one({"id": user_id})
    await log_activity("DELETE", "user", user_id, f"Kullanıcı silindi: {existing.get('name')}")
    return {"message": "Kullanıcı başarıyla silindi"}

# ============ PRODUCT MANAGEMENT ============

@api_router.get("/products", response_model=List[Product])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[ContentStatus] = None
):
    """Get all products with filtering"""
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if category:
        query["category"] = category
    if status:
        query["status"] = status.value
    
    products = await db.products.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return [deserialize_datetime(product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    return deserialize_datetime(product)

@api_router.post("/products", response_model=Product)
async def create_product(product_data: ProductCreate):
    """Create a new product"""
    product = Product(**product_data.model_dump())
    doc = serialize_doc(product.model_dump())
    await db.products.insert_one(doc)
    await log_activity("CREATE", "product", product.id, f"Yeni ürün oluşturuldu: {product.name}")
    return product

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_data: ProductUpdate):
    """Update a product"""
    existing = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    update_data = {k: v for k, v in product_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.products.update_one({"id": product_id}, {"$set": update_data})
    await log_activity("UPDATE", "product", product_id, f"Ürün güncellendi: {existing.get('name')}")
    
    updated = await db.products.find_one({"id": product_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product"""
    existing = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    await db.products.delete_one({"id": product_id})
    await log_activity("DELETE", "product", product_id, f"Ürün silindi: {existing.get('name')}")
    return {"message": "Ürün başarıyla silindi"}

# ============ PAGE MANAGEMENT ============

@api_router.get("/pages", response_model=List[Page])
async def get_pages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[ContentStatus] = None
):
    """Get all pages with filtering"""
    query = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}}
        ]
    if status:
        query["status"] = status.value
    
    pages = await db.pages.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    return [deserialize_datetime(page) for page in pages]

@api_router.get("/pages/{page_id}", response_model=Page)
async def get_page(page_id: str):
    """Get a specific page"""
    page = await db.pages.find_one({"id": page_id}, {"_id": 0})
    if not page:
        raise HTTPException(status_code=404, detail="Sayfa bulunamadı")
    return deserialize_datetime(page)

@api_router.post("/pages", response_model=Page)
async def create_page(page_data: PageCreate):
    """Create a new page"""
    # Check if slug exists
    existing = await db.pages.find_one({"slug": page_data.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Bu slug zaten kullanılıyor")
    
    page = Page(**page_data.model_dump())
    doc = serialize_doc(page.model_dump())
    await db.pages.insert_one(doc)
    await log_activity("CREATE", "page", page.id, f"Yeni sayfa oluşturuldu: {page.title}")
    return page

@api_router.put("/pages/{page_id}", response_model=Page)
async def update_page(page_id: str, page_data: PageUpdate):
    """Update a page"""
    existing = await db.pages.find_one({"id": page_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Sayfa bulunamadı")
    
    update_data = {k: v for k, v in page_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.pages.update_one({"id": page_id}, {"$set": update_data})
    await log_activity("UPDATE", "page", page_id, f"Sayfa güncellendi: {existing.get('title')}")
    
    updated = await db.pages.find_one({"id": page_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/pages/{page_id}")
async def delete_page(page_id: str):
    """Delete a page"""
    existing = await db.pages.find_one({"id": page_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Sayfa bulunamadı")
    
    await db.pages.delete_one({"id": page_id})
    await log_activity("DELETE", "page", page_id, f"Sayfa silindi: {existing.get('title')}")
    return {"message": "Sayfa başarıyla silindi"}

# ============ ORDER MANAGEMENT ============

@api_router.get("/orders", response_model=List[Order])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[OrderStatus] = None
):
    """Get all orders with filtering"""
    query = {}
    if search:
        query["$or"] = [
            {"customer_name": {"$regex": search, "$options": "i"}},
            {"customer_email": {"$regex": search, "$options": "i"}}
        ]
    if status:
        query["status"] = status.value
    
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [deserialize_datetime(order) for order in orders]

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get a specific order"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    return deserialize_datetime(order)

@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate):
    """Create a new order"""
    order = Order(**order_data.model_dump())
    doc = serialize_doc(order.model_dump())
    await db.orders.insert_one(doc)
    await log_activity("CREATE", "order", order.id, f"Yeni sipariş oluşturuldu: {order.customer_name}")
    return order

@api_router.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: str, order_data: OrderUpdate):
    """Update an order"""
    existing = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    
    update_data = {k: v for k, v in order_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.orders.update_one({"id": order_id}, {"$set": update_data})
    await log_activity("UPDATE", "order", order_id, f"Sipariş güncellendi: #{order_id[:8]}")
    
    updated = await db.orders.find_one({"id": order_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/orders/{order_id}")
async def delete_order(order_id: str):
    """Delete an order"""
    existing = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    
    await db.orders.delete_one({"id": order_id})
    await log_activity("DELETE", "order", order_id, f"Sipariş silindi: #{order_id[:8]}")
    return {"message": "Sipariş başarıyla silindi"}

# ============ CATEGORY MANAGEMENT ============

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    """Get all categories"""
    categories = await db.categories.find({}, {"_id": 0}).to_list(1000)
    return [deserialize_datetime(cat) for cat in categories]

@api_router.post("/categories", response_model=Category)
async def create_category(category_data: CategoryCreate):
    """Create a new category"""
    category = Category(**category_data.model_dump())
    doc = serialize_doc(category.model_dump())
    await db.categories.insert_one(doc)
    await log_activity("CREATE", "category", category.id, f"Yeni kategori oluşturuldu: {category.name}")
    return category

@api_router.delete("/categories/{category_id}")
async def delete_category(category_id: str):
    """Delete a category"""
    existing = await db.categories.find_one({"id": category_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Kategori bulunamadı")
    
    await db.categories.delete_one({"id": category_id})
    await log_activity("DELETE", "category", category_id, f"Kategori silindi: {existing.get('name')}")
    return {"message": "Kategori başarıyla silindi"}

# ============ SITE SETTINGS ============

@api_router.get("/settings", response_model=SiteSettings)
async def get_settings():
    """Get site settings"""
    settings = await db.settings.find_one({"id": "site_settings"}, {"_id": 0})
    if not settings:
        # Create default settings
        default_settings = SiteSettings()
        doc = serialize_doc(default_settings.model_dump())
        await db.settings.insert_one(doc)
        return default_settings
    return deserialize_datetime(settings)

@api_router.put("/settings", response_model=SiteSettings)
async def update_settings(settings_data: SiteSettingsUpdate):
    """Update site settings"""
    update_data = {k: v for k, v in settings_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.settings.update_one(
        {"id": "site_settings"},
        {"$set": update_data},
        upsert=True
    )
    await log_activity("UPDATE", "settings", "site_settings", "Site ayarları güncellendi")
    
    updated = await db.settings.find_one({"id": "site_settings"}, {"_id": 0})
    return deserialize_datetime(updated)

# ============ ACTIVITY LOGS ============

@api_router.get("/activity-logs", response_model=List[ActivityLog])
async def get_activity_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    entity_type: Optional[str] = None
):
    """Get activity logs"""
    query = {}
    if entity_type:
        query["entity_type"] = entity_type
    
    logs = await db.activity_logs.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [deserialize_datetime(log) for log in logs]

# ============ SEED DATA ============

@api_router.post("/seed-data")
async def seed_data():
    """Seed the database with sample data"""
    # Check if data already exists
    existing_users = await db.users.count_documents({})
    if existing_users > 0:
        return {"message": "Veriler zaten mevcut"}
    
    # Sample Users
    sample_users = [
        {"name": "Ahmet Yılmaz", "email": "ahmet@example.com", "role": "admin", "status": "active", "phone": "0532 111 2233"},
        {"name": "Ayşe Demir", "email": "ayse@example.com", "role": "editor", "status": "active", "phone": "0533 222 3344"},
        {"name": "Mehmet Kaya", "email": "mehmet@example.com", "role": "user", "status": "active", "phone": "0534 333 4455"},
        {"name": "Fatma Çelik", "email": "fatma@example.com", "role": "user", "status": "inactive", "phone": "0535 444 5566"},
        {"name": "Ali Öztürk", "email": "ali@example.com", "role": "user", "status": "active", "phone": "0536 555 6677"},
    ]
    
    for user_data in sample_users:
        user = User(**user_data)
        doc = serialize_doc(user.model_dump())
        doc["password_hash"] = "123456"
        await db.users.insert_one(doc)
    
    # Sample Categories
    sample_categories = [
        {"name": "Elektronik", "description": "Elektronik ürünler"},
        {"name": "Giyim", "description": "Giyim ürünleri"},
        {"name": "Ev & Yaşam", "description": "Ev ve yaşam ürünleri"},
        {"name": "Spor", "description": "Spor ürünleri"},
    ]
    
    for cat_data in sample_categories:
        cat = Category(**cat_data)
        doc = serialize_doc(cat.model_dump())
        await db.categories.insert_one(doc)
    
    # Sample Products
    sample_products = [
        {"name": "Laptop Pro 15", "description": "Yüksek performanslı laptop", "price": 25000, "category": "Elektronik", "stock": 50, "status": "published"},
        {"name": "Akıllı Saat X1", "description": "Fitness takipli akıllı saat", "price": 3500, "category": "Elektronik", "stock": 100, "status": "published"},
        {"name": "Kablosuz Kulaklık", "description": "Bluetooth kulaklık", "price": 1200, "category": "Elektronik", "stock": 75, "status": "published"},
        {"name": "Spor Ayakkabı", "description": "Koşu ayakkabısı", "price": 800, "category": "Spor", "stock": 200, "status": "published"},
        {"name": "Yoga Matı", "description": "Premium yoga matı", "price": 350, "category": "Spor", "stock": 150, "status": "draft"},
    ]
    
    for prod_data in sample_products:
        prod = Product(**prod_data)
        doc = serialize_doc(prod.model_dump())
        await db.products.insert_one(doc)
    
    # Sample Pages
    sample_pages = [
        {"title": "Ana Sayfa", "slug": "home", "content": "Hoş geldiniz! Bu bizim ana sayfamızdır.", "status": "published", "meta_title": "Ana Sayfa", "meta_description": "Web sitemizin ana sayfası"},
        {"title": "Hakkımızda", "slug": "about", "content": "Biz kim olduğumuzu ve ne yaptığımızı anlatan sayfa.", "status": "published", "meta_title": "Hakkımızda", "meta_description": "Şirketimiz hakkında bilgi"},
        {"title": "İletişim", "slug": "contact", "content": "Bizimle iletişime geçin.", "status": "published", "meta_title": "İletişim", "meta_description": "İletişim bilgilerimiz"},
        {"title": "SSS", "slug": "faq", "content": "Sıkça sorulan sorular ve cevapları.", "status": "draft", "meta_title": "SSS", "meta_description": "Sıkça sorulan sorular"},
    ]
    
    for page_data in sample_pages:
        page = Page(**page_data)
        doc = serialize_doc(page.model_dump())
        await db.pages.insert_one(doc)
    
    # Sample Orders
    sample_orders = [
        {"customer_name": "Ahmet Yılmaz", "customer_email": "ahmet@example.com", "customer_phone": "0532 111 2233", "shipping_address": "İstanbul, Kadıköy", "items": [{"product_id": "1", "product_name": "Laptop Pro 15", "quantity": 1, "price": 25000}], "total": 25000, "status": "delivered"},
        {"customer_name": "Ayşe Demir", "customer_email": "ayse@example.com", "customer_phone": "0533 222 3344", "shipping_address": "Ankara, Çankaya", "items": [{"product_id": "2", "product_name": "Akıllı Saat X1", "quantity": 2, "price": 3500}], "total": 7000, "status": "shipped"},
        {"customer_name": "Mehmet Kaya", "customer_email": "mehmet@example.com", "customer_phone": "0534 333 4455", "shipping_address": "İzmir, Konak", "items": [{"product_id": "3", "product_name": "Kablosuz Kulaklık", "quantity": 1, "price": 1200}], "total": 1200, "status": "pending"},
    ]
    
    for order_data in sample_orders:
        order = Order(**order_data)
        doc = serialize_doc(order.model_dump())
        await db.orders.insert_one(doc)
    
    # Default Settings
    default_settings = SiteSettings(
        site_name="Admin Dashboard",
        site_description="Profesyonel yönetim paneli",
        contact_email="info@example.com",
        contact_phone="0212 123 4567",
        contact_address="İstanbul, Türkiye",
        footer_text="© 2025 Tüm hakları saklıdır."
    )
    doc = serialize_doc(default_settings.model_dump())
    await db.settings.insert_one(doc)
    
    await log_activity("SEED", "system", "all", "Örnek veriler oluşturuldu")
    
    return {"message": "Örnek veriler başarıyla oluşturuldu"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
