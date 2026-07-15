import random
from main import SessionLocal, Place, PlaceReview


def create_dummy_reviews():
    db = SessionLocal()

    try:
        places = db.query(Place).all()

        print(f"총 장소 개수 : {len(places)}")

        count = 0

        for place in places:

            # 장소마다 기존 리뷰 삭제 (중복 방지)
            db.query(PlaceReview)\
                .filter(
                    PlaceReview.place_content_id == place.content_id
                )\
                .delete()

            # 0~100개 랜덤 리뷰 생성
            review_count = random.randint(0, 100)

            for _ in range(review_count):

                review = PlaceReview(
                    place_content_id=place.content_id,
                    rating=round(
                        random.uniform(1, 5),
                        1
                    )
                )

                db.add(review)

            count += review_count


        db.commit()

        print("더미 리뷰 생성 완료")
        print(f"생성된 리뷰 개수 : {count}")


    except Exception as e:
        db.rollback()
        print(e)

    finally:
        db.close()


if __name__ == "__main__":
    create_dummy_reviews()