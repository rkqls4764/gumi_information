# import_data.py
import json
from pathlib import Path
from main import SessionLocal, Place

DATA_DIR = Path(r"C:\Users\SSAFY\Downloads\startcamp_3일차\data\구미_경북권")

FILES = [
    "구미_경북권_관광지.json",
    "구미_경북권_레포츠.json",
    "구미_경북권_문화시설.json",
    "구미_경북권_쇼핑.json",
    "구미_경북권_숙박.json",
    "구미_경북권_여행코스.json",
    "구미_경북권_음식점.json",
    "구미_경북권_축제공연행사.json",
]

def to_float(value):
    if value in ("", None):
        return None
    try:
        return float(value)
    except:
        return None

def to_int(value):
    if value in ("", None):
        return None
    try:
        return int(value)
    except:
        return None

def import_all():
    db = SessionLocal()
    try:
        for filename in FILES:
            path = DATA_DIR / filename
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            for item in data.get("items", []):
                exists = db.query(Place).filter(Place.content_id == item.get("contentid")).first()
                if exists:
                    continue

                place = Place(
                    content_id=item.get("contentid"),
                    content_type_id=to_int(item.get("contenttypeid")),
                    title=item.get("title", ""),
                    addr1=item.get("addr1", ""),
                    addr2=item.get("addr2", ""),
                    zipcode=item.get("zipcode", ""),
                    tel=item.get("tel", ""),
                    mapx=to_float(item.get("mapx")),
                    mapy=to_float(item.get("mapy")),
                    mlevel=to_int(item.get("mlevel")),
                    areacode=item.get("areacode", ""),
                    sigungucode=item.get("sigungucode", ""),
                    l_dong_regn_cd=item.get("lDongRegnCd", ""),
                    l_dong_signgu_cd=item.get("lDongSignguCd", ""),
                    cat1=item.get("cat1", ""),
                    cat2=item.get("cat2", ""),
                    cat3=item.get("cat3", ""),
                    lcls_systm1=item.get("lclsSystm1", ""),
                    lcls_systm2=item.get("lclsSystm2", ""),
                    lcls_systm3=item.get("lclsSystm3", ""),
                    firstimage=item.get("firstimage", ""),
                    firstimage2=item.get("firstimage2", ""),
                    cpyrht_div_cd=item.get("cpyrhtDivCd", ""),
                    createdtime=item.get("createdtime", ""),
                    modifiedtime=item.get("modifiedtime", ""),
                    source_region=data.get("region", "")
                )
                db.add(place)

        db.commit()
        print("Import complete")
    finally:
        db.close()

if __name__ == "__main__":
    import_all()