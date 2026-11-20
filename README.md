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

## 카드에 보이는 것

- **무엇인가** — `data/ko.json`의 `what`. 개발 용어를 모르는 사람을 위해 풀어 쓴 설명(저장소 소개 글 기준, 써 본 평가 아님).
- **올린 곳** — 저장소를 소유한 계정의 표시 이름과 구분.
  - 공식: 그 제품·규격을 만든 회사·단체가 직접 올린 저장소 (`data/seeds.json`의 `official`)
  - 단체 / 개인: GitHub 계정 종류
  - ✓ GitHub 인증: GitHub가 그 조직의 도메인을 확인했다는 표시. 없다고 가짜라는 뜻은 아님
  - 계정 정보는 GitHub API로 받아 `data/owners.json`에 30일 저장
- 한 줄 평 · 장점 · 주의 · 종류 · 난이도 · 라이선스 · 갱신일 · 점수 내역 · 설치 명령

## 동작

```
data/seeds.json ──→ scripts/collect.py ──→ data/skills.json, data/diff.json
                     (GitHub API; 불가 시 data/snapshot.json)
                                    └──→ scripts/build.py ──→ marketplace.json · docs/ · reports/
                                         (화면 틀: scripts/template.html)
```

- 스케줄: `.github/workflows/weekly.yml` — 매주 월요일 07:17 KST, 수동 실행 가능
- 신규 저장소 추가: `data/seeds.json`의 `repos`에 한 줄 추가
- 자동 발견: `discover_queries` (토큰 있을 때만, `data/diff.json`의 `candidates`에 기록 → 사람이 seeds로 승격)

## 로컬 실행

```
pip install requests
python scripts/collect.py && python scripts/build.py

# 별 수·갱신일은 그대로 두고 한글 설명(ko.json)과 올린 곳 정보만 다시 반영
python scripts/collect.py --meta-only && python scripts/build.py
```

## 하지 않는 것

자동 로그인, 무단 크롤링, 블로그 자동 게시. 설치 전 각 저장소의 README와 스크립트를 직접 확인하세요.

## AI 활용 실험실 홈페이지 (2026-11-21)
- 홈: docs/index.html, 기존 자동 수집 카탈로그: docs/catalog.html
- 활용법 / 실험·비교 / 스킬 라이브러리 / AI 소식 / 소개 페이지 추가
- 첫 실험: docs/experiment-001.html (실행 전 설계서)
- 스킬 상세: docs/skill-clip.html (수동 적용용 v0.1 초안)
- 실험 기록 및 스킬 문서: docs/downloads/
- 생성 코드: scripts/build_lab.py. 기존 scripts/build.py가 카탈로그와 새 페이지를 함께 재생성합니다.
- 주간 추천: docs/picks.html. 매주 새로 올라온 스킬 가운데 시험해 볼 만한 것을 5개쯤 고릅니다. 자료는 data/picks.json(양식: data/picks.README.md)이고, scripts/build_lab.py가 읽어 페이지를 만듭니다. 문서만 보고 고른 것이며 직접 돌려 본 결과가 아닙니다.
- 검수: python scripts/check_site.py
- 실측 영상·점수·성과는 아직 없으며 준비 상태로 표시합니다.
- 블로그만 연결됨. 인스타그램과 JEJUINSIDER는 정확한 URL 확인 후 연결합니다.
