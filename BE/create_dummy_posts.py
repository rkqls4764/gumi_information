import random
from datetime import datetime, timedelta

from main import SessionLocal
from main import Post   # main.py에 있는 게시글 모델명에 맞게 수정


# 경북/대구 주민들이 올릴만한 게시글 데이터
post_templates = [
    {
        "title": "구미 맛집 추천해주세요",
        "summary": "구미에서 가족이랑 가기 좋은 맛집 있으면 추천 부탁드립니다!"
    },
    {
        "title": "금오산 다녀왔어요",
        "summary": "날씨 좋아서 금오산 산책했는데 경치가 정말 좋네요."
    },
    {
        "title": "대구 근교 나들이 장소 추천",
        "summary": "주말에 가볍게 다녀올 만한 곳 찾고 있습니다."
    },
    {
        "title": "구미 카페 추천",
        "summary": "조용하고 분위기 좋은 카페 아시는 분 있나요?"
    },
    {
        "title": "주말에 어디 갈까요?",
        "summary": "구미 근처 드라이브하기 좋은 장소 추천해주세요."
    },
    {
        "title": "요즘 날씨에 산책하기 좋은 곳",
        "summary": "저녁에 걷기 좋은 산책 코스 공유해주세요!"
    },
    {
        "title": "대구 맛집 찾고 있습니다",
        "summary": "대구에서 현지인 추천 맛집 있으면 알려주세요."
    },
    {
        "title": "구미 행사 정보 공유",
        "summary": "이번 주말 구미에서 열리는 행사 있나요?"
    },
    {
        "title": "아이와 가볼만한 곳",
        "summary": "아이랑 함께 방문하기 좋은 장소 추천 부탁드립니다."
    },
    {
        "title": "구미 생활 정보 공유",
        "summary": "구미 살면서 알게 된 좋은 정보 같이 공유해요."
    },
    {
        "title": "경북 여행 추천",
        "summary": "경북 쪽 하루 여행 코스 추천받고 싶습니다."
    },
    {
        "title": "숨은 명소 찾습니다",
        "summary": "사람 많이 모르는 조용한 장소 있을까요?"
    }
]


authors = [
    "구미주민",
    "금오산러버",
    "대구직장인",
    "경북여행자",
    "동네사람",
    "구미살이",
    "주말나들이",
    "지역탐방러"
]


def create_dummy_posts():

    db = SessionLocal()

    try:
        # 기존 게시글 삭제
        db.query(Post).delete()

        print("기존 게시글 삭제 완료")


        posts = []

        for i in range(100):

            template = random.choice(post_templates)

            # 날짜 랜덤 생성 (최근 1년)
            random_date = datetime.now() - timedelta(
                days=random.randint(0, 365)
            )


            post = Post(
                title=f"{template['title']}",
                summary=template["summary"],

                author=random.choice(authors),

                date=random_date.strftime("%Y-%m-%d"),

                # 랜덤 조회수
                views=random.randint(0, 500),

                # 랜덤 좋아요
                likes=random.randint(0, 100),

                # 비밀번호 통일
                password="1234"
            )

            posts.append(post)


        db.add_all(posts)
        db.commit()


        print("더미 게시글 생성 완료")
        print(f"생성된 게시글 개수 : {len(posts)}")


    except Exception as e:
        db.rollback()
        print("오류 발생:", e)


    finally:
        db.close()



if __name__ == "__main__":
    create_dummy_posts()