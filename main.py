from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import hashlib
import hmac
import base64
import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

app = FastAPI(title="Naver Crawler API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 네이버 검색광고 API 설정
NAVER_API_CUSTOMER_ID = os.getenv("NAVER_API_CUSTOMER_ID", "wangholy1:naver")
NAVER_API_LICENSE = os.getenv("NAVER_API_LICENSE", "01000000006a4f450842ff67bf50816ad0b679dd44241f6b641599b10cf7b3fd6e39cbb6c6")
NAVER_API_SECRET = os.getenv("NAVER_API_SECRET", "AQAAAABqT0UIQv9nv1CBatC2ed1Ea/SXPmw5pFA12eIEoWlSXQ==")

# 요청 모델
class SearchAnalysisRequest(BaseModel):
    keyword: str
    placeUrl: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

# 네이버 검색광고 API 시그니처 생성
def generate_signature(timestamp: str, method: str, uri: str) -> str:
    """네이버 검색광고 API 서명 생성"""
    message = f"{timestamp}.{method}.{uri}"
    signature = hmac.new(
        NAVER_API_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

# 네이버 검색광고 API 호출
def call_naver_api(keyword: str) -> Dict:
    """네이버 검색광고 API로 키워드 검색량 조회"""
    try:
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        uri = "/keywordstool"
        
        signature = generate_signature(timestamp, method, uri)
        
        headers = {
            "X-Timestamp": timestamp,
            "X-API-KEY": NAVER_API_LICENSE,
            "X-Customer": NAVER_API_CUSTOMER_ID,
            "X-Signature": signature,
            "Content-Type": "application/json"
        }
        
        # 키워드 검색량 조회 API
        url = f"https://api.naver.com/keywordstool"
        params = {
            "hintKeywords": keyword,
            "showDetail": "1"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "data": data
            }
        else:
            print(f"API 오류: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"API 오류: {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        print(f"API 호출 오류: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Selenium 초기화
def init_driver():
    """Chrome 드라이버 초기화"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# 네이버 플레이스 순위 크롤링
def crawl_place_ranking(keyword: str, target_url: Optional[str] = None) -> Dict:
    """네이버 플레이스 순위 크롤링 (광고 제외)"""
    driver = None
    try:
        driver = init_driver()
        
        # 네이버 검색
        search_url = f"https://m.search.naver.com/search.naver?query={keyword}&where=m&sm=mob_hty.idx"
        driver.get(search_url)
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # 플레이스 목록 찾기
        places = []
        my_rank = None
        
        # 광고가 아닌 일반 플레이스 찾기
        place_elements = driver.find_elements(By.CSS_SELECTOR, "div.place_list_wrap li, div.lst_total li")
        
        for idx, place in enumerate(place_elements[:20], 1):
            try:
                # 광고 요소 제외
                if "ad" in place.get_attribute("class").lower():
                    continue
                
                # 업체명
                name_elem = place.find_element(By.CSS_SELECTOR, ".tit, .name, h2, .title")
                name = name_elem.text.strip() if name_elem else "업체명 없음"
                
                # 카테고리
                try:
                    category_elem = place.find_element(By.CSS_SELECTOR, ".category, .cate")
                    category = category_elem.text.strip()
                except:
                    category = ""
                
                # 리뷰 수
                try:
                    review_elem = place.find_element(By.CSS_SELECTOR, ".cnt, .review_count")
                    review_text = review_elem.text.strip()
                    review_count = int(''.join(filter(str.isdigit, review_text)))
                except:
                    review_count = 0
                
                # URL
                try:
                    link_elem = place.find_element(By.CSS_SELECTOR, "a")
                    place_url = link_elem.get_attribute("href")
                except:
                    place_url = ""
                
                place_info = {
                    "rank": idx,
                    "name": name,
                    "category": category,
                    "reviewCount": review_count,
                    "url": place_url
                }
                
                places.append(place_info)
                
                # 내 순위 확인
                if target_url and target_url in place_url:
                    my_rank = idx
                
            except Exception as e:
                print(f"플레이스 파싱 오류: {str(e)}")
                continue
        
        return {
            "success": True,
            "myRank": my_rank,
            "competitors": places[:10]  # 상위 10개만 반환
        }
        
    except Exception as e:
        print(f"크롤링 오류: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "myRank": None,
            "competitors": []
        }
    finally:
        if driver:
            driver.quit()

# 경쟁사 키워드 추출
def extract_competitor_keywords(competitors: List[Dict]) -> List[Dict]:
    """경쟁사 키워드 추출 (간단 버전)"""
    result = []
    
    for comp in competitors[:5]:  # 상위 5개 경쟁사만
        keywords = []
        
        # 업체명에서 키워드 추출
        name = comp.get("name", "")
        category = comp.get("category", "")
        
        # 카테고리 기반 키워드 추출
        if "영어" in name or "영어" in category:
            keywords.extend(["영어학원", "영어교육", "영어회화"])
        if "수학" in name or "수학" in category:
            keywords.extend(["수학학원", "수학교육", "수학전문"])
        if "학원" in name:
            keywords.append("학원")
        if "교습소" in name:
            keywords.append("교습소")
        
        # 지역명 추출
        if any(word in name for word in ["인천", "서구", "청라"]):
            keywords.append("인천학원")
        
        result.append({
            "businessName": name,
            "keywords": list(set(keywords))[:5]  # 중복 제거 후 최대 5개
        })
    
    return result

# 검색량 데이터 파싱
def parse_search_volume(api_response: Dict) -> Dict:
    """네이버 API 응답에서 검색량 데이터 파싱"""
    try:
        if not api_response.get("success"):
            return {
                "monthlyAvg": 0,
                "competition": "알 수 없음",
                "recommendation": "분석중"
            }
        
        data = api_response.get("data", {})
        keywords = data.get("keywordList", [])
        
        if not keywords:
            return {
                "monthlyAvg": 0,
                "competition": "낮음",
                "recommendation": "데이터 없음"
            }
        
        # 첫 번째 키워드 데이터 사용
        keyword_data = keywords[0]
        monthly_avg = keyword_data.get("monthlyPcQcCnt", 0) + keyword_data.get("monthlyMobileQcCnt", 0)
        comp_idx = keyword_data.get("compIdx", "01")
        
        # 경쟁 강도 판단
        comp_map = {
            "01": "낮음",
            "02": "보통",
            "03": "높음",
            "04": "매우 높음"
        }
        competition = comp_map.get(comp_idx, "보통")
        
        # 추천도 판단
        if monthly_avg >= 1000 and comp_idx in ["01", "02"]:
            recommendation = "적극 추천"
        elif monthly_avg >= 500:
            recommendation = "추천"
        elif monthly_avg >= 100:
            recommendation = "보통"
        else:
            recommendation = "낮은 검색량"
        
        return {
            "monthlyAvg": monthly_avg,
            "competition": competition,
            "recommendation": recommendation
        }
        
    except Exception as e:
        print(f"데이터 파싱 오류: {str(e)}")
        return {
            "monthlyAvg": 0,
            "competition": "알 수 없음",
            "recommendation": "오류 발생"
        }

@app.get("/", response_model=HealthResponse)
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "message": "Naver Crawler API is running"
    }

@app.post("/analyze")
async def analyze_keyword(request: SearchAnalysisRequest):
    """키워드 분석 (검색량 + 순위)"""
    try:
        keyword = request.keyword
        place_url = request.placeUrl
        
        print(f"분석 시작: {keyword}, {place_url}")
        
        # 1. 네이버 검색광고 API로 검색량 조회
        api_response = call_naver_api(keyword)
        search_volume = parse_search_volume(api_response)
        
        # 2. Selenium으로 플레이스 순위 크롤링
        ranking_data = crawl_place_ranking(keyword, place_url)
        
        # 3. 경쟁사 키워드 추출
        competitors = ranking_data.get("competitors", [])
        keywords = extract_competitor_keywords(competitors)
        
        return {
            "success": True,
            "searchVolume": search_volume,
            "ranking": {
                "myRank": ranking_data.get("myRank"),
                "competitors": competitors
            },
            "keywords": keywords
        }
        
    except Exception as e:
        print(f"분석 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-api")
async def test_naver_api():
    """네이버 API 테스트"""
    result = call_naver_api("영어학원")
    return result

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
