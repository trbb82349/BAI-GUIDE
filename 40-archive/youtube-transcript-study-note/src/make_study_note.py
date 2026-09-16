from __future__ import annotations

import re
from collections import Counter
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_DIR / "input" / "transcript.txt"
OUTPUT_PATH = PROJECT_DIR / "output" / "study-note.md"

STOPWORDS = {
    "그리고",
    "그러면",
    "그래서",
    "하지만",
    "오늘은",
    "먼저",
    "마지막으로",
    "있습니다",
    "합니다",
    "것입니다",
    "좋습니다",
    "수",
    "때",
    "것",
    "이",
    "그",
    "저",
    "더",
}


def clean_transcript(text: str) -> str:
    lines = []
    previous_line = ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line in {"WEBVTT", "Kind: captions"}:
            continue
        if line.startswith("Language:"):
            continue
        if "-->" in line:
            continue
        line = re.sub(r"<\d{1,2}:\d{2}:\d{2}\.\d{3}>", "", line)
        line = re.sub(r"</?c>", "", line)
        line = re.sub(r"<[^>]+>", "", line)
        line = re.sub(r"^\[?\d{1,2}:\d{2}(?::\d{2})?\]?\s*", "", line)
        line = re.sub(r"\s+", " ", line).strip()
        if line and line != previous_line:
            lines.append(line)
            previous_line = line
    return " ".join(lines)


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?。！？]|[다요죠니다습니다])\s+", text)
    return [sentence.strip() for sentence in sentences if len(sentence.strip()) > 4]


def pick_key_points(sentences: list[str], limit: int = 5) -> list[str]:
    if len(sentences) <= limit:
        return sentences

    scored = []
    cue_words = ("중요", "핵심", "질문", "요약", "정리", "확인", "예를 들어", "복습")
    for index, sentence in enumerate(sentences):
        score = min(len(sentence), 120) / 40
        score += sum(1 for word in cue_words if word in sentence)
        if index == 0:
            score += 1
        scored.append((score, index, sentence))

    selected = sorted(scored, reverse=True)[:limit]
    return [sentence for _, _, sentence in sorted(selected, key=lambda item: item[1])]


def extract_keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[A-Za-z가-힣0-9]{2,}", text)
    candidates = [word for word in words if word not in STOPWORDS and len(word) >= 2]
    return [word for word, _ in Counter(candidates).most_common(limit)]


def make_questions(key_points: list[str]) -> list[str]:
    questions = []
    if key_points:
        questions.append("오늘 내용의 핵심을 한 문장으로 설명하면 무엇인가?")
    if len(key_points) >= 2:
        questions.append("가장 중요하다고 생각한 근거 또는 예시는 무엇인가?")
    questions.append("이 내용을 내 공부나 작업에 바로 적용한다면 무엇부터 해볼 수 있는가?")
    return questions


def build_note(raw_text: str) -> str:
    cleaned = clean_transcript(raw_text)
    sentences = split_sentences(cleaned)
    key_points = pick_key_points(sentences)
    keywords = extract_keywords(cleaned)
    questions = make_questions(key_points)

    summary = key_points[0] if key_points else "자막에서 핵심 내용을 찾지 못했습니다."

    lines = [
        "# 공부 노트",
        "",
        "## 한 줄 요약",
        "",
        f"- {summary}",
        "",
        "## 핵심 포인트",
        "",
    ]
    lines.extend(f"- {point}" for point in key_points)
    lines.extend(["", "## 키워드", ""])
    lines.extend(f"- {keyword}" for keyword in keywords)
    lines.extend(["", "## 복습 질문", ""])
    lines.extend(f"- {question}" for question in questions)
    lines.extend([""])
    return "\n".join(lines)


def main() -> None:
    if not INPUT_PATH.exists():
        raise SystemExit(f"입력 파일이 없습니다: {INPUT_PATH}")

    raw_text = INPUT_PATH.read_text(encoding="utf-8")
    note = build_note(raw_text)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(note, encoding="utf-8")
    print(f"공부 노트를 만들었습니다: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
