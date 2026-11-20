#!/usr/bin/env python3
"""GitHub AI 스킬·MCP·에이전트 저장소 수집 → data/skills.json

- data/seeds.json 의 repos 를 GitHub REST API 로 조회 (⭐, push, 라이선스, 설명, 토픽)
- discover_queries 로 신규 후보 검색 (GITHUB_TOKEN 있을 때만, 없으면 건너뜀)
- 100점 평가 (실용성25 설치편의15 완성도20 유지보수15 비용10 보안15) — 검증 가능한 항목만 자동, 나머지는 미검증(None)
- 5 카테고리 자동 분류: 코딩 / 기획·문서 / 마케팅·콘텐츠 / 자동화 / 비개발자
- 이전 skills.json 과 비교해 신규·변동을 data/diff.json 에 기록
"""
import json, os, re, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SEEDS = json.loads((DATA / "seeds.json").read_text(encoding="utf-8"))
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
HEAD = {"Accept": "application/vnd.github+json", "User-Agent": "skill-market-bot"}
if TOKEN:
    HEAD["Authorization"] = f"Bearer {TOKEN}"
API = "https://api.github.com"

ALLOWED_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "CC0-1.0", "MPL-2.0", "Unlicense", "CC-BY-4.0"}

CATEGORY_RULES = [
    ("비개발자", r"beginner|for-beginners|tutorial|course|non.?dev|입문|no.?code"),
    ("마케팅·콘텐츠", r"marketing|seo|content|social|brand|design|figma|video|instagram|youtube|blog|copy"),
    ("기획·문서", r"docx|pdf|pptx|xlsx|document|slides|spec|plan|product|prd|research|writing|notion"),
    ("자동화", r"mcp|automation|workflow|browser|playwright|n8n|server|integration|scrap"),
    ("코딩", r"code|coding|tdd|test|review|debug|refactor|engineer|dev|agent|subagent|cursor|copilot|codex|cli|skill"),
]
CATEGORIES = ["코딩", "기획·문서", "마케팅·콘텐츠", "자동화", "비개발자"]


def gh(url, params=None, retry=2):
    for i in range(retry + 1):
        r = requests.get(url, headers=HEAD, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        limited = r.headers.get("X-RateLimit-Remaining") == "0" or r.status_code == 429
        if limited and i < retry:
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = min(max(reset - time.time(), 5), 90)
            print(f"  rate-limit, {wait:.0f}s 대기", file=sys.stderr)
            time.sleep(wait)
            continue
        print(f"  {url} → {r.status_code}", file=sys.stderr)
        return None
    return None


def classify(text, hint=None):
    if hint and hint in CATEGORIES:
        return hint
    t = (text or "").lower()
    for cat, pat in CATEGORY_RULES:
        if re.search(pat, t):
            return cat
    return "코딩"


def difficulty(seed, repo):
    t = seed.get("type")
    if t in ("curation", "education", "tool"):
        return "입문"
    if seed.get("official") and t == "skill":
        return "입문"
    if t in ("host", "automation") or (repo.get("size", 0) > 200_000):
        return "고급" if t == "automation" else "중급"
    return "중급"


def score(seed, repo, days_since_push):
    """검증 가능한 항목만 점수화. 실용성·완성도는 미검증(None) 유지."""
    stars = repo.get("stargazers_count", 0)
    lic = (repo.get("license") or {}).get("spdx_id")
    s = {}
    # 유지보수 15: 최근 push
    s["유지보수"] = 15 if days_since_push <= 7 else 12 if days_since_push <= 30 else 8 if days_since_push <= 90 else 3
    # 설치편의 15: 유형 기반
    s["설치편의"] = {"curation": 15, "education": 14, "tool": 13, "skill": 12, "marketplace": 12, "mcp": 9, "agent": 10, "rules": 13, "host": 8, "automation": 6}.get(seed.get("type"), 9)
    # 비용 10: 알려진 유료 의존 없으면 10
    s["비용"] = 7 if seed.get("repo") in ("openai/codex", "upstash/context7") else 10
    # 보안 15: 라이선스 명확 + 공식
    s["보안"] = (8 if lic in ALLOWED_LICENSES else 3) + (7 if seed.get("official") else 4)
    # 실용성 25 / 완성도 20: ⭐ 로 근사 (상한), 사람 검증 전까지 '자동추정' 표기
    s["실용성(자동)"] = min(25, 10 + int(stars / 8000))
    s["완성도(자동)"] = min(20, 8 + int(stars / 10000))
    s["합계"] = sum(s.values())
    return s


KO = json.loads((DATA / "ko.json").read_text(encoding="utf-8")) if (DATA / "ko.json").exists() else {}
SNAPSHOT = json.loads((DATA / "snapshot.json").read_text(encoding="utf-8")) if (DATA / "snapshot.json").exists() else {"repos": {}}
API_OK = None  # 첫 호출에서 판정


def api_reachable():
    global API_OK
    if API_OK is None:
        try:
            API_OK = requests.get(f"{API}/repos/anthropics/skills", headers=HEAD, timeout=10).status_code == 200
        except Exception:
            API_OK = False
        if not API_OK:
            print("GitHub API 접근 불가 → data/snapshot.json 사용", file=sys.stderr)
    return API_OK


def from_snapshot(seed):
    full = seed["repo"]
    s = SNAPSHOT["repos"].get(full)
    if not s:
        return None
    owner, name = full.split("/")
    return {"html_url": f"https://github.com/{full}", "name": name, "owner": {"login": owner},
            "description": s.get("description", ""), "stargazers_count": s["stars"], "forks_count": 0,
            "open_issues_count": 0, "pushed_at": s["pushed_at"] + "T00:00:00Z",
            "license": {"spdx_id": s["license"]} if s.get("license") and s["license"] != "미표기" else None,
            "topics": [], "archived": False, "size": 0, "_source": f"snapshot {SNAPSHOT.get('as_of')}"}


def fetch_repo(seed):
    full = seed["repo"]
    print(f"- {full}", file=sys.stderr)
    r = gh(f"{API}/repos/{full}") if api_reachable() else from_snapshot(seed)
    if not r:
        return None
    pushed = datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))
    days = (datetime.now(timezone.utc) - pushed).days
    lic = (r.get("license") or {}).get("spdx_id") or "미표기"
    desc = r.get("description") or ""
    text = f"{full} {desc} {' '.join(r.get('topics', []))} {seed.get('type','')}"
    k = KO.get(full, {})
    return {
        "ko": k.get("ko", ""), "ko_desc": k.get("desc", ""), "rec": k.get("rec", ""), "comment": k.get("comment", ""),
        "pros": k.get("pros", ""), "cons": k.get("cons", ""),
        "repo": full,
        "url": r["html_url"],
        "name": r["name"],
        "owner": r["owner"]["login"],
        "description": desc,
        "type": seed.get("type"),
        "official": bool(seed.get("official")),
        "compat": seed.get("compat", []),
        "stars": r.get("stargazers_count", 0),
        "forks": r.get("forks_count", 0),
        "open_issues": r.get("open_issues_count", 0),
        "pushed_at": r["pushed_at"][:10],
        "days_since_push": days,
        "license": lic,
        "license_ok": lic in ALLOWED_LICENSES,
        "topics": r.get("topics", []),
        "archived": r.get("archived", False),
        "category": classify(text, k.get("category") or seed.get("hint_category")),
        "difficulty": difficulty(seed, r),
        "score": score(seed, r, days),
        "source": r.get("_source", "github-api"),
    }


