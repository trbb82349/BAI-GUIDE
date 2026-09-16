from __future__ import annotations

import argparse
import csv
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FEEDS = PROJECT_ROOT / "input" / "korean-news-feeds.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "korean-news-report.md"
USER_AGENT = "BAI-daily-news-summary/1.0"
KST = ZoneInfo("Asia/Seoul")


@dataclass(frozen=True)
class Feed:
    name: str
    category: str
    url: str


@dataclass(frozen=True)
class NewsItem:
    title: str
    source: str
    category: str
    summary: str
    url: str
    published_at: datetime | None


def read_feeds(path: Path) -> list[Feed]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    required_fields = {"name", "category", "url"}
    if not rows:
        raise ValueError(f"RSS 목록이 비어 있습니다: {path}")

    missing = required_fields - set(rows[0].keys())
    if missing:
        raise ValueError(f"RSS 목록에 필요한 열이 없습니다: {', '.join(sorted(missing))}")

    return [Feed(row["name"].strip(), row["category"].strip(), row["url"].strip()) for row in rows]


def fetch_text(url: str, timeout: int) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def clean_text(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_date(value: str) -> datetime | None:
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=KST)
    return parsed.astimezone(KST)


def child_text(element: ET.Element, tag: str) -> str:
    found = element.find(tag)
    return clean_text(found.text if found is not None and found.text else "")


def normalize_title(title: str, source: str) -> str:
    title = clean_text(title)
    if source:
        title = re.sub(rf"\s+[-|]\s+{re.escape(source)}$", "", title)
    return title.strip()


def parse_rss(xml_text: str, feed: Feed) -> list[NewsItem]:
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")
    parsed_items: list[NewsItem] = []

    for item in items:
        raw_title = child_text(item, "title")
        link = child_text(item, "link")
        description = child_text(item, "description")
        pub_date = child_text(item, "pubDate")
        source = child_text(item, "source") or feed.name
        title = normalize_title(raw_title, source)

        if not title or not link:
            continue

        parsed_items.append(
            NewsItem(
                title=title,
                source=source,
                category=feed.category,
                summary=summarize_description(title, description),
                url=link,
                published_at=parse_date(pub_date),
            )
        )

    return parsed_items


def summarize_description(title: str, description: str) -> str:
    text = description or title
    text = re.sub(r"관련뉴스|더보기|전체기사|무단전재.*", "", text)
    text = clean_text(text)

    if not text or title in text or len(text) > 260:
        return f"{title} 관련 소식입니다. 자세한 내용은 원문 링크에서 확인하세요."

    sentences = re.split(r"(?<=[.!?。])\s+|(?<=[다요죠음됨임])\s+", text)
    short = " ".join(sentence.strip() for sentence in sentences[:2] if sentence.strip())
    short = short or text

    if len(short) > 180:
        short = short[:177].rstrip() + "..."

    return short


def collect_news(feeds: list[Feed], per_feed: int, timeout: int) -> tuple[list[NewsItem], list[str]]:
    collected: list[NewsItem] = []
    errors: list[str] = []

    for feed in feeds:
        try:
            xml_text = fetch_text(feed.url, timeout)
            collected.extend(parse_rss(xml_text, feed)[:per_feed])
        except Exception as exc:
            errors.append(f"{feed.name}: {exc}")

    return deduplicate(collected), errors


def deduplicate(items: list[NewsItem]) -> list[NewsItem]:
    seen: set[str] = set()
    unique_items: list[NewsItem] = []

    for item in items:
        key = re.sub(r"\W+", "", item.title.lower())
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(item)

    return unique_items


def sort_news(items: list[NewsItem]) -> list[NewsItem]:
    oldest = datetime(1970, 1, 1, tzinfo=KST)
    return sorted(items, key=lambda item: item.published_at or oldest, reverse=True)


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "시간 정보 없음"
    return value.strftime("%Y-%m-%d %H:%M")


def render_report(items: list[NewsItem], errors: list[str], limit: int) -> str:
    now = datetime.now(KST)
    selected = sort_news(items)[:limit]
    category_counts = Counter(item.category for item in items)
    source_counts = Counter(item.source for item in selected)

    lines = [
        "# 한국 뉴스 요약 보고서",
        "",
        f"- 작성 시각: {now.strftime('%Y-%m-%d %H:%M')} KST",
        f"- 수집 기사: {len(items)}개",
        f"- 보고서 포함: {len(selected)}개",
        "",
        "## 한눈에 보기",
        "",
    ]

    if not selected:
        lines.extend(
            [
                "수집된 뉴스가 없습니다. RSS 주소나 인터넷 연결을 확인하세요.",
                "",
            ]
        )
    else:
        for index, item in enumerate(selected, start=1):
            lines.append(f"{index}. [{item.category}] {item.title} - {item.source}")
        lines.append("")

    lines.extend(["## 주요 뉴스 요약", ""])

    for index, item in enumerate(selected, start=1):
        lines.extend(
            [
                f"### {index}. {item.title}",
                "",
                f"- 분야: {item.category}",
                f"- 출처: {item.source}",
                f"- 게시 시각: {format_datetime(item.published_at)}",
                f"- 링크: {item.url}",
                "",
                f"요약: {item.summary}",
                "",
            ]
        )

    lines.extend(["## 수집 현황", ""])
    if category_counts:
        lines.append("분야별 기사 수:")
        for category, count in sorted(category_counts.items()):
            lines.append(f"- {category}: {count}개")
        lines.append("")

    if source_counts:
        lines.append("보고서에 포함된 출처:")
        for source, count in sorted(source_counts.items()):
            lines.append(f"- {source}: {count}개")
        lines.append("")

    if errors:
        lines.extend(["## 수집 실패", ""])
        for error in errors:
            lines.append(f"- {error}")
        lines.append("")

    lines.extend(
        [
            "## 다음 자동화 단계",
            "",
            "- RSS 주소를 원하는 언론사나 주제로 바꾸기",
            "- 보고서 파일을 이메일 본문으로 보내기",
            "- Windows 작업 스케줄러로 매일 실행하기",
            "",
        ]
    )

    return "\n".join(lines)


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="한국 뉴스 RSS를 읽어 한글 요약 보고서를 만듭니다.")
    parser.add_argument("--feeds", type=Path, default=DEFAULT_FEEDS, help="RSS 목록 CSV 경로")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="보고서 Markdown 저장 경로")
    parser.add_argument("--limit", type=int, default=10, help="보고서에 넣을 기사 수")
    parser.add_argument("--per-feed", type=int, default=8, help="RSS 하나당 가져올 기사 수")
    parser.add_argument("--timeout", type=int, default=15, help="RSS 요청 제한 시간")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    feeds = read_feeds(args.feeds)
    items, errors = collect_news(feeds, args.per_feed, args.timeout)
    report = render_report(items, errors, args.limit)
    write_report(args.output, report)
    print(f"보고서를 만들었습니다: {args.output}")
    if errors:
        print(f"일부 RSS 수집 실패: {len(errors)}건")


if __name__ == "__main__":
    main()
