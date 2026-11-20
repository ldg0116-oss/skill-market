#!/usr/bin/env python3
"""data/skills.json → .claude-plugin/marketplace.json, docs/index.html, docs/skills.json, reports/weekly-YYYY-MM-DD.md"""
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
    sc = s["score"]
    compat = " ".join(f"<span class=tag>{html.escape(c)}</span>" for c in s.get("compat", [])[:4])
    grade = s.get("rec") or ("추천" if rec else "")
    badge = f"<span class='rec g-{grade}'>{grade}</span>" if grade else ""
    off = "<span class=off>공식</span>" if s["official"] else ""
    stale = f"<span class=stale>{s['days_since_push']}일 전</span>" if s["days_since_push"] > 90 else f"<span class=fresh>{s['pushed_at']}</span>"
    title = html.escape(s.get("ko") or s["repo"])
    sub = html.escape(s["repo"]) if s.get("ko") else ""
    desc = html.escape(s.get("ko_desc") or s["description"] or "")
    comment = f"<p class=cmt>{html.escape(s['comment'])}</p>" if s.get("comment") else ""
    if s.get("pros") or s.get("cons"):
        comment += f"<div class=pc><span class=pro>＋ {html.escape(s.get('pros',''))}</span><span class=con>－ {html.escape(s.get('cons',''))}</span></div>"
    search = f"{s['repo']} {s.get('ko','')} {s.get('ko_desc','')} {s['description']} {s.get('comment','')}".lower()
    return f"""<article class=card data-cat="{html.escape(s['category'])}" data-type="{s['type']}" data-diff="{s['difficulty']}" data-name="{html.escape(search)}">
  <header><a href="{s['url']}" target=_blank rel=noopener>{title}</a> {badge}{off}</header>
  {f'<div class=sub>{sub}</div>' if sub else ''}
  <p class=desc>{desc}</p>{comment}
  <div class=meta><span>★ {fmt_stars(s['stars'])}</span> {stale} <span>{html.escape(s['license'])}</span> <span>{s['type']}</span> <span>{s['difficulty']}</span></div>
  <div class=tags>{compat}</div>
  <div class=score title="실용성 {sc['실용성(자동)']} · 설치 {sc['설치편의']} · 완성도 {sc['완성도(자동)']} · 유지보수 {sc['유지보수']} · 비용 {sc['비용']} · 보안 {sc['보안']}"><b>{sc['합계']}</b>/100</div>
  <div class=install><code>{html.escape(install_cmd(s))}</code><button onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent)">복사</button></div>
</article>"""

cards = []
for cat in CATS:
    items = [s for s in SKILLS if s["category"] == cat]
    for i, s in enumerate(items):
        cards.append(card(s, i < TOP_PER_CAT))
cat_btns = "".join(f'<button data-f="{html.escape(c)}">{html.escape(c)} <small>{sum(1 for s in SKILLS if s["category"]==c)}</small></button>' for c in CATS)
new_list = ", ".join(DIFF.get("new", [])[:10]) or "없음"
jump = ", ".join(f"{j['repo']}({j['from']}→{j['to']})" for j in DIFF.get("star_jump", [])[:10]) or "없음"

