# Railway 메모리 관리 가이드

## 💰 중요: Railway 비용 절약 방법

Railway는 **메모리 사용량(RAM)**에 따라 비용이 청구됩니다!
Selenium + Chrome은 메모리를 많이 사용하므로 **확실한 정리**가 필수입니다.

---

## 🔒 메모리 누수 방지 조치

### 1. driver.quit() 강제 실행
```python
finally:
    if driver:
        try:
            driver.close()      # 모든 윈도우 닫기
            driver.quit()       # WebDriver 프로세스 킬
            driver = None       # 변수 초기화
        except:
            driver = None
    
    # 가비지 컬렉션 강제 실행
    import gc
    gc.collect()
```

### 2. 메모리 모니터링
모든 크롤링 요청마다 메모리 사용량을 로그로 출력:
```
💾 [크롤링 시작 전] 메모리 사용량: 120.45 MB
💾 [WebDriver 생성 후] 메모리 사용량: 245.32 MB
💾 [크롤링 완료 (driver.quit() 전)] 메모리 사용량: 298.67 MB
💾 [크롤링 완료 (메모리 정리 후)] 메모리 사용량: 135.21 MB
```

### 3. Chrome 최적화 옵션
```python
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-background-networking')

# 이미지/CSS 로딩 비활성화 (속도 + 메모리 절약)
prefs = {
    'profile.managed_default_content_settings.images': 2,
    'profile.managed_default_content_settings.stylesheets': 2
}
```

---

## 📊 Railway 메모리 사용량 확인 방법

### Railway 대시보드:
1. 프로젝트 클릭
2. **Metrics 탭** 클릭
3. **Memory** 그래프 확인

### 정상 범위:
- **유휴 상태**: 100-150 MB
- **크롤링 중**: 250-350 MB
- **크롤링 후**: 120-180 MB (정리 완료)

### ⚠️ 비정상 신호:
- **크롤링 후에도 300MB 이상**: 메모리 누수!
- **시간이 지날수록 증가**: driver.quit() 실패!
- **500MB 이상**: 즉시 조치 필요!

---

## 💡 비용 절약 팁

### 1. 불필요한 크롤링 최소화
- 같은 키워드 반복 조회 방지
- 캐싱 활용 (동일 키워드 24시간 내 재조회 시 캐시 반환)

### 2. 크롤링 타임아웃 설정
```python
driver.set_page_load_timeout(30)  # 30초 초과 시 중단
```

### 3. Railway 플랜 선택
- **Free Trial**: $5 크레딧 (테스트용)
- **Starter ($5/월)**: 512MB RAM, 소규모
- **Pro ($20/월)**: 8GB RAM, 중대규모

---

## 🔍 문제 해결

### 메모리 누수 발생 시:
1. Railway Deploy Logs 확인
2. `✅ WebDriver 정상 종료` 메시지 확인
3. 없으면 코드 수정 필요

### 비용 급증 시:
1. Metrics 탭에서 메모리 그래프 확인
2. 비정상 스파이크 확인
3. 해당 시간대 로그 분석

---

## 📈 예상 비용 (참고)

### 무료 플랜 ($5 크레딧):
- 크롤링 1회당 약 30초
- 월 500회 정도 가능

### Starter ($5/월):
- 크롤링 1회당 약 30초
- 월 2,000-3,000회 가능

### Pro ($20/월):
- 크롤링 1회당 약 30초
- 월 10,000회 이상 가능

**중요**: 메모리 정리를 확실히 하면 **비용 50% 이상 절감** 가능!

---

## ✅ 체크리스트

매일 확인사항:
- [ ] Railway Metrics에서 메모리 사용량 확인
- [ ] Deploy Logs에서 `✅ WebDriver 정상 종료` 확인
- [ ] 메모리 사용량이 비정상적으로 높지 않은지 확인
- [ ] 크롤링 후 메모리가 정상 범위로 돌아오는지 확인

---

**원장님, 이 가이드를 참고해서 주기적으로 모니터링해주세요!** 💰

메모리 관리만 잘하면 Railway 비용을 크게 절약할 수 있습니다!
