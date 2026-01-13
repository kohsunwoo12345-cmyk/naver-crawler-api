# Naver Crawler API

네이버 검색광고 API + Selenium 크롤링 서버

## 기술 스택
- **FastAPI**: Python 웹 프레임워크
- **Selenium**: 웹 자동화 및 크롤링
- **Chrome (Headless)**: 브라우저 엔진
- **네이버 검색광고 API**: 검색량 데이터

## 주요 기능
1. **네이버 검색광고 API**: 월 평균 검색량, 경쟁 강도
2. **Selenium 크롤링**: 플레이스 순위, 경쟁사 정보
3. **경쟁사 키워드 추출**: 자동 키워드 분석
4. **메모리 최적화**: driver.quit() 자동 처리

## 환경 변수
```
NAVER_API_CUSTOMER_ID=1978176
NAVER_API_LICENSE=0100000000713f505bb5fda08833f32b6a9ae08c5ea5789f134c7b140446e58bdb4183fc1d
NAVER_API_SECRET=AQAAAABxP1Bbtf2giDPzK2qa4Ixetc774mZsCjCKxTp2BVV29g==
PORT=8000
```

## API 엔드포인트
- `GET /`: 헬스 체크
- `POST /analyze`: 키워드 분석
- `GET /test-api`: 네이버 API 테스트

## Docker 배포
```bash
docker build -t naver-crawler .
docker run -p 8000:8000 \
  -e NAVER_API_CUSTOMER_ID=1978176 \
  -e NAVER_API_LICENSE=... \
  -e NAVER_API_SECRET=... \
  naver-crawler
```

## Railway 배포
1. GitHub 저장소 연결
2. 환경 변수 설정 (4개)
3. 자동 빌드 & 배포

## 로컬 개발
```bash
pip install -r requirements.txt
python main.py
```

## 메모리 관리
- Selenium WebDriver는 사용 후 자동 종료 (`driver.quit()`)
- Headless 모드로 메모리 사용량 최소화
- 이미지/CSS 로딩 비활성화로 속도 향상

## 배포 정보
- 저장소: https://github.com/kohsunwoo12345-cmyk/naver-crawler-api
- Railway URL: https://web-production-14c4.up.railway.app
