"""다운로드 폴더의 파일을 종류별로 폴더를 만들어 정리합니다.

사용법:
    python scripts/download-organize.py [폴더경로]

인자를 생략하면 사용자 다운로드 폴더(~/Downloads)를 사용합니다.

분류 규칙:
- 문서: pdf, docx, doc, hwp, txt, md, ppt, pptx
- 이미지: jpg, jpeg, png, gif, webp, svg, heic
- 영상·오디오: mp4, mov, mkv, avi, mp3, wav, m4a
- 압축: zip, rar, 7z, tar, gz
- 데이터: csv, xlsx, xls, json, xml, tsv
- 기타: 위에 속하지 않는 모든 확장자
"""
import shutil
import sys
from pathlib import Path


CATEGORIES = {
    "문서": {".pdf", ".docx", ".doc", ".hwp", ".txt", ".md", ".ppt", ".pptx"},
    "이미지": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".heic"},
    "영상오디오": {".mp4", ".mov", ".mkv", ".avi", ".mp3", ".wav", ".m4a"},
    "압축": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "데이터": {".csv", ".xlsx", ".xls", ".json", ".xml", ".tsv"},
}


def classify(suffix: str) -> str:
    suffix = suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return "기타"


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads"

    if not folder.exists():
        print(f"폴더를 찾지 못함: {folder}")
        sys.exit(1)

    moved = {}
    for path in folder.iterdir():
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue

        category = classify(path.suffix)
        target_dir = folder / category
        target_dir.mkdir(exist_ok=True)
        try:
            shutil.move(str(path), str(target_dir / path.name))
            moved[category] = moved.get(category, 0) + 1
        except Exception as e:
            print(f"이동 실패: {path.name} — {e}")

    print(f"\n정리 완료: {folder}")
    if not moved:
        print("  옮길 파일이 없습니다.")
        return
    for category, count in moved.items():
        print(f"  {category}: {count}개")


if __name__ == "__main__":
    main()
