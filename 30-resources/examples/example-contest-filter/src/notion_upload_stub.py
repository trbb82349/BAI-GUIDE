from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "output" / "contests_filtered.csv"


def build_preview_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"먼저 python src/main.py를 실행하세요: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [
            {
                "name": row["title"],
                "status": "검수 대기",
                "deadline": row["deadline"],
                "source": row["source"],
                "url": row["url"],
                "summary": row["description"],
            }
            for row in csv.DictReader(f)
        ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Notion 업로드 확장 구조 미리보기")
    parser.add_argument("--upload", action="store_true", help="이 예시는 실제 업로드를 수행하지 않습니다.")
    args = parser.parse_args()

    rows = build_preview_rows(INPUT_PATH)
    if args.upload:
        raise SystemExit("이 학생용 예시는 외부 쓰기 작업을 하지 않습니다. 개인 프로젝트에서 별도 구현하세요.")

    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print("\n미리보기만 출력했습니다. 외부 서비스 쓰기는 별도 단계로 분리하세요.")


if __name__ == "__main__":
    main()
