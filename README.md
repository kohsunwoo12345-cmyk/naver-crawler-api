# Naver Crawler API

네이버 검색광고 API와 Selenium을 활용한 검색량 및 순위 분석 서버

## 기능

- 네이버 검색광고 API를 통한 키워드 검색량 조회
- Selenium을 이용한 네이버 플레이스 순위 크롤링 (광고 제외)
- 경쟁사 정보 및 키워드 추출

## 환경 변수

Railway 배포 시 다음 환경 변수를 설정하세요:

```
NAVER_API_CUSTOMER_ID=wangholy1:naver
NAVER_API_LICENSE=01000000006a4f450842ff67bf50816ad0b679dd44241f6b641599b10cf7b3fd6e39cbb6c6
NAVER_API_SECRET=AQAAAABqT0UIQv9nv1CBatC2ed1Ea/SXPmw5pFA12eIEoWlSXQ==
PORT=8000
```

## API 엔드포인트

### POST /analyze
키워드 분석 (검색량 + 순위)

**요청:**
```json
{
  "keyword": "인천 영어학원",
  "placeUrl": "https://m.place.naver.com/place/..."
}
```

**응답:**
```json
{
  "success": true,
  "searchVolume": {
    "monthlyAvg": 1200,
    "competition": "높음",
    "recommendation": "추천"
  },
  "ranking": {
    "myRank": 3,
    "competitors": [...]
  },
  "keywords": [...]
}
```

### GET /
헬스 체크

### GET /test-api
네이버 API 테스트

## 로컬 실행

```bash
pip install -r requirements.txt
python main.py
```

서버가 http://localhost:8000 에서 실행됩니다.

## Railway 배포

1. Railway 계정 생성: https://railway.app
2. GitHub 연동 또는 CLI 배포
3. 환경 변수 설정
4. Chrome 빌드팩 추가 (Selenium 사용)

## 기술 스택

- FastAPI - 웹 프레임워크
- Selenium - 웹 크롤링
- Requests - HTTP 클라이언트
- Uvicorn - ASGI 서버

## 주의사항

- Chrome 드라이버 필요 (Railway는 자동 설치)
- 크롤링 속도 제한 고려
- 네이버 API 사용량 제한 확인
