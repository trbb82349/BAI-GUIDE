# 로컬 검수 흐름

1. `python src/main.py`를 실행합니다.
2. `output/contests_filtered.md`로 빠르게 후보를 읽습니다.
3. `output/review_queue.md`를 Codex에게 주고 유지, 보류, 제외 판단을 요청합니다.
4. 검수 결과를 반영한 뒤 `output/notion_export.md`를 마지막으로 확인합니다.
5. 외부 서비스 쓰기는 별도 개인 프로젝트에서 구현합니다.

핵심은 자동화가 모든 결정을 대신하지 않는다는 점입니다. 수집과 필터는 스크립트가 맡고, 애매한 판단은 사람이 읽을 수 있는 Markdown으로 남깁니다.
