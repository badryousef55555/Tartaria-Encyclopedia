#!/usr/bin/env python3
"""Build the offline Arabic HTML edition of the Awfaq encyclopedia."""
from pathlib import Path
import html, json, re, zipfile, datetime

ROOT = Path(__file__).resolve().parent
VOLUMES = ROOT / "volumes"
DIST = ROOT / "dist"
SITE = DIST / "html"
FAMILIES = [
"المفاهيم والمصطلحات والنشأة","تاريخ الأوفاق والمربعات العددية",
"الرياضيات والبنية العددية للأوفاق","علم الحروف والأبجد والرموز",
"الطلاسم والتمائم والأحراز","الأسماء والرموز والأختام",
"الكوسمولوجيا والمراسلات الكونية","التقاليد الحضارية المقارنة",
"الأوفاق والطلاسم في التراث الإسلامي","الأعلام والمؤلفات والمدارس",
"المخطوطات والنصوص والتحقيق","القطع والآثار والممارسات المادية",
"الاستقبال الحديث والثقافة الشعبية","النقد والتحقيق والمعاجم والفهارس"
]
CSS = """
:root{--bg:#f4f1e9;--paper:#fffefa;--ink:#28251f;--muted:#756f64;--line:#e4ddcf;--accent:#795b36;--soft:#eee7da}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/2 "Segoe UI",Tahoma,Arial,sans-serif}
header{background:linear-gradient(120deg,#24231f,#58462f);color:white;padding:28px max(20px,calc((100% - 1160px)/2))}
header small{color:#e6d7bd}header h1{font-size:clamp(1.5rem,4vw,2.4rem);line-height:1.5;margin:8px 0}
main{max-width:1160px;margin:28px auto;padding:0 18px}.panel,article,.family{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:clamp(20px,4vw,42px);box-shadow:0 8px 28px #3027180b}
article h2{color:#6e512e;margin-top:2em;border-bottom:1px solid var(--line);padding-bottom:5px}article h3{color:#51402c}
p{margin:.3em 0 1em}li{margin:5px 0}a{color:var(--accent)}input{width:100%;padding:12px;border:1px solid #d8cebd;border-radius:10px;font:inherit}
.status{display:inline-block;background:#f3ead8;color:#73552e;padding:3px 12px;border-radius:20px;font-size:.8rem}
.meta{color:var(--muted);font-size:.9rem}.nav{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px;margin-top:32px;border-top:1px solid var(--line);padding-top:16px}
.nav a,.button{padding:8px 13px;border:1px solid var(--line);border-radius:9px;text-decoration:none;background:var(--paper)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}.family{padding:20px}.family h2{font-size:1.08rem;margin:0 0 8px}.family a{display:block;text-decoration:none;padding:4px 0;border-bottom:1px solid #f0ece4}
.result{padding:12px;border-bottom:1px solid var(--line)}.result a{font-weight:700;text-decoration:none}
blockquote{margin:1em 0;padding:10px 16px;background:var(--soft);border-right:3px solid #b38a52}code{background:var(--soft);padding:2px 5px;border-radius:4px}
footer{max-width:1160px;margin:24px auto 42px;padding:0 18px;color:var(--muted);font-size:.82rem}
@media(max-width:600px){header{padding:22px 18px}.nav{justify-content:flex-start}article{padding:20px}}
@media print{body{background:#fff}header{background:#fff;color:#000;padding:0}main{margin:0}article{box-shadow:none;border:0;padding:0}.nav{display:none}}
"""
def inline(s):
    s=html.escape(s,quote=True)
    s=re.sub(r"\x60([^\x60]+)\x60",r"<code>\1</code>",s)
    s=re.sub(r"\*\*([^*]+)\*\*",r"<strong>\1</strong>",s)
    s=re.sub(r"\*([^*]+)\*",r"<em>\1</em>",s)
    s=re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",r'<a href="\2" target="_blank" rel="noopener">\1</a>',s)
    return s
