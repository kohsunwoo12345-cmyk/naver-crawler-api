from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import hashlib
import hmac
import base64
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import json
import os
import traceback

app = FastAPI(title="Naver Crawler API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 네이버 검색광고 API 설정 (새 계정)
NAVER_API_CUSTOMER_ID = os.getenv("NAVER_API_CUSTOMER_ID", "1978176")
NAVER_API_LICENSE = os.getenv("NAVER_API_LICENSE", "0100000000713f505bb5fda08833f32b6a9ae08c5ea5789f134c7b140446e58bdb4183fc1d")
NAVER_API_SECRET = os.getenv("NAVER_API_SECRET", "AQAAAABxP1Bbtf2giDPzK2qa4Ixetc774mZsCjCKxTp2BVV29g==")

# 환경 변수 검증 (상세)
print(f"=" * 60)
print(f"🔧 Environment Variables Check:")
print(f"  - CUSTOMER_ID: {NAVER_API_CUSTOMER_ID if NAVER_API_CUSTOMER_ID else '❌ NOT SET'}")
print(f"  - LICENSE: {NAVER_API_LICENSE[:20] + '...' if NAVER_API_LICENSE else '❌ NOT SET'}")
print(f"  - SECRET: {NAVER_API_SECRET[:20] + '...' if NAVER_API_SECRET else '❌ NOT SET'}")
print(f"  - PORT: {os.getenv('PORT', '8000')}")
print(f"=" * 60)

# 환경 변수 누락 시 경고
if not NAVER_API_CUSTOMER_ID or not NAVER_API_LICENSE or not NAVER_API_SECRET:
    print("⚠️  WARNING: Some environment variables are missing!")
    print("⚠️  Please set all required variables in Railway dashboard.")

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
        # 지역명 제거 (인천, 서울, 부산 등)
        regions = ["인천", "서울", "부산", "대구", "대전", "광주", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
                   "서구", "북구", "동구", "남구", "중구", "청라", "검단", "송도", "강남", "강북", "서초", "종로", "마포", "강서", "해운대"]
        core_keyword = keyword
        for region in regions:
            core_keyword = core_keyword.replace(region + " ", "").replace(region, "")
        core_keyword = core_keyword.strip()
        
        print(f"원본 키워드: {keyword} → 핵심 키워드: {core_keyword}")
        
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
        url = "https://api.naver.com/keywordstool"
        params = {
            "hintKeywords": core_keyword,  # 핵심 키워드로 검색
            "showDetail": "1"
        }
        
        print(f"네이버 API 호출: {core_keyword}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            keywords = data.get("keywordList", [])
            if keywords:
                print(f"✅ {len(keywords)}개 키워드 발견")
                return {
                    "success": True,
                    "data": data
                }
            else:
                print("⚠️  키워드 데이터 없음")
                return {
                    "success": False,
                    "error": "키워드 데이터 없음"
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
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

# 네이버 플레이스 순위 크롤링 (개선 버전)
def crawl_place_ranking(keyword: str, target_url: Optional[str] = None) -> Dict:
    """네이버 플레이스 순위 크롤링 (BeautifulSoup + 광고 제외)"""
    try:
        print(f"🕷️  크롤링 시작: {keyword}")
        
        # 네이버 통합검색 모바일 API 직접 호출
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword)
        
        # 네이버 모바일 검색 결과 페이지
        search_url = f"https://m.search.naver.com/search.naver?query={encoded_keyword}&sm=mtb_jum&where=m&oquery={encoded_keyword}&tqi=iWe9cdqo15wssZCVXMRsssssttR-215835"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://m.naver.com/'
        }
        
        print(f"크롤링 URL: {search_url}")
        response = requests.get(search_url, headers=headers, timeout=30)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code} 오류")
            return {
                "success": False,
                "myRank": None,
                "competitors": []
            }
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        places = []
        my_rank = None
        rank = 0
        
        # 여러 선택자 패턴 시도
        selectors = [
            'div.place_didyoumean ul li',
            'div.list_image_type ul li',
            'ul.list_search li',
            'div.api_subject_bx ul li',
            'div[class*="place"] ul li',
            'li[class*="place"]',
            'ul[class*="list"] > li'
        ]
        
        place_containers = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ 선택자 '{selector}' - {len(elements)}개 발견")
                place_containers = elements
                break
        
        if not place_containers:
            print("⚠️  플레이스 컨테이너를 찾을 수 없음")
            # HTML 구조 분석 출력
            print(f"HTML 길이: {len(response.text)} bytes")
            print(f"HTML 샘플:\n{response.text[:1000]}")
            
            # 대안: 간단한 예시 데이터 반환
            return {
                "success": True,
                "myRank": None,
                "competitors": [
                    {"rank": 1, "name": "크롤링 제한", "category": "네이버 보안", "reviewCount": 0, "url": ""},
                    {"rank": 2, "name": "실제 순위는", "category": "브라우저에서", "reviewCount": 0, "url": ""},
                    {"rank": 3, "name": "확인 가능", "category": "수동 확인", "reviewCount": 0, "url": ""}
                ]
            }
        
        print(f"총 {len(place_containers)}개 플레이스 발견")
        
        for idx, place in enumerate(place_containers[:20], 1):
            try:
                # 광고 제외
                ad_marker = place.select_one('.ad_marker, .ad, [class*="ad"], [class*="Ad"]')
                if ad_marker:
                    ad_classes = str(ad_marker.get('class', []))
                    if 'ad' in ad_classes.lower():
                        print(f"광고 제외: {idx}")
                        continue
                
                rank += 1
                
                # 업체명
                name_elem = place.select_one('.place_bluelink, .YwYLL, span.place_name, strong.name, .tit, a.title')
                name = name_elem.get_text(strip=True) if name_elem else f"업체 {rank}"
                
                # 카테고리
                category_elem = place.select_one('.category, .cate, .type, .KCMnt, .info_distance')
                category = category_elem.get_text(strip=True) if category_elem else "일반"
                
                # 리뷰 수
                review_count = 0
                review_elem = place.select_one('.review_count, .cnt, em.num, .NSTUp, .review')
                if review_elem:
                    review_text = review_elem.get_text(strip=True)
                    numbers = ''.join(filter(str.isdigit, review_text))
                    review_count = int(numbers) if numbers else 0
                
                # URL
                link_elem = place.select_one('a[href*="place.naver.com"], a[href*="/place/"], a.place_bluelink, a.title')
                place_url = ""
                if link_elem:
                    href = link_elem.get('href', '')
                    if href.startswith('http'):
                        place_url = href
                    elif href.startswith('/'):
                        place_url = f"https://m.place.naver.com{href}"
                    else:
                        place_url = f"https://m.place.naver.com/{href}"
                
                place_info = {
                    "rank": rank,
                    "name": name,
                    "category": category,
                    "reviewCount": review_count,
                    "url": place_url
                }
                
                print(f"순위 {rank}: {name} ({category}) - {review_count}개 리뷰")
                
                places.append(place_info)
                
                # 내 순위 확인
                if target_url and place_url and (target_url in place_url or place_url in target_url):
                    my_rank = rank
                    print(f"✅ 내 순위 발견: {rank}위")
                
                # 상위 10개만 수집
                if rank >= 10:
                    break
                    
            except Exception as e:
                print(f"플레이스 파싱 오류 (idx={idx}): {str(e)}")
                continue
        
        print(f"✅ 총 {len(places)}개 플레이스 추출 완료")
        
        return {
            "success": True,
            "myRank": my_rank,
            "competitors": places[:10]
        }
        
    except Exception as e:
        print(f"❌ 크롤링 오류: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "myRank": None,
            "competitors": []
        }
        if driver:
            try:
                driver.quit()
                print("✅ WebDriver 정상 종료")
            except Exception as e:
                print(f"⚠️  WebDriver 종료 오류: {str(e)}")

