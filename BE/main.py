from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "sqlite:///./tour.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

FESTIVAL_CONTENT_TYPE_ID = 15

# lcls_systm2 분류체계 코드 -> 캘린더 카테고리 매핑
# EV01: 대부분의 축제/페스티벌, EV02: 공연류, EV03: 박람회/전시성 행사
CATEGORY_MAP = {
    "EV01": "축제",
    "EV02": "공연",
    "EV03": "행사",
}
DEFAULT_CATEGORY = "기타"

# ==========================================
# 1. 여행지 데이터 모델 (기존 유지)
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
# 1-1. 축제 상세정보 데이터 모델 (신규 추가)
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
# 2. 커뮤니티 게시판 데이터 모델 (비밀번호 추가)
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
    password = Column(String, nullable=False)  # 🔥 수정/삭제용 비밀번호 필드 추가

Base.metadata.create_all(bind=engine)

# ==========================================
# 3. Pydantic 스키마 정의
# ==========================================
class PostCreate(BaseModel):
    title: str
    summary: str
    author: str
    date: str
    password: str  # 생성 시 비밀번호 필수

class PostUpdate(BaseModel):
    title: str
    summary: str
    author: str
    password: str  # 수정 시 본인 인증용 비밀번호 확인

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def place_to_dict(place):
    return {col.name: getattr(place, col.name) for col in Place.__table__.columns}


def to_iso_date(yyyymmdd: Optional[str]) -> Optional[str]:
    """'20260701' -> '2026-07-01'. 값이 없거나 형식이 이상하면 None."""
    if not yyyymmdd or len(yyyymmdd) != 8:
        return None
    return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


def resolve_category(lcls_systm2: Optional[str]) -> str:
    return CATEGORY_MAP.get(lcls_systm2, DEFAULT_CATEGORY)


@app.get("/health")
def health():
    return {"status": "ok"}

# [기존] 여행지 API 생략 (그대로 유지됨)
@app.get("/places")
def list_places(keyword: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Place)
    if keyword:
        query = query.filter(Place.title.contains(keyword))
    return [place_to_dict(p) for p in query.order_by(Place.title).all()]

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
# 축제 캘린더 API 엔드포인트
# ------------------------------------------
@app.get("/festivals")
def list_festivals(
    category: Optional[str] = Query(None, description="축제 | 행사 | 공연 | 전시 | 기타"),
    db: Session = Depends(get_db),
):
    """
    캘린더 화면(FE)이 바로 쓸 수 있는 형태로 축제/행사 목록을 반환한다.
    festival_details가 아직 없는 축제(=날짜 미조회)는 목록에서 제외한다.
    """
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
            continue  # 날짜 정보가 없는 항목은 캘린더에 표시할 수 없으므로 제외

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
# 락인(CRUD) 커뮤니티 API 엔드포인트
# ------------------------------------------

# 1. 목록 조회
@app.get("/api/posts", response_model=List[PostResponse])
def read_posts(search: str = "", db: Session = Depends(get_db)):
    query = db.query(Post)
    if search:
        query = query.filter(Post.title.contains(search) | Post.summary.contains(search))
    return query.order_by(Post.id.desc()).all()

# 2. 상세 조회 및 조회수 증가
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글이 없습니다.")
    
    # 조회수 1 증가 후 저장
    post.views += 1
    db.commit()
    db.refresh(post)
    return post

# 3. 게시글 작성
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

# 4. 게시글 수정 (비밀번호 검증)
@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 비밀번호 비교 검증
    if post.password != post_data.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
    
    post.title = post_data.title
    post.summary = post_data.summary
    post.author = post_data.author
    
    db.commit()
    db.refresh(post)
    return post

# 5. 게시글 삭제 (비밀번호 검증을 쿼리 스트링 혹은 바디 대용으로 처리하기 위해 명세 고도화)
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

# 🔥 [신규 추가] 6. 게시글 좋아요(추천) 증가 API
@app.post("/api/posts/{post_id}/like", response_model=PostResponse)
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 좋아요 수 1 증가
    post.likes += 1
    db.commit()
    db.refresh(post)
    return post
