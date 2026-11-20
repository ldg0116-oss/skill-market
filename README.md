# skill-market

GitHub의 AI 스킬·MCP 서버·에이전트 저장소를 **주 1회 자동 수집 → 검증 → 5개 카테고리 분류**하고, Claude Code 마켓플레이스와 웹 카탈로그로 내놓는 도구.

- 카탈로그: `docs/index.html` (GitHub Pages / Cloudflare Pages 배포용)
- 마켓플레이스: `.claude-plugin/marketplace.json`
- 주간 리포트: `reports/latest.md` (블로그 글 초안 소재)

## Claude Code에서 쓰기

```
/plugin marketplace add ldg0116-oss/skill-market
/plugin install <이름>@skill-market
```

## 카테고리

코딩 · 기획·문서 · 마케팅·콘텐츠 · 자동화 · 비개발자 — 카테고리별 상위 5개에 "추천" 표시.

## 점수 (100)

| 항목 | 배점 | 산출 |
| --- | --- | --- |
| 실용성 | 25 | ⭐ 기반 자동추정 (사람 검증 전 참고용) |
| 설치 편의 | 15 | 유형별 (큐레이션 15 … 자동화 플랫폼 6) |
| 기능 완성도 | 20 | ⭐ 기반 자동추정 |
| 유지보수 | 15 | 최근 push: 7일 15 · 30일 12 · 90일 8 · 그 이상 3 |
| 비용 | 10 | 유료 의존 알려진 경우 7 |
| 보안·신뢰 | 15 | 허용 라이선스 8 + 공식 저장소 7 |

## 동작

```
data/seeds.json ──→ scripts/collect.py ──→ data/skills.json, data/diff.json
                     (GitHub API; 불가 시 data/snapshot.json)
                                    └──→ scripts/build.py ──→ marketplace.json · docs/ · reports/
```

- 스케줄: `.github/workflows/weekly.yml` — 매주 월요일 07:17 KST, 수동 실행 가능
- 신규 저장소 추가: `data/seeds.json`의 `repos`에 한 줄 추가
- 자동 발견: `discover_queries` (토큰 있을 때만, `data/diff.json`의 `candidates`에 기록 → 사람이 seeds로 승격)

## 로컬 실행

```
pip install requests
python scripts/collect.py && python scripts/build.py
```

## 하지 않는 것

자동 로그인, 무단 크롤링, 블로그 자동 게시. 설치 전 각 저장소의 README와 스크립트를 직접 확인하세요.
