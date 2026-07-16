import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, or_, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from openai import OpenAI
from dotenv import load_dotenv

# 💡 .env 파일 환경 변수 로드 (OPENAI_API_KEY 로드용)
load_dotenv()

DATABASE_URL = "sqlite:///./tour.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

FESTIVAL_CONTENT_TYPE_ID = 15

# lcls_systm2 분류체계 코드 -> 캘린더 카테고리 매핑
CATEGORY_MAP = {
    "EV01": "축제",
    "EV02": "공연",
    "EV03": "행사",
}
DEFAULT_CATEGORY = "기타"

# ==========================================
# 1. 여행지 데이터 모델
# ==========================================
class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(String, unique=True, index=True)
    content_type_id = Column(Integer, index=True)
    title = Column(String, index=True)
    addr1 = Column(String)
    addr2 = Column(String)
    zipcode = Column(String)
    tel = Column(String)
    mapx = Column(Float)
    mapy = Column(Float)
    mlevel = Column(Integer)
    areacode = Column(String)
    sigungucode = Column(String)
    l_dong_regn_cd = Column(String)
    l_dong_signgu_cd = Column(String)
    cat1 = Column(String)
    cat2 = Column(String)
    cat3 = Column(String)
    lcls_systm1 = Column(String)
    lcls_systm2 = Column(String)
    lcls_systm3 = Column(String)
    firstimage = Column(String)
    firstimage2 = Column(String)
    cpyrht_div_cd = Column(String)
    createdtime = Column(String)
    modifiedtime = Column(String)
    source_region = Column(String)

class PlaceReview(Base):
    __tablename__ = "place_reviews"
    id = Column(Integer, primary_key=True, index=True)
    place_content_id = Column(String, index=True, nullable=False)
    rating = Column(Float, nullable=False)
    created_at = Column(
        String,
        default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )

# ==========================================
# 1-1. 축제 상세정보 데이터 모델
# ==========================================
class FestivalDetail(Base):
    __tablename__ = "festival_details"
    content_id = Column(String, primary_key=True, index=True)
    eventstartdate = Column(String)
    eventenddate = Column(String)
    playtime = Column(String)
    eventplace = Column(String)
    eventhomepage = Column(String)
    sponsor1 = Column(String)
    sponsor1tel = Column(String)
    sponsor2 = Column(String)
    sponsor2tel = Column(String)
    agelimit = Column(String)
    bookingplace = Column(String)
    placeinfo = Column(String)
    program = Column(String)
    subevent = Column(String)
    usetimefestival = Column(String)
    discountinfofestival = Column(String)
    spendtimefestival = Column(String)
    festivalgrade = Column(String)
    fetched_at = Column(String)

