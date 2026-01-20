from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os

# 데이터베이스 URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./superplac.db")

# 엔진 생성
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """데이터베이스 테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블이 생성되었습니다.")

def seed_products():
    """초기 상품 데이터 삽입"""
    from database.models import Product
    
    db = SessionLocal()
    
    # 기존 상품이 있는지 확인
    if db.query(Product).count() > 0:
        print("⚠️  상품 데이터가 이미 존재합니다.")
        db.close()
        return
    
    products = [
        # Instagram
        Product(
            name="인스타그램 팔로워",
            platform="instagram",
            service_type="instagram_followers",
            description="고품질 실제 계정 팔로워. 자연스러운 증가로 안전합니다.",
            base_price=0.05,  # 팔로워당 50원
            min_quantity=100,
            max_quantity=50000,
            delivery_time="1-3일"
        ),
        Product(
            name="인스타그램 좋아요",
            platform="instagram",
            service_type="instagram_likes",
            description="게시물에 즉시 좋아요가 증가합니다.",
            base_price=0.02,
            min_quantity=100,
            max_quantity=100000,
            delivery_time="즉시"
        ),
        Product(
            name="인스타그램 조회수",
            platform="instagram",
            service_type="instagram_views",
            description="릴스 및 비디오 조회수 증가.",
            base_price=0.01,
            min_quantity=1000,
            max_quantity=1000000,
            delivery_time="즉시"
        ),
        Product(
            name="인스타그램 저장",
            platform="instagram",
            service_type="instagram_saves",
            description="게시물 저장 수 증가로 알고리즘 노출 향상.",
            base_price=0.03,
            min_quantity=50,
            max_quantity=10000,
            delivery_time="1-2일"
        ),
        
        # YouTube
        Product(
            name="유튜브 구독자",
            platform="youtube",
            service_type="youtube_subscribers",
            description="실제 활동하는 구독자로 채널 성장.",
            base_price=0.3,  # 구독자당 300원
            min_quantity=100,
            max_quantity=10000,
            delivery_time="3-7일"
        ),
        Product(
            name="유튜브 조회수",
            platform="youtube",
            service_type="youtube_views",
            description="영상 조회수 증가로 알고리즘 추천 향상.",
            base_price=0.015,
            min_quantity=1000,
            max_quantity=1000000,
            delivery_time="1-3일"
        ),
        Product(
            name="유튜브 좋아요",
            platform="youtube",
            service_type="youtube_likes",
            description="영상 좋아요 증가로 인기도 상승.",
            base_price=0.04,
            min_quantity=100,
            max_quantity=50000,
            delivery_time="1-2일"
        ),
        
        # Threads
        Product(
            name="쓰레드 팔로워",
            platform="threads",
            service_type="threads_followers",
            description="메타의 새로운 플랫폼 쓰레드 팔로워 증가.",
            base_price=0.06,
            min_quantity=100,
            max_quantity=20000,
            delivery_time="1-3일"
        ),
        Product(
            name="쓰레드 좋아요",
            platform="threads",
            service_type="threads_likes",
            description="쓰레드 게시물 좋아요 증가.",
            base_price=0.02,
            min_quantity=50,
            max_quantity=10000,
            delivery_time="즉시"
        ),
        
        # Facebook
        Product(
            name="페이스북 팔로워",
            platform="facebook",
            service_type="facebook_followers",
            description="페이지 팔로워 증가로 도달률 향상.",
            base_price=0.05,
            min_quantity=100,
            max_quantity=50000,
            delivery_time="2-5일"
        ),
        Product(
            name="페이스북 좋아요",
            platform="facebook",
            service_type="facebook_likes",
            description="게시물 및 페이지 좋아요 증가.",
            base_price=0.03,
            min_quantity=100,
            max_quantity=50000,
            delivery_time="1-3일"
        ),
        
        # Naver
        Product(
            name="네이버 플레이스 지수 상승",
            platform="naver",
            service_type="naver_place_score",
            description="플레이스 방문자 리뷰 증가로 지수 상승.",
            base_price=5.0,  # 지수당 5,000원
            min_quantity=10,
            max_quantity=1000,
            delivery_time="7-14일"
        ),
        Product(
            name="네이버 블로그 방문자",
            platform="naver",
            service_type="naver_blog_visitors",
            description="블로그 실 방문자 유입으로 검색 순위 상승.",
            base_price=0.1,
            min_quantity=500,
            max_quantity=100000,
            delivery_time="1-3일"
        ),
    ]
    
    db.add_all(products)
    db.commit()
    
    print(f"✅ {len(products)}개의 상품이 추가되었습니다.")
    db.close()

if __name__ == "__main__":
    init_db()
    seed_products()
