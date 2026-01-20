# 🚀 Railway 배포 가이드

## Railway란?
Railway는 Python, Node.js 등의 백엔드 서버를 간편하게 배포할 수 있는 플랫폼입니다.

## 배포 절차

### 1단계: Railway 계정 생성
1. https://railway.app 접속
2. "Start a New Project" 클릭
3. GitHub 계정으로 로그인

### 2단계: GitHub 저장소 연결
1. "Deploy from GitHub repo" 선택
2. `naver-crawler-api` 저장소 선택
3. "Deploy Now" 클릭

### 3단계: 환경 변수 설정
Railway 대시보드에서 다음 환경 변수를 추가하세요:

```
NAVER_API_CUSTOMER_ID=wangholy1:naver
NAVER_API_LICENSE=01000000006a4f450842ff67bf50816ad0b679dd44241f6b641599b10cf7b3fd6e39cbb6c6
NAVER_API_SECRET=AQAAAABqT0UIQv9nv1CBatC2ed1Ea/SXPmw5pFA12eIEoWlSXQ==
PORT=8000
```

**설정 방법:**
1. Railway 프로젝트 클릭
2. "Variables" 탭 클릭
3. 각 변수 추가 (New Variable 버튼)

### 4단계: Chromium 빌드팩 추가 (Selenium용)
Railway는 자동으로 Chrome을 설치하지 않으므로 Nixpacks 설정이 필요합니다.

**이미 `railway.json`에 설정되어 있습니다:**
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && playwright install chromium"
  }
}
```

### 5단계: 배포 확인
1. Railway가 자동으로 빌드 시작
2. 빌드 로그 확인 (Build Logs)
3. 배포 완료 후 URL 확인 (예: `https://naver-crawler-api.railway.app`)

### 6단계: API 테스트
배포된 URL로 헬스 체크:
```bash
curl https://your-app.railway.app/
```

응답:
```json
{
  "status": "healthy",
  "message": "Naver Crawler API is running"
}
```

### 7단계: Cloudflare Pages API 업데이트
배포된 Railway URL을 복사하고, `/home/user/webapp/src/index.tsx` 파일에서 다음 부분을 수정:

```typescript
// 현재 (임시):
const CRAWLER_API_URL = 'https://naver-crawler-api.railway.app/analyze'

// 실제 Railway 배포 URL로 변경:
const CRAWLER_API_URL = 'https://your-actual-app.railway.app/analyze'
```

그 후 다시 빌드 및 배포:
```bash
cd /home/user/webapp
npm run build
npx wrangler pages deploy dist --project-name superplace-academy
```

## 문제 해결

### Chrome 드라이버 오류
**증상:** `selenium.common.exceptions.WebDriverException`

**해결:**
Railway의 Settings → Environment에서 다음 추가:
```
PYTHONUNBUFFERED=1
```

### 메모리 부족 오류
**증상:** 크롤링 중 서버 크래시

**해결:**
Railway Pro 플랜으로 업그레이드 (512MB → 8GB RAM)

### API 응답 느림
**증상:** 타임아웃 오류

**해결:**
- Cloudflare API에서 타임아웃 설정 증가
- 크롤링 대상 페이지 수 제한

## 비용
- **Free Plan**: 월 $5 크레딧 (약 500시간 실행)
- **Pro Plan**: 월 $20 (무제한 실행, 더 많은 메모리)

## 대안 배포 플랫폼
- **Render**: https://render.com (무료 플랜 있음)
- **Fly.io**: https://fly.io (무료 플랜 있음)
- **Heroku**: https://heroku.com (유료)

## GitHub 저장소
https://github.com/kohsunwoo12345-cmyk/naver-crawler-api