# ==========================================
# 2. 커뮤니티 게시판 데이터 모델
# ==========================================
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    author = Column(String, default="익명")
    date = Column(String, nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    password = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# ==========================================
# 3. Pydantic 스키마 정의
# ==========================================
class PostCreate(BaseModel):
    title: str
    summary: str
    author: str
    date: str
    password: str

class PostUpdate(BaseModel):
    title: str
    summary: str
    author: str
    password: str

class PostResponse(BaseModel):
    id: int
    title: str
    summary: str
    author: str
    date: str
    views: int
    likes: int

    class Config:
        from_attributes = True
        
class PlaceReviewCreate(BaseModel):
    rating: float

class PlaceReviewResponse(BaseModel):
    id: int
    place_content_id: str
    rating: float
    created_at: str

    class Config:
        from_attributes = True

# 🤖 [수정] 프론트엔드 카테고리 입력을 포함하는 스키마
class ChatRequest(BaseModel):
    message: str
    category: Optional[str] = None  # "운동", "음식", "여행", "쇼핑" 등


# ==========================================
# 4. FastAPI 앱 설정 및 CORS
# ==========================================
app = FastAPI(title="Tour API Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🤖 OpenAI 인스턴스 초기화
client = OpenAI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def place_to_dict(place):
    return {col.name: getattr(place, col.name) for col in Place.__table__.columns}

def to_iso_date(yyyymmdd: Optional[str]) -> Optional[str]:
    if not yyyymmdd or len(yyyymmdd) != 8:
        return None
    return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"

def resolve_category(lcls_systm2: Optional[str]) -> str:
    return CATEGORY_MAP.get(lcls_systm2, DEFAULT_CATEGORY)

import re

# 지역명 매핑
REGIONS = {
    "구미": ["구미", "구미시"],
    "칠곡": ["칠곡", "칠곡군"],
    "김천": ["김천", "김천시"],
    "대구": ["대구", "대구광역시"],
    "경산": ["경산", "경산시"],
}

def map_type_from_place(place):

    text = " ".join([
        str(place.title or ""),
        str(place.addr1 or ""),
        str(place.addr2 or ""),
        str(place.cat1 or ""),
        str(place.cat2 or ""),
        str(place.cat3 or ""),
        str(place.lcls_systm1 or ""),
        str(place.lcls_systm2 or ""),
        str(place.lcls_systm3 or "")
    ]).lower()


    content_type_id = int(place.content_type_id or 0)


    # 음식점
    if (
        content_type_id == 39
        or re.search(
            r"음식|맛집|식당|한식|중식|일식|양식|분식|카페|커피|치킨|피자|국밥|백반",
            text
        )
    ):
        return "food"


    # 카페
    if re.search(
        r"카페|커피|cafe|coffee|디저트|베이커리|브런치",
        text
    ):
        return "cafe"


    # 숙박
    if re.search(
        r"숙박|호텔|민박|펜션|리조트",
        text
    ):
        return "stay"
    
    # 쇼핑
    if re.search(
        r"시장|마트|쇼핑|백화점|아울렛|상점|몰",
        text
    ):
        return "shopping"


    # 운동
    if re.search(
        r"레포츠|스포츠|운동|등산|트레킹|캠핑|자전거|골프|수영|헬스",
        text
    ):
        return "activity"


    # 축제
    if re.search(
        r"축제|공연|행사",
        text
    ):
        return "festival"


    # 관광
    if (
        content_type_id in [12,14,15,28]
        or re.search(
            r"관광|명소|문화|공원|사찰|성지",
            text
        )
    ):
        return "tour"


    return "tour"
@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------
# 🤖 [고도화 추가] 카테고리 필터링 연동 GPT 챗봇 엔드포인트
# ------------------------------------------
@app.post("/api/chat")
def chat_with_db(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    user_prompt = request.message
    category = request.category

    try:
        # ==============================
        # 1. DB 데이터 가져오기
        # ==============================
        places = db.query(Place).all()

        # ==============================
        # 지역 필터
        # ==============================
        region_keyword = None

        for region, keywords in REGIONS.items():
            for keyword in keywords:
                if keyword in user_prompt:
                    region_keyword = region
                    break

            if region_keyword:
                break


        if region_keyword:
            # 지역명이 있으면 해당 지역만 검색
            places = [
                p for p in places
                if any(
                    keyword in (p.addr1 or "")
                    for keyword in REGIONS[region_keyword]
                )
            ]

        else:
            # 지역명이 없으면 전체 지역 검색
            places = places

            print("\n========== 지역 필터 결과 ==========")
            print("검색 지역:", region_keyword)
            print("필터 개수:", len(places))

            for p in places[:20]:
                print(
                    f"""
                이름: {p.title}
                주소: {p.addr1}

                content_type_id: {p.content_type_id}

                cat1: {p.cat1}
                cat2: {p.cat2}
                cat3: {p.cat3}

                lcls1: {p.lcls_systm1}
                lcls2: {p.lcls_systm2}
                lcls3: {p.lcls_systm3}

                카테고리: {map_type_from_place(p)}
                """
                )

            print("====================================\n")

        db_context = []

        for place in places:

            place_type = map_type_from_place(place)


            # 관심사 필터
            if category:

                category_map = {
                    "음식": "food",
                    "카페": "cafe",
                    "여행": "tour",
                    "관광": "tour",
                    "운동": "activity",
                    "쇼핑": "shopping"
                }


                target_category = category_map.get(category)


                if target_category and place_type != target_category:
                    continue


            db_context.append(
                {
                    "이름": place.title,
                    "카테고리": place_type,
                    "주소": place.addr1 or "정보 없음",
                    "전화": place.tel or "정보 없음",
                    "지역": place.source_region or "",
                }
            )


        # 너무 긴 데이터 방지
        db_context = db_context[:500]

        print("\n========== GPT 전달 데이터 ==========")
        print("GPT 전달 개수:", len(db_context))

        for data in db_context:
            print(data)

        print("====================================\n")

        # ==============================
        # 2. GPT 프롬프트
        # ==============================

        system_instruction = f"""
너는 구미/경북 지역 전문 장소 추천 AI이다.

사용자가 선택한 관심사:
[{category or "전체"}]

사용자 요청:
{user_prompt}


아래 DB 데이터만 사용해서 추천한다.

중요 규칙:
- 반드시 DB에 존재하는 장소만 추천한다.
- 존재하지 않는 장소를 절대 만들지 않는다.
- 주소와 장소명은 DB 원본 그대로 사용한다.
- 최대 3개 장소만 추천한다.
- 사용자의 질문 의도를 가장 우선한다.
- 관심사가 있으면 관심사와 일치하는 장소만 추천한다.
- 지역명이 포함되어 있으면 해당 지역 장소를 우선한다.
- 지역명이 없으면 구미/경북 전체 데이터에서 장소가 겹치지 않게 추천한다.


추천할 장소가 없는 경우:

현재 조건에 맞는 장소를 찾지 못했어요 😢
다른 지역이나 관심사를 선택해서 다시 검색해보세요!

추천 결과 출력 형식:

첫 줄에는 친근한 소개 멘트를 작성한다.

소개 멘트는 반드시 문장 끝을 "~할게구미", "~추천해줄게구미", "~찾아봤다구미" 같은
구미 지역 서비스만의 말투로 표현한다.

예시:
- 구미에서 이런 맛집을 추천해줄게구미 😊
- 칠곡에서 가볼 만한 장소를 찾아봤다구미 🌿
- 대구에서 맛있는 카페를 찾아줄게구미 ☕
- 원하는 조건에 맞는 장소를 골라봤다구미 😊

단, 예시 문장을 그대로 복사하지 말고
사용자의 지역과 관심사에 맞게 자연스럽게 변경한다.

이후 아래 형식을 유지한다:

🍽️ 장소명
⭐ 추천 이유
📍 주소

🍽️ 장소명
⭐ 추천 이유
📍 주소

🍽️ 장소명
⭐ 추천 이유
📍 주소

DB 데이터:

{db_context}

"""


        # ==============================
        # 3. GPT 호출
        # ==============================

        completion = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )


        return {
            "reply": completion.choices[0].message.content
        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"챗봇 오류: {str(e)}"
        )
# ------------------------------------------
# [기존] 여행지 API
# ------------------------------------------
@app.get("/places")
def list_places(
    keyword: Optional[str] = Query(None),
    minLat: Optional[float] = Query(None),
    maxLat: Optional[float] = Query(None),
    minLng: Optional[float] = Query(None),
    maxLng: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):

    query = db.query(Place)


    # 검색어
    if keyword:
        query = query.filter(
            Place.title.contains(keyword)
        )


    # 지도 영역 필터
    if (
        minLat is not None
        and maxLat is not None
        and minLng is not None
        and maxLng is not None
    ):
        query = query.filter(
            Place.mapy >= minLat,
            Place.mapy <= maxLat,
            Place.mapx >= minLng,
            Place.mapx <= maxLng
        )


    # 최대 개수 제한
    places = (
        query
        .order_by(Place.title)
        .limit(100)
        .all()
    )


    result = []

    for place in places:
        item = place_to_dict(place)

        review_data = (
            db.query(
                func.avg(PlaceReview.rating).label("avg_rating"),
                func.count(PlaceReview.id).label("review_count")
            )
            .filter(
                PlaceReview.place_content_id == place.content_id
            )
            .first()
        )

        item["avg_rating"] = round(review_data.avg_rating, 1) if review_data.avg_rating else 0
        item["review_count"] = review_data.review_count or 0

        result.append(item)


    return result

@app.get("/places/{content_id}")
def get_place(content_id: str, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.content_id == content_id).first()
    if not place: return {"detail": "not found"}
    return place_to_dict(place)

@app.get("/places/{content_id}/reviews")
def list_place_reviews(content_id: str, db: Session = Depends(get_db)):
    reviews = (
        db.query(PlaceReview)
        .filter(PlaceReview.place_content_id == content_id)
        .order_by(PlaceReview.id.desc())
        .all()
    )
    return [
        {
            "id": review.id,
            "place_content_id": review.place_content_id,
            "rating": review.rating,
            "created_at": review.created_at,
        }
        for review in reviews
    ]

@app.post("/places/{content_id}/reviews", response_model=PlaceReviewResponse)
def create_place_review(content_id: str, review_data: PlaceReviewCreate, db: Session = Depends(get_db)):
    if review_data.rating < 0 or review_data.rating > 10:
        raise HTTPException(status_code=400, detail="리뷰 평점은 0~10 사이여야 합니다.")
    review = PlaceReview(place_content_id=content_id, rating=review_data.rating)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

# ------------------------------------------
# [기존] 축제 캘린더 API
# ------------------------------------------
@app.get("/festivals")
def list_festivals(
    category: Optional[str] = Query(None, description="축제 | 행사 | 공연 | 전시 | 기타"),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Place, FestivalDetail)
        .join(FestivalDetail, Place.content_id == FestivalDetail.content_id)
        .filter(Place.content_type_id == FESTIVAL_CONTENT_TYPE_ID)
        .order_by(FestivalDetail.eventstartdate)
        .all()
    )

    result = []
    for place, detail in rows:
        start = to_iso_date(detail.eventstartdate)
        end = to_iso_date(detail.eventenddate) or start
        if not start:
            continue

        cat = resolve_category(place.lcls_systm2)
        if category and category != cat:
            continue

        result.append(
            {
                "id": place.content_id,
                "title": place.title,
                "category": cat,
                "start": start,
                "end": end,
                "time": detail.playtime or None,
                "location": detail.eventplace or place.addr1,
            }
        )
    return result

# ------------------------------------------
# [기존] 커뮤니티 API 엔드포인트
# ------------------------------------------
@app.get("/api/posts", response_model=List[PostResponse])
def read_posts(search: str = "", db: Session = Depends(get_db)):
    query = db.query(Post)
    if search:
        query = query.filter(Post.title.contains(search) | Post.summary.contains(search))
    return query.order_by(Post.id.desc()).all()

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글이 없습니다.")
    post.views += 1
    db.commit()
    db.refresh(post)
    return post

@app.post("/api/posts", response_model=PostResponse)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(
        title=post_data.title,
        summary=post_data.summary,
        author=post_data.author,
        date=post_data.date,
        password=post_data.password,
        views=0,
        likes=0
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.password != post_data.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    
    post.title = post_data.title
    post.summary = post_data.summary
    post.author = post_data.author
    
    db.commit()
    db.refresh(post)
    return post

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, password: str = Query(...), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    if post.password != password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    db.delete(post)
    db.commit()
    return {"message": "삭제 완료"}

@app.post("/api/posts/{post_id}/like", response_model=PostResponse)
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    post.likes += 1
    db.commit()
    db.refresh(post)
    return post