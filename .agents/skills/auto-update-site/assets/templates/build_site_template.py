"""
build_site.py 템플릿 — data/data.json → docs/index.html 변환
"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT      = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "data.json"
OUT_FILE  = ROOT / "docs" / "index.html"
KST       = timezone(timedelta(hours=9))


def card_html(item: dict) -> str:
    """항목 하나를 카드 HTML로 변환. 주제에 맞게 수정."""
    return f"""
    <div class="card">
      <div class="card-name">{item.get('name', '')}</div>
      <div class="card-date">등록일 {item.get('added_date', '')}</div>
    </div>"""


def build():
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    items   = data["items"]
    now_kst = datetime.now(KST).strftime("%Y년 %m월 %d일 %H:%M")
    total   = len(items)
    cards   = "\n".join(card_html(item) for item in items)

    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>자동 업데이트 트래커</title>
  <style>
    /* TODO: 디자인 커스터마이즈 */
    body {{ font-family: sans-serif; max-width: 1200px; margin: 0 auto; padding: 24px; }}
    .header {{ background: #222; color: #fff; padding: 32px; border-radius: 12px; margin-bottom: 24px; }}
    .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
    .card {{ background: #fff; border: 1px solid #ddd; border-radius: 10px; padding: 16px; }}
    .update-bar {{ font-size: 13px; color: #666; margin-bottom: 20px; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>자동 업데이트 트래커</h1>
    <p>총 {total}개 항목 · 매주 자동 업데이트</p>
  </div>
  <div class="update-bar">마지막 업데이트: <strong>{now_kst}</strong></div>
  <div class="cards-grid">
    {cards}
  </div>
<script>
  /* TODO: 필터·정렬 JS 추가 */
</script>
</body>
</html>"""

    OUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built: {OUT_FILE} ({total} items)")


if __name__ == "__main__":
    build()
