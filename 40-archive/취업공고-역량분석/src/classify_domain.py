"""
수집한 공고 CSV(title, company_desc 컬럼 포함)를 읽어서
공고 제목 + 회사소개 텍스트에 등장하는 키워드를 기준으로
업종/분야(domain) 라벨을 하나씩 붙인다.

- 규칙 기반(키워드 매칭)이라 결과를 눈으로 바로 확인/수정할 수 있다.
- DOMAIN_RULES 순서가 우선순위: 위에서부터 먼저 매칭되는 업종으로 확정한다.
  (한 회사가 여러 키워드에 걸칠 수 있어서, 더 구체적인 업종을 위쪽에 둔다)
- 아무 키워드에도 안 걸리면 '기타'로 분류한다.
"""

import argparse
import csv
from collections import Counter
from pathlib import Path

DOMAIN_RULES: list[tuple[str, list[str]]] = [
    ("헬스케어/제약/바이오", ["헬스케어", "바이오", "제약", "의료", "메디컬", "병원", "약국", "파마", "pharm", "임상", "진단", "건강", "웰니스"]),
    ("금융/핀테크", ["금융", "은행", "증권", "보험", "결제", "핀테크", "자산관리", "캐피탈", "fintech"]),
    ("모빌리티/자율주행/로보틱스", ["자율주행", "모빌리티", "로봇", "로보틱스", "휴머노이드", "드론", "내비게이션", "전기차"]),
    ("제조/스마트팩토리", ["제조", "스마트팩토리", "스마트 팩토리", "산업용", "4차산업", "4차 산업", "반도체"]),
    ("커머스/유통", ["커머스", "이커머스", "쇼핑", "유통", "리테일", "마켓플레이스", "주문"]),
    ("물류/공급망", ["물류", "배송", "풀필먼트", "scm", "공급망"]),
    ("게임", ["게임", "게이밍"]),
    ("미디어/콘텐츠", ["미디어", "콘텐츠", "엔터테인먼트", "방송", "영상", "ott"]),
    ("교육", ["교육", "에듀테크", "이러닝", "홈스쿨링", "아카데미"]),
    ("공공/정책", ["공공", "정부", "공기업", "지자체"]),
    ("IT서비스/플랫폼", ["플랫폼", "saas", "소프트웨어", "it서비스", "솔루션"]),
]
FALLBACK_DOMAIN = "기타"


def classify(text: str) -> tuple[str, str]:
    lowered = text.lower()
    for domain, keywords in DOMAIN_RULES:
        for kw in keywords:
            if kw.lower() in lowered:
                return domain, kw
    return FALLBACK_DOMAIN, ""


def find_latest_csv(output_dir: Path) -> Path:
    candidates = sorted(output_dir.glob("jobkorea_ai_jobs_*.csv"))
    candidates = [c for c in candidates if "_domain" not in c.stem]
    if not candidates:
        raise FileNotFoundError(f"{output_dir}에 jobkorea_ai_jobs_*.csv 파일이 없습니다.")
    return candidates[-1]


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="공고 CSV에 업종/분야 라벨 붙이기")
    parser.add_argument("--input", default=None, help="입력 CSV 경로 (기본: output/ 폴더에서 가장 최근 파일)")
    parser.add_argument("--output", default=None, help="출력 CSV 경로 (기본: <입력파일명>_domain.csv)")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else find_latest_csv(project_root / "output")
    output_path = Path(args.output) if args.output else input_path.with_name(f"{input_path.stem}_domain.csv")

    with input_path.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    domain_counter = Counter()
    for row in rows:
        text = f"{row.get('title', '')} {row.get('company', '')} {row.get('company_desc', '')}"
        domain, matched_kw = classify(text)
        row["domain"] = domain
        row["matched_keyword"] = matched_kw
        domain_counter[domain] += 1

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"입력: {input_path.name} ({len(rows)}건)")
    print(f"출력: {output_path}")
    print("\n업종별 공고 수:")
    for domain, count in domain_counter.most_common():
        print(f"  {domain}: {count}건")


if __name__ == "__main__":
    main()
