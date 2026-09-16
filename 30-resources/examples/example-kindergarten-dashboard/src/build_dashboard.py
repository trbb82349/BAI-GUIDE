from __future__ import annotations

import csv
from html import escape
from pathlib import Path
from statistics import mean


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "input" / "sample-kindergartens.csv"
OUTPUT_DIR = BASE_DIR / "output"


def to_int(value: str) -> int:
    return int(str(value).replace(",", "").strip())


def parse_hour(value: str) -> float:
    hour, minute = value.split(":")
    return int(hour) + int(minute) / 60


def load_rows() -> list[dict[str, str]]:
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def enrich_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    enriched: list[dict[str, object]] = []
    for row in rows:
        students = to_int(row["students"])
        capacity = to_int(row["capacity"])
        teachers = to_int(row["teachers"])
        classrooms = to_int(row["classrooms"])
        fee = to_int(row["monthly_fee_won"])
        aftercare_hour = parse_hour(row["aftercare_until"])

        occupancy_rate = students / capacity
        students_per_teacher = students / teachers
        students_per_classroom = students / classrooms
        care_score = max(0, 100 - students_per_teacher * 5)
        space_score = max(0, 100 - students_per_classroom * 2.5)
        aftercare_score = min(100, max(0, (aftercare_hour - 16.5) * 35))
        cost_score = 100 if row["type"] == "공립" else max(0, 100 - fee / 4000)
        bus_score = 8 if row["has_bus"] == "yes" else 0
        special_score = 6 if row["special_class"] == "yes" else 0
        study_score = round(
            care_score * 0.32
            + space_score * 0.24
            + aftercare_score * 0.18
            + cost_score * 0.18
            + bus_score
            + special_score,
            1,
        )

        memo = []
        if students_per_teacher <= 8:
            memo.append("교사 1인당 원아 수 낮음")
        if occupancy_rate >= 0.9:
            memo.append("정원 여유 적음")
        if aftercare_hour >= 18.5:
            memo.append("돌봄 시간 김")
        if row["has_bus"] == "yes":
            memo.append("통학차량 있음")
        if not memo:
            memo.append("추가 비교 필요")

        enriched.append(
            {
                **row,
                "students": students,
                "capacity": capacity,
                "teachers": teachers,
                "classrooms": classrooms,
                "monthly_fee_won": fee,
                "occupancy_rate": round(occupancy_rate, 3),
                "students_per_teacher": round(students_per_teacher, 1),
                "students_per_classroom": round(students_per_classroom, 1),
                "aftercare_hour": round(aftercare_hour, 1),
                "study_score": study_score,
                "memo": "; ".join(memo),
            }
        )
    return sorted(enriched, key=lambda item: (-float(item["study_score"]), str(item["name"])))


def write_csv(rows: list[dict[str, object]]) -> None:
    output_path = OUTPUT_DIR / "processed-kindergartens.csv"
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, object]]) -> None:
    top = rows[:3]
    avg_score = mean(float(row["study_score"]) for row in rows)
    lines = [
        "# 유치원 샘플 분석 요약",
        "",
        f"- 분석 대상: {len(rows)}곳",
        f"- 평균 학습용 점수: {avg_score:.1f}",
        f"- 공립: {sum(1 for row in rows if row['type'] == '공립')}곳",
        f"- 사립: {sum(1 for row in rows if row['type'] == '사립')}곳",
        "",
        "## 상위 후보",
        "",
    ]
    for index, row in enumerate(top, 1):
        lines.extend(
            [
                f"### {index}. {row['name']}",
                "",
                f"- 점수: {row['study_score']}",
                f"- 교사 1인당 원아 수: {row['students_per_teacher']}명",
                f"- 정원 대비 현원: {float(row['occupancy_rate']) * 100:.1f}%",
                f"- 메모: {row['memo']}",
                "",
            ]
        )
    (OUTPUT_DIR / "analysis-summary.md").write_text("\n".join(lines), encoding="utf-8")


def metric_bar(value: float, max_value: float, invert: bool = False) -> str:
    ratio = min(1.0, value / max_value if max_value else 0)
    if invert:
        ratio = 1 - ratio
    return f"{max(6, int(ratio * 100))}%"


def write_html(rows: list[dict[str, object]]) -> None:
    cards = []
    for row in rows:
        score = float(row["study_score"])
        occupancy_percent = float(row["occupancy_rate"]) * 100
        cards.append(
            f"""
            <article class="card">
              <div class="card-head">
                <span class="badge">{escape(str(row['type']))}</span>
                <strong>{score:.1f}</strong>
              </div>
              <h2>{escape(str(row['name']))}</h2>
              <p class="sub">{escape(str(row['district']))} · {escape(str(row['memo']))}</p>
              <div class="metrics">
                <div><span>정원 대비 현원</span><b>{occupancy_percent:.1f}%</b><i style="width:{metric_bar(occupancy_percent, 100)}"></i></div>
                <div><span>교사 1인당</span><b>{row['students_per_teacher']}명</b><i style="width:{metric_bar(float(row['students_per_teacher']), 15, invert=True)}"></i></div>
                <div><span>월 부담</span><b>{int(row['monthly_fee_won']):,}원</b><i style="width:{metric_bar(float(row['monthly_fee_won']), 260000, invert=True)}"></i></div>
              </div>
            </article>
            """
        )

    table_rows = []
    for row in rows:
        table_rows.append(
            "<tr>"
            f"<td>{escape(str(row['name']))}</td>"
            f"<td>{escape(str(row['district']))}</td>"
            f"<td>{row['students_per_teacher']}</td>"
            f"<td>{float(row['occupancy_rate']) * 100:.1f}%</td>"
            f"<td>{escape(str(row['aftercare_until']))}</td>"
            f"<td>{int(row['monthly_fee_won']):,}원</td>"
            f"<td>{row['study_score']}</td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>유치원 샘플 데이터 대시보드</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f7f8fa; color: #1f2933; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d9dee7; padding: 24px; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    .lead {{ margin: 0; color: #607083; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; }}
    .card {{ background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 18px; }}
    .card-head {{ display: flex; align-items: center; justify-content: space-between; }}
    .badge {{ border: 1px solid #a8b4c5; border-radius: 999px; padding: 4px 8px; font-size: 12px; color: #394b63; }}
    .card h2 {{ margin: 14px 0 4px; font-size: 20px; }}
    .sub {{ min-height: 42px; margin: 0 0 16px; color: #607083; line-height: 1.45; }}
    .metrics div {{ margin-top: 10px; }}
    .metrics span {{ display: inline-block; width: 108px; color: #607083; font-size: 13px; }}
    .metrics b {{ font-size: 13px; }}
    .metrics i {{ display: block; height: 8px; margin-top: 5px; background: #3b82f6; border-radius: 999px; }}
    section {{ margin-top: 26px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d9dee7; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e8ecf2; text-align: left; font-size: 14px; }}
    th {{ background: #eef2f7; }}
    @media (max-width: 640px) {{ main {{ padding: 14px; }} table {{ font-size: 12px; }} th, td {{ padding: 8px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>유치원 샘플 데이터 대시보드</h1>
    <p class="lead">작은 CSV에서 전처리, 파생지표, 화면 구현까지 이어지는 예시입니다.</p>
  </header>
  <main>
    <section class="grid">
      {''.join(cards)}
    </section>
    <section>
      <h2>비교 표</h2>
      <table>
        <thead>
          <tr><th>이름</th><th>지역</th><th>교사 1인당</th><th>충원율</th><th>돌봄 종료</th><th>월 부담</th><th>점수</th></tr>
        </thead>
        <tbody>{''.join(table_rows)}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
    cleaned_html = "\n".join(line.rstrip() for line in html.splitlines()) + "\n"
    (OUTPUT_DIR / "dashboard.html").write_text(cleaned_html, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = enrich_rows(load_rows())
    write_csv(rows)
    write_summary(rows)
    write_html(rows)
    print(f"처리 완료: {len(rows)}곳")
    print(f"결과 폴더: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