page = f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>스킬 마켓</title>
<meta name=description content="GitHub AI 스킬·MCP·에이전트 저장소를 주 1회 수집·검증·분류. 카테고리별 추천과 설치 명령.">
<style>
:root{{--bg:#fff;--fg:#111;--mut:#666;--line:#e5e5e5;--card:#fafafa;--acc:#0e4e33;--acc2:#eea51b}}
@media(prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#111;--fg:#eee;--mut:#999;--line:#2a2a2a;--card:#181818;--acc:#4caf7a}}}}
:root[data-theme=dark]{{--bg:#111;--fg:#eee;--mut:#999;--line:#2a2a2a;--card:#181818;--acc:#4caf7a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif}}
.wrap{{max-width:1100px;margin:0 auto;padding:24px 16px}}h1{{font-size:24px;margin:0 0 4px}}.sub{{color:var(--mut);margin:0 0 16px;font-size:13px}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 20px;align-items:center}}.bar button{{border:1px solid var(--line);background:var(--card);color:var(--fg);padding:6px 12px;border-radius:20px;cursor:pointer;font-size:13px}}
.bar button.on{{background:var(--acc);color:#fff;border-color:var(--acc)}}.bar input{{flex:1;min-width:160px;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}}.card{{border:1px solid var(--line);background:var(--card);border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:6px}}
.card header{{font-weight:600;display:flex;gap:6px;align-items:center;flex-wrap:wrap}}.card a{{color:var(--fg);text-decoration:none}}.card a:hover{{text-decoration:underline}}
.desc{{margin:0;color:var(--mut);font-size:13px;min-height:38px}}.meta{{font-size:12px;color:var(--mut);display:flex;gap:10px;flex-wrap:wrap}}
.tags .tag{{font-size:11px;border:1px solid var(--line);border-radius:6px;padding:1px 6px;margin-right:4px;color:var(--mut)}}
.rec{{font-size:11px;background:var(--acc2);color:#111;border-radius:6px;padding:1px 6px}}.g-필수{{background:#c0392b;color:#fff}}.g-선택{{background:var(--line);color:var(--fg)}}.g-보류{{background:transparent;border:1px solid var(--line);color:var(--mut)}}
.pc{{display:flex;flex-direction:column;gap:2px;font-size:12px}}.pro{{color:var(--acc)}}.con{{color:#c0392b}}
.sub{{font-size:11px;color:var(--mut);margin-top:-4px}}.cmt{{margin:0;font-size:12.5px;border-left:2px solid var(--acc2);padding-left:8px;color:var(--fg)}}.off{{font-size:11px;background:var(--acc);color:#fff;border-radius:6px;padding:1px 6px}}
.stale{{color:#c0392b}}.fresh{{color:var(--mut)}}.score{{font-size:12px;color:var(--mut)}}.score b{{color:var(--fg);font-size:14px}}
.install{{display:flex;gap:6px;align-items:center;margin-top:auto}}.install code{{flex:1;font-size:11px;background:var(--bg);border:1px solid var(--line);padding:6px 8px;border-radius:6px;overflow-x:auto;white-space:nowrap}}
.install button{{font-size:12px;padding:5px 10px;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;cursor:pointer}}
.note{{font-size:13px;color:var(--mut);border-left:3px solid var(--acc2);padding:6px 12px;margin:0 0 16px;background:var(--card)}}
footer{{margin-top:32px;font-size:12px;color:var(--mut)}}
</style></head><body><div class=wrap>
<h1>스킬 마켓</h1>
<p class=sub>갱신 {html.escape(DATA['generated_at'][:10])} · {len(SKILLS)}개 저장소 · Claude Code에서 <code>/plugin marketplace add ldg0116-oss/skill-market</code></p>
<p class=note>이번 주 신규: {html.escape(new_list)} · 급상승: {html.escape(jump)}. 점수의 실용성·완성도는 ⭐ 기반 자동추정이며 사람 검증 전까지 참고용.</p>
<div class=bar><button data-f="" class=on>전체 <small>{len(SKILLS)}</small></button>{cat_btns}<input id=q placeholder="검색: 이름·설명"></div>
<div class=grid id=grid>{''.join(cards)}</div>
<footer>출처: GitHub API (스냅샷 모드일 땐 data/snapshot.json). 라이선스 "미표기"는 API에 없다는 뜻. 설치 전 저장소 README·스크립트를 직접 확인하세요.</footer>
</div>
<script>
const btns=[...document.querySelectorAll('.bar button')],q=document.getElementById('q'),cards=[...document.querySelectorAll('.card')];let f='';
function apply(){{const s=q.value.trim().toLowerCase();cards.forEach(c=>{{c.style.display=((!f||c.dataset.cat===f)&&(!s||c.dataset.name.includes(s)))?'':'none'}})}}
btns.forEach(b=>b.onclick=()=>{{btns.forEach(x=>x.classList.remove('on'));b.classList.add('on');f=b.dataset.f;apply();try{{localStorage.setItem('sm-f',f)}}catch(e){{}}}});
q.oninput=apply;try{{const sv=localStorage.getItem('sm-f');if(sv){{const b=btns.find(x=>x.dataset.f===sv);if(b)b.click()}}}}catch(e){{}}
</script></body></html>"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")
(ROOT / "docs" / "skills.json").write_text(json.dumps(DATA, ensure_ascii=False), encoding="utf-8")

# ---------- weekly report (블로그 초안 소재) ----------
lines = [f"# 주간 스킬 리포트 {TODAY}", "", f"수집 {len(SKILLS)}개 · 신규 {len(DIFF.get('new', []))} · 급상승 {len(DIFF.get('star_jump', []))} · 90일 이상 미갱신 {len(DIFF.get('stale', []))}", ""]
for cat in CATS:
    items = [s for s in SKILLS if s["category"] == cat][:TOP_PER_CAT]
    lines += [f"## {cat} — 추천 {len(items)}", "", "| 스킬 | 등급 | ★ | 점수 | 장점 | 단점 | 한 줄 평 |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for s in items:
        nm = f"{s['ko']} ([{s['repo']}]({s['url']}))" if s.get("ko") else f"[{s['repo']}]({s['url']})"
        lines.append(f"| {nm} | {s.get('rec','')} | {fmt_stars(s['stars'])} | {s['score']['합계']} | {s.get('pros','')} | {s.get('cons','')} | {s.get('comment','')} |")
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