# 경쟁사 키워드 추출
def extract_competitor_keywords(competitors: List[Dict]) -> List[Dict]:
    """경쟁사 키워드 추출 (개선 버전)"""
    result = []
    
    for comp in competitors[:5]:  # 상위 5개 경쟁사만
        keywords = []
        
        # 업체명에서 키워드 추출
        name = comp.get("name", "")
        category = comp.get("category", "")
        
        # 업체명에서 핵심 키워드 추출
        if "영어" in name or "영어" in category or "English" in name:
            keywords.extend(["영어학원", "영어교육", "영어회화", "토익", "토플"])
        if "수학" in name or "수학" in category:
            keywords.extend(["수학학원", "수학교육", "수학전문", "수능수학"])
        if "국어" in name or "논술" in name:
            keywords.extend(["국어학원", "논술학원", "독서논술"])
        if "과학" in name:
            keywords.extend(["과학학원", "과학교육"])
        if "학원" in name:
            keywords.append("종합학원")
        if "교습소" in name or "교실" in name:
            keywords.append("교습소")
        if "아카데미" in name or "Academy" in name:
            keywords.append("아카데미")
            
        # 대상 학년 추출
        if any(word in name for word in ["초등", "유아", "어린이"]):
            keywords.append("초등학원")
        if "중등" in name or "중학" in name:
            keywords.append("중등학원")
        if "고등" in name or "입시" in name:
            keywords.append("고등학원")
            
        # 지역명 추출
        regions = ["인천", "서구", "청라", "검단", "경서", "가정", "석남"]
        for region in regions:
            if region in name:
                keywords.append(f"{region}학원")
                break
        
        # 특수 프로그램
        if any(word in name for word in ["원어민", "화상", "스피킹"]):
            keywords.append("원어민영어")
        if "방과후" in name:
            keywords.append("방과후학원")
            
        # 중복 제거 및 최대 8개로 제한
        keywords = list(set(keywords))[:8]
        
        # 키워드가 없으면 기본 키워드 추가
        if not keywords:
            keywords = ["학원", "교육", "학습"]
        
        result.append({
            "businessName": name,
            "keywords": keywords
        })
    
    return result

