"""
업종 라벨이 붙은 공고 CSV(domain, skills 컬럼 포함)를 읽어서
업종별로 skills 빈도를 따로 계산한다.

- 입력: classify_domain.py의 출력(*_domain.csv)
- 출력: 업종별 기술 빈도표(long format) CSV + 콘솔에 업종별 TOP 기술 요약 출력
"""

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def find_latest_domain_csv(output_dir: Path) -> Path:
    candidates = sorted(output_dir.glob("*_domain.csv"))
    if not candidates:
        raise FileNotFoundError(f"{output_dir}에 *_domain.csv 파일이 없습니다. classify_domain.py를 먼저 실행하세요.")
    return candidates[-1]


def analyze(rows: list[dict]) -> tuple[dict[str, Counter], Counter]:
    domain_skill_counter: dict[str, Counter] = defaultdict(Counter)
    domain_posting_counter: Counter = Counter()

    for row in rows:
        domain = row.get("domain", "기타") or "기타"
        domain_posting_counter[domain] += 1
        skills = row.get("skills", "")
        for skill in skills.split(";"):
            skill = skill.strip()
            if skill:
                domain_skill_counter[domain][skill] += 1

    return domain_skill_counter, domain_posting_counter


def save_long_csv(domain_skill_counter: dict[str, Counter], domain_posting_counter: Counter, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "domain_posting_count", "skill", "skill_count", "skill_pct_in_domain"])
        for domain, posting_count in domain_posting_counter.most_common():
            for skill, count in domain_skill_counter[domain].most_common():
                pct = round(count / posting_count * 100, 1)
                writer.writerow([domain, posting_count, skill, count, pct])


def print_summary(domain_skill_counter: dict[str, Counter], domain_posting_counter: Counter, top_n: int) -> None:
    for domain, posting_count in domain_posting_counter.most_common():
        print(f"\n[{domain}] 공고 {posting_count}건")
        top_skills = domain_skill_counter[domain].most_common(top_n)
        if not top_skills:
            print("  (skills 정보 없음)")
            continue
        for skill, count in top_skills:
            pct = round(count / posting_count * 100, 1)
            print(f"  {skill}: {count}건 ({pct}%)")


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="업종별 기술 빈도 분석")
    parser.add_argument("--input", default=None, help="입력 CSV 경로 (기본: output/ 폴더에서 가장 최근 *_domain.csv)")
    parser.add_argument("--output", default=None, help="출력 CSV 경로 (기본: <입력파일명>_skills_by_domain.csv)")
    parser.add_argument("--top", type=int, default=10, help="업종별로 출력할 상위 기술 개수 (기본 10)")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else find_latest_domain_csv(project_root / "output")
    output_path = Path(args.output) if args.output else input_path.with_name(f"{input_path.stem}_skills_by_domain.csv")

    with input_path.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    domain_skill_counter, domain_posting_counter = analyze(rows)

    print(f"입력: {input_path.name} ({len(rows)}건)")
    print_summary(domain_skill_counter, domain_posting_counter, args.top)

    save_long_csv(domain_skill_counter, domain_posting_counter, output_path)
    print(f"\n저장 위치: {output_path}")


if __name__ == "__main__":
    main()
