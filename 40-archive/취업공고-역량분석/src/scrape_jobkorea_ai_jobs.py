"""
잡코리아 'AI잡스' 페이지(https://www.jobkorea.co.kr/recruit/ai-jobs)에서
데이터/AI 관련 채용공고를 수집해 CSV로 저장한다.

- robots.txt 기준: 이 페이지와 /Recruit/GI_Read/ 상세 링크는 일반 크롤러에 허용됨
  (검색 기능 /Search/, /recruit/ai-jobs/search 는 차단 대상이라 사용하지 않음)
- 목록 카드에 이미 회사명/공고제목/기술스택 태그/경력/지역/마감일이 구조화되어 있어
  1차 버전은 상세 페이지까지 들어가지 않고 목록 정보만 수집한다.
- 무한 스크롤 페이지라 target_count에 도달할 때까지 스크롤 + 대기를 반복한다.
"""

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path
from urllib.robotparser import RobotFileParser

from playwright.sync_api import sync_playwright

BASE_URL = "https://www.jobkorea.co.kr/recruit/ai-jobs"
ROBOTS_URL = "https://www.jobkorea.co.kr/robots.txt"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
SCROLL_PAUSE_SEC = 1.5

EXTRACT_JS = """
() => {
    const cards = Array.from(document.querySelectorAll('li.recruit-item'));
    return cards.map(card => {
        const link = card.querySelector('a.recruit-link');
        const titleEl = card.querySelector('a.recruit-link h3.title');
        const companyEl = card.querySelector('.company .company-name a');
        const descEl = card.querySelector('.company .company-description .more-info p');
        const dateEl = card.querySelector('.actions .date');
        const keywordEls = Array.from(card.querySelectorAll('ul.keywords > li.item'));

        const skills = [];
        const career = [];
        const workLocation = [];
        const badges = [];
        keywordEls.forEach(li => {
            const text = (li.dataset.originalText || li.textContent || '').trim();
            if (!text) return;
            const cls = li.className || '';
            if (cls.includes('celebrate')) badges.push(text);
            else if (cls.includes('primary')) skills.push(text);
            else if (/^(신입|경력)/.test(text)) career.push(text);
            else workLocation.push(text);
        });

        return {
            recruit_no: link ? link.dataset.gno || '' : '',
            title: titleEl ? titleEl.textContent.trim() : '',
            company: companyEl ? companyEl.textContent.trim() : '',
            company_desc: descEl ? descEl.textContent.trim() : '',
            skills: skills.join(';'),
            career: career.join(';'),
            location: workLocation.join(';'),
            badges: badges.join(';'),
            deadline_text: dateEl ? dateEl.textContent.trim() : '',
            deadline_date: link ? (link.dataset.applyclosedt || '') : '',
            detail_url: link ? new URL(link.getAttribute('href'), window.location.href).href : '',
        };
    });
}
"""


def check_robots_allowed(path: str) -> bool:
    rp = RobotFileParser()
    rp.set_url(ROBOTS_URL)
    rp.read()
    return rp.can_fetch(USER_AGENT, path)


def collect(target_count: int, max_scrolls: int = 200, stall_limit: int = 5) -> list[dict]:
    seen: dict[str, dict] = {}
    stall_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        for i in range(max_scrolls):
            rows = page.evaluate(EXTRACT_JS)
            before = len(seen)
            for row in rows:
                key = row.get("recruit_no") or row.get("detail_url")
                if key:
                    seen[key] = row

            if len(seen) >= target_count:
                break

            if len(seen) == before:
                stall_count += 1
                if stall_count >= stall_limit:
                    print(f"  (스크롤해도 새 공고가 안 늘어나 {i + 1}번째에서 중단, 총 {len(seen)}건)")
                    break
            else:
                stall_count = 0

            page.mouse.wheel(0, 2500)
            time.sleep(SCROLL_PAUSE_SEC)

        browser.close()

    return list(seen.values())[:target_count]


def save_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "recruit_no", "title", "company", "company_desc", "skills", "career",
        "location", "badges", "deadline_text", "deadline_date", "detail_url",
    ]
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="잡코리아 AI잡스 공고 수집")
    parser.add_argument("--count", type=int, default=50, help="수집할 공고 개수 (기본 50)")
    parser.add_argument(
        "--output",
        default=None,
        help="저장 경로 (기본: ../output/jobkorea_ai_jobs_<timestamp>.csv)",
    )
    args = parser.parse_args()

    if not check_robots_allowed("/recruit/ai-jobs"):
        print("robots.txt에서 이 경로를 허용하지 않습니다. 수집을 중단합니다.")
        return

    print(f"수집 시작: 목표 {args.count}건 (스크롤 간 {SCROLL_PAUSE_SEC}초 대기)")
    rows = collect(args.count)
    print(f"수집 완료: {len(rows)}건")

    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = Path(__file__).resolve().parent.parent / "output" / f"jobkorea_ai_jobs_{timestamp}.csv"

    save_csv(rows, output_path)
    print(f"저장 위치: {output_path}")


if __name__ == "__main__":
    main()
