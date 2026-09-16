"""폴더 안 파일들의 이름 앞에 오늘 날짜를 일괄로 붙입니다.

사용법:
    python scripts/file-rename-dated.py [폴더경로]

인자를 생략하면 현재 폴더를 사용합니다.

결과 예시:
    report.docx -> 2026-06-22-report.docx
    photo.jpg   -> 2026-06-22-photo.jpg

이미 YYYY-MM-DD- 형식으로 시작하는 파일은 건너뜁니다.
하위 폴더는 건드리지 않고, 폴더 자체도 이름을 바꾸지 않습니다.
"""
import re
import sys
from datetime import date
from pathlib import Path


DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    if not folder.exists():
        print(f"폴더를 찾지 못함: {folder}")
        sys.exit(1)

    today = date.today().isoformat()
    renamed = 0
    skipped = 0
    for path in folder.iterdir():
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if DATE_PREFIX_RE.match(path.name):
            skipped += 1
            continue
        new_name = f"{today}-{path.name}"
        path.rename(path.with_name(new_name))
        renamed += 1

    print(f"이름 변경 {renamed}개, 건너뜀 {skipped}개 (이미 날짜로 시작)")


if __name__ == "__main__":
    main()
