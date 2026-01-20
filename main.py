from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
from database.database import get_db, init_db, seed_products
from database.models import Product, Order, Payment, OrderStatus, PaymentStatus
import os

# FastAPI 앱 초기화
app = FastAPI(
    title="SUPERPLAC 인플랩",
    description="소셜 미디어 트래픽 구매 플랫폼",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ========== Pydantic 모델 ==========

class ProductResponse(BaseModel):
    id: int
    name: str
    platform: str
    service_type: str
    description: Optional[str]
    base_price: float
    min_quantity: int
    max_quantity: int
    delivery_time: Optional[str]
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    product_id: int
    customer_email: EmailStr
    customer_name: str
    target_url: str
    quantity: int
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    product_id: int
    customer_email: str
    customer_name: str
    target_url: str
    quantity: int
    unit_price: float
    total_price: float
    status: str
    
    class Config:
        from_attributes = True

class PaymentCreate(BaseModel):
    order_id: int
    method: str  # card, kakaopay, naverpay, bank

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    method: str
    amount: float
    status: str
    transaction_id: Optional[str]
    
    class Config:
        from_attributes = True

# ========== 헬스 체크 ==========

@app.get("/")
async def root(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """API 헬스 체크"""
    return {
        "status": "healthy",
        "service": "SUPERPLAC 인플랩",
        "version": "1.0.0"
    }

# ========== 상품 API ==========

@app.get("/api/products", response_model=List[ProductResponse])
async def get_products(
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """전체 상품 목록 조회"""
    query = db.query(Product).filter(Product.is_active == 1)
    
    if platform:
        query = query.filter(Product.platform == platform)
    
    products = query.all()
    return products

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """상품 상세 조회"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    
    return product

@app.get("/api/products/platform/{platform}", response_model=List[ProductResponse])
async def get_products_by_platform(platform: str, db: Session = Depends(get_db)):
    """플랫폼별 상품 조회"""
    products = db.query(Product).filter(
        Product.platform == platform,
        Product.is_active == 1
    ).all()
    
    return products

@app.get("/api/platforms")
async def get_platforms():
    """지원 플랫폼 목록"""
    return {
        "platforms": [
            {
                "id": "instagram",
                "name": "Instagram",
                "icon": "fab fa-instagram",
                "color": "#E4405F"
            },
            {
                "id": "youtube",
                "name": "YouTube",
                "icon": "fab fa-youtube",
                "color": "#FF0000"
            },
            {
                "id": "threads",
                "name": "Threads",
                "icon": "fas fa-at",
                "color": "#000000"
            },
            {
                "id": "facebook",
                "name": "Facebook",
                "icon": "fab fa-facebook",
                "color": "#1877F2"
            },
            {
                "id": "naver",
                "name": "Naver",
                "icon": "fas fa-n",
                "color": "#03C75A"
            }
        ]
    }

# ========== 주문 API ==========

@app.post("/api/orders", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """주문 생성"""
    # 상품 조회
    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    
    # 수량 검증
    if order_data.quantity < product.min_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"최소 주문 수량은 {product.min_quantity}개입니다."
        )
    
    if order_data.quantity > product.max_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"최대 주문 수량은 {product.max_quantity}개입니다."
        )
    
    # 가격 계산 (수량에 따른 할인)
    unit_price = product.base_price
    if order_data.quantity >= 10000:
        unit_price *= 0.8  # 20% 할인
    elif order_data.quantity >= 5000:
        unit_price *= 0.85  # 15% 할인
    elif order_data.quantity >= 1000:
        unit_price *= 0.9  # 10% 할인
    
    total_price = unit_price * order_data.quantity
    
    # 주문 생성
    new_order = Order(
        product_id=order_data.product_id,
        customer_email=order_data.customer_email,
        customer_name=order_data.customer_name,
        target_url=order_data.target_url,
        quantity=order_data.quantity,
        unit_price=unit_price,
        total_price=total_price,
        status="pending",
        notes=order_data.notes
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return new_order

@app.get("/api/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """주문 조회"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    
    return order

@app.put("/api/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """주문 상태 업데이트"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    
    order.status = status
    db.commit()
    
    return {"message": "주문 상태가 업데이트되었습니다.", "status": status}

# ========== 결제 API ==========

@app.post("/api/payments", response_model=PaymentResponse)
async def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    """결제 생성"""
    # 주문 조회
    order = db.query(Order).filter(Order.id == payment_data.order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다.")
    
    # 이미 결제가 존재하는지 확인
    existing_payment = db.query(Payment).filter(Payment.order_id == payment_data.order_id).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="이미 결제가 진행된 주문입니다.")
    
    # 결제 생성 (실제로는 PG사 API 호출)
    import uuid
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    new_payment = Payment(
        order_id=payment_data.order_id,
        method=payment_data.method,
        amount=order.total_price,
        status="approved",  # 실제로는 PG사 응답에 따라 설정
        transaction_id=transaction_id
    )
    
    db.add(new_payment)
    
    # 주문 상태 업데이트
    order.status = "processing"
    
    db.commit()
    db.refresh(new_payment)
    
    return new_payment

@app.get("/api/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """결제 조회"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="결제 정보를 찾을 수 없습니다.")
    
    return payment

# ========== 통계 API ==========

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """통계 데이터"""
    total_products = db.query(Product).filter(Product.is_active == 1).count()
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == "pending").count()
    completed_orders = db.query(Order).filter(Order.status == "completed").count()
    
    # 총 매출
    from sqlalchemy import func
    total_revenue = db.query(func.sum(Order.total_price)).scalar() or 0
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_revenue": float(total_revenue)
    }

# ========== 시작 시 데이터베이스 초기화 ==========

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    print("=" * 60)
    print("🚀 SUPERPLAC 인플랩 서버 시작")
    print("=" * 60)
    init_db()
    seed_products()
    print("✅ 데이터베이스 초기화 완료")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