def to_html(src):
    out=[]; para=[]; active=None
    def flush():
        if para: out.append("<p>"+" ".join(inline(x) for x in para)+"</p>"); para.clear()
    def close():
        nonlocal active
        if active: out.append(f"</{active}>"); active=None
    for line in src.replace("\r","").splitlines():
        if not line.strip(): flush(); close(); continue
        h=re.match(r"^(#{1,4})\s+(.+)$",line)
        if h: flush(); close(); n=len(h.group(1)); out.append(f"<h{n}>{inline(h.group(2))}</h{n}>"); continue
        b=re.match(r"^\s*[-*]\s+(.+)$",line); n=re.match(r"^\s*\d+[.)]\s+(.+)$",line)
        if b or n:
            flush(); kind="ul" if b else "ol"
            if active!=kind: close(); active=kind; out.append(f"<{kind}>")
            out.append("<li>"+inline((b or n).group(1))+"</li>"); continue
        q=re.match(r"^\s*>\s?(.*)$",line)
        if q: flush(); close(); out.append("<blockquote>"+inline(q.group(1))+"</blockquote>"); continue
        if re.match(r"^\s*---+\s*$",line): flush(); close(); out.append("<hr>"); continue
        para.append(line.strip())
    flush(); close()
    return "\n".join(out)

