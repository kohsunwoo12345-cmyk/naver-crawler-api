from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class Platform(str, enum.Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    THREADS = "threads"
    FACEBOOK = "facebook"
    NAVER = "naver"

class ServiceType(str, enum.Enum):
    # Instagram
    INSTAGRAM_FOLLOWERS = "instagram_followers"
    INSTAGRAM_LIKES = "instagram_likes"
    INSTAGRAM_VIEWS = "instagram_views"
    INSTAGRAM_SAVES = "instagram_saves"
    INSTAGRAM_SHARES = "instagram_shares"
    
    # YouTube
    YOUTUBE_SUBSCRIBERS = "youtube_subscribers"
    YOUTUBE_VIEWS = "youtube_views"
    YOUTUBE_LIKES = "youtube_likes"
    YOUTUBE_COMMENTS = "youtube_comments"
    
    # Threads
    THREADS_FOLLOWERS = "threads_followers"
    THREADS_LIKES = "threads_likes"
    THREADS_REPOSTS = "threads_reposts"
    
    # Facebook
    FACEBOOK_FOLLOWERS = "facebook_followers"
    FACEBOOK_LIKES = "facebook_likes"
    FACEBOOK_SHARES = "facebook_shares"
    FACEBOOK_COMMENTS = "facebook_comments"
    
    # Naver
    NAVER_PLACE_SCORE = "naver_place_score"
    NAVER_BLOG_VISITORS = "naver_blog_visitors"
    NAVER_CAFE_MEMBERS = "naver_cafe_members"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FAILED = "failed"
    REFUNDED = "refunded"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)
    service_type = Column(String(100), nullable=False)
    description = Column(Text)
    base_price = Column(Float, nullable=False)  # 기본 단가
    min_quantity = Column(Integer, default=100)
    max_quantity = Column(Integer, default=100000)
    delivery_time = Column(String(50))  # 예: "1-3일", "즉시"
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    customer_email = Column(String(255), nullable=False)
    customer_name = Column(String(255))
    target_url = Column(String(500), nullable=False)  # Instagram URL, YouTube URL 등
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="orders")
    payment = relationship("Payment", back_populates="order", uselist=False)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    method = Column(String(50), nullable=False)  # card, kakaopay, naverpay, etc
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    transaction_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="payment")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
