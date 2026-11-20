#!/usr/bin/env python3
"""data/skills.json → .claude-plugin/marketplace.json, docs/index.html, docs/skills.json, reports/weekly-YYYY-MM-DD.md

화면 틀은 scripts/template.html 에 있고, 여기서는 카드와 숫자를 채워 넣는다.
"""
import json, html
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "skills.json").read_text(encoding="utf-8"))
DIFF_P = ROOT / "data" / "diff.json"
DIFF = json.loads(DIFF_P.read_text(encoding="utf-8")) if DIFF_P.exists() else {}
KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).strftime("%Y-%m-%d")
CATS = DATA["categories"]
SKILLS = DATA["skills"]
TOP_PER_CAT = 5
E = html.escape

# 설치 명령 (유형별)
def install_cmd(s):
    t, repo = s["type"], s["repo"]
    known = {
        "anthropics/skills": "/plugin marketplace add anthropics/skills → /plugin install document-skills@anthropic-agent-skills",
        "obra/superpowers": "/plugin marketplace add obra/superpowers-marketplace → /plugin install superpowers@superpowers-marketplace",
        "wshobson/agents": "/plugin marketplace add wshobson/agents",
        "upstash/context7": "npx ctx7 setup --claude",
        "microsoft/playwright-mcp": "claude mcp add playwright npx @playwright/mcp@latest",
        "davila7/claude-code-templates": "npx claude-code-templates@latest",
        "vercel-labs/skills": "npx add-skill <owner/repo>",
        "google-gemini/gemini-cli": "npm i -g @google/gemini-cli",
        "openai/codex": "npm i -g @openai/codex",
        "affaan-m/everything-claude-code": "/plugin marketplace add affaan-m/everything-claude-code",
    }
    if repo in known:
        return known[repo]
    if t in ("skill", "marketplace", "agent"):
        return f"/plugin marketplace add {repo}"
    if t == "mcp":
        return f"claude mcp add <name> -- npx -y <package>  (README 확인)"
    return f"git clone https://github.com/{repo}"


# ---------- 올린 곳 ----------
# 공식 = seeds.json 에서 official 로 표시한 저장소(그 제품·규격을 만든 곳이 직접 올린 것).
# 단체/개인 = GitHub 계정 종류. verified = GitHub가 그 조직의 도메인을 확인했는지(collect.py 가 API로 받음).
PUB_KINDS = [("official", "공식"), ("org", "단체"), ("user", "개인"), ("unknown", "미확인")]

def pub_of(s):
    p = s.get("publisher") or {}
    key = "official" if s.get("official") else {"org": "org", "user": "user"}.get(p.get("kind"), "unknown")
    return {"key": key, "label": dict(PUB_KINDS)[key], "name": p.get("name") or s["owner"], "login": p.get("login") or s["owner"],
            "verified": p.get("verified") is True, "is_org": p.get("kind") == "org"}

def pub_text(s):
    p = pub_of(s)
    return f"{p['name']} ({p['label']}{', GitHub 인증' if p['verified'] else ''})"

# 유형을 쉬운 말로
TYPE_KO = {"skill": "스킬 묶음", "marketplace": "플러그인 장터", "agent": "에이전트 모음", "mcp": "연결 장치(MCP)", "curation": "목록 모음",
           "education": "강좌·문서", "tool": "설치 도구", "rules": "규칙 모음", "host": "AI 도구 본체", "automation": "자동화 프로그램"}


# ---------- marketplace.json ----------
plugins = []
for s in SKILLS:
    if s["type"] not in ("skill", "marketplace", "agent"):
        continue
    plugins.append({
        "name": s["name"].lower().replace("_", "-"),
        "source": {"source": "github", "repo": s["repo"]},
        "description": f"[{s['category']}·{s.get('rec') or s['difficulty']}·{s['score']['합계']}점] {s.get('ko','')} — {(s.get('ko_desc') or s['description'])[:120]}",
        "version": TODAY,
        "author": {"name": s["owner"]},
        "homepage": s["url"],
        "license": s["license"],
        "keywords": [s["category"], s["type"], s["difficulty"]] + s.get("compat", [])[:3],
    })