def discover():
    """신규 후보 검색 — 토큰 없으면 생략 (검색 API는 미인증 10회/분)."""
    found = {}
    if not TOKEN or not api_reachable():
        print("GITHUB_TOKEN 없음/API 불가 → discover 생략", file=sys.stderr)
        return found
    known = {s["repo"].lower() for s in SEEDS["repos"]}
    for q in SEEDS.get("discover_queries", []):
        res = gh(f"{API}/search/repositories", {"q": q, "sort": "stars", "per_page": 15})
        for item in (res or {}).get("items", []):
            full = item["full_name"]
            if full.lower() in known or full in found:
                continue
            found[full] = {"repo": full, "url": item["html_url"], "stars": item["stargazers_count"],
                           "description": item.get("description") or "", "pushed_at": item["pushed_at"][:10],
                           "license": (item.get("license") or {}).get("spdx_id") or "미표기", "query": q}
        time.sleep(2)
    return found


def main():
    prev_path = DATA / "skills.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else {"skills": []}
    prev_map = {s["repo"]: s for s in prev.get("skills", [])}

    skills = [x for x in (fetch_repo(s) for s in SEEDS["repos"]) if x]
    skills.sort(key=lambda s: (-s["score"]["합계"], -s["stars"]))

    # 변동 기록
    diff = {"generated_at": datetime.now(timezone.utc).isoformat(), "new": [], "star_jump": [], "stale": [], "candidates": []}
    for s in skills:
        p = prev_map.get(s["repo"])
        if not p:
            diff["new"].append(s["repo"])
        elif s["stars"] - p.get("stars", 0) >= max(500, int(p.get("stars", 0) * 0.05)):
            diff["star_jump"].append({"repo": s["repo"], "from": p["stars"], "to": s["stars"]})
        if s["days_since_push"] > 90:
            diff["stale"].append({"repo": s["repo"], "days": s["days_since_push"]})
    cands = discover()
    diff["candidates"] = sorted(cands.values(), key=lambda c: -c["stars"])[:20]

    out = {"generated_at": diff["generated_at"], "count": len(skills), "categories": CATEGORIES, "skills": skills}
    prev_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "diff.json").write_text(json.dumps(diff, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"수집 {len(skills)}개, 신규 {len(diff['new'])}, 급상승 {len(diff['star_jump'])}, 후보 {len(diff['candidates'])}", file=sys.stderr)


if __name__ == "__main__":
    main()
