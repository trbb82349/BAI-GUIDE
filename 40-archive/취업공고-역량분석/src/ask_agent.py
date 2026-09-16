"""
지금까지 모은 취업공고 분석 결과(업종 분포 / 업종별 요구 기술 / 성장 전망 리서치)에 대해
터미널에서 자연어 비슷하게 물어보면 답해주는 아주 단순한 규칙 기반(키워드 매칭) Q&A 에이전트.

- LLM API 키가 없어도 바로 쓸 수 있도록, 지금은 키워드 매칭 + 미리 계산된 데이터로만 답한다.
  나중에 API 키가 생기면 answer() 함수 안에서 (검색된 데이터 + 질문)을 LLM에 넘겨
  자연스러운 문장으로 바꿔주는 식으로 확장하면 된다.
- 질문/답변을 전부 notes/agent_qa_log.csv에 기록한다. 지금은 나 혼자 테스트하는 로그지만,
  나중에 동아리 친구들이 써보기 시작하면 이 로그 자체가 "실제 사용자가 뭘 궁금해하는지"를
  보여주는 데이터가 된다 (교수님이 말씀하신 '실사용자 데이터 분석'의 씨앗).
"""

import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from build_dashboard import GROWTH_OUTLOOK, find_latest, load_domain_rows

# Windows 콘솔은 기본적으로 cp949를 쓸 때가 있어서, 파이프 입력/한글 질문이 깨지지 않도록
# 표준입출력 인코딩을 명시적으로 UTF-8로 고정한다.
for _stream in (sys.stdin, sys.stdout):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = PROJECT_ROOT / "notes"
LOG_PATH = NOTES_DIR / "agent_qa_log.csv"

DOMAIN_ALIASES = {
    "모빌리티/자율주행/로보틱스": ["모빌리티", "자율주행", "로봇", "로보틱스"],
    "제조/스마트팩토리": ["제조", "스마트팩토리", "공장"],
    "헬스케어/제약/바이오": ["헬스케어", "의료", "바이오", "제약", "병원"],
    "IT서비스/플랫폼": ["it서비스", "플랫폼", "소프트웨어"],
    "게임": ["게임"],
    "교육": ["교육", "에듀"],
    "미디어/콘텐츠": ["미디어", "콘텐츠"],
    "금융/핀테크": ["금융", "핀테크", "은행"],
    "커머스/유통": ["커머스", "이커머스", "유통", "쇼핑"],
    "기타": ["기타"],
}
SKILL_KEYWORDS = ["스킬", "기술", "언어", "툴", "도구"]
OUTLOOK_KEYWORDS = ["전망", "성장", "미래", "유망"]
COUNT_KEYWORDS = ["몇 건", "몇건", "전체", "현황", "얼마나"]
HELP_KEYWORDS = ["도움말", "help", "사용법"]


def find_domain(question: str) -> str | None:
    q = question.lower()
    for domain, aliases in DOMAIN_ALIASES.items():
        if any(alias in q for alias in aliases):
            return domain
    return None


def load_data() -> tuple[Counter, dict[str, list[tuple[str, int, float]]]]:
    domain_csv = find_latest("*_domain.csv", exclude_substr="skills_by_domain")
    skills_csv = find_latest("*_skills_by_domain.csv")

    rows = load_domain_rows(domain_csv) if domain_csv else []
    domain_counts = Counter(r.get("domain", "기타") or "기타" for r in rows)

    skills_by_domain: dict[str, list[tuple[str, int, float]]] = defaultdict(list)
    if skills_csv:
        with skills_csv.open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                skills_by_domain[row["domain"]].append(
                    (row["skill"], int(row["skill_count"]), float(row["skill_pct_in_domain"]))
                )
    return domain_counts, skills_by_domain


def answer(question: str, domain_counts: Counter, skills_by_domain: dict) -> str:
    q = question.strip()
    total = sum(domain_counts.values())

    if not q:
        return "질문을 입력해주세요."

    if any(k in q for k in HELP_KEYWORDS):
        return (
            "이렇게 물어보세요 (예시):\n"
            "  - '헬스케어 스킬 알려줘'   -> 업종별 요구 기술 TOP5\n"
            "  - '금융 전망 어때'         -> 성장 전망 리서치 결과\n"
            "  - '모빌리티'               -> 업종 개요 (건수+기술+전망)\n"
            "  - '전체 현황'              -> 전체 수집 현황 요약\n"
            "종료하려면 '종료'를 입력하세요."
        )

    domain = find_domain(q)

    if domain is None:
        if any(k in q for k in COUNT_KEYWORDS):
            top_domain, top_count = domain_counts.most_common(1)[0]
            return (
                f"지금까지 총 {total}건의 잡코리아 AI잡스 공고를 모았고, {len(domain_counts)}개 "
                f"업종으로 분류했습니다. 가장 공고가 많은 업종은 '{top_domain}'({top_count}건)입니다."
            )
        return "무슨 뜻인지 잘 모르겠어요. '도움말'을 입력하면 사용법을 알려드릴게요."

    count = domain_counts.get(domain, 0)
    pct = round(count / total * 100, 1) if total else 0
    wants_skill = any(k in q for k in SKILL_KEYWORDS)
    wants_outlook = any(k in q for k in OUTLOOK_KEYWORDS)
    show_all = not (wants_skill or wants_outlook)

    parts = [f"[{domain}] 공고 {count}건 (전체의 {pct}%)"]

    if wants_skill or show_all:
        top_skills = skills_by_domain.get(domain, [])[:5]
        if top_skills:
            skill_text = ", ".join(f"{s}({p}%)" for s, _, p in top_skills)
            parts.append(f"요구 기술 TOP5: {skill_text}")
        else:
            parts.append("이 업종은 수집된 기술 스택 정보가 없습니다.")

    if wants_outlook or show_all:
        outlook = next((row for row in GROWTH_OUTLOOK if row[0] == domain), None)
        if outlook:
            _, level, reason = outlook
            parts.append(f"성장 전망: {level} — {reason}")
        else:
            parts.append("이 업종은 아직 성장 전망을 따로 조사하지 않았습니다.")

    return "\n".join(parts)


def log_qa(question: str, response: str) -> None:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    is_new = not LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp", "question", "answer"])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            question,
            response.replace("\n", " / "),
        ])


def main() -> None:
    domain_counts, skills_by_domain = load_data()
    if not domain_counts:
        print("output/ 폴더에 분석 결과 CSV가 없습니다. classify_domain.py를 먼저 실행하세요.")
        return

    print("취업공고 분석 Q&A 에이전트 (종료하려면 '종료' 입력)")
    print("사용법을 모르면 '도움말'을 입력하세요.\n")

    while True:
        try:
            question = input("질문> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question in ("종료", "quit", "exit"):
            break
        response = answer(question, domain_counts, skills_by_domain)
        print(response, "\n")
        log_qa(question, response)

    print(f"\n대화 기록 저장 위치: {LOG_PATH}")


if __name__ == "__main__":
    main()
