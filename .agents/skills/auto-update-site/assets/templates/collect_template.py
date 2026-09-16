"""
collect.py 템플릿 — 데이터 수집 + AI 분석 후 data.json 업데이트
GitHub Actions에서 스케줄 실행됨.

필요한 환경변수 (GitHub Secrets):
  GEMINI_API_KEY
  (필요에 따라 추가: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 등)
"""
import json
import os
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST       = timezone(timedelta(hours=9))
ROOT      = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "data.json"

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")


# ── Gemini API (무료) ──────────────────────────────────────
def call_gemini(prompt: str) -> str:
    if not GEMINI_KEY:
        print("  [SKIP] Gemini API 키 없음")
        return "[]"
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.7},
    }).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.loads(res.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"  [ERROR] Gemini 실패: {e}")
        return "[]"


# ── 데이터 수집 함수 (주제에 맞게 수정) ───────────────────
def fetch_raw_data() -> list[str]:
    """외부 소스에서 원시 데이터를 수집해 텍스트 목록으로 반환."""
    # 예: 네이버 블로그 검색, RSS 피드, 공공 API 등
    # TODO: 실제 수집 로직 구현
    #
    # [주의] 게시판처럼 페이지를 넘겨가며 "새 항목만" 증분 수집하는 로직을 짤 때:
    # 처음 이 소스를 추가할 때 1페이지(최근 것)만 채워두고 시작하는 경우가 많은데,
    # 이후 "이미 아는 항목 ID 목록에 없으면 새 항목"으로 판단하는 방식만 쓰면
    # 위험하다 — 2페이지 이후는 한 번도 저장해본 적 없는 영역이라 전부 "새 항목"으로
    # 오인해서, 페이지를 계속 넘기며 몇 달 전 옛날 글까지 안전 상한까지 다 끌어올
    # 수 있다(실제로 이 스킬을 쓴 프로젝트에서 발생한 사고). 페이지네이션을 직접
    # 구현한다면 "한 페이지 안에 이미 아는 항목이 하나라도 섞여 있으면 그 페이지에서
    # 멈춘다"처럼, 페이지 전체가 새 항목일 때만 다음 페이지로 넘어가도록 만들 것.
    return []


# ── 메인 ───────────────────────────────────────────────────
def main():
    today = datetime.now(KST).strftime("%Y-%m-%d")
    print(f"[collect.py] 실행: {today}")

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    existing_ids = {item["id"] for item in data["items"]}
    print(f"  기존 항목: {len(existing_ids)}개")

    raw_snippets = fetch_raw_data()
    if not raw_snippets:
        print("  수집 결과 없음.")
        data["meta"]["last_updated"] = today
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return

    prompt = f"""아래 정보를 분석해서 신규 항목을 JSON 배열로 반환하세요.
이미 있는 항목 ID: {list(existing_ids)}

수집된 정보:
{chr(10).join(raw_snippets[:20])}

반환 형식 (JSON 배열만, 다른 텍스트 없이):
[
  {{
    "id": "영어-소문자-하이픈",
    "name": "항목명",
    "added_date": "{today}"
  }}
]"""

    print("  Gemini 분석 중...")
    response = call_gemini(prompt)

    try:
        match = re.search(r"\[.*\]", response, re.DOTALL)
        new_items = json.loads(match.group()) if match else []
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON 파싱 실패: {e}")
        new_items = []

    added = 0
    for item in new_items:
        if item.get("id") and item["id"] not in existing_ids:
            data["items"].append(item)
            existing_ids.add(item["id"])
            added += 1
            print(f"  신규 추가: {item.get('name', item['id'])}")

    if added == 0:
        print("  신규 항목 없음.")

    data["meta"]["last_updated"] = today
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  저장 완료. 총 {len(data['items'])}개")


if __name__ == "__main__":
    main()
