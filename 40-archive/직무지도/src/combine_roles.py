"""자동 추출(job_roles.json) + 수동 검토(manual_roles.json)를 하나로 합쳐
직무지도 유사도 계산에 쓸 최종 데이터셋을 만든다.

자동 추출 결과 중에는 같은 PDF 안에 목표 직무와 무관한 역할이 섞여 있는 경우가
있다 (예: 발전소 채용 PDF에 AI전문가와 함께 들어있는 고압가스안전관리원).
그런 무관한 역할과, 텍스트가 비어서 유사도 계산에 쓸 수 없는 역할은 제외한다.

실행:
    python src/combine_roles.py

출력:
    output/job_roles_final.json
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 자동 추출은 됐지만 목표 직무와 무관해서 최종 데이터셋에서 제외하는 역할.
# (같은 채용 PDF 안에 여러 직군이 섞여 있어서 자동으로는 걸러지지 않음)
EXCLUDE_ROLE_NAMES = {"발전기술원, 수질관리기술원", "고압가스안전관리원"}


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def normalize(rec: dict, source: str) -> dict:
    return {
        "category": rec.get("category") or rec.get("source_category"),
        "org": rec.get("source_org"),
        "title": rec.get("source_title"),
        "role_name": rec["role_name"],
        "duties": rec.get("duties", ""),
        "knowledge": rec.get("knowledge", ""),
        "skills": rec.get("skills", ""),
        "extraction": source,
    }


def main() -> None:
    auto = load(ROOT / "output" / "job_roles.json")
    manual = load(ROOT / "input" / "manual_roles.json")

    combined = []
    for rec in auto:
        if rec["role_name"] in EXCLUDE_ROLE_NAMES:
            continue
        norm = normalize(rec, "auto")
        if not (norm["duties"] or norm["knowledge"] or norm["skills"]):
            continue  # 텍스트를 못 뽑은 역할(추출 실패)은 유사도 계산에 못 쓰니 제외
        combined.append(norm)

    for rec in manual:
        combined.append(normalize(rec, "manual"))

    by_category: dict[str, int] = {}
    for rec in combined:
        by_category[rec["category"]] = by_category.get(rec["category"], 0) + 1

    out_path = ROOT / "output" / "job_roles_final.json"
    out_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"최종 데이터셋: {len(combined)}개 역할")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat}: {count}개")
    print(f"저장: {out_path}")


if __name__ == "__main__":
    main()
