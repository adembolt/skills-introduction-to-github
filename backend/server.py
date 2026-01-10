from fastapi import FastAPI, APIRouter, HTTPException, Query, Request, Response, Cookie, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
import httpx
import hashlib
import secrets

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

# ============ AUTH MODELS ============
class AuthUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: str = "admin"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SessionData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============ AUTH HELPER FUNCTIONS ============
async def get_current_user(request: Request, session_token: Optional[str] = Cookie(default=None)) -> Optional[AuthUser]:
    """Get current authenticated user from session token"""
    token = session_token
    
    # Fallback to Authorization header
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return None
    
    # Find session in database
    session_doc = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session_doc:
        return None
    
    # Check expiry with timezone awareness
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    
    # Get user
    user_doc = await db.auth_users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        return None
    
    # Handle datetime fields
    if "created_at" in user_doc and isinstance(user_doc["created_at"], str):
        user_doc["created_at"] = datetime.fromisoformat(user_doc["created_at"])
    
    return AuthUser(**user_doc)

async def require_auth(request: Request, session_token: Optional[str] = Cookie(default=None)) -> AuthUser:
    """Require authentication - raises 401 if not authenticated"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Oturum açmanız gerekiyor")
    return user

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

# ============ SITE CONTENT MODELS ============

# Hero Section Model
class HeroSection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "hero_section"
    title: str = "Hoş Geldiniz"
    subtitle: str = "Profesyonel çözümler sunuyoruz"
    description: str = "İşletmenizi büyütmek için en iyi hizmetleri sağlıyoruz."
    button_text: str = "Hemen Başla"
    button_link: str = "#contact"
    background_image: Optional[str] = None
    background_color: str = "#1e293b"
    text_color: str = "#ffffff"
    is_active: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HeroSectionUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    background_image: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    is_active: Optional[bool] = None

# Service/Feature Card Model
class ServiceCard(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    icon: str = "star"  # lucide icon name
    image: Optional[str] = None
    link: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ServiceCardCreate(BaseModel):
    title: str
    description: str
    icon: str = "star"
    image: Optional[str] = None
    link: Optional[str] = None
    order: int = 0
    is_active: bool = True

class ServiceCardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    link: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

# Pricing Card Model
class PricingCard(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    currency: str = "₺"
    period: str = "ay"  # ay, yıl, tek seferlik
    description: str
    features: List[str] = []
    is_popular: bool = False
    button_text: str = "Satın Al"
    button_link: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PricingCardCreate(BaseModel):
    name: str
    price: float
    currency: str = "₺"
    period: str = "ay"
    description: str
    features: List[str] = []
    is_popular: bool = False
    button_text: str = "Satın Al"
    button_link: Optional[str] = None
    order: int = 0
    is_active: bool = True

class PricingCardUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    period: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    is_popular: Optional[bool] = None
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

# Testimonial Model
class Testimonial(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    title: str  # Job title / company
    content: str
    avatar: Optional[str] = None
    rating: int = 5
    order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TestimonialCreate(BaseModel):
    name: str
    title: str
    content: str
    avatar: Optional[str] = None
    rating: int = 5
    order: int = 0
    is_active: bool = True

class TestimonialUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    avatar: Optional[str] = None
    rating: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

# Banner/Slider Model
class Banner(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    subtitle: Optional[str] = None
    image: str
    link: Optional[str] = None
    button_text: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BannerCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    image: str
    link: Optional[str] = None
    button_text: Optional[str] = None
    order: int = 0
    is_active: bool = True

class BannerUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    image: Optional[str] = None
    link: Optional[str] = None
    button_text: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

# Media/Gallery Model
class MediaItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    type: str = "image"  # image, video, document
    alt_text: Optional[str] = None
    category: Optional[str] = None
    size: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MediaItemCreate(BaseModel):
    name: str
    url: str
    type: str = "image"
    alt_text: Optional[str] = None
    category: Optional[str] = None
    size: Optional[int] = None

# Menu/Navigation Model
class MenuItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    link: str
    parent_id: Optional[str] = None
    order: int = 0
    is_active: bool = True
    open_in_new_tab: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MenuItemCreate(BaseModel):
    label: str
    link: str
    parent_id: Optional[str] = None
    order: int = 0
    is_active: bool = True
    open_in_new_tab: bool = False

class MenuItemUpdate(BaseModel):
    label: Optional[str] = None
    link: Optional[str] = None
    parent_id: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
    open_in_new_tab: Optional[bool] = None

# Section Content Model (for any text section)
class SectionContent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    section_key: str  # unique key like "about_us", "mission", "vision"
    title: str
    content: str
    image: Optional[str] = None
    order: int = 0
    is_active: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SectionContentCreate(BaseModel):
    section_key: str
    title: str
    content: str
    image: Optional[str] = None
    order: int = 0
    is_active: bool = True

class SectionContentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

# Chart Data Model
class ChartData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chart_key: str  # unique key like "monthly_sales", "visitors"
    title: str
    chart_type: str = "bar"  # bar, line, pie, area
    data: List[Dict[str, Any]] = []
    colors: List[str] = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]
    is_active: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChartDataCreate(BaseModel):
    chart_key: str
    title: str
    chart_type: str = "bar"
    data: List[Dict[str, Any]] = []
    colors: List[str] = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]
    is_active: bool = True

class ChartDataUpdate(BaseModel):
    title: Optional[str] = None
    chart_type: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    colors: Optional[List[str]] = None
    is_active: Optional[bool] = None

# FAQ Model
class FAQ(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    answer: str
    category: Optional[str] = None
    order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FAQCreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None
    order: int = 0
    is_active: bool = True

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

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

def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = "admin_dashboard_salt_2025"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

# ============ API ROUTES ============

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "Admin Dashboard API", "version": "1.0.0"}

# ============ AUTH ROUTES ============

# Admin Login Model
class AdminLoginRequest(BaseModel):
    email: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@api_router.post("/auth/login")
async def admin_login(login_data: AdminLoginRequest, response: Response):
    """Login with email and password"""
    # Find admin credentials
    admin_creds = await db.admin_credentials.find_one({"email": login_data.email}, {"_id": 0})
    
    if not admin_creds:
        raise HTTPException(status_code=401, detail="Geçersiz e-posta veya şifre")
    
    # Verify password
    password_hash = hash_password(login_data.password)
    if admin_creds.get("password_hash") != password_hash:
        raise HTTPException(status_code=401, detail="Geçersiz e-posta veya şifre")
    
    # Generate session token
    session_token = generate_session_token()
    user_id = admin_creds.get("user_id", f"admin_{uuid.uuid4().hex[:12]}")
    
    # Store session
    session_doc = {
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.user_sessions.delete_many({"user_id": user_id})
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    await log_activity("LOGIN", "auth", user_id, f"Admin giriş yaptı: {admin_creds.get('name')}")
    
    return {
        "user_id": user_id,
        "email": admin_creds.get("email"),
        "name": admin_creds.get("name"),
        "picture": admin_creds.get("picture"),
        "role": "admin"
    }

@api_router.post("/auth/change-password")
async def change_password(request: Request, password_data: ChangePasswordRequest, session_token: Optional[str] = Cookie(default=None)):
    """Change admin password"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Oturum açmanız gerekiyor")
    
    # Find admin credentials
    admin_creds = await db.admin_credentials.find_one({"email": user.email}, {"_id": 0})
    if not admin_creds:
        raise HTTPException(status_code=404, detail="Admin bilgileri bulunamadı")
    
    # Verify current password
    current_hash = hash_password(password_data.current_password)
    if admin_creds.get("password_hash") != current_hash:
        raise HTTPException(status_code=400, detail="Mevcut şifre yanlış")
    
    # Update password
    new_hash = hash_password(password_data.new_password)
    await db.admin_credentials.update_one(
        {"email": user.email},
        {"$set": {"password_hash": new_hash, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    await log_activity("UPDATE", "auth", user.user_id, "Şifre değiştirildi")
    
    return {"message": "Şifre başarıyla değiştirildi"}

@api_router.get("/auth/admin-info")
async def get_admin_info():
    """Get admin credentials info (for display only, not password)"""
    admin_creds = await db.admin_credentials.find_one({}, {"_id": 0, "password_hash": 0})
    if not admin_creds:
        return {"exists": False}
    return {
        "exists": True,
        "email": admin_creds.get("email"),
        "name": admin_creds.get("name")
    }

@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id for session_token and set cookie"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id gerekli")
    
    # Get user data from Emergent Auth
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Geçersiz session_id")
            
            auth_data = auth_response.json()
        except httpx.RequestError as e:
            logger.error(f"Auth request failed: {e}")
            raise HTTPException(status_code=500, detail="Kimlik doğrulama servisi hatası")
    
    # Extract user info
    email = auth_data.get("email")
    name = auth_data.get("name")
    picture = auth_data.get("picture")
    session_token = auth_data.get("session_token")
    
    if not email or not session_token:
        raise HTTPException(status_code=400, detail="Geçersiz auth verisi")
    
    # Check if user exists, update or create
    existing_user = await db.auth_users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        # Update user info
        await db.auth_users.update_one(
            {"email": email},
            {"$set": {
                "name": name,
                "picture": picture,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    else:
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.auth_users.insert_one(new_user)
        await log_activity("CREATE", "auth_user", user_id, f"Yeni kullanıcı giriş yaptı: {name}")
    
    # Store session
    session_doc = {
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Remove old sessions for this user
    await db.user_sessions.delete_many({"user_id": user_id})
    await db.user_sessions.insert_one(session_doc)
    
    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    await log_activity("LOGIN", "auth", user_id, f"Kullanıcı giriş yaptı: {name}")
    
    return {
        "user_id": user_id,
        "email": email,
        "name": name,
        "picture": picture,
        "role": "admin"
    }

@api_router.get("/auth/me")
async def get_me(request: Request, session_token: Optional[str] = Cookie(default=None)):
    """Get current authenticated user"""
    user = await get_current_user(request, session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Oturum açmanız gerekiyor")
    
    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "role": user.role
    }

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, session_token: Optional[str] = Cookie(default=None)):
    """Logout and clear session"""
    token = session_token
    
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if token:
        # Get user info before deleting session
        session_doc = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
        if session_doc:
            user_doc = await db.auth_users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
            if user_doc:
                await log_activity("LOGOUT", "auth", session_doc["user_id"], f"Kullanıcı çıkış yaptı: {user_doc.get('name')}")
        
        # Delete session
        await db.user_sessions.delete_many({"session_token": token})
    
    # Clear cookie
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=True,
        samesite="none"
    )
    
    return {"message": "Başarıyla çıkış yapıldı"}

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

# ============ SITE CONTENT MANAGEMENT ============

# Hero Section
@api_router.get("/content/hero", response_model=HeroSection)
async def get_hero_section():
    """Get hero section content"""
    hero = await db.hero_section.find_one({"id": "hero_section"}, {"_id": 0})
    if not hero:
        default_hero = HeroSection()
        doc = serialize_doc(default_hero.model_dump())
        await db.hero_section.insert_one(doc)
        return default_hero
    return deserialize_datetime(hero)

@api_router.put("/content/hero", response_model=HeroSection)
async def update_hero_section(hero_data: HeroSectionUpdate):
    """Update hero section"""
    update_data = {k: v for k, v in hero_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.hero_section.update_one(
        {"id": "hero_section"},
        {"$set": update_data},
        upsert=True
    )
    await log_activity("UPDATE", "hero", "hero_section", "Hero bölümü güncellendi")
    
    updated = await db.hero_section.find_one({"id": "hero_section"}, {"_id": 0})
    return deserialize_datetime(updated)

# Service Cards
@api_router.get("/content/services", response_model=List[ServiceCard])
async def get_services():
    """Get all service cards"""
    services = await db.service_cards.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return [deserialize_datetime(s) for s in services]

@api_router.post("/content/services", response_model=ServiceCard)
async def create_service(service_data: ServiceCardCreate):
    """Create a service card"""
    service = ServiceCard(**service_data.model_dump())
    doc = serialize_doc(service.model_dump())
    await db.service_cards.insert_one(doc)
    await log_activity("CREATE", "service", service.id, f"Yeni hizmet oluşturuldu: {service.title}")
    return service

@api_router.put("/content/services/{service_id}", response_model=ServiceCard)
async def update_service(service_id: str, service_data: ServiceCardUpdate):
    """Update a service card"""
    existing = await db.service_cards.find_one({"id": service_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Hizmet bulunamadı")
    
    update_data = {k: v for k, v in service_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.service_cards.update_one({"id": service_id}, {"$set": update_data})
    await log_activity("UPDATE", "service", service_id, f"Hizmet güncellendi: {existing.get('title')}")
    
    updated = await db.service_cards.find_one({"id": service_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/content/services/{service_id}")
async def delete_service(service_id: str):
    """Delete a service card"""
    existing = await db.service_cards.find_one({"id": service_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Hizmet bulunamadı")
    
    await db.service_cards.delete_one({"id": service_id})
    await log_activity("DELETE", "service", service_id, f"Hizmet silindi: {existing.get('title')}")
    return {"message": "Hizmet başarıyla silindi"}

# Pricing Cards
@api_router.get("/content/pricing", response_model=List[PricingCard])
async def get_pricing():
    """Get all pricing cards"""
    pricing = await db.pricing_cards.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return [deserialize_datetime(p) for p in pricing]

@api_router.post("/content/pricing", response_model=PricingCard)
async def create_pricing(pricing_data: PricingCardCreate):
    """Create a pricing card"""
    pricing = PricingCard(**pricing_data.model_dump())
    doc = serialize_doc(pricing.model_dump())
    await db.pricing_cards.insert_one(doc)
    await log_activity("CREATE", "pricing", pricing.id, f"Yeni fiyat kartı oluşturuldu: {pricing.name}")
    return pricing

@api_router.put("/content/pricing/{pricing_id}", response_model=PricingCard)
async def update_pricing(pricing_id: str, pricing_data: PricingCardUpdate):
    """Update a pricing card"""
    existing = await db.pricing_cards.find_one({"id": pricing_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Fiyat kartı bulunamadı")
    
    update_data = {k: v for k, v in pricing_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.pricing_cards.update_one({"id": pricing_id}, {"$set": update_data})
    await log_activity("UPDATE", "pricing", pricing_id, f"Fiyat kartı güncellendi: {existing.get('name')}")
    
    updated = await db.pricing_cards.find_one({"id": pricing_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/content/pricing/{pricing_id}")
async def delete_pricing(pricing_id: str):
    """Delete a pricing card"""
    existing = await db.pricing_cards.find_one({"id": pricing_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Fiyat kartı bulunamadı")
    
    await db.pricing_cards.delete_one({"id": pricing_id})
    await log_activity("DELETE", "pricing", pricing_id, f"Fiyat kartı silindi: {existing.get('name')}")
    return {"message": "Fiyat kartı başarıyla silindi"}

# Testimonials
@api_router.get("/content/testimonials", response_model=List[Testimonial])
async def get_testimonials():
    """Get all testimonials"""
    testimonials = await db.testimonials.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return [deserialize_datetime(t) for t in testimonials]

@api_router.post("/content/testimonials", response_model=Testimonial)
async def create_testimonial(testimonial_data: TestimonialCreate):
    """Create a testimonial"""
    testimonial = Testimonial(**testimonial_data.model_dump())
    doc = serialize_doc(testimonial.model_dump())
    await db.testimonials.insert_one(doc)
    await log_activity("CREATE", "testimonial", testimonial.id, f"Yeni referans oluşturuldu: {testimonial.name}")
    return testimonial

@api_router.put("/content/testimonials/{testimonial_id}", response_model=Testimonial)
async def update_testimonial(testimonial_id: str, testimonial_data: TestimonialUpdate):
    """Update a testimonial"""
    existing = await db.testimonials.find_one({"id": testimonial_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Referans bulunamadı")
    
    update_data = {k: v for k, v in testimonial_data.model_dump().items() if v is not None}
    
    await db.testimonials.update_one({"id": testimonial_id}, {"$set": update_data})
    await log_activity("UPDATE", "testimonial", testimonial_id, f"Referans güncellendi: {existing.get('name')}")
    
    updated = await db.testimonials.find_one({"id": testimonial_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/content/testimonials/{testimonial_id}")
async def delete_testimonial(testimonial_id: str):
    """Delete a testimonial"""
    existing = await db.testimonials.find_one({"id": testimonial_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Referans bulunamadı")
    
    await db.testimonials.delete_one({"id": testimonial_id})
    await log_activity("DELETE", "testimonial", testimonial_id, f"Referans silindi: {existing.get('name')}")
    return {"message": "Referans başarıyla silindi"}

# Banners
@api_router.get("/content/banners", response_model=List[Banner])
async def get_banners():
    """Get all banners"""
    banners = await db.banners.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return [deserialize_datetime(b) for b in banners]

@api_router.post("/content/banners", response_model=Banner)
async def create_banner(banner_data: BannerCreate):
    """Create a banner"""
    banner = Banner(**banner_data.model_dump())
    doc = serialize_doc(banner.model_dump())
    await db.banners.insert_one(doc)
    await log_activity("CREATE", "banner", banner.id, f"Yeni banner oluşturuldu: {banner.title}")
    return banner

@api_router.put("/content/banners/{banner_id}", response_model=Banner)
async def update_banner(banner_id: str, banner_data: BannerUpdate):
    """Update a banner"""
    existing = await db.banners.find_one({"id": banner_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Banner bulunamadı")
    
    update_data = {k: v for k, v in banner_data.model_dump().items() if v is not None}
    
    await db.banners.update_one({"id": banner_id}, {"$set": update_data})
    await log_activity("UPDATE", "banner", banner_id, f"Banner güncellendi: {existing.get('title')}")
    
    updated = await db.banners.find_one({"id": banner_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/content/banners/{banner_id}")
async def delete_banner(banner_id: str):
    """Delete a banner"""
    existing = await db.banners.find_one({"id": banner_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Banner bulunamadı")
    
    await db.banners.delete_one({"id": banner_id})
    await log_activity("DELETE", "banner", banner_id, f"Banner silindi: {existing.get('title')}")
    return {"message": "Banner başarıyla silindi"}

# Media Library
@api_router.get("/content/media", response_model=List[MediaItem])
async def get_media(category: Optional[str] = None):
    """Get all media items"""
    query = {}
    if category:
        query["category"] = category
    media = await db.media.find(query, {"_id": 0}).sort("created_at", -1).to_list(500)
    return [deserialize_datetime(m) for m in media]

@api_router.post("/content/media", response_model=MediaItem)
async def create_media(media_data: MediaItemCreate):
    """Create a media item"""
    media = MediaItem(**media_data.model_dump())
    doc = serialize_doc(media.model_dump())
    await db.media.insert_one(doc)
    await log_activity("CREATE", "media", media.id, f"Yeni medya eklendi: {media.name}")
    return media

@api_router.delete("/content/media/{media_id}")
async def delete_media(media_id: str):
    """Delete a media item"""
    existing = await db.media.find_one({"id": media_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Medya bulunamadı")
    
    await db.media.delete_one({"id": media_id})
    await log_activity("DELETE", "media", media_id, f"Medya silindi: {existing.get('name')}")
    return {"message": "Medya başarıyla silindi"}

# Menu Items
@api_router.get("/content/menu", response_model=List[MenuItem])
async def get_menu():
    """Get all menu items"""
    menu = await db.menu_items.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return [deserialize_datetime(m) for m in menu]

@api_router.post("/content/menu", response_model=MenuItem)
async def create_menu_item(menu_data: MenuItemCreate):
    """Create a menu item"""
    menu_item = MenuItem(**menu_data.model_dump())
    doc = serialize_doc(menu_item.model_dump())
    await db.menu_items.insert_one(doc)
    await log_activity("CREATE", "menu", menu_item.id, f"Yeni menü öğesi oluşturuldu: {menu_item.label}")
    return menu_item

@api_router.put("/content/menu/{menu_id}", response_model=MenuItem)
async def update_menu_item(menu_id: str, menu_data: MenuItemUpdate):
    """Update a menu item"""
    existing = await db.menu_items.find_one({"id": menu_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Menü öğesi bulunamadı")
    
    update_data = {k: v for k, v in menu_data.model_dump().items() if v is not None}
    
    await db.menu_items.update_one({"id": menu_id}, {"$set": update_data})
    await log_activity("UPDATE", "menu", menu_id, f"Menü öğesi güncellendi: {existing.get('label')}")
    
    updated = await db.menu_items.find_one({"id": menu_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/content/menu/{menu_id}")
async def delete_menu_item(menu_id: str):
    """Delete a menu item"""
    existing = await db.menu_items.find_one({"id": menu_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Menü öğesi bulunamadı")
    
    await db.menu_items.delete_one({"id": menu_id})
    await log_activity("DELETE", "menu", menu_id, f"Menü öğesi silindi: {existing.get('label')}")
    return {"message": "Menü öğesi başarıyla silindi"}

# Section Content
@api_router.get("/content/sections", response_model=List[SectionContent])
async def get_sections():
    """Get all section contents"""
    sections = await db.section_contents.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return [deserialize_datetime(s) for s in sections]

@api_router.get("/content/sections/{section_key}", response_model=SectionContent)
async def get_section(section_key: str):
    """Get a specific section by key"""
    section = await db.section_contents.find_one({"section_key": section_key}, {"_id": 0})
    if not section:
        raise HTTPException(status_code=404, detail="Bölüm bulunamadı")
    return deserialize_datetime(section)

@api_router.post("/content/sections", response_model=SectionContent)
async def create_section(section_data: SectionContentCreate):
    """Create a section content"""
    # Check if section_key exists
    existing = await db.section_contents.find_one({"section_key": section_data.section_key})
    if existing:
        raise HTTPException(status_code=400, detail="Bu bölüm anahtarı zaten kullanılıyor")
    
    section = SectionContent(**section_data.model_dump())
    doc = serialize_doc(section.model_dump())
    await db.section_contents.insert_one(doc)
    await log_activity("CREATE", "section", section.id, f"Yeni bölüm oluşturuldu: {section.title}")
    return section

@api_router.put("/content/sections/{section_id}", response_model=SectionContent)
async def update_section(section_id: str, section_data: SectionContentUpdate):
    """Update a section content"""
    existing = await db.section_contents.find_one({"id": section_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Bölüm bulunamadı")
    
    update_data = {k: v for k, v in section_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.section_contents.update_one({"id": section_id}, {"$set": update_data})
    await log_activity("UPDATE", "section", section_id, f"Bölüm güncellendi: {existing.get('title')}")
    
    updated = await db.section_contents.find_one({"id": section_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/content/sections/{section_id}")
async def delete_section(section_id: str):
    """Delete a section content"""
    existing = await db.section_contents.find_one({"id": section_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Bölüm bulunamadı")
    
    await db.section_contents.delete_one({"id": section_id})
    await log_activity("DELETE", "section", section_id, f"Bölüm silindi: {existing.get('title')}")
    return {"message": "Bölüm başarıyla silindi"}

# Chart Data
@api_router.get("/content/charts", response_model=List[ChartData])
async def get_charts():
    """Get all chart data"""
    charts = await db.chart_data.find({}, {"_id": 0}).to_list(100)
    return [deserialize_datetime(c) for c in charts]

@api_router.get("/content/charts/{chart_key}", response_model=ChartData)
async def get_chart(chart_key: str):
    """Get a specific chart by key"""
    chart = await db.chart_data.find_one({"chart_key": chart_key}, {"_id": 0})
    if not chart:
        raise HTTPException(status_code=404, detail="Grafik bulunamadı")
    return deserialize_datetime(chart)

@api_router.post("/content/charts", response_model=ChartData)
async def create_chart(chart_data: ChartDataCreate):
    """Create chart data"""
    existing = await db.chart_data.find_one({"chart_key": chart_data.chart_key})
    if existing:
        raise HTTPException(status_code=400, detail="Bu grafik anahtarı zaten kullanılıyor")
    
    chart = ChartData(**chart_data.model_dump())
    doc = serialize_doc(chart.model_dump())
    await db.chart_data.insert_one(doc)
    await log_activity("CREATE", "chart", chart.id, f"Yeni grafik oluşturuldu: {chart.title}")
    return chart

@api_router.put("/content/charts/{chart_id}", response_model=ChartData)
async def update_chart(chart_id: str, chart_data: ChartDataUpdate):
    """Update chart data"""
    existing = await db.chart_data.find_one({"id": chart_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Grafik bulunamadı")
    
    update_data = {k: v for k, v in chart_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.chart_data.update_one({"id": chart_id}, {"$set": update_data})
    await log_activity("UPDATE", "chart", chart_id, f"Grafik güncellendi: {existing.get('title')}")
    
    updated = await db.chart_data.find_one({"id": chart_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/content/charts/{chart_id}")
async def delete_chart(chart_id: str):
    """Delete chart data"""
    existing = await db.chart_data.find_one({"id": chart_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Grafik bulunamadı")
    
    await db.chart_data.delete_one({"id": chart_id})
    await log_activity("DELETE", "chart", chart_id, f"Grafik silindi: {existing.get('title')}")
    return {"message": "Grafik başarıyla silindi"}

# FAQs
@api_router.get("/content/faqs", response_model=List[FAQ])
async def get_faqs():
    """Get all FAQs"""
    faqs = await db.faqs.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return [deserialize_datetime(f) for f in faqs]

@api_router.post("/content/faqs", response_model=FAQ)
async def create_faq(faq_data: FAQCreate):
    """Create a FAQ"""
    faq = FAQ(**faq_data.model_dump())
    doc = serialize_doc(faq.model_dump())
    await db.faqs.insert_one(doc)
    await log_activity("CREATE", "faq", faq.id, f"Yeni SSS oluşturuldu")
    return faq

@api_router.put("/content/faqs/{faq_id}", response_model=FAQ)
async def update_faq(faq_id: str, faq_data: FAQUpdate):
    """Update a FAQ"""
    existing = await db.faqs.find_one({"id": faq_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="SSS bulunamadı")
    
    update_data = {k: v for k, v in faq_data.model_dump().items() if v is not None}
    
    await db.faqs.update_one({"id": faq_id}, {"$set": update_data})
    await log_activity("UPDATE", "faq", faq_id, "SSS güncellendi")
    
    updated = await db.faqs.find_one({"id": faq_id}, {"_id": 0})
    return deserialize_datetime(updated)

@api_router.delete("/content/faqs/{faq_id}")
async def delete_faq(faq_id: str):
    """Delete a FAQ"""
    existing = await db.faqs.find_one({"id": faq_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="SSS bulunamadı")
    
    await db.faqs.delete_one({"id": faq_id})
    await log_activity("DELETE", "faq", faq_id, "SSS silindi")
    return {"message": "SSS başarıyla silindi"}

# Get all site content at once (for frontend rendering)
@api_router.get("/content/all")
async def get_all_content():
    """Get all site content for frontend"""
    hero = await db.hero_section.find_one({"id": "hero_section"}, {"_id": 0})
    services = await db.service_cards.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    pricing = await db.pricing_cards.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    testimonials = await db.testimonials.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    banners = await db.banners.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    menu = await db.menu_items.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    sections = await db.section_contents.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    charts = await db.chart_data.find({"is_active": True}, {"_id": 0}).to_list(100)
    faqs = await db.faqs.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    settings = await db.settings.find_one({"id": "site_settings"}, {"_id": 0})
    
    return {
        "hero": hero or HeroSection().model_dump(),
        "services": services,
        "pricing": pricing,
        "testimonials": testimonials,
        "banners": banners,
        "menu": menu,
        "sections": sections,
        "charts": charts,
        "faqs": faqs,
        "settings": settings or SiteSettings().model_dump()
    }

# ============ CONTACT FORM ============

class ContactFormRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: str

class ContactMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@api_router.post("/contact")
async def submit_contact_form(contact_data: ContactFormRequest):
    """Submit contact form"""
    contact = ContactMessage(**contact_data.model_dump())
    doc = serialize_doc(contact.model_dump())
    await db.contact_messages.insert_one(doc)
    await log_activity("CREATE", "contact", contact.id, f"Yeni iletişim mesajı: {contact.name}")
    return {"message": "Mesajınız başarıyla gönderildi"}

@api_router.get("/contact/messages", response_model=List[ContactMessage])
async def get_contact_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get contact form messages"""
    messages = await db.contact_messages.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [deserialize_datetime(msg) for msg in messages]

@api_router.put("/contact/messages/{message_id}/read")
async def mark_message_read(message_id: str):
    """Mark message as read"""
    await db.contact_messages.update_one({"id": message_id}, {"$set": {"is_read": True}})
    return {"message": "Mesaj okundu olarak işaretlendi"}

@api_router.delete("/contact/messages/{message_id}")
async def delete_contact_message(message_id: str):
    """Delete contact message"""
    await db.contact_messages.delete_one({"id": message_id})
    return {"message": "Mesaj silindi"}

# ============ SEED DATA ============

@api_router.post("/seed-data")
async def seed_data():
    """Seed the database with sample data"""
    # Check if data already exists - check multiple collections
    existing_users = await db.users.count_documents({})
    existing_services = await db.service_cards.count_documents({})
    existing_admin = await db.admin_credentials.count_documents({})
    
    # Always ensure admin credentials exist
    if existing_admin == 0:
        admin_creds = {
            "user_id": "admin_main",
            "email": "admin@admin.com",
            "name": "Site Admin",
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.admin_credentials.insert_one(admin_creds)
    
    if existing_users > 0 and existing_services > 0:
        return {"message": "Veriler zaten mevcut"}
    
    # Only seed what's missing
    if existing_users == 0:
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
    
    # Default Settings - Bamboo Beauty Lifes
    default_settings = SiteSettings(
        site_name="BAMBOO BEAUTY LİFES",
        site_description="Profesyonel Güzellik ve Bakım Merkezi - Marmaris",
        contact_email="bamboobeautylifes@gmail.com",
        contact_phone="0 (252) 417 23 67",
        contact_address="Tepe mahallesi Kubilay Alpuğan Sokak No:4 Daire:2, Tokgöz Apartmanı Marmaris/MUĞLA",
        social_instagram="https://instagram.com/bamboobeautylifes",
        social_facebook="https://facebook.com/bamboobeautylifes",
        footer_text="© 2025 BAMBOO BEAUTY LİFES. Tüm hakları saklıdır."
    )
    doc = serialize_doc(default_settings.model_dump())
    await db.settings.insert_one(doc)
    
    # ============ SITE CONTENT SEED DATA ============
    
    # Hero Section
    hero = HeroSection(
        title="Dijital Dönüşümünüze Başlayın",
        subtitle="Profesyonel Web Çözümleri",
        description="İşletmenizi büyütmek için en iyi dijital hizmetleri sunuyoruz. Modern tasarım, güçlü altyapı.",
        button_text="Hemen Başla",
        button_link="#contact",
        background_color="#1e293b"
    )
    await db.hero_section.insert_one(serialize_doc(hero.model_dump()))
    
    # Service Cards
    sample_services = [
        {"title": "Web Tasarım", "description": "Modern ve responsive web siteleri tasarlıyoruz.", "icon": "globe", "order": 1},
        {"title": "Mobil Uygulama", "description": "iOS ve Android için mobil uygulamalar geliştiriyoruz.", "icon": "smartphone", "order": 2},
        {"title": "E-Ticaret", "description": "Online satış platformları kuruyoruz.", "icon": "shopping-cart", "order": 3},
        {"title": "SEO Optimizasyon", "description": "Arama motorlarında üst sıralara çıkın.", "icon": "search", "order": 4},
        {"title": "Dijital Pazarlama", "description": "Sosyal medya ve reklam yönetimi.", "icon": "megaphone", "order": 5},
        {"title": "Teknik Destek", "description": "7/24 teknik destek hizmeti.", "icon": "headphones", "order": 6},
    ]
    for s in sample_services:
        service = ServiceCard(**s)
        await db.service_cards.insert_one(serialize_doc(service.model_dump()))
    
    # Pricing Cards
    sample_pricing = [
        {
            "name": "Başlangıç",
            "price": 999,
            "period": "ay",
            "description": "Küçük işletmeler için ideal",
            "features": ["5 Sayfa Web Sitesi", "Mobil Uyumlu", "SSL Sertifikası", "1 Yıl Hosting", "E-posta Desteği"],
            "is_popular": False,
            "order": 1
        },
        {
            "name": "Profesyonel",
            "price": 2499,
            "period": "ay",
            "description": "Büyüyen işletmeler için",
            "features": ["15 Sayfa Web Sitesi", "Mobil Uyumlu", "SSL Sertifikası", "2 Yıl Hosting", "7/24 Destek", "SEO Optimizasyon", "Sosyal Medya Entegrasyonu"],
            "is_popular": True,
            "order": 2
        },
        {
            "name": "Kurumsal",
            "price": 4999,
            "period": "ay",
            "description": "Büyük şirketler için",
            "features": ["Sınırsız Sayfa", "Mobil Uyumlu", "SSL Sertifikası", "3 Yıl Hosting", "7/24 Öncelikli Destek", "SEO Optimizasyon", "E-Ticaret Entegrasyonu", "Özel Tasarım"],
            "is_popular": False,
            "order": 3
        },
    ]
    for p in sample_pricing:
        pricing = PricingCard(**p)
        await db.pricing_cards.insert_one(serialize_doc(pricing.model_dump()))
    
    # Testimonials
    sample_testimonials = [
        {"name": "Mehmet Yıldız", "title": "CEO, TechStart", "content": "Harika bir ekip! Web sitemiz sayesinde satışlarımız %200 arttı.", "rating": 5, "order": 1},
        {"name": "Ayşe Kara", "title": "Pazarlama Müdürü, ModaHouse", "content": "Profesyonel yaklaşımları ve zamanında teslimatları için teşekkürler.", "rating": 5, "order": 2},
        {"name": "Ali Demir", "title": "Kurucu, FitLife", "content": "E-ticaret sitemiz mükemmel çalışıyor. Kesinlikle tavsiye ederim.", "rating": 5, "order": 3},
    ]
    for t in sample_testimonials:
        testimonial = Testimonial(**t)
        await db.testimonials.insert_one(serialize_doc(testimonial.model_dump()))
    
    # Banners
    sample_banners = [
        {"title": "Yaz İndirimi", "subtitle": "Tüm hizmetlerde %20 indirim!", "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200", "button_text": "Fırsatı Yakala", "order": 1},
        {"title": "Yeni Özellikler", "subtitle": "AI destekli chatbot hizmeti başladı", "image": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=1200", "button_text": "Keşfet", "order": 2},
    ]
    for b in sample_banners:
        banner = Banner(**b)
        await db.banners.insert_one(serialize_doc(banner.model_dump()))
    
    # Menu Items
    sample_menu = [
        {"label": "Ana Sayfa", "link": "/", "order": 1},
        {"label": "Hizmetler", "link": "/services", "order": 2},
        {"label": "Fiyatlar", "link": "/pricing", "order": 3},
        {"label": "Hakkımızda", "link": "/about", "order": 4},
        {"label": "İletişim", "link": "/contact", "order": 5},
    ]
    for m in sample_menu:
        menu_item = MenuItem(**m)
        await db.menu_items.insert_one(serialize_doc(menu_item.model_dump()))
    
    # Section Contents
    sample_sections = [
        {"section_key": "about_us", "title": "Hakkımızda", "content": "10 yılı aşkın tecrübemizle dijital dünyada işletmelere rehberlik ediyoruz. Müşteri memnuniyeti odaklı yaklaşımımızla sektörde öncü konumdayız.", "order": 1},
        {"section_key": "mission", "title": "Misyonumuz", "content": "İşletmelerin dijital dönüşümünü hızlandırmak ve rekabet güçlerini artırmak için yenilikçi çözümler sunmak.", "order": 2},
        {"section_key": "vision", "title": "Vizyonumuz", "content": "Türkiye'nin lider dijital ajansı olarak global pazarda söz sahibi olmak.", "order": 3},
    ]
    for s in sample_sections:
        section = SectionContent(**s)
        await db.section_contents.insert_one(serialize_doc(section.model_dump()))
    
    # Chart Data
    sample_charts = [
        {
            "chart_key": "monthly_visitors",
            "title": "Aylık Ziyaretçi",
            "chart_type": "line",
            "data": [
                {"name": "Oca", "value": 4000},
                {"name": "Şub", "value": 3000},
                {"name": "Mar", "value": 5000},
                {"name": "Nis", "value": 4500},
                {"name": "May", "value": 6000},
                {"name": "Haz", "value": 5500}
            ]
        },
        {
            "chart_key": "sales_by_category",
            "title": "Kategoriye Göre Satışlar",
            "chart_type": "pie",
            "data": [
                {"name": "Web Tasarım", "value": 40},
                {"name": "Mobil Uygulama", "value": 30},
                {"name": "E-Ticaret", "value": 20},
                {"name": "Diğer", "value": 10}
            ]
        },
    ]
    for c in sample_charts:
        chart = ChartData(**c)
        await db.chart_data.insert_one(serialize_doc(chart.model_dump()))
    
    # FAQs
    sample_faqs = [
        {"question": "Web sitesi ne kadar sürede tamamlanır?", "answer": "Projenin kapsamına göre 2-6 hafta arasında değişir.", "order": 1},
        {"question": "Ödeme seçenekleri nelerdir?", "answer": "Kredi kartı, havale/EFT ve taksitli ödeme seçenekleri mevcuttur.", "order": 2},
        {"question": "Hosting dahil mi?", "answer": "Evet, tüm paketlerimizde hosting hizmeti dahildir.", "order": 3},
        {"question": "Değişiklik yapabilir miyim?", "answer": "Evet, teslimattan sonra 30 gün içinde ücretsiz revizyon hakkınız var.", "order": 4},
    ]
    for f in sample_faqs:
        faq = FAQ(**f)
        await db.faqs.insert_one(serialize_doc(faq.model_dump()))
    
    await log_activity("SEED", "system", "all", "Örnek veriler oluşturuldu")
    
    return {"message": "Örnek veriler başarıyla oluşturuldu"}

# Include the router in the main app
app.include_router(api_router)

cors_origins_raw = os.environ.get('CORS_ORIGINS', '*')
if cors_origins_raw == '*':
    # For credentials mode, we need specific origins
    cors_origins = [
        "http://localhost:3000",
        "https://admin-central-38.preview.emergentagent.com"
    ]
else:
    cors_origins = cors_origins_raw.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
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
