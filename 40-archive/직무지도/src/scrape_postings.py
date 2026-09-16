"""알리오(job.alio.go.kr) 공개 채용공고를 직무 키워드별로 수집한다.

실행:
    python src/scrape_postings.py

출력:
    output/postings.json  - 공고별 상세 필드 전체
    output/postings.csv   - 유사도 계산에 쓸 핵심 컬럼만 정리한 표
"""

import csv
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://job.alio.go.kr"
LIST_URL = f"{BASE_URL}/mobile2021/recruit/recruit.do"
DETAIL_URL = f"{BASE_URL}/mobile2021/recruit/recruitView.do"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
REQUEST_DELAY = 0.5  # 초 단위. 공공 사이트에 부담을 주지 않기 위한 최소 대기.

# 직무 카테고리별 검색 키워드. 알리오 검색은 제목/본문 아무데나 있어도 걸리기 때문에
# (예: "고객관리"로 검색하면 실제로는 상수도 현장직 이름일 뿐인 공고가 걸림)
# 검색은 넓게 하되, 아래 TITLE_MATCH_ONLY로 "제목에 실제로 키워드가 있는 공고"만 채택한다.
CATEGORY_KEYWORDS = {
    "데이터분석": ["데이터분석", "빅데이터", "데이터사이언티스트", "데이터전문가"],
    "BI": ["BI", "비즈니스인텔리전스", "데이터시각화", "대시보드"],
    "CRM분석": ["CRM", "고객경험", "고객데이터", "고객관계관리"],
    "마케팅분석": ["마케팅분석", "디지털마케팅", "마케팅데이터", "마케팅"],
    "AI·ML": ["AI", "인공지능", "머신러닝", "딥러닝", "데이터과학"],
}

# 제목에 키워드가 실제로 들어있는 공고만 채택한다. (우대내용/결격사유 등 본문에만
# 우연히 등장하는 대량 공채 노이즈를 걸러내기 위함 - 실제 수집에서 확인된 문제)
TITLE_MATCH_ONLY = True
MAX_PAGES_PER_KEYWORD = 3
MAX_POSTINGS_PER_CATEGORY = 10

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"


def fetch_list(keyword: str, page: int = 1) -> list[dict]:
    """검색 키워드로 공고 목록 한 페이지를 가져와 (idx, title, org)만 뽑는다."""
    resp = requests.get(
        LIST_URL,
        params={"pageNo": page, "search_yn": "Y", "keyword": keyword},
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    postings = []
    for a in soup.select("a[href*='recruitView.do?idx=']"):
        idx_match = re.search(r"idx=(\d+)", a["href"])
        if not idx_match:
            continue
        tit = a.select_one(".tit")
        org = a.select_one(".workPlace")
        postings.append(
            {
                "idx": idx_match.group(1),
                "title": tit.get_text(strip=True) if tit else "",
                "org": org.get_text(strip=True) if org else "",
            }
        )
    return postings


def fetch_detail(idx: str) -> dict:
    """공고 상세 페이지의 표(기관명/표준직무(NCS)/응시자격 등)를 key-value로 뽑는다."""
    resp = requests.get(DETAIL_URL, params={"idx": idx}, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    fields = {}
    attachments = {}
    for row in soup.select(".table_list table tr"):
        th = row.select_one("th")
        td = row.select_one("td")
        if not th or not td:
            continue
        for br in td.select("br"):
            br.replace_with("\n")
        key = th.get_text(strip=True)
        value = re.sub(r"\n\s*\n+", "\n", td.get_text().strip())
        fields[key] = value

        links = [
            {"name": a.get_text(strip=True), "url": urljoin(BASE_URL, a["href"])}
            for a in td.select("a[href]")
        ]
        if links:
            attachments[key] = links

    title_el = soup.select_one(".recruit_view .top .tit")
    return {
        "detail_title": title_el.get_text(strip=True) if title_el else "",
        "fields": fields,
        "attachments": attachments,
    }


def title_matches(keyword: str, title: str) -> bool:
    """제목에 키워드가 실제로 들어있는지 확인한다.

    영문 키워드(AI, BI, CRM 등)는 단어 경계를 체크한다. 그냥 부분일치로 하면
    "BI"가 "BIM전문가"의 일부로 잘못 걸리는 것 같은 오탐이 생긴다.
    """
    if re.fullmatch(r"[A-Za-z]+", keyword):
        return re.search(rf"(?<![A-Za-z]){re.escape(keyword)}(?![A-Za-z])", title) is not None
    return keyword in title


def collect_category(category: str, keywords: list[str]) -> list[dict]:
    seen_idx = set()
    collected = []
    for keyword in keywords:
        for page in range(1, MAX_PAGES_PER_KEYWORD + 1):
            items = fetch_list(keyword, page)
            if not items:
                break  # 더 이상 페이지가 없음
            for item in items:
                if item["idx"] in seen_idx:
                    continue
                seen_idx.add(item["idx"])
                if TITLE_MATCH_ONLY and not title_matches(keyword, item["title"]):
                    continue
                collected.append({**item, "matched_keyword": keyword})
                if len(collected) >= MAX_POSTINGS_PER_CATEGORY:
                    return collected
            time.sleep(REQUEST_DELAY)
    return collected


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    all_records = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        print(f"[{category}] 목록 수집 중... (키워드: {', '.join(keywords)})")
        listed = collect_category(category, keywords)
        print(f"  -> {len(listed)}건 발견, 상세 조회 시작")

        for item in listed:
            time.sleep(REQUEST_DELAY)
            detail = fetch_detail(item["idx"])
            all_records.append(
                {
                    "category": category,
                    "matched_keyword": item["matched_keyword"],
                    "idx": item["idx"],
                    "title": item["title"] or detail["detail_title"],
                    "org": item["org"],
                    "url": urljoin(BASE_URL, f"/mobile2021/recruit/recruitView.do?idx={item['idx']}"),
                    "fields": detail["fields"],
                    "attachments": detail["attachments"],
                }
            )

    json_path = OUTPUT_DIR / "postings.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"저장: {json_path} ({len(all_records)}건)")

    csv_path = OUTPUT_DIR / "postings.csv"
    key_fields = ["기관명", "표준직무(NCS)", "근무분야", "고용형태", "응시자격", "우대조건", "우대내용"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "matched_keyword", "idx", "title", "org", "url", *key_fields])
        for rec in all_records:
            fields = rec["fields"]
            writer.writerow(
                [
                    rec["category"],
                    rec["matched_keyword"],
                    rec["idx"],
                    rec["title"],
                    rec["org"],
                    rec["url"],
                    *[fields.get(k, "").replace("\n", " ") for k in key_fields],
                ]
            )
    print(f"저장: {csv_path}")


if __name__ == "__main__":
    main()
