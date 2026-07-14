from typing import Optional, List
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 기존 데이터베이스 파일 (tour.db) 유지
DATABASE_URL = "sqlite:///./tour.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ==========================================
# 1. [기존] 여행지 데이터 모델
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


# ==========================================
# 2. [신규 추가] 커뮤니티 게시판 데이터 모델
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


# 데이터베이스 테이블 생성 (기존 테이블은 유지되고 신규 'posts' 테이블만 추가로 자동 생성됨)
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. Pydantic 스키마 정의 (데이터 검증용)
# ==========================================
class PostCreate(BaseModel):
    title: str
    summary: str
    author: str
    date: str

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


# ==========================================
# 5. API 엔드포인트
# ==========================================
@app.get("/health")
def health():
    return {"status": "ok"}

# [기존] 여행지 목록 API
@app.get("/places")
def list_places(keyword: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Place)
    if keyword:
        query = query.filter(Place.title.contains(keyword))
    places = query.order_by(Place.title).all()
    return [place_to_dict(p) for p in places]

# [기존] 여행지 단건 조회 API
@app.get("/places/{content_id}")
def get_place(content_id: str, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.content_id == content_id).first()
    if not place:
        return {"detail": "not found"}
    return place_to_dict(place)


# ------------------------------------------
# [신규 추가] 커뮤니티 API 엔드포인트
# ------------------------------------------

# 1. 게시글 목록 조회 (최신 ID 순으로 정렬)
@app.get("/api/posts", response_model=List[PostResponse])
def read_posts(search: str = "", db: Session = Depends(get_db)):
    query = db.query(Post)
    if search:
        query = query.filter(Post.title.contains(search) | Post.summary.contains(search))
    return query.order_by(Post.id.desc()).all()

# 2. 게시글 작성
@app.post("/api/posts", response_model=PostResponse)
def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(
        title=post_data.title,
        summary=post_data.summary,
        author=post_data.author,
        date=post_data.date,
        views=0,
        likes=0
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post