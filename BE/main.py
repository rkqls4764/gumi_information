import os
from typing import Optional, List
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, or_
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from openai import OpenAI
from dotenv import load_dotenv

# 💡 .env 파일 환경 변수 로드 (OPENAI_API_KEY 취득용)
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
# 1-1. 축제 상세정보 데이터 모델 (기존 유지)
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
# 2. 커뮤니티 게시판 데이터 모델 (기존 유지)
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
# 3. Pydantic 스키마 정의 (기존 유지 + GPT 추가)
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

# 🤖 [신규 추가] GPT 요청용 Pydantic 모델
class ChatRequest(BaseModel):
    message: str


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

# 🤖 [신규 추가] OpenAI 클라이언트 인스턴스 초기화 (자동으로 환경변수의 OPENAI_API_KEY 로드)
# 만약 키를 코드에 명시적으로 넣어야 한다면 client = OpenAI(api_key="sk-...") 로 선언 가능하지만, .env 기반이 안전합니다.
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
    """'20260701' -> '2026-07-01'. 값이 없거나 형식이 이상하면 None."""
    if not yyyymmdd or len(yyyymmdd) != 8:
        return None
    return f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


def resolve_category(lcls_systm2: Optional[str]) -> str:
    return CATEGORY_MAP.get(lcls_systm2, DEFAULT_CATEGORY)


@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------
# 🤖 [신규 추가] DB 연동 GPT 챗봇 API 엔드포인트
# ------------------------------------------
@app.post("/api/chat")
def chat_with_local_gpt(request: ChatRequest, db: Session = Depends(get_db)):
    user_prompt = request.message

    # 1. 사용자의 질문 키워드로 sqlite의 `places` 테이블 시맨틱 검색
    db_context_list = []
    try:
        # 띄어쓰기 기준으로 검색 키워드를 나눕니다 (예: "금오산 맛집" -> ["금오산", "맛집"])
        keywords = [k for k in user_prompt.split() if len(k) > 1]
        
        if keywords:
            # title 또는 addr1 필드에서 키워드와 연관된 레코드 최대 5개 검색
            filters = []
            for kw in keywords:
                filters.append(Place.title.contains(kw))
                filters.append(Place.addr1.contains(kw))
            
            matched_places = db.query(Place).filter(or_(*filters)).limit(5).all()
            
            for place in matched_places:
                db_context_list.append(
                    f"- 장소명: {place.title} | 주소: {place.addr1 or '정보 없음'} | 전화번호: {place.tel or '정보 없음'}"
                )
    except Exception as e:
        print(f"[DB 검색 오류 수집 - 무시하고 GPT 기본 구동]: {e}")

    # 2. GPT에 보낼 프롬프트 조립
    system_instruction = (
        "당신은 구미 및 경상북도 지역 커뮤니티 서비스 'LocalHub'의 친절하고 유능한 챗봇 안내원입니다.\n"
        "항상 상냥하고 밝은 톤으로 질문에 응답하며, 질문자의 요청에 최대한 도움이 되는 실용적인 정보를 전달해 주세요."
    )

    # DB에 걸맞는 구미 여행지/명소 정보가 매칭되었다면, GPT에게 주입
    if db_context_list:
        context_str = "\n".join(db_context_list)
        system_instruction += (
            f"\n\n[보안 및 답변 규칙]: 사용자의 질문과 가장 매칭되는 서비스 내 실제 데이터베이스 정보입니다.\n"
            f"답변 시 아래 리스트된 장소 정보를 활용하여 실제 주소 등을 친절하게 유도 및 추천해 주세요.\n"
            f"🍀 데이터베이스 내 관련 장소 목록:\n{context_str}"
        )

    # 3. gpt-5-mini API 호출 (temperature 생략으로 오류 완전 차단)
    try:
        completion = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        bot_response = completion.choices[0].message.content
        return {"reply": bot_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API 통신 중 문제가 발생했습니다: {str(e)}")


# ------------------------------------------
# [기존] 여행지 API
# ------------------------------------------
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