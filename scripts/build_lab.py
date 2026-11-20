"""Editorial pages, kept separate from the weekly repository catalogue."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs'

CSS = '''
:root{--ink:#17221e;--muted:#5c6c64;--line:#dce5df;--green:#176143;--pale:#edf5ef;--bg:#fafcfb}*{box-sizing:border-box;min-width:0}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 system-ui,"Malgun Gothic",sans-serif}a{color:inherit;text-underline-offset:4px}button,input,textarea{font:inherit}a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid #bb7e16;outline-offset:4px}header{border-bottom:1px solid var(--line);background:white}.nav{max-width:1200px;margin:auto;display:flex;justify-content:space-between;align-items:center;padding:22px 28px;gap:24px}.brand{font-weight:850;letter-spacing:-1px;text-decoration:none;font-size:21px}.brand span{color:var(--green)}nav{display:flex;gap:24px;flex-wrap:wrap}nav a{text-decoration:none;font-size:14px;color:var(--muted)}nav a[aria-current]{color:var(--green);font-weight:750}main{max-width:1144px;margin:auto;padding:0 28px 80px}.eyebrow{text-transform:uppercase;color:var(--green);font-size:13px;letter-spacing:2px;font-weight:750}.hero{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:65px;align-items:center;padding:78px 0 70px}h1{font-size:clamp(34px,4.5vw,59px);line-height:1.2;letter-spacing:-2.5px;margin:18px 0 24px;color:#000}h2{font-size:27px;line-height:1.4;letter-spacing:-1px;margin:8px 0 18px}h3{font-size:20px;line-height:1.45;margin:12px 0}.lede{color:var(--muted);max-width:620px;font-size:18px}.actions{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0}.button,button{display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--line);border-radius:8px;padding:11px 19px;background:white;text-decoration:none;font-weight:650;cursor:pointer}.primary{background:var(--green);color:white;border-color:var(--green)}.stage{background:#182b24;color:white;padding:28px;border-radius:18px;box-shadow:0 22px 50px #162b2414;transform:rotate(1deg)}.stage-top{display:flex;justify-content:space-between;font-size:13px;color:#cfdfd5}.frames{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:22px 0}.frame{aspect-ratio:9/12;background:linear-gradient(155deg,#799481,#354d42);border:1px solid #a9c1b17a;border-radius:10px;display:flex;flex-direction:column;justify-content:space-between;padding:18px}.frame strong{font-size:32px}.frame p{background:#13251fe6;padding:10px;border-radius:5px;font-size:14px;line-height:1.6}.frame.after{background:linear-gradient(155deg,#c8dfc6,#728e77)}.stage small{color:#c6d6cb}.section{padding:42px 0;border-top:1px solid var(--line)}.section-head{display:flex;justify-content:space-between;gap:20px;align-items:center}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.grid.two{grid-template-columns:repeat(2,1fr)}.card{background:white;border:1px solid var(--line);border-radius:12px;padding:25px}.card p{color:var(--muted)}.card a{font-weight:650}.tag{display:inline-block;padding:4px 10px;border-radius:5px;background:var(--pale);color:var(--green);font-size:13px;font-weight:650}.tag.wait{background:#fff2d9;color:#805611}.meta{font-size:14px;color:var(--muted)}.topic-list{display:flex;gap:12px;flex-wrap:wrap}.topic-list a{padding:12px 22px;background:white;border:1px solid var(--line);border-radius:8px;text-decoration:none}.intro{padding:54px 0 36px;max-width:860px}.intro h1{font-size:clamp(32px,4vw,48px)}.notice{background:var(--pale);border-left:3px solid var(--green);padding:18px 22px;margin:22px 0}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;background:white;min-width:550px}th,td{text-align:left;padding:16px;border-bottom:1px solid var(--line)}th{background:var(--pale);font-size:14px}details{border:1px solid var(--line);border-radius:10px;background:white;margin:14px 0;padding:18px}summary{cursor:pointer;font-weight:700}textarea{width:100%;min-height:330px;padding:18px;border:1px solid var(--line);border-radius:8px;background:white;line-height:1.7}footer{border-top:1px solid var(--line);padding:32px 28px;color:var(--muted);font-size:14px}.foot{max-width:1088px;margin:auto;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}.quiet{color:var(--muted)}.skip{position:absolute;top:-100px}.skip:focus{top:0;background:white;padding:16px;z-index:9}.steps{counter-reset:step;list-style:none;padding:0}.steps li{border-bottom:1px solid var(--line);padding:18px 0}.steps li:before{counter-increment:step;content:counter(step);display:inline-grid;place-items:center;background:var(--pale);width:30px;height:30px;border-radius:50%;margin-right:14px;color:var(--green)}@media(max-width:760px){.nav{align-items:flex-start;flex-direction:column;padding:18px 20px;gap:14px}nav{gap:12px 20px}main{padding:0 20px 50px}.hero{grid-template-columns:1fr;padding:38px 0;gap:28px}h1{letter-spacing:-1.6px}.stage{transform:none}.grid,.grid.two{grid-template-columns:1fr}.section{padding:30px 0}.section-head{align-items:flex-start;flex-direction:column;gap:0}.intro{padding:34px 0 20px}.frame{aspect-ratio:9/11}}
'''

NAV = [('index.html','홈'),('guides.html','활용법'),('experiments.html','실험·비교'),('library.html','스킬 라이브러리'),('news.html','AI 소식')]

def page(name, title, body, active=None):
    nav=''.join(f'<a href="{url}"'+(' aria-current="page"' if url==(active or name) else '')+f'>{label}</a>' for url,label in NAV)
    text=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | SKILL MARKET</title><meta name="description" content="AI 스킬을 직접 써보고 개선하는 실험실. 결과물 비교, 제작 과정과 재사용 가능한 스킬을 기록합니다."><meta property="og:title" content="{escape(title)} | SKILL MARKET"><meta property="og:description" content="직접 만들고 고쳐보며 더 나은 AI 활용법을 나눕니다."><meta property="og:type" content="website"><link rel="stylesheet" href="assets/lab.css"><script src="assets/lab.js" defer></script></head><body><a class="skip" href="#main">본문으로 이동</a><header><div class="nav"><a class="brand" href="index.html">SKILL <span>MARKET</span></a><nav aria-label="주 메뉴">{nav}</nav></div></header><main id="main">{body}</main><footer><div class="foot"><span>SKILL MARKET · 직접 만들고, 고쳐보고, 공유합니다.</span><span><a href="about.html">소개</a> · <a href="https://blog.naver.com/ldg0116">네이버 블로그</a> · <a href="https://github.com/ldg0116-oss/skill-market">GitHub</a></span></div></footer></body></html>'''
    (OUT/name).write_text(text,encoding='utf-8')

def intro(label,title,desc):
    return f'<div class="intro"><span class="eyebrow">{label}</span><h1>{title}</h1><p class="lede">{desc}</p></div>'

EXPERIMENT_CARD='''<article class="card"><span class="tag wait">설계 완료 · 실행 전</span><h3>AI 클립, 자막과 말투를<br>고치면 얼마나 달라질까?</h3><p>같은 내용으로 네 버전을 만들어 자막과 음성의 효과를 따로 확인합니다.</p><p class="meta">EXP-001 · 영상 · 자막 · 내레이션</p><a href="experiment-001.html">실험 설계 보기</a></article>'''
SKILL_CARD='''<article class="card"><span class="tag">v0.1 · 검증 전 초안</span><h3>사진과 설명이 함께<br>전달되는 세로 영상</h3><p>장면마다 한 가지 요점. 자막·사진·내레이션을 함께 점검하는 제작 규칙입니다.</p><p class="meta">수동 적용 · 입력 예시 · 검수 체크리스트</p><a href="skill-clip.html">스킬 상세 보기</a></article>'''

PROMPT='''다음 자료로 약 25초의 9:16 세로 영상 장면표를 만들어 주세요.
주제: [독자가 해결할 질문]
대상: [누가 보는 영상인가]
확인된 사실과 출처·기준일: [자료 입력]
사용 가능한 사진·영상: [권리와 AI 생성 여부 포함]
원문에서 더 볼 내용: [설명]

규칙:
1. 제공 자료에 없는 사실을 만들지 말고 확인이 필요한 부분을 표시하세요.
2. 첫 장면에 질문, 다음 장면에 답과 근거, 마지막에 원문 안내를 배치하세요.
3. 장면마다 요점은 하나, 자막은 최대 두 줄을 기본으로 하세요.
4. 내레이션은 한 문장에 한 가지 정보를 담은 자연스러운 구어체로 쓰세요.
5. 사진의 핵심을 가리지 않도록 자막 위치를 제안하세요.
6. 숫자·고유명사의 발음 확인 항목을 따로 적으세요.
7. AI 연출·제휴 관계에 필요한 고지를 빠뜨리지 마세요.

출력: 구간 / 사진·화면 / 자막 / 내레이션 / 검수 사항.
추정 시간과 실제 합성 음성 길이는 구분하세요.'''

RECORD='''# EXP-001 실험 기록
제작일:
주제 / 대상 / 원문:
공식 출처와 확인 기준일:
모델·버전 / 음성 서비스·화자:
스킬 버전 / 프롬프트 / 참조 파일:
고정 조건:
변경 조건:
시도 횟수와 선택 기준:
사람의 수정 내역:
작업 시간 / 확인 가능한 비용:
원본·결과물 위치:

## 버전별 평가
A 기준본:
B 자막 개선:
C 음성 개선:
D 통합 개선:
평가 인원 / 노출 순서 / 자체 평가 여부:
이해도 / 가독성 / 음성 자연스러움 / 선호 이유:
문제 발생 구간(초):

## 공개 후 관찰 (24시간 / 72시간 / 7일)
플랫폼 / 공개 주소 / 발행 시간:
조회·도달 / 평균 시청시간 / 완주율 / 저장 / 공유 / 원문 유입:
미제공 지표는 미확인으로 기록:

## 결론
확인된 개선:
개선되지 않은 부분:
판단하기 어려운 부분:
다음에 바꿀 요소 하나:
'''

def build():
    (OUT/'assets').mkdir(parents=True,exist_ok=True)
    (OUT/'downloads').mkdir(exist_ok=True)
    (OUT/'assets/lab.css').write_text(CSS,encoding='utf-8')
    (OUT/'assets/lab.js').write_text('''document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const el=document.getElementById(b.dataset.copy);const status=b.parentElement.querySelector('[role="status"]');try{await navigator.clipboard.writeText(el.value);status.textContent='복사했습니다.'}catch{el.focus();el.select();status.textContent='자동 복사가 지원되지 않습니다. 선택한 내용을 직접 복사해 주세요.'}}));''',encoding='utf-8')
    (OUT/'downloads/experiment-001.md').write_text(RECORD,encoding='utf-8')
    (OUT/'downloads/clip-skill-v0.1.md').write_text('# 세로 영상 제작 규칙 v0.1\n\n검증 전 초안 · 자동 실행 프로그램이 아닌 수동 적용용 규칙입니다.\n\n'+PROMPT+'\n\n## 검수\n사실·출처, 사진 권리, 자막 잘림, 음성 발음, AI·제휴 고지, 원문 링크를 확인합니다.\n',encoding='utf-8')
    stage='''<div class="stage" aria-label="자막 배치 설명용 모형"><div class="stage-top"><span>EXP-001 / CLIP LAB</span><span>실험 준비 중</span></div><div class="frames"><div class="frame"><strong>A</strong><p>많은 내용을 한 화면에<br>한꺼번에 설명하면<br>읽기 어려워질까요?</p></div><div class="frame after"><strong>D</strong><p>한 장면,<br>한 가지 요점.</p></div></div><small>자막 구성 예시입니다. 실제 비교 영상과 평가 결과는 아직 없습니다.</small></div>'''
    page('index.html','AI로 더 잘 만드는 방법',f'''<section class="hero"><div><span class="eyebrow">Make · Test · Improve</span><h1>AI로 만들고,<br>더 나은 방법을<br>찾습니다.</h1><p class="lede">글·이미지·영상을 직접 만들며 배웁니다.<br>시행착오는 실험으로, 배운 것은 스킬로.</p><div class="actions"><a class="button primary" href="experiment-001.html">첫 실험 살펴보기</a><a class="button" href="library.html">스킬 찾아보기</a></div><p class="meta">직접 실행한 결과와 검증 전 아이디어를 구분합니다.</p></div>{stage}</section><section class="section"><div class="section-head"><h2>이번에 만들고 있는 것</h2><a href="experiments.html">실험 전체 보기</a></div><div class="grid two">{EXPERIMENT_CARD}{SKILL_CARD}</div></section><section class="section"><h2>무엇을 더 잘 만들고 싶나요?</h2><div class="topic-list"><a href="guides.html#writing">블로그·글쓰기</a><a href="guides.html#image">이미지·썸네일</a><a href="guides.html#video">릴스·클립</a></div><p class="meta">웹사이트·자동화·데이터 분석은 실제 실험이 준비되면 확장합니다.</p></section><section class="section"><div class="grid"><article><span class="eyebrow">Learn</span><h3>문제 하나부터</h3><p>어색한 말투, 복잡한 자막처럼 실제 제작에서 만난 문제를 고릅니다.</p></article><article><span class="eyebrow">Compare</span><h3>조건을 맞춰 비교</h3><p>무엇을 바꿨는지 기록하고 결과와 한계를 함께 보여줍니다.</p></article><article><span class="eyebrow">Share</span><h3>다시 쓸 수 있는 스킬</h3><p>효과를 확인한 규칙을 정리해 다음 작업에 적용합니다.</p></article></div></section><section class="section"><h2>조회수도, 과정도 기록합니다.</h2><p class="lede">좋은 결과물과 높은 조회수는 다른 질문입니다. 플랫폼과 관찰 기간을 나눠 성과를 기록합니다.</p><a class="button" href="experiments.html#results">성과 기록 방식 보기</a></section>''')
    page('experiments.html','실험·비교',intro('Experiment journal','더 나아졌는지,<br>직접 확인합니다.','모델 이름보다 결과와 조건을 먼저 봅니다. 실행하지 않은 실험에는 점수나 순위를 매기지 않습니다.')+f'<div class="grid two">{EXPERIMENT_CARD}{SKILL_CARD}</div><section class="section" id="results"><h2>발행 후 성과일지</h2><div class="notice">아직 공개 성과가 없습니다. 첫 실험의 최종본을 발행한 뒤 관찰을 시작합니다.</div><p>24시간 · 72시간 · 7일 기준으로 조회·도달, 시청시간, 저장, 공유와 확인 가능한 원문 유입을 기록합니다. 플랫폼 간 조회수를 합산해 순위를 만들지 않습니다.</p><a href="downloads/experiment-001.md" download>실험 기록 템플릿 다운로드</a></section>')
    page('experiment-001.html','AI 클립 자막·내레이션 개선',intro('EXP-001 · Video','자막과 말투를 고치면<br>영상이 좋아질까요?','같은 내용의 네 버전으로 자막과 내레이션의 효과를 따로 확인합니다.')+'''<span class="tag wait">설계 완료 · 실행 및 평가 전</span><div class="notice">실제 A/B/C/D 영상, 평가 점수, 트래픽 성과는 아직 없습니다. 이 페이지는 첫 실험의 공개 설계서입니다.</div><section class="section"><h2>무엇을 비교하나요?</h2><div class="scroll"><table><thead><tr><th>버전</th><th>자막</th><th>내레이션</th></tr></thead><tbody><tr><td>A · 기준본</td><td>기존 규칙</td><td>기준 음성</td></tr><tr><td>B · 자막 개선</td><td>새 규칙</td><td>A와 같은 음성</td></tr><tr><td>C · 음성 개선</td><td>A와 같은 자막</td><td>새 방식</td></tr><tr><td>D · 통합 개선</td><td>새 규칙</td><td>새 방식</td></tr></tbody></table></div><p>기존 무음 영상은 화면 참고 자료입니다. 음성 효과를 비교하려면 A에도 기준 내레이션을 만들어야 합니다.</p></section><section class="section"><h2>바꾸는 것과 고정하는 것</h2><div class="grid two"><article class="card"><h3>고정 조건</h3><p>주제·사실·사진·사진 순서·9:16 비율·화자·음악 사용 여부·마지막 안내 문구. 25초를 목표로 실제 길이를 기록합니다.</p></article><article class="card"><h3>변경 조건</h3><p>자막은 한 장면 한 요점과 최대 두 줄. 음성은 짧은 구어체 문장과 자연스러운 쉼. 필요한 타이밍 조정도 기록합니다.</p></article></div></section><section class="section"><h2>실행 순서</h2><ol class="steps"><li>주제·대상·공식 출처와 기준일 확정</li><li>같은 자료로 네 버전 제작, 원본 보존</li><li>버전 이름을 가리고 순서를 바꿔 평가</li><li>문제 구간을 기록하고 최종본 선정</li><li>블로그·인스타·클립에 맞춰 공개 후 관찰</li></ol></section><section class="section"><h2>어떻게 좋아졌다고 판단하나요?</h2><p>이해도, 자막 가독성, 음성 자연스러움과 선호 이유를 기록합니다. 가능하면 제작에 참여하지 않은 3~5명이 평가하고, 혼자 평가하면 자체 평가라고 밝힙니다.</p><p>점수보다 읽기 어렵거나 발음이 어색했던 구간을 우선합니다. 한 편의 결과를 모든 모델과 소재에 일반화하지 않습니다.</p></section><section class="section"><h2>기록하고 다시 실행하기</h2><div class="actions"><a class="button primary" href="downloads/experiment-001.md" download>기록 템플릿 다운로드</a><a class="button" href="skill-clip.html">사용할 스킬 보기</a></div><p class="meta">실행 모델·버전, 화자, 비용, 작업시간: 실행 시 기록 예정.</p></section>''',active='experiments.html')
    page('skill-clip.html','사진과 설명이 함께 전달되는 세로 영상',intro('Skill library · v0.1','사진과 설명이 함께<br>전달되는 세로 영상','한 장면에 한 가지 요점. 장면표부터 자막·내레이션 검수까지 적용하는 제작 규칙입니다.')+f'''<span class="tag wait">검증 전 초안 · 수동 적용</span><div class="notice">완성 영상이나 개선 효과가 검증된 스킬은 아닙니다. 복사 가능한 제작 지침이며 영상 생성·게시를 자동 실행하지 않습니다.</div><div class="actions"><a class="button primary" href="downloads/clip-skill-v0.1.md" download>스킬 문서 다운로드</a><a class="button" href="experiment-001.html">검증 실험 보기</a></div><section class="section"><h2>이럴 때 사용하세요</h2><div class="grid two"><article class="card"><h3>잘 맞는 작업</h3><p>사진과 사실 자료를 바탕으로 짧은 설명 영상을 만들 때. 자막이 길거나 내레이션이 딱딱해 수정 기준이 필요할 때.</p></article><article class="card"><h3>별도 확인이 필요한 작업</h3><p>정밀한 상품 재현, 의료·법률 판단, 실시간 뉴스, 사용 권리가 없는 자료. 이 규칙이 사실 검증이나 저작권 확인을 대신하지 않습니다.</p></article></div></section><section class="section"><h2>준비할 자료</h2><p>독자가 해결할 질문 하나, 확인된 사실과 출처, 사용 가능한 사진, 원문 안내 문구가 필요합니다. 대본 작성 도구·음성 도구·영상 편집 도구의 이용 조건은 각각 확인하세요.</p><p class="meta">확인된 실행 환경: 아직 없음 · 호환성 검증 전</p></section><section class="section"><h2>복사해서 시작하기</h2><label for="prompt">대괄호 안을 실제 자료로 바꿔 사용하세요.</label><textarea id="prompt" readonly>{escape(PROMPT)}</textarea><div class="actions"><button class="primary" data-copy="prompt">입력 예시 복사</button><span role="status" aria-live="polite"></span></div></section><section class="section"><h2>사용 순서</h2><ol class="steps"><li>자료를 입력하고 장면표 작성</li><li>출처와 대본을 검토한 후 음성 생성</li><li>실제 음성 길이에 맞춰 사진·자막 배치</li><li>휴대전화 크기로 읽고 소리를 들어 검수</li><li>수정 내역과 시간을 기록하고 결과 보존</li></ol><details><summary>발행 전 체크리스트</summary><ul><li>제목의 질문에 실제로 답하는가?</li><li>자막이 잘리거나 너무 빨리 사라지지 않는가?</li><li>숫자·약어·고유명사가 정확하게 들리는가?</li><li>사진의 핵심이 가려지지 않는가?</li><li>사진 권리·AI 연출·제휴 고지를 확인했는가?</li><li>원문 링크가 해당 글을 여는가?</li></ul></details></section><section class="section"><h2>변경 내역</h2><p><b>v0.1 · 2026.11.21</b> — 최초 실험용 규칙과 기록 템플릿 작성. 실험 후 확인된 개선만 다음 버전에 반영합니다.</p></section>''',active='library.html')
    page('guides.html','활용법',intro('Practical guides','한 가지 문제를,<br>하나씩 해결합니다.','직접 따라 할 수 있는 제작 규칙부터 시작합니다. 검증된 팁과 시험 중인 제안을 구분합니다.')+f'<section class="section" id="video"><h2>릴스·클립 만들기</h2><div class="grid two">{SKILL_CARD}{EXPERIMENT_CARD}</div></section><section class="section" id="writing"><h2>블로그·글쓰기</h2><p>준비 중인 과제: 같은 사실 자료로 검색 질문에 답하는 글 만들기. 실행 결과가 준비되면 활용법을 공개합니다.</p></section><section class="section" id="image"><h2>이미지·썸네일</h2><p>준비 중인 과제: 작은 화면에서도 차이가 보이는 비교 이미지 만들기. 현재는 공개된 검증 결과가 없습니다.</p></section>')
    page('library.html','스킬 라이브러리',intro('Reusable skills','배운 것을,<br>다음 작업에 씁니다.','직접 만든 규칙과 외부에서 수집한 도구를 구분해 살펴보세요.')+f'<div class="grid two">{SKILL_CARD}<article class="card"><span class="tag">외부 자료 · 자동 수집</span><h3>GitHub 스킬 카탈로그</h3><p>기존 검색·카테고리·정렬·설치 명령을 그대로 제공합니다. 자동 추정 점수는 직접 사용한 성능 평가가 아닙니다.</p><a href="catalog.html">외부 스킬 검색하기</a></article></div>')
    page('news.html','AI 소식',intro('AI news','새 소식에서,<br>다음 실험을 찾습니다.','공식 발표를 확인하고 실제 제작에 어떤 변화가 있는지 살펴봅니다.')+'<div class="notice">새 운영 방향에 맞춘 첫 기사를 준비 중입니다. 확인하지 않은 뉴스나 예시 기사를 실제 기사처럼 표시하지 않습니다.</div><section class="section"><h2>이렇게 다룹니다</h2><div class="grid"><article><h3>공식 발표 확인</h3><p>발표일·출시 상태·이용 조건과 공식 출처를 함께 기록합니다.</p></article><article><h3>내 작업과 연결</h3><p>글·이미지·영상 제작에서 무엇이 달라지는지 질문합니다.</p></article><article><h3>직접 시험</h3><p>회사 설명과 직접 실행한 결과를 구분해 실험 페이지에 연결합니다.</p></article></div></section>')
    page('about.html','소개',intro('About the lab','완벽한 답보다,<br>더 나아지는 과정을.','AI 스킬을 공부하며 글·이미지·영상을 직접 만듭니다. 잘된 결과뿐 아니라 부족한 점과 실제 반응도 함께 기록합니다.')+'<section class="section"><h2>채널마다 다른 역할</h2><p>홈페이지에는 실험 조건과 스킬을, 블로그에는 자세한 제작 과정을, 인스타그램과 클립에는 결과와 핵심 차이를 담습니다.</p><a class="button primary" href="https://blog.naver.com/ldg0116">블로그 방문</a><p class="meta">인스타그램과 JEJUINSIDER 주소는 확인 후 연결할 예정입니다.</p></section><section class="section"><h2>공개 원칙</h2><p>실행하지 않은 결과를 만들지 않습니다. 사용한 모델과 수정 내용을 기록합니다. 한 번의 성공을 정답으로 말하지 않습니다. 광고·협찬·제휴 관계는 해당 콘텐츠에서 밝힙니다.</p></section>')
    print('Lab: 8 pages, stylesheet, copy interaction, 2 downloads')

if __name__ == '__main__':
    build()