def main():
    docs=[]
    for no in range(1,15):
        dirs=[p for p in VOLUMES.glob(f"{no:02d}-*") if p.is_dir() and not p.name.endswith("-hriz")]
        if len(dirs)!=1: raise SystemExit(f"Family {no}: expected one canonical folder, got {len(dirs)}")
        files=sorted(dirs[0].glob("*.md"))
        if len(files)!=9: raise SystemExit(f"Family {no}: expected 9 chapters, got {len(files)}")
        for ch,path in enumerate(files,1):
            src=path.read_text(encoding="utf-8")
            m=re.search(r"^#\s+(.+)$",src,re.M)
            docs.append({"family":no,"chapter":ch,"title":m.group(1).strip() if m else path.stem,
                         "source":src,"href":f"chapter-{ch:02d}.html"})
    if len(docs)!=126: raise SystemExit(f"Expected 126 source chapters, got {len(docs)}")
    if SITE.exists():
        import shutil; shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    for no,name in enumerate(FAMILIES,1):
        folder=SITE/f"family-{no:02d}"; folder.mkdir()
        group=[d for d in docs if d["family"]==no]
        for i,d in enumerate(group):
            nav=['<a href="family-index.html">فهرس العائلة والبحث</a>']
            if i: nav.append(f'<a href="{group[i-1]["href"]}">الفصل السابق</a>')
            if i<8: nav.append(f'<a href="{group[i+1]["href"]}">الفصل التالي</a>')
            page=f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(d['title'])}</title><style>{CSS}</style></head><body><header><small>موسوعة الأوفاق والطلاسم · {name}</small><h1>{html.escape(d['title'])}</h1><span class="status">مسودة غير معتمدة</span></header><main><article><p class="meta">العائلة {no} من 14 · الفصل {d['chapter']} من 9</p>{to_html(d['source'])}<div class="nav">{''.join(nav)}<a href="../index.html">الفهرس العام</a></div></article></main><footer>نسخة HTML محلية مستقلة تعمل دون اتصال. حالة المحتوى مسودة غير معتمدة.</footer></body></html>"""
            (folder/d["href"]).write_text(page,encoding="utf-8")
        rows=[{"title":d["title"],"href":d["href"],"text":re.sub(r"\s+"," ",d["source"])} for d in group]
        data=json.dumps(rows,ensure_ascii=False).replace("</","<\\/")
        cards="".join(f'<div class="result"><a href="{d["href"]}">{html.escape(d["title"])}</a></div>' for d in group)
        family=f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{name}</title><style>{CSS}</style></head><body><header><small>14 عائلة · 126 فصلاً</small><h1>العائلة {no:02d}: {name}</h1><span class="status">مسودة غير معتمدة</span></header><main><section class="panel"><h2>بحث داخل العائلة</h2><input id="q" type="search" placeholder="اكتب كلمة أو عبارة للبحث"><div id="results"></div></section><section class="panel"><h2>الفصول التسعة</h2>{cards}</section><div class="nav"><a href="../index.html">الفهرس العام</a></div></main><script>const D={data};const q=document.getElementById('q'),r=document.getElementById('results');q.addEventListener('input',()=>{{const s=q.value.trim().toLocaleLowerCase();if(!s){{r.innerHTML='';return}}const hits=D.filter(x=>x.text.toLocaleLowerCase().includes(s));r.innerHTML=hits.map(x=>'<div class="result"><a href="'+x.href+'">'+x.title+'</a></div>').join('')||'<p>لا توجد نتائج.</p>'}});</script></body></html>"""
        (folder/"family-index.html").write_text(family,encoding="utf-8")
    cards=[]
    for no,name in enumerate(FAMILIES,1):
        links="".join(f'<a href="family-{no:02d}/{d["href"]}">{d["chapter"]}. {html.escape(d["title"])}</a>' for d in docs if d["family"]==no)
        cards.append(f'<section class="family"><h2>{no:02d} · {name}</h2><p class="meta">9 فصول · مسودة غير معتمدة</p>{links}<a href="family-{no:02d}/family-index.html"><strong>بحث داخل العائلة ←</strong></a></section>')
    index=f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>موسوعة الأوفاق والطلاسم</title><style>{CSS}</style></head><body><header><small>موسوعة عربية بحثية · 14 عائلة · 126 فصلاً</small><h1>موسوعة الأوفاق والطلاسم وعلوم الحروف والرموز</h1><p>تاريخها، علومها، رموزها، مخطوطاتها، أعلامها، ومدارسها</p><span class="status">مسودة موسوعية غير معتمدة</span></header><main><section class="panel"><h2>الفهرس العام</h2><p>اختر عائلة لاستعراض فصولها أو البحث داخلها.</p></section><div class="grid">{''.join(cards)}</div></main><footer>نسخة HTML محلية تعمل دون اتصال. جميع الفصول مسودات غير معتمدة.</footer></body></html>"""
    (SITE/"index.html").write_text(index,encoding="utf-8")
    (SITE/"README.txt").write_text("ابدأ بفتح index.html. يضم الموقع 14 فهرس عائلة و126 صفحة فصل HTML مستقلة.\n",encoding="utf-8")
    (SITE/"manifest.json").write_text(json.dumps({"title":"موسوعة الأوفاق والطلاسم","families":14,"chapters":126,"format":"HTML","status":"draft","built_at":datetime.datetime.now().isoformat(timespec="seconds")},ensure_ascii=False,indent=2),encoding="utf-8")
    archive=DIST/"موسوعة-الأوفاق-والطلاسم-HTML.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in SITE.rglob("*"):
            if f.is_file(): z.write(f,f.relative_to(DIST))
    with zipfile.ZipFile(archive) as z:
        bad=z.testzip(); names=z.namelist()
        pages=[n for n in names if n.endswith(".html")]
        chapters=[n for n in pages if re.search(r"/chapter-\d{2}\.html$",n)]
        indexes=[n for n in pages if n.endswith("family-index.html")]
        if bad or len(chapters)!=126 or len(indexes)!=14 or "html/index.html" not in names:
            raise SystemExit(f"HTML archive verification failed: bad={bad}, chapters={len(chapters)}, family_indexes={len(indexes)}")
    print(f"SUCCESS: 126 chapter HTML pages, 14 family indexes, 1 master index; ZIP_TEST=PASS; bytes={archive.stat().st_size}")

if __name__=="__main__": main()