market = {
    "name": "skill-market",
    "owner": {"name": "ldg0116-oss", "url": "https://github.com/ldg0116-oss"},
    "metadata": {"description": "주 1회 자동 수집·검증·분류되는 AI 스킬 마켓 (코딩/기획·문서/마케팅·콘텐츠/자동화/비개발자)", "version": TODAY},
    "plugins": plugins,
}
(ROOT / ".claude-plugin").mkdir(exist_ok=True)
(ROOT / ".claude-plugin" / "marketplace.json").write_text(json.dumps(market, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- docs/index.html ----------
def fmt_stars(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)

def card(s, rec):
    sc, p = s["score"], pub_of(s)
    grade = s.get("rec") or ("추천" if rec else "")
    badge = f'<span class="grade g-{E(grade)}">{E(grade)}</span>' if grade else ""
    title = E(s.get("ko") or s["repo"])
    ver = '<span class="ver" title="GitHub가 이 계정의 회사 도메인을 확인했습니다">✓ GitHub 인증</span>' if p["verified"] else ""
    avatar = f'<img class="{"org" if p["is_org"] else "usr"}" src="https://github.com/{E(p["login"])}.png?size=44" alt="" width="22" height="22" loading="lazy" onerror="this.remove()">'
    tag = f'<p class="c-tag">{E(s.get("ko_desc") or s["description"] or "")}</p>' if (s.get("ko_desc") or s["description"]) else ""
    what = f'<p class="c-what">{E(s["what"])}</p>' if s.get("what") else ""
    cmt = f'<p class="c-cmt"><b>한 줄 평</b>{E(s["comment"])}</p>' if s.get("comment") else ""
    pc = ""
    if s.get("pros") or s.get("cons"):
        pc = '<ul class="c-pc">' + (f'<li class="pro"><b>장점</b><span>{E(s["pros"])}</span></li>' if s.get("pros") else "") \
             + (f'<li class="con"><b>주의</b><span>{E(s["cons"])}</span></li>' if s.get("cons") else "") + "</ul>"
    fresh = f'<span class="old">갱신 {s["days_since_push"]}일 전</span>' if s["days_since_push"] > 90 else f'<span>갱신 {E(s["pushed_at"])}</span>'
    compat = "".join(f'<span class="works">{E(c)}</span>' for c in s.get("compat", [])[:4])
    search = " ".join([s["repo"], s.get("ko", ""), s.get("ko_desc", ""), s.get("what", ""), s["description"] or "", s.get("comment", ""),
                       p["name"], p["label"], TYPE_KO.get(s["type"], s["type"])]).lower()
    parts = f"실용성 {sc['실용성(자동)']}/25 · 설치 편의 {sc['설치편의']}/15 · 완성도 {sc['완성도(자동)']}/20 · 유지보수 {sc['유지보수']}/15 · 비용 {sc['비용']}/10 · 보안·신뢰 {sc['보안']}/15"
    return f"""<article class="card" data-cat="{E(s['category'])}" data-pub="{p['key']}" data-score="{sc['합계']}" data-stars="{s['stars']}" data-pushed="{E(s['pushed_at'])}" data-name="{E(search)}">
  <header class="c-head"><h2><a href="{E(s['url'])}" target="_blank" rel="noopener">{title}</a></h2>{badge}<span class="stars" title="GitHub 별 수">★ {fmt_stars(s['stars'])}</span></header>
  <div class="c-pub">{avatar}<span class="who">{E(p['name'])}</span><span class="kind k-{p['key']}">{p['label']}</span>{ver}<a class="repo" href="{E(s['url'])}" target="_blank" rel="noopener">{E(s['repo'])}</a></div>
  {tag}{what}{cmt}{pc}
  <div class="c-meta"><span>{E(TYPE_KO.get(s['type'], s['type']))}</span><span>난이도 {E(s['difficulty'])}</span><span>라이선스 {E(s['license'])}</span>{fresh}{compat}</div>
  <details class="c-score"><summary><span>점수</span><b>{sc['합계']}</b><span class="bar"><i style="width:{min(100, sc['합계'])}%"></i></span><span class="more">내역</span></summary><p class="parts">{parts}</p></details>
  <div class="c-install"><code>{E(install_cmd(s))}</code><button type="button" class="copy">복사</button></div>
</article>"""

cards = []
for cat in CATS:
    items = [s for s in SKILLS if s["category"] == cat]
    for i, s in enumerate(items):
        cards.append(card(s, i < TOP_PER_CAT))
cat_btns = "".join(f'<button type="button" class="chip" data-f="{E(c)}" aria-pressed="false">{E(c)} <small>{sum(1 for s in SKILLS if s["category"]==c)}</small></button>' for c in CATS)
pub_counts = {k: sum(1 for s in SKILLS if pub_of(s)["key"] == k) for k, _ in PUB_KINDS}
pub_btns = "".join(f'<button type="button" class="chip" data-p="{k}" aria-pressed="false">{label} <small>{pub_counts[k]}</small></button>' for k, label in PUB_KINDS if pub_counts[k])
new_list = ", ".join(DIFF.get("new", [])[:10]) or "없음"
jump = ", ".join(f"{j['repo']}({j['from']}→{j['to']})" for j in DIFF.get("star_jump", [])[:10]) or "없음"

page = (Path(__file__).resolve().parent / "template.html").read_text(encoding="utf-8")
for key, val in {
    "__UPDATED__": E(DATA["generated_at"][:10]), "__COUNT__": str(len(SKILLS)), "__N_OFFICIAL__": str(pub_counts["official"]),
    "__NEW__": E(new_list), "__JUMP__": E(jump), "__CAT_BTNS__": cat_btns, "__PUB_BTNS__": pub_btns, "__CARDS__": "\n".join(cards),
}.items():
    page = page.replace(key, val)
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "catalog.html").write_text(page, encoding="utf-8")
(ROOT / "docs" / "skills.json").write_text(json.dumps(DATA, ensure_ascii=False), encoding="utf-8")

# ---------- weekly report (블로그 초안 소재) ----------
lines = [f"# 주간 스킬 리포트 {TODAY}", "", f"수집 {len(SKILLS)}개 · 신규 {len(DIFF.get('new', []))} · 급상승 {len(DIFF.get('star_jump', []))} · 90일 이상 미갱신 {len(DIFF.get('stale', []))}", ""]
for cat in CATS:
    items = [s for s in SKILLS if s["category"] == cat][:TOP_PER_CAT]
    lines += [f"## {cat} — 추천 {len(items)}", "", "| 스킬 | 올린 곳 | 등급 | ★ | 점수 | 무엇인가 | 장점 | 단점 | 한 줄 평 |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in items:
        nm = f"{s['ko']} ([{s['repo']}]({s['url']}))" if s.get("ko") else f"[{s['repo']}]({s['url']})"
        lines.append(f"| {nm} | {pub_text(s)} | {s.get('rec','')} | {fmt_stars(s['stars'])} | {s['score']['합계']} | {s.get('what','')} | {s.get('pros','')} | {s.get('cons','')} | {s.get('comment','')} |")
    lines.append("")
if DIFF.get("candidates"):
    lines += ["## 검토 대기 후보 (discover)", "", "| 저장소 | ★ | 설명 |", "| --- | --- | --- |"]
    for c in DIFF["candidates"][:15]:
        lines.append(f"| [{c['repo']}]({c['url']}) | {fmt_stars(c['stars'])} | {c['description'][:80]} |")
    lines.append("")
if DIFF.get("stale"):
    lines += ["## 미갱신 경고", ""] + [f"- {x['repo']}: {x['days']}일" for x in DIFF["stale"]] + [""]
lines += ["---", "블로그 글 소재: 신규·급상승 항목 중 1개를 골라 4개 AI에 설치·실행 비교."]
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports" / f"weekly-{TODAY}.md").write_text("\n".join(lines), encoding="utf-8")
(ROOT / "reports" / "latest.md").write_text("\n".join(lines), encoding="utf-8")
print(f"marketplace {len(plugins)} plugins · catalog {len(SKILLS)} cards · reports/weekly-{TODAY}.md")

from build_lab import build as build_lab
build_lab()
