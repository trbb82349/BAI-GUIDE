"""직무 카테고리 간 키워드 유사도를 계산해서 지도 시각화용 데이터를 만든다.

방법:
    1. 카테고리별로 소속 역할들의 '하는 일 + 필요지식 + 필요기술' 텍스트를 합친다.
    2. 텍스트에서 한글/영문 키워드 토큰을 뽑는다 (형태소 분석기가 없어서 간단한
       정규식 토큰화를 쓴다 - 조사가 안 떨어져 나가는 등 완벽하지 않지만,
       "Tableau", "Python", "AI", "마케팅" 같은 핵심 키워드는 잘 잡힌다).
    3. TF-IDF로 카테고리별 키워드 벡터를 만들고, 코사인 유사도로 카테고리 간
       거리를 계산한다. (raw frequency 대신 TF-IDF를 쓰는 이유: "의사소통능력"
       처럼 모든 직무에 공통으로 나오는 단어가 유사도를 왜곡하지 않도록 하기 위함)

실행: python src/build_similarity.py
출력: output/job_map_data.json (지도 HTML이 그대로 읽어서 쓰는 데이터)
"""

import json
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 유사도 계산에서 의미가 거의 없는 범용 직무 역량 단어. 모든 공공기관 채용공고에
# 상투적으로 들어가는 표현이라 미리 제거한다 (그래도 TF-IDF가 어느 정도 걸러주지만,
# 카테고리가 5개뿐이라 IDF 효과가 약해 명시적으로 한 번 더 제거).
STOPWORDS = {
    "의사소통능력", "문제해결능력", "대인관계능력", "자원관리능력", "자기개발능력",
    "정보능력", "기술능력", "직업윤리", "수리능력", "조직이해능력", "자기계발능력",
    "능력", "지식", "이해", "업무", "관련", "수행", "기획", "관리", "분석",
}

TOKEN_RE = re.compile(r"[가-힣]{2,}|[A-Za-z][A-Za-z0-9+.#]{1,}")


def tokenize(text: str) -> list[str]:
    tokens = TOKEN_RE.findall(text)
    return [t for t in tokens if t not in STOPWORDS]


def build_category_texts(roles: list[dict]) -> dict[str, list[dict]]:
    by_category: dict[str, list[dict]] = {}
    for role in roles:
        by_category.setdefault(role["category"], []).append(role)
    return by_category


def tfidf_vectors(category_tokens: dict[str, list[str]]) -> dict[str, dict[str, float]]:
    categories = list(category_tokens.keys())
    doc_freq = Counter()
    for cat, tokens in category_tokens.items():
        for term in set(tokens):
            doc_freq[term] += 1

    n_docs = len(categories)
    vectors = {}
    for cat, tokens in category_tokens.items():
        tf = Counter(tokens)
        total = sum(tf.values()) or 1
        vec = {}
        for term, count in tf.items():
            idf = math.log((n_docs + 1) / (doc_freq[term] + 1)) + 1
            vec[term] = (count / total) * idf
        vectors[cat] = vec
    return vectors


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def top_terms(vec: dict[str, float], n: int = 8) -> list[str]:
    return [t for t, _ in sorted(vec.items(), key=lambda kv: kv[1], reverse=True)[:n]]


def main() -> None:
    roles = json.loads((ROOT / "output" / "job_roles_final.json").read_text(encoding="utf-8"))
    by_category = build_category_texts(roles)

    # 지도에 항상 5개 카테고리 노드를 다 보여준다 (역할이 0개인 카테고리도 "데이터 없음" 노드로 표시)
    all_categories = ["데이터분석", "BI", "CRM분석", "마케팅분석", "AI·ML"]

    category_tokens = {}
    for cat in all_categories:
        text = " ".join(
            " ".join([r.get("duties", ""), r.get("knowledge", ""), r.get("skills", "")])
            for r in by_category.get(cat, [])
        )
        category_tokens[cat] = tokenize(text)

    vectors = tfidf_vectors(category_tokens)

    nodes = []
    for cat in all_categories:
        role_count = len(by_category.get(cat, []))
        nodes.append(
            {
                "id": cat,
                "role_count": role_count,
                "top_terms": top_terms(vectors[cat]) if role_count else [],
                "roles": [
                    {
                        "org": r.get("org", ""),
                        "title": r.get("title", ""),
                        "role_name": r.get("role_name", ""),
                        "duties": r.get("duties", ""),
                        "knowledge": r.get("knowledge", ""),
                        "skills": r.get("skills", ""),
                    }
                    for r in by_category.get(cat, [])
                ],
            }
        )

    edges = []
    for i, cat_a in enumerate(all_categories):
        for cat_b in all_categories[i + 1 :]:
            sim = cosine_similarity(vectors[cat_a], vectors[cat_b])
            if sim > 0.02:  # 너무 약한 연결은 지도에서 생략
                edges.append({"source": cat_a, "target": cat_b, "similarity": round(sim, 4)})

    edges.sort(key=lambda e: e["similarity"], reverse=True)

    data = {"nodes": nodes, "edges": edges}
    out_path = ROOT / "output" / "job_map_data.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print("카테고리별 상위 키워드:")
    for node in nodes:
        print(f"  [{node['id']}] ({node['role_count']}개 역할) {', '.join(node['top_terms']) or '(데이터 없음)'}")
    print("\n카테고리 간 유사도 (상위):")
    for e in edges:
        print(f"  {e['source']} <-> {e['target']}: {e['similarity']}")
    print(f"\n저장: {out_path}")


if __name__ == "__main__":
    main()
