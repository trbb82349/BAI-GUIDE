from __future__ import annotations

import csv
from html import escape
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "input" / "sample-culture-cards.csv"
OUTPUT_DIR = BASE_DIR / "output"


STATUS_META = {
    "possible": ("가능", "#047857", "#ecfdf5"),
    "conditional": ("조건부", "#b45309", "#fffbeb"),
    "check": ("확인 필요", "#0369a1", "#eff6ff"),
    "exclude": ("비추천", "#be123c", "#fff1f2"),
}


def split_items(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def load_rows() -> list[dict[str, str]]:
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_summary(rows: list[dict[str, str]]) -> None:
    output_path = OUTPUT_DIR / "culture-card-summary.csv"
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "place", "title", "status", "confirmed_count", "needs_review_count", "next_action"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "id": row["id"],
                    "place": row["place"],
                    "title": row["title"],
                    "status": row["status"],
                    "confirmed_count": len(split_items(row["confirmed"])),
                    "needs_review_count": len(split_items(row["needs_review"])),
                    "next_action": row["next_action"],
                }
            )


def list_block(title: str, items: list[str], class_name: str) -> str:
    if not items:
        return ""
    rendered = "".join(f"<li>{escape(item)}</li>" for item in items)
    return f"""
      <section class="{class_name}">
        <h3>{escape(title)}</h3>
        <ul>{rendered}</ul>
      </section>
    """


def render_card(row: dict[str, str]) -> str:
    label, fg, bg = STATUS_META.get(row["status"], ("검토", "#334155", "#f8fafc"))
    confirmed = split_items(row["confirmed"])
    needs_review = split_items(row["needs_review"])
    sources = split_items(row["evidence_sources"])
    source_text = " · ".join(sources)
    return f"""
    <article class="decision-card" style="--status-fg:{fg};--status-bg:{bg};">
      <div class="visual-band">
        <span>{escape(row['place'][:2])}</span>
      </div>
      <header>
        <span class="status">{escape(label)}</span>
        <h2>{escape(row['place'])}</h2>
        <p class="title">{escape(row['title'])}</p>
      </header>
      <p class="reason">{escape(row['status_reason'])}</p>
      {list_block("확인된 근거", confirmed, "confirmed")}
      {list_block("확인 필요", needs_review, "needs-review")}
      <section class="sources">
        <h3>근거 출처</h3>
        <p>{escape(source_text)}</p>
      </section>
      <a class="action" href="{escape(row['url'])}" target="_blank" rel="noopener noreferrer">{escape(row['next_action'])}</a>
    </article>
    """


def write_html(rows: list[dict[str, str]]) -> None:
    cards = "\n".join(render_card(row) for row in rows)
    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lumoa HTML 카드 UI 예시</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f6f3ef; color: #24211e; }}
    header.page {{ padding: 28px 22px 18px; background: #ffffff; border-bottom: 1px solid #ded7ce; }}
    .page-inner {{ max-width: 1120px; margin: 0 auto; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .lead {{ margin: 0; color: #675f58; line-height: 1.55; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 22px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 16px; }}
    .decision-card {{ background: #fff; border: 1px solid #ded7ce; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; min-height: 560px; }}
    .visual-band {{ height: 108px; background: linear-gradient(135deg, #274c77, #f4a261); display: flex; align-items: center; justify-content: center; color: #fff; }}
    .visual-band span {{ width: 58px; height: 58px; border-radius: 50%; border: 2px solid rgba(255,255,255,.8); display: grid; place-items: center; font-size: 20px; font-weight: 700; background: rgba(0,0,0,.18); }}
    .decision-card header {{ padding: 16px 16px 10px; border-bottom: 1px solid #ece6df; }}
    .status {{ display: inline-block; color: var(--status-fg); background: var(--status-bg); border: 1px solid var(--status-fg); border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 700; }}
    h2 {{ margin: 12px 0 4px; font-size: 21px; }}
    .title {{ margin: 0; color: #675f58; font-size: 14px; }}
    .reason {{ padding: 14px 16px 0; margin: 0; line-height: 1.55; color: #3d3935; min-height: 86px; }}
    section {{ margin: 14px 16px 0; padding: 13px; border-radius: 8px; }}
    section h3 {{ margin: 0 0 8px; font-size: 13px; }}
    ul {{ margin: 0; padding-left: 18px; line-height: 1.55; }}
    .confirmed {{ background: #effaf5; border: 1px solid #c8ead9; }}
    .needs-review {{ background: #eef6ff; border: 1px solid #c7ddf5; }}
    .sources {{ background: #f7f7f5; border: 1px solid #e3e0da; margin-top: auto; }}
    .sources p {{ margin: 0; color: #5b554e; font-size: 13px; line-height: 1.5; }}
    .action {{ margin: 14px 16px 16px; display: block; text-align: center; text-decoration: none; color: #ffffff; background: #24211e; border-radius: 6px; padding: 12px; font-weight: 700; }}
    @media (max-width: 640px) {{ h1 {{ font-size: 24px; }} main {{ padding: 14px; }} .decision-card {{ min-height: auto; }} }}
  </style>
</head>
<body>
  <header class="page">
    <div class="page-inner">
      <h1>Lumoa HTML 카드 UI 예시</h1>
      <p class="lead">데이터 결과를 상태, 근거, 확인 필요 항목으로 나누어 사용자가 판단하기 쉽게 보여줍니다.</p>
    </div>
  </header>
  <main>
    <section class="grid">
      {cards}
    </section>
  </main>
</body>
</html>
"""
    cleaned_html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    (OUTPUT_DIR / "lumoa-cards.html").write_text(cleaned_html, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    write_summary(rows)
    write_html(rows)
    print(f"카드 생성: {len(rows)}개")
    print(f"결과 폴더: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