# 관련 키워드 추출
def extract_related_keywords(api_response: Dict, original_keyword: str = "", limit: int = 10) -> List[Dict]:
    """네이버 API에서 관련 키워드 추출 (CTR 포함)"""
    try:
        if not api_response.get("success"):
            return []
        
        data = api_response.get("data", {})
        keywords = data.get("keywordList", [])
        
        if not keywords:
            return []
        
        # 상위 N개 키워드 추출
        result = []
        for kw in keywords[:limit]:
            monthly_pc = kw.get("monthlyPcQcCnt", 0)
            monthly_mobile = kw.get("monthlyMobileQcCnt", 0)
            total_search = monthly_pc + monthly_mobile
            
            # CTR (클릭률) 계산
            pc_ctr = kw.get("monthlyAvePcCtr", 0)
            mobile_ctr = kw.get("monthlyAveMobileCtr", 0)
            
            # 가중 평균 CTR
            if total_search > 0:
                weighted_ctr = (pc_ctr * monthly_pc + mobile_ctr * monthly_mobile) / total_search
            else:
                weighted_ctr = 0
            
            # 경쟁 강도
            comp_idx = kw.get("compIdx", "01")
            comp_map = {
                "01": "낮음",
                "02": "보통",
                "03": "높음",
                "04": "매우 높음"
            }
            competition = comp_map.get(comp_idx, "보통")
            
            result.append({
                "keyword": kw.get("relKeyword", ""),
                "monthlySearchVolume": total_search,
                "monthlyPcSearch": monthly_pc,
                "monthlyMobileSearch": monthly_mobile,
                "averageCtr": round(weighted_ctr, 2),  # 평균 클릭률 (%)
                "pcCtr": round(pc_ctr, 2),
                "mobileCtr": round(mobile_ctr, 2),
                "competition": competition
            })
        
        return result
        
    except Exception as e:
        print(f"관련 키워드 추출 오류: {str(e)}")
        return []

# 검색량 데이터 파싱 (확장 버전)
def parse_search_volume_extended(api_response: Dict, original_keyword: str = "") -> Dict:
    """네이버 API 응답에서 검색량 + CTR 데이터 파싱"""
    try:
        if not api_response.get("success"):
            return {
                "monthlyAvg": 0,
                "monthlyPcSearch": 0,
                "monthlyMobileSearch": 0,
                "averageCtr": 0,
                "pcCtr": 0,
                "mobileCtr": 0,
                "competition": "알 수 없음",
                "recommendation": "분석중"
            }
        
        data = api_response.get("data", {})
        keywords = data.get("keywordList", [])
        
        if not keywords:
            return {
                "monthlyAvg": 0,
                "monthlyPcSearch": 0,
                "monthlyMobileSearch": 0,
                "averageCtr": 0,
                "pcCtr": 0,
                "mobileCtr": 0,
                "competition": "낮음",
                "recommendation": "데이터 없음"
            }
        
        # 원본 키워드와 가장 유사한 키워드 찾기
        keyword_data = keywords[0]  # 기본값
        
        if original_keyword:
            # 지역명 제거
            regions = ["인천", "서울", "부산", "대구", "대전", "광주", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
                       "서구", "북구", "동구", "남구", "중구", "청라", "검단", "송도", "강남", "강북", "서초", "종로", "마포", "강서", "해운대"]
            core_original = original_keyword
            for region in regions:
                core_original = core_original.replace(region + " ", "").replace(region, "")
            core_original = core_original.strip()
            
            # 정확히 일치하는 키워드 찾기
            for kw in keywords:
                if kw.get("relKeyword", "").strip() == core_original:
                    keyword_data = kw
                    break
            else:
                # 부분 일치 찾기
                for kw in keywords:
                    if core_original in kw.get("relKeyword", "") or kw.get("relKeyword", "") in core_original:
                        keyword_data = kw
                        break
        
        monthly_pc = keyword_data.get("monthlyPcQcCnt", 0)
        monthly_mobile = keyword_data.get("monthlyMobileQcCnt", 0)
        monthly_avg = monthly_pc + monthly_mobile
        
        # CTR 데이터
        pc_ctr = keyword_data.get("monthlyAvePcCtr", 0)
        mobile_ctr = keyword_data.get("monthlyAveMobileCtr", 0)
        
        # 가중 평균 CTR
        if monthly_avg > 0:
            weighted_ctr = (pc_ctr * monthly_pc + mobile_ctr * monthly_mobile) / monthly_avg
        else:
            weighted_ctr = 0
        
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
            "monthlyPcSearch": monthly_pc,
            "monthlyMobileSearch": monthly_mobile,
            "averageCtr": round(weighted_ctr, 2),
            "pcCtr": round(pc_ctr, 2),
            "mobileCtr": round(mobile_ctr, 2),
            "competition": competition,
            "recommendation": recommendation
        }
        
    except Exception as e:
        print(f"데이터 파싱 오류: {str(e)}")
        return {
            "monthlyAvg": 0,
            "monthlyPcSearch": 0,
            "monthlyMobileSearch": 0,
            "averageCtr": 0,
            "pcCtr": 0,
            "mobileCtr": 0,
            "competition": "알 수 없음",
            "recommendation": "오류 발생"
        }

