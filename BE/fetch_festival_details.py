"""
fetch_festival_details.py

tour.db의 places 테이블에서 content_type_id=15(축제공연행사) 항목들의
content_id를 가져와 TourAPI의 detailIntro2를 개별 호출하고,
eventstartdate/eventenddate 등 상세 정보를 festival_details 테이블에 저장한다.

사용 전 준비:
  1. .env 파일 (또는 환경변수)에 아래 값을 넣어둘 것
       TOURAPI_SERVICE_KEY=발급받은_서비스키_Decoding값
  2. pip install requests python-dotenv --break-system-packages
  3. tour.db 경로가 다르면 DB_PATH 수정

실행:
  python fetch_festival_details.py
"""

import os
import sqlite3
import time
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

SERVICE_KEY = os.getenv("TOURAPI_SERVICE_KEY")
DB_PATH = os.path.join(os.path.dirname(__file__), "tour.db")
BASE_URL = "https://apis.data.go.kr/B551011/KorService2/detailIntro2"
CONTENT_TYPE_ID_FESTIVAL = 15
REQUEST_DELAY_SEC = 0.3  # API 과다호출 방지용 딜레이

# detailIntro2 응답에서 뽑아올 필드 (contenttypeid=15 기준)
FESTIVAL_FIELDS = [
    "eventstartdate",
    "eventenddate",
    "playtime",
    "eventplace",
    "eventhomepage",
    "sponsor1",
    "sponsor1tel",
    "sponsor2",
    "sponsor2tel",
    "agelimit",
    "bookingplace",
    "placeinfo",
    "program",
    "subevent",
    "usetimefestival",
    "discountinfofestival",
    "spendtimefestival",
    "festivalgrade",
]


def ensure_table(conn: sqlite3.Connection) -> None:
    columns_sql = ",\n        ".join(f"{f} VARCHAR" for f in FESTIVAL_FIELDS)
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS festival_details (
            content_id VARCHAR PRIMARY KEY,
            {columns_sql},
            fetched_at VARCHAR,
            FOREIGN KEY (content_id) REFERENCES places(content_id)
        )
        """
    )
    conn.commit()


def get_festival_content_ids(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute(
        "SELECT content_id, title FROM places WHERE content_type_id = ?",
        (CONTENT_TYPE_ID_FESTIVAL,),
    )
    return cur.fetchall()


def fetch_detail_intro(content_id: str) -> dict | None:
    params = {
        "serviceKey": SERVICE_KEY,
        "MobileOS": "ETC",
        "MobileApp": "LocalHub",
        "contentId": content_id,
        "contentTypeId": CONTENT_TYPE_ID_FESTIVAL,
        "_type": "json",
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)

    # 서비스키 오류 등은 XML로 내려오는 경우가 있어 우선 텍스트로 확인
    text = resp.text.strip()
    if text.startswith("<"):
        print(f"  [!] {content_id}: XML 에러 응답 -> {text[:200]}")
        return None

    data = resp.json()
    header = data.get("response", {}).get("header", {})
    if header.get("resultCode") != "0000":
        print(f"  [!] {content_id}: {header.get('resultMsg')}")
        return None

    items = data.get("response", {}).get("body", {}).get("items", "")
    if not items:
        print(f"  [!] {content_id}: 상세 정보 없음")
        return None

    item = items.get("item")
    if isinstance(item, list):
        item = item[0] if item else None
    return item


def upsert_festival_detail(conn: sqlite3.Connection, content_id: str, item: dict) -> None:
    values = [item.get(f, "") for f in FESTIVAL_FIELDS]
    placeholders = ", ".join("?" for _ in FESTIVAL_FIELDS)
    update_clause = ", ".join(f"{f} = excluded.{f}" for f in FESTIVAL_FIELDS)

    conn.execute(
        f"""
        INSERT INTO festival_details (content_id, {", ".join(FESTIVAL_FIELDS)}, fetched_at)
        VALUES (?, {placeholders}, datetime('now'))
        ON CONFLICT(content_id) DO UPDATE SET
            {update_clause},
            fetched_at = excluded.fetched_at
        """,
        [content_id, *values],
    )


def main():
    if not SERVICE_KEY:
        print("TOURAPI_SERVICE_KEY가 설정되어 있지 않아요. .env 파일을 확인하세요.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    ensure_table(conn)

    rows = get_festival_content_ids(conn)
    print(f"대상 축제 {len(rows)}건")

    ok, fail = 0, 0
    for content_id, title in rows:
        print(f"- {title} ({content_id}) 조회 중...")
        item = fetch_detail_intro(content_id)
        if item:
            upsert_festival_detail(conn, content_id, item)
            conn.commit()
            ok += 1
        else:
            fail += 1
        time.sleep(REQUEST_DELAY_SEC)

    print(f"\n완료: 성공 {ok}건 / 실패 {fail}건")
    conn.close()


if __name__ == "__main__":
    main()