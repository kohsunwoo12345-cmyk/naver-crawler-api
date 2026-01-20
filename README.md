# SUPERPLAC 인플랩 (InfluLab)

소셜 미디어 트래픽 구매 플랫폼

## 📱 지원 플랫폼

- **Instagram**: 팔로워, 좋아요, 조회수, 저장, 공유
- **YouTube**: 구독자, 조회수, 좋아요, 댓글
- **Threads**: 팔로워, 좋아요, 리포스트
- **Facebook**: 팔로워, 좋아요, 공유, 댓글
- **Naver**: 플레이스 지수, 블로그 방문자, 카페 멤버

## 🏗️ 기술 스택

### Backend
- **FastAPI**: Python 웹 프레임워크
- **SQLAlchemy**: ORM
- **SQLite**: 데이터베이스 (개발), PostgreSQL (프로덕션)
- **Pydantic**: 데이터 검증

### Frontend
- **HTML5/CSS3/JavaScript**: 현대적 반응형 UI
- **Bootstrap 5**: UI 컴포넌트
- **Font Awesome**: 아이콘
- **Chart.js**: 통계 차트

## 🚀 주요 기능

### 1. 상품 카탈로그
- 플랫폼별 서비스 분류
- 실시간 가격 표시
- 수량별 할인
- 배송 예상 시간

### 2. 주문 시스템
- 장바구니
- 즉시 구매
- 주문 추적
- 진행 상황 알림

### 3. 결제 시스템
- 신용카드/체크카드
- 간편결제 (카카오페이, 네이버페이)
- 가상계좌
- 포인트 적립

### 4. 관리자 대시보드
- 주문 관리
- 상품 관리
- 통계 분석
- 고객 관리

## 📦 설치 및 실행

### 로컬 개발
```bash
# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 초기화
python -m backend.init_db

# 서버 실행
python main.py
```

### 환경 변수
```
DATABASE_URL=sqlite:///./superplac.db
SECRET_KEY=your-secret-key-here
PORT=8000
```

## 🌐 API 엔드포인트

### 상품
- `GET /api/products` - 전체 상품 목록
- `GET /api/products/{id}` - 상품 상세
- `GET /api/products/platform/{platform}` - 플랫폼별 상품

### 주문
- `POST /api/orders` - 주문 생성
- `GET /api/orders/{id}` - 주문 조회
- `PUT /api/orders/{id}/status` - 주문 상태 업데이트

### 결제
- `POST /api/payments/card` - 카드 결제
- `POST /api/payments/simple` - 간편결제
- `GET /api/payments/{id}/status` - 결제 상태 조회

## 📊 데이터베이스 스키마

### Products (상품)
- id, name, platform, service_type, price, quantity, delivery_time, description

### Orders (주문)
- id, user_id, product_id, quantity, total_price, status, created_at

### Payments (결제)
- id, order_id, method, amount, status, transaction_id, created_at

## 🔒 보안

- HTTPS 필수
- API 키 인증
- SQL Injection 방지
- XSS 방지
- CSRF 토큰

## 📝 라이센스

Copyright © 2026 SUPERPLAC. All rights reserved.

## 👥 개발자

SUPERPLAC Team - AI-Powered Social Media Growth Platform
