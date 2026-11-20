"""Check generated local routes, fragment targets and unfinished substitutions."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

root=Path(__file__).resolve().parent.parent/'docs'
class Links(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.refs=[]; self.ids=set(); self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for key in ('href','src'):
            if key in a:self.refs.append(a[key])
pages={p:Links(p.read_text(encoding='utf-8-sig')) for p in root.glob('*.html')}
errors=[]
for p,parsed in pages.items():
    for ref in parsed.refs:
        u=urlsplit(ref)
        if u.scheme or u.netloc:continue
        target=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve()
        if not target.exists():errors.append(f'{p.name}: missing {ref}')
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append(f'{p.name}: missing anchor {ref}')
    if '__CARDS__' in p.read_text(encoding='utf-8-sig'):errors.append('Unexpanded catalogue')
assert not errors,'\n'.join(errors)
print(f'PASS: {len(pages)} HTML pages and all local assets/downloads/anchors')
