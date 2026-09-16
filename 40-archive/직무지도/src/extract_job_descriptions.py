"""공고에 첨부된 '직무기술서' PDF를 내려받아 역할별 직무 텍스트를 뽑는다.

알리오 공고 하나에는 보통 '【 NCS기반 채용 직무 설명자료 : 역할명 】' 형식의
블록이 역할 수만큼 여러 개 들어있다. 블록 단위로 나눠서 분류체계(NCS)와
직무수행내용/필요지식/필요기술 텍스트를 따로 뽑는다.

실행 순서: scrape_postings.py 를 먼저 실행해 output/postings.json 을 만든 뒤 실행한다.

    python src/extract_job_descriptions.py

출력:
    input/job_description_pdfs/  - 내려받은 원본 PDF
    output/job_roles.json        - 역할 단위로 쪼갠 직무 텍스트
"""

import json
import re
import time
from pathlib import Path

import requests
from pypdf import PdfReader

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
REQUEST_DELAY = 0.5

ROOT = Path(__file__).resolve().parent.parent
POSTINGS_JSON = ROOT / "output" / "postings.json"
PDF_DIR = ROOT / "input" / "job_description_pdfs"
OUTPUT_JSON = ROOT / "output" / "job_roles.json"

# 기관마다 직무기술서 양식이 달라 표기가 조금씩 다르다. 확인된 두 가지 패턴만 자동 인식한다.
#   패턴1: 【NCS기반 채용 직무 설명자료 : 역할명】 / [NCS기반 채용 직무설명자료 : 역할명]
#   패턴2: 【역할명 직무기술서】 (콜론 없이 역할명이 앞에 오는 형식)
# 둘 다 안 맞는 PDF는 자동 추출을 포기하고 output/unmatched_pdfs.json에 남겨 수동 검토로 넘긴다.
ROLE_HEADER_RE = re.compile(r"[【\[]\s*(?:NCS\s*기반\s*)?채용\s*직무\s*(?:설명자료|기술서)\s*[:：]\s*(.+?)\s*[】\]]")
ROLE_HEADER_FALLBACK_RE = re.compile(r"[【\[]\s*(.+?)\s*직무기술서\s*[】\]]")


def collect_pdf_attachments() -> list[dict]:
    """postings.json에서 '직무기술서' 필드가 .pdf인 첨부만 (fileNo, 소속 공고 정보)로 모은다."""
    postings = json.loads(POSTINGS_JSON.read_text(encoding="utf-8"))
    seen_file_no = set()
    attachments = []
    for rec in postings:
        for link in rec.get("attachments", {}).get("직무기술서", []):
            if not link["url"].endswith(".pdf") and ".pdf" not in link["name"].lower():
                continue
            match = re.search(r"fileNo=(\d+)", link["url"])
            if not match:
                continue
            file_no = match.group(1)
            if file_no in seen_file_no:
                continue
            seen_file_no.add(file_no)
            attachments.append(
                {
                    "file_no": file_no,
                    "url": link["url"],
                    "name": link["name"],
                    "source_idx": rec["idx"],
                    "source_category": rec["category"],
                    "source_title": rec["title"],
                    "source_org": rec["org"],
                }
            )
    return attachments


def download_pdf(url: str, dest: Path) -> bool:
    if dest.exists():
        return True
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200 or not resp.content.startswith(b"%PDF"):
        return False
    dest.write_bytes(resp.content)
    return True


def split_into_roles(pdf_text: str) -> list[dict]:
    """직무기술서 헤더 기준으로 텍스트를 역할 블록으로 나눈다. 알려진 두 패턴을 순서대로 시도한다."""
    headers = list(ROLE_HEADER_RE.finditer(pdf_text))
    if not headers:
        headers = list(ROLE_HEADER_FALLBACK_RE.finditer(pdf_text))
    if not headers:
        return []

    roles = []
    for i, m in enumerate(headers):
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(pdf_text)
        block = pdf_text[start:end]
        roles.append({"role_name": m.group(1).strip(), "block_text": block.strip()})
    return roles


def extract_section(block_text: str, section_name: str, next_section_names: list[str]) -> str:
    """block_text 안에서 '직무수행내용', '필요지식', '필요기술' 같은 항목의 본문만 뽑는다."""
    pattern = re.escape(section_name) + r"\s*(.+?)(?=" + "|".join(re.escape(n) for n in next_section_names) + "|$)"
    m = re.search(pattern, block_text, re.DOTALL)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip()


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    attachments = collect_pdf_attachments()
    print(f"직무기술서 PDF 첨부 {len(attachments)}건 발견 (중복 제거)")

    all_roles = []
    unmatched = []
    section_order = ["직무수행내용", "필요지식", "필요기술", "직무수행태도", "직업기초능력", "참고"]

    for att in attachments:
        dest = PDF_DIR / f"{att['file_no']}.pdf"
        ok = download_pdf(att["url"], dest)
        time.sleep(REQUEST_DELAY)
        if not ok:
            print(f"  다운로드 실패: {att['name']}")
            continue

        try:
            reader = PdfReader(str(dest))
            full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            print(f"  PDF 읽기 실패 ({att['name']}): {e}")
            continue

        roles = split_into_roles(full_text)
        if not roles:
            print(f"  형식 불일치(수동 검토 필요): {att['name']} ({att['file_no']}.pdf)")
            unmatched.append({**att, "pdf_path": str(dest.relative_to(ROOT))})
            continue

        for role in roles:
            duties = extract_section(role["block_text"], "직무수행내용", section_order[1:])
            knowledge = extract_section(role["block_text"], "필요지식", section_order[2:])
            skills = extract_section(role["block_text"], "필요기술", section_order[3:])
            all_roles.append(
                {
                    "source_idx": att["source_idx"],
                    "source_category": att["source_category"],
                    "source_title": att["source_title"],
                    "source_org": att["source_org"],
                    "role_name": role["role_name"],
                    "duties": duties,
                    "knowledge": knowledge,
                    "skills": skills,
                }
            )

        print(f"  {att['name']} -> 역할 {len(roles)}개 추출")

    OUTPUT_JSON.write_text(json.dumps(all_roles, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장: {OUTPUT_JSON} (자동 추출된 역할 {len(all_roles)}개)")

    unmatched_path = ROOT / "output" / "unmatched_pdfs.json"
    unmatched_path.write_text(json.dumps(unmatched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장: {unmatched_path} (수동 검토 대상 {len(unmatched)}건)")


if __name__ == "__main__":
    main()
