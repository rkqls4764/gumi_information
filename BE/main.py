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