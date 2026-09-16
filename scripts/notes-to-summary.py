"""여러 메모 파일을 하나의 정리 문서로 합칩니다.

사용법:
    python scripts/notes-to-summary.py [메모폴더] [출력파일]

인자를 생략하면 00-inbox/ideas/와 10-projects/summary-output/output/summary.md를 사용합니다.
"""
import sys
from pathlib import Path


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("00-inbox/ideas")
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("10-projects/summary-output/output/summary.md")

    if not folder.exists():
        print(f"폴더를 찾지 못함: {folder}")
        sys.exit(1)

    files = sorted(folder.glob("*.md"))
    if not files:
        print(f"메모 파일이 없습니다: {folder}")
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as out:
        out.write(f"# 메모 정리 — {folder.name}\n\n")
        for path in files:
            out.write(f"## {path.stem}\n\n")
            out.write(path.read_text(encoding="utf-8"))
            out.write("\n\n---\n\n")

    print(f"저장 완료: {output} (파일 {len(files)}개 합침)")


if __name__ == "__main__":
    main()
