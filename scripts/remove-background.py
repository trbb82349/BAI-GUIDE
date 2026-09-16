"""사진 폴더의 배경을 지워서 대상만 남긴 투명 배경 PNG(누끼)로 저장합니다.

사용법:
    python scripts/remove-background.py [입력폴더] [출력폴더]

인자를 생략하면 입력폴더는 현재 폴더, 출력폴더는 "입력폴더/누끼-결과"를 사용합니다.

지원 확장자: jpg, jpeg, png, webp, bmp
결과 파일: 같은 파일명 + .png (투명 배경)

준비물:
    pip install rembg pillow
    처음 실행할 때 AI 모델(약 170MB)을 인터넷에서 한 번 내려받습니다.
    이후에는 인터넷 연결 없이도 동작합니다.
"""
import sys
from pathlib import Path

try:
    from PIL import Image
    from rembg import remove
except ImportError:
    print("필요한 라이브러리가 없습니다. 아래 명령으로 먼저 설치하세요.")
    print("    pip install rembg pillow")
    sys.exit(1)


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def main():
    input_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    output_folder = (
        Path(sys.argv[2]) if len(sys.argv) > 2 else input_folder / "누끼-결과"
    )

    if not input_folder.exists():
        print(f"폴더를 찾지 못함: {input_folder}")
        sys.exit(1)

    images = sorted(
        p
        for p in input_folder.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not images:
        print(f"처리할 이미지가 없습니다: {input_folder}")
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    done = 0
    failed = 0
    print(f"이미지 {len(images)}개 처리 시작 (첫 실행은 AI 모델 다운로드로 시간이 걸릴 수 있습니다)")
    for path in images:
        try:
            with Image.open(path) as img:
                result = remove(img)
            out_path = output_folder / f"{path.stem}.png"
            result.save(out_path)
            done += 1
            print(f"  완료: {path.name} -> {out_path.name}")
        except Exception as e:
            failed += 1
            print(f"  실패: {path.name} — {e}")

    print(f"\n처리 완료: 성공 {done}개, 실패 {failed}개")
    print(f"결과 폴더: {output_folder}")


if __name__ == "__main__":
    main()
