import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, func
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

@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------
# 🤖 [고도화 추가] 카테고리 필터링 연동 GPT 챗봇 엔드포인트
# ------------------------------------------
@app.post("/api/chat")
def chat_with_filtered_db(request: ChatRequest, db: Session = Depends(get_db)):
    user_prompt = request.message
    category = request.category

    db_context_list = []
    
    try:
        # 기본 쿼리 빌더 시작
        query = db.query(Place)
        
        # 1. 사용자가 선택한 카테고리가 있을 경우 데이터베이스 필터링 적용
        if category:
            if category == "음식":
                # A05 = 식음료/음식점 관련 코드
                query = query.filter(Place.cat1 == "A05")
            elif category == "여행":
                # A01(자연), A02(인문/문화) 관련 코드
                query = query.filter(or_(Place.cat1 == "A01", Place.cat1 == "A02"))
            elif category == "쇼핑":
                # A04 = 쇼핑 관련 코드
                query = query.filter(Place.cat1 == "A04")
            elif category == "운동":
                # A03 = 레포츠/액티비티 관련 코드
                query = query.filter(Place.cat1 == "A03")
        
        # 2. 질문에서 추가 키워드가 있다면 제목(title)이나 주소(addr1) 검색도 결합
        keywords = [k for k in user_prompt.split() if len(k) > 1]
        if keywords:
            filters = []
            for kw in keywords:
                filters.append(Place.title.contains(kw))
                filters.append(Place.addr1.contains(kw))
            query = query.filter(or_(*filters))
            
        # 3. 매칭되는 로컬 데이터 최대 5개 추출
        matched_places = query.limit(5).all()
        
        for place in matched_places:
            db_context_list.append(
                f"- 이름: {place.title} | 주소: {place.addr1 or '정보 없음'} | 전화: {place.tel or '정보 없음'} | 분류: {place.cat3 or '정보 없음'}"
            )
            
    except Exception as e:
        print(f"[카테고리 DB 필터링 오류]: {e}")

    # 4. GPT 시스템 프롬프트 가이드 제작
    system_instruction = (
        "당신은 구미 및 경북 지역 가이드 'LocalHub'의 스마트한 AI 가이드입니다.\n"
        "항상 상냥하고 경쾌한 조력자 톤으로 대답해 주시고, 맛깔스러운 사투리를 섞지 않으며 정확한 표준 정보로 안내해 주세요.\n"
    )
    
    if category:
        system_instruction += f"현재 사용자가 선택한 탐색 테마는 [{category}] 입니다. 이에 초점을 맞춰 맞춤형 제안을 진행해 주세요.\n"

    # DB에서 필터링된 실제 음식점/액티비티/여행지 정보 주입
    if db_context_list:
        context_str = "\n".join(db_context_list)
        system_instruction += (
            f"\n\n[필독 - 우리 로컬 데이터베이스의 매칭 결과]:\n"
            f"사용자에게 아래 장소 목록의 실제 이름, 위치 주소, 상세 정보를 가독성 있게 구조화하여 친절히 소개하고 추천해 주세요.\n"
            f"데이터 리스트:\n{context_str}"
        )
    else:
        if category:
            system_instruction += (
                f"\n\n[안내 사항]: 사용자가 선택한 '{category}' 테마에 부합하는 직접 매칭된 DB 장소가 이번엔 검색되지 않았습니다. "
                f"가지고 계신 자체 지식(구미 및 경상북도 지역 위주)을 적극 활용하여 가장 유명한 {category} 장소들을 추천해 주세요."
            )

    # 5. gpt-5-mini 호출
    try:
        completion = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        return {"reply": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI 연동 실패: {str(e)}")


# ------------------------------------------
# [기존] 여행지 API
# ------------------------------------------
@app.get("/places")
def list_places(
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Place)

    if keyword:
        query = query.filter(
            Place.title.contains(keyword)
        )

    places = query.order_by(Place.title).all()

    result = []

    for place in places:

        avg_rating = (
            db.query(func.avg(PlaceReview.rating))
            .filter(
                PlaceReview.place_content_id
                == place.content_id
            )
            .scalar()
        )

        item = place_to_dict(place)

        item["avg_rating"] = round(
            float(avg_rating or 0),
            1
        )

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