"""
지금까지의 분석 결과(수집 현황 / 업종 분포 / 업종별 기술 빈도)를
한 눈에 볼 수 있는 정적 HTML 대시보드로 만든다.

- 외부 라이브러리/CDN 없이 순수 HTML+CSS(+최소 JS 없이 <details>로 접기/펼치기)만 사용
- output/ 폴더의 최신 *_domain.csv, *_skills_by_domain.csv를 읽어서 표/막대그래프를 만든다
- "앞으로 알아갈 내용"(ROADMAP)은 아직 데이터가 없는 계획 항목이라 아래 리스트를 직접 채워서 관리한다.
  새 분석이 하나 끝날 때마다 이 리스트에서 항목을 옮기거나 추가하면 된다.
"""

import csv
import html
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

# 아직 실행하지 않은 다음 계획들. 완료되면 위쪽(DONE_ITEMS)으로 옮기고 여기서 지운다.
ROADMAP_ITEMS = [
    "사람인 수집 여부/방법 결정 (공식 Open API 신청 가능 여부 확인)",
    "표본 100건 이상으로 확대 (잡코리아 다른 직무 카테고리 페이지 탐색 필요)",
    "게임/교육/금융/미디어/커머스처럼 표본이 적은 업종 데이터 추가 확보",
    "포트폴리오 방향 추천: 내가 가진 기술 vs 관심 업종에서 요구하는 기술 비교",
    "Q&A 에이전트를 동아리 친구들에게 공유해서 실제 질문 로그 쌓기 (지금은 나 혼자 터미널 테스트만)",
    "LLM API 키 확보되면 ask_agent.py의 답변을 자연어 생성으로 업그레이드",
]

DONE_ITEMS = [
    "잡코리아 AI잡스 페이지에서 채용공고 100건 수집 (robots.txt 허용 범위 안에서)",
    "공고를 업종/분야로 규칙 기반 분류 (모빌리티, 제조, 헬스케어 등)",
    "관심 업종(IT서비스/금융/헬스케어) 데이터·AI 인력 성장 전망 리서치 완료 "
    "(notes/domain-demand-outlook-2026.md, 정부 통계·산업 리포트 기반)",
    "업종별 기술 스택 빈도 분석",
    "터미널용 Q&A 에이전트 v1 완성 (src/ask_agent.py, 키워드 매칭 기반, API 키 불필요)",
]

# 관심 업종 3개의 "성장 전망" 리서치 결과 요약 (notes/domain-demand-outlook-2026.md 참고).
# 이건 CSV에서 계산되는 값이 아니라 사람이 조사한 결과라 여기 직접 채워서 관리한다.
# 주의: "강/중/약"은 업종 자체의 절대 성장 속도가 아니라, 이번 조사에서 확보한 근거의
# 양과 일관성 기준 상대 평가임 (원문 노트의 한계/주의사항 섹션 참고).
GROWTH_OUTLOOK = [
    ("IT서비스/플랫폼", "강", "국가통계 3종(SW·AI·데이터산업 실태조사) 일치 + 클라우드산업 실제 25%대 성장(2024). "
     "다만 AI 채용공고 증가율 자체는 top5 밖 (이미 규모가 커서 증가율은 완만)"),
    ("금융/핀테크", "중~강", "정책 드라이버(마이데이터 2.0, 생성형AI 지원방안)는 가장 뚜렷하나, "
     "AI 채용공고 증가율 top5에도 못 들 만큼 업종 전체 성장 신호는 셋 중 가장 약함"),
    ("헬스케어/의료AI", "중~강", "AI 채용공고 123%↑(조사 대상 10개 산업 중 4위) + 원격의료 법제화(2026.12 시행)로 "
     "최대 걸림돌이던 규제가 완화되는 중. 다만 국가통계 수준의 인력 부족률 수치는 여전히 미확보"),
]


def find_latest(pattern: str, exclude_substr: str | None = None) -> Path | None:
    candidates = sorted(OUTPUT_DIR.glob(pattern))
    if exclude_substr:
        candidates = [c for c in candidates if exclude_substr not in c.name]
    return candidates[-1] if candidates else None


def load_domain_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_skills_by_domain(path: Path) -> dict[str, list[tuple[str, int, float]]]:
    result: dict[str, list[tuple[str, int, float]]] = defaultdict(list)
    with path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            domain = row["domain"]
            result[domain].append((row["skill"], int(row["skill_count"]), float(row["skill_pct_in_domain"])))
    return result


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def render_domain_bars(domain_counts: list[tuple[str, int]], total: int) -> str:
    rows = []
    for domain, count in domain_counts:
        pct = round(count / total * 100, 1)
        rows.append(f"""
        <div class="bar-row">
          <div class="bar-label">{esc(domain)}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%"></div>
          </div>
          <div class="bar-value">{count}건 ({pct}%)</div>
        </div>""")
    return "\n".join(rows)


def render_skill_table(rows: list[tuple[str, int, float]], top_n: int = 10) -> str:
    if not rows:
        return "<p class='muted'>수집된 기술 스택 정보가 없습니다.</p>"
    items = "".join(
        f"<tr><td>{esc(skill)}</td><td>{count}건</td><td>{pct}%</td></tr>"
        for skill, count, pct in rows[:top_n]
    )
    return f"""
    <table>
      <thead><tr><th>기술</th><th>건수</th><th>비중</th></tr></thead>
      <tbody>{items}</tbody>
    </table>"""


def render_domain_sections(domain_counts: list[tuple[str, int]], skills_by_domain: dict) -> str:
    sections = []
    for i, (domain, count) in enumerate(domain_counts):
        open_attr = " open" if i == 0 else ""
        table = render_skill_table(skills_by_domain.get(domain, []))
        sections.append(f"""
    <details class="domain-detail"{open_attr}>
      <summary>{esc(domain)} <span class="muted">({count}건)</span></summary>
      {table}
    </details>""")
    return "\n".join(sections)


def render_growth_outlook(rows: list[tuple[str, str, str]]) -> str:
    items = "".join(
        f"<tr><td>{esc(domain)}</td><td>{esc(level)}</td><td>{esc(reason)}</td></tr>"
        for domain, level, reason in rows
    )
    return f"""
    <table>
      <thead><tr><th>업종</th><th>성장 전망</th><th>근거 요약</th></tr></thead>
      <tbody>{items}</tbody>
    </table>"""


def render_list(items: list[str], done: bool) -> str:
    mark = "✅" if done else "▢"
    return "\n".join(f"<li>{mark} {esc(item)}</li>" for item in items)


def build_html() -> str:
    domain_csv = find_latest("*_domain.csv", exclude_substr="skills_by_domain")
    skills_csv = find_latest("*_skills_by_domain.csv")
    if domain_csv is None:
        raise FileNotFoundError("output/ 폴더에 *_domain.csv가 없습니다. classify_domain.py를 먼저 실행하세요.")

    rows = load_domain_rows(domain_csv)
    total = len(rows)

    domain_posting_counter = Counter(r.get("domain", "기타") or "기타" for r in rows)
    domain_counts = domain_posting_counter.most_common()

    overall_skill_counter = Counter()
    for r in rows:
        for skill in (r.get("skills") or "").split(";"):
            skill = skill.strip()
            if skill:
                overall_skill_counter[skill] += 1
    overall_top = [(s, c, round(c / total * 100, 1)) for s, c in overall_skill_counter.most_common(15)]

    skills_by_domain = load_skills_by_domain(skills_csv) if skills_csv else {}

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>취업공고 역량분석 대시보드</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #ffffff; --fg: #1a1a1a; --muted: #6b7280; --card: #f5f5f7;
    --accent: #4f46e5; --border: #e5e7eb;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #0f1117; --fg: #e8e8ec; --muted: #9096a3; --card: #1a1d27; --border: #2a2e3a; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 2rem 1.25rem 4rem; background: var(--bg); color: var(--fg);
    font-family: -apple-system, "Malgun Gothic", "Segoe UI", sans-serif; line-height: 1.55;
  }}
  .wrap {{ max-width: 880px; margin: 0 auto; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
  .subtitle {{ color: var(--muted); margin-top: 0; margin-bottom: 2rem; font-size: 0.9rem; }}
  section {{ margin-bottom: 2.5rem; }}
  h2 {{ font-size: 1.1rem; border-left: 4px solid var(--accent); padding-left: 0.6rem; margin-bottom: 1rem; }}
  .stat-row {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
  .stat-card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 1rem 1.25rem; flex: 1; min-width: 140px;
  }}
  .stat-card .num {{ font-size: 1.6rem; font-weight: 700; }}
  .stat-card .label {{ color: var(--muted); font-size: 0.85rem; margin-top: 0.15rem; }}
  .bar-row {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.6rem; }}
  .bar-label {{ width: 190px; flex-shrink: 0; font-size: 0.9rem; }}
  .bar-track {{
    flex: 1; background: var(--card); border-radius: 6px; height: 20px; overflow: hidden;
    border: 1px solid var(--border);
  }}
  .bar-fill {{ background: var(--accent); height: 100%; border-radius: 6px 0 0 6px; }}
  .bar-value {{ width: 130px; flex-shrink: 0; font-size: 0.85rem; color: var(--muted); text-align: right; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 0.75rem; font-size: 0.9rem; }}
  th, td {{ text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid var(--border); }}
  th {{ color: var(--muted); font-weight: 600; }}
  details.domain-detail {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 0.75rem 1rem; margin-bottom: 0.6rem;
  }}
  summary {{ cursor: pointer; font-weight: 600; }}
  .muted {{ color: var(--muted); font-weight: 400; }}
  ul.roadmap {{ list-style: none; padding-left: 0; }}
  ul.roadmap li {{ padding: 0.35rem 0; border-bottom: 1px dashed var(--border); font-size: 0.92rem; }}
  footer {{ color: var(--muted); font-size: 0.8rem; margin-top: 3rem; }}
</style>
</head>
<body>
<div class="wrap">

  <h1>취업공고 역량분석 대시보드</h1>
  <p class="subtitle">잡코리아 AI잡스 기준 · 생성 시각 {generated_at}</p>

  <section>
    <h2>수집 현황</h2>
    <div class="stat-row">
      <div class="stat-card"><div class="num">{total}건</div><div class="label">수집된 공고 수</div></div>
      <div class="stat-card"><div class="num">{len(domain_counts)}개</div><div class="label">분류된 업종/분야 수</div></div>
      <div class="stat-card"><div class="num">잡코리아</div><div class="label">현재 수집 대상 사이트</div></div>
    </div>
  </section>

  <section>
    <h2>업종/분야 분포</h2>
    {render_domain_bars(domain_counts, total)}
  </section>

  <section>
    <h2>전체 공통 기술 TOP 15</h2>
    {render_skill_table(overall_top, top_n=15)}
    <p class="muted" style="font-size:0.85rem;margin-top:0.5rem;">
      업종을 가리지 않고 전체 공고에서 가장 많이 등장한 기술입니다.
    </p>
  </section>

  <section>
    <h2>업종별 기술 스택 TOP 10</h2>
    {render_domain_sections(domain_counts, skills_by_domain)}
  </section>

  <section>
    <h2>관심 업종 성장 전망 (리서치)</h2>
    {render_growth_outlook(GROWTH_OUTLOOK)}
    <p class="muted" style="font-size:0.85rem;margin-top:0.5rem;">
      위 "업종/분야 분포"는 지금 이 순간의 공고 수 스냅샷이고, 이 표는 별도로
      "앞으로 수요가 늘어날 곳"을 정부 통계·산업 리포트로 조사한 결과입니다(둘은 다른 질문).
      "강/중/약"은 업종의 절대적 성장 속도가 아니라 이번 조사에서 확보한 근거의 양과
      일관성 기준 상대 평가이며, 전체 근거와 출처·한계는
      <code>notes/domain-demand-outlook-2026.md</code>에 정리되어 있습니다.
    </p>
  </section>

  <section>
    <h2>진행 상태</h2>
    <ul class="roadmap">
{render_list(DONE_ITEMS, done=True)}
{render_list(ROADMAP_ITEMS, done=False)}
    </ul>
  </section>

  <footer>
    데이터: {esc(domain_csv.name)} · src/build_dashboard.py로 생성됨 (재실행하면 최신 데이터로 갱신)
  </footer>

</div>
</body>
</html>
"""


def main() -> None:
    html_content = build_html()
    output_path = OUTPUT_DIR / "dashboard.html"
    output_path.write_text(html_content, encoding="utf-8")
    print(f"저장 위치: {output_path}")


if __name__ == "__main__":
    main()
