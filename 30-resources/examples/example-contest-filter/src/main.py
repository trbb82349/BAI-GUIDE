from __future__ import annotations

import csv
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"


@dataclass
class Contest:
    source: str
    title: str
    organizer: str
    deadline: str
    category: str
    description: str
    url: str
    score: int = 0
    matched_keywords: str = ""
    review_reason: str = ""


class ContestHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.current_field: str | None = None
        self.current_link: str = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag == "article" and attr.get("class") == "contest":
            self.current = {"source": attr.get("data-source", "html")}
            self.current_link = ""
        elif self.current is not None and tag == "h2":
            self.current_field = "title"
        elif self.current is not None and tag == "p":
            field_map = {
                "organizer": "organizer",
                "deadline": "deadline",
                "category": "category",
                "description": "description",
            }
            self.current_field = field_map.get(attr.get("class", ""))
        elif self.current is not None and tag == "a":
            self.current_link = attr.get("href", "") or ""

    def handle_data(self, data: str) -> None:
        if self.current is None or self.current_field is None:
            return
        text = data.strip()
        if text:
            previous = self.current.get(self.current_field, "")
            self.current[self.current_field] = f"{previous} {text}".strip()

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h2", "p"}:
            self.current_field = None
        if tag == "article" and self.current is not None:
            self.current["url"] = self.current_link
            self.items.append(self.current)
            self.current = None
            self.current_field = None


def read_keyword_rules() -> tuple[dict[str, int], dict[str, int]]:
    include: dict[str, int] = {}
    exclude: dict[str, int] = {}
    with (INPUT_DIR / "keywords.csv").open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            target = include if row["type"] == "include" else exclude
            target[row["keyword"]] = int(row["weight"])
    return include, exclude


def collect_from_csv() -> list[Contest]:
    with (INPUT_DIR / "sample-contests.csv").open("r", encoding="utf-8-sig", newline="") as f:
        return [Contest(**row) for row in csv.DictReader(f)]


def collect_from_html() -> list[Contest]:
    parser = ContestHTMLParser()
    parser.feed((INPUT_DIR / "sample-site.html").read_text(encoding="utf-8"))
    return [Contest(**item) for item in parser.items]


def score_contests(contests: list[Contest], include: dict[str, int], exclude: dict[str, int]) -> list[Contest]:
    scored: list[Contest] = []
    for item in contests:
        text = f"{item.title} {item.category} {item.description}"
        included = [keyword for keyword in include if keyword.lower() in text.lower()]
        excluded = [keyword for keyword in exclude if keyword.lower() in text.lower()]
        item.score = sum(include[keyword] for keyword in included) - sum(exclude[keyword] for keyword in excluded)
        item.matched_keywords = ", ".join(included + [f"제외:{keyword}" for keyword in excluded])
        if excluded:
            item.review_reason = "제외 키워드 포함"
        elif item.score >= 3:
            item.review_reason = "우선 검토"
        elif item.score > 0:
            item.review_reason = "보류 검토"
        else:
            item.review_reason = "관련 키워드 부족"
        scored.append(item)
    return scored


def dedupe(contests: list[Contest]) -> list[Contest]:
    seen: set[str] = set()
    unique: list[Contest] = []
    for item in contests:
        key = item.url or item.title
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def export_csv(path: Path, contests: list[Contest]) -> None:
    fields = list(Contest.__dataclass_fields__.keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in contests:
            writer.writerow(item.__dict__)


def export_markdown(path: Path, contests: list[Contest]) -> None:
    lines = [
        "# 공모전 필터 결과",
        "",
        f"- 필터 통과: {len(contests)}건",
        "- 기준: 점수 3점 이상, 제외 키워드가 있으면 보류 또는 제외 검토",
        "",
        "| 점수 | 대회명 | 주최 | 마감 | 근거 | 링크 |",
        "|---:|---|---|---|---|---|",
    ]
    for item in contests:
        lines.append(
            f"| {item.score} | {escape_cell(item.title)} | {escape_cell(item.organizer)} | "
            f"{item.deadline} | {escape_cell(item.matched_keywords)} | [상세]({item.url}) |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_review_queue(path: Path, contests: list[Contest]) -> None:
    lines = [
        "# Codex 로컬 검수 큐",
        "",
        "아래 후보를 읽고 각 항목을 `유지`, `보류`, `제외` 중 하나로 판단합니다.",
        "판단할 때는 제목만 보지 말고 설명, 마감일, 키워드 근거를 함께 확인합니다.",
        "",
    ]
    for index, item in enumerate(contests, 1):
        lines.extend(
            [
                f"## {index}. {item.title}",
                "",
                f"- 주최: {item.organizer}",
                f"- 마감: {item.deadline}",
                f"- 분류: {item.category}",
                f"- 점수: {item.score}",
                f"- 매칭 근거: {item.matched_keywords or '없음'}",
                f"- 설명: {item.description}",
                f"- 링크: {item.url}",
                "",
                "검수 메모:",
                "- 판단:",
                "- 이유:",
                "- 추가 확인:",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def export_summary_prompt(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "# Codex 요약 요청문",
                "",
                "다음 파일을 함께 읽어줘.",
                "",
                "- `output/contests_filtered.csv`",
                "- `output/review_queue.md`",
                "",
                "요청:",
                "1. 유지할 후보 3개를 골라줘.",
                "2. 각 후보가 데이터 분석, 자동화, 시각화 학습에 왜 맞는지 써줘.",
                "3. 근거가 부족한 후보는 제외하지 말고 보류 사유와 추가 확인 질문을 남겨줘.",
                "4. 최종 공유용 Markdown 요약을 만들어줘.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def export_notion_preview(path: Path, contests: list[Contest]) -> None:
    lines = [
        "# Notion 업로드 전 검토용 초안",
        "",
        "이 파일은 외부 서비스에 쓰기 전에 사람이 확인하는 중간 산출물입니다.",
        "실제 업로드는 기본 실행에 포함하지 않습니다.",
        "",
    ]
    for item in contests:
        lines.extend(
            [
                f"## {item.title}",
                "",
                f"- 상태: 검수 대기",
                f"- 주최: {item.organizer}",
                f"- 마감: {item.deadline}",
                f"- 점수: {item.score}",
                f"- URL: {item.url}",
                f"- 요약: {item.description}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    include, exclude = read_keyword_rules()
    raw = dedupe(collect_from_csv() + collect_from_html())
    scored = score_contests(raw, include, exclude)
    filtered = sorted(
        [item for item in scored if item.score >= 3 and not item.review_reason.startswith("제외")],
        key=lambda item: (-item.score, item.deadline, item.title),
    )

    export_csv(OUTPUT_DIR / "contests_raw.csv", scored)
    export_csv(OUTPUT_DIR / "contests_filtered.csv", filtered)
    export_markdown(OUTPUT_DIR / "contests_filtered.md", filtered)
    export_review_queue(OUTPUT_DIR / "review_queue.md", filtered)
    export_summary_prompt(OUTPUT_DIR / "summary_prompt.md")
    export_notion_preview(OUTPUT_DIR / "notion_export.md", filtered)

    print(f"수집: {len(raw)}건")
    print(f"필터 통과: {len(filtered)}건")
    print(f"결과 폴더: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