# 검색량 데이터 파싱
def parse_search_volume(api_response: Dict, original_keyword: str = "") -> Dict:
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
        
        # 원본 키워드와 가장 유사한 키워드 찾기
        keyword_data = keywords[0]  # 기본값
        
        if original_keyword:
            # 지역명 제거
            regions = ["인천", "서울", "부산", "대구", "대전", "광주", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
                       "서구", "북구", "동구", "남구", "중구", "청라", "검단", "송도", "강남", "강북", "서초", "종로", "마포", "강서", "해운대"]
            core_original = original_keyword
            for region in regions:
                core_original = core_original.replace(region + " ", "").replace(region, "")
            core_original = core_original.strip()
            
            print(f"🔍 원본 키워드: {original_keyword} → 핵심: {core_original}")
            
            # 정확히 일치하는 키워드 찾기
            for kw in keywords:
                if kw.get("relKeyword", "").strip() == core_original:
                    keyword_data = kw
                    print(f"✅ 정확 일치: {kw.get('relKeyword')}")
                    break
            else:
                # 부분 일치 찾기
                for kw in keywords:
                    if core_original in kw.get("relKeyword", "") or kw.get("relKeyword", "") in core_original:
                        keyword_data = kw
                        print(f"✅ 부분 일치: {kw.get('relKeyword')}")
                        break
                else:
                    print(f"⚠️  일치하는 키워드 없음, 첫 번째 사용: {keywords[0].get('relKeyword')}")
        
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
        
        print(f"\n{'='*60}")
        print(f"📊 분석 시작: {keyword}")
        print(f"📍 플레이스 URL: {place_url if place_url else '미입력'}")
        print(f"{'='*60}\n")
        
        # 1. 네이버 검색광고 API로 검색량 조회
        print(f"🔍 1단계: 네이버 검색광고 API 호출 중...")
        api_response = call_naver_api(keyword)
        print(f"✅ API 응답: success={api_response.get('success')}")
        
        # 확장 버전 (CTR 포함)
        search_volume_extended = parse_search_volume_extended(api_response, keyword)
        print(f"📈 검색량: {search_volume_extended.get('monthlyAvg')}, 경쟁도: {search_volume_extended.get('competition')}, 평균 CTR: {search_volume_extended.get('averageCtr')}%")
        
        # 관련 키워드 추출 (10개)
        related_keywords = extract_related_keywords(api_response, keyword, limit=10)
        print(f"🔑 관련 키워드: {len(related_keywords)}개 발견")
        
        # 기존 호환성을 위한 간단한 버전
        search_volume = parse_search_volume(api_response, keyword)
        print(f"📈 검색량: {search_volume.get('monthlyAvg')}, 경쟁도: {search_volume.get('competition')}")
        
        # 2. BeautifulSoup으로 플레이스 순위 크롤링
        print(f"\n🕷️  2단계: 플레이스 순위 크롤링 중...")
        ranking_data = crawl_place_ranking(keyword, place_url)
        print(f"✅ 크롤링 완료: {len(ranking_data.get('competitors', []))}개 업체 발견")
        
        # 3. 경쟁사 키워드 추출
        print(f"\n🔑 3단계: 경쟁사 키워드 추출 중...")
        competitors = ranking_data.get("competitors", [])
        keywords = extract_competitor_keywords(competitors)
        print(f"✅ 키워드 추출 완료: {len(keywords)}개 업체")
        
        print(f"\n{'='*60}")
        print(f"✅ 분석 완료!")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "searchVolume": search_volume,
            "searchVolumeExtended": search_volume_extended,  # CTR 포함
            "relatedKeywords": related_keywords,  # 관련 키워드
            "ranking": {
                "myRank": ranking_data.get("myRank"),
                "competitors": competitors
            },
            "keywords": keywords
        }
        
    except Exception as e:
        print(f"\n❌ 분석 오류: {str(e)}")
        import traceback
        traceback.print_exc()
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
