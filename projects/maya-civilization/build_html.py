#!/usr/bin/env python3
"""Build the Arabic, offline-first Maya Civilization encyclopedia HTML edition."""
from pathlib import Path
from html import escape
import json, shutil, zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist" / "html"
ZIP = ROOT / "dist" / "موسوعة-حضارة-المايا-HTML.zip"

FAMILIES = [
("01-concepts-origins","المفهوم والنشأة والجذور التاريخية",[
"تعريف حضارة المايا ومفهوم الهوية الماياوية","المجال الجغرافي والبيئي لعالم المايا","الجذور البشرية والاستيطان المبكر","تشكّل المجتمعات الزراعية الأولى","بدايات التقاليد الثقافية والرمزية","نشأة المراكز السكانية والاحتفالية","العصر ما قبل الكلاسيكي ومراحله","ظهور السمات الحضارية المميزة للمايا","مصادر دراسة البدايات وإشكالات التأريخ"]),
("02-politics-kingdoms","التاريخ السياسي والسلالات والممالك",[
"التحولات السياسية في العصر ما قبل الكلاسيكي","نشوء الممالك والمدن المستقلة","مفهوم الملكية المقدسة والسلطة","الأسر الحاكمة والأنساب والسلالات","التحالفات والصراعات والحروب","العلاقات السياسية بين تيكال وكالاكموول","الممالك الإقليمية في العصر الكلاسيكي","التحولات السياسية في العصر ما بعد الكلاسيكي","الغزو الإسباني والمقاومة ونهاية الممالك المستقلة"]),
("03-cities-architecture","المدن والعمارة والتخطيط العمراني",[
"نشأة المدينة الماياوية ووظائفها","تخطيط المراكز الحضرية والساحات","الأهرامات والمعابد والمنصات","القصور والمساكن الملكية","الملاعب والمنشآت الاحتفالية","الطرق والمنشآت المائية والهندسة المدنية","النقوش والواجهات والعمارة التصويرية","دراسة المدن الكبرى: تيكال وبالينكي وكوبان وتشيتشن إيتزا","تقنيات البناء والترميم وحفظ المواقع"]),
("04-society-economy","المجتمع والاقتصاد والحياة اليومية",[
"البنية الطبقية والاجتماعية","الأسرة والقرابة والأنساب","الفلاحون والزراعة والمجتمعات الريفية","الحرفيون والعمال والمتخصصون","التجارة والأسواق وشبكات التبادل","المحاصيل والغذاء وأنظمة الإنتاج","الملابس والزينة والعناية بالجسد","التعليم والتنشئة والعمل والمعيشة","الموت والدفن والذاكرة الاجتماعية"]),
("05-religion-myths","الدين والأساطير والطقوس والتصور الكوني",[
"تصور الكون والعوالم لدى المايا","الآلهة والكائنات المقدسة","أساطير الخلق والبدايات","كتاب بوبول فو ومكانته ومصادره","الطقوس والتقويم الديني","القرابين والنذور والطقوس الملكية","الدم والتضحية والقرابين البشرية في سياقها التاريخي","الكهنة والعرافون والمتخصصون الدينيون","استمرار المعتقدات وتحولاتها بعد الغزو"]),
("06-language-writing-arts","الكتابة واللغة والأدب والفنون",[
"اللغات الماياوية وتطورها","نشأة الكتابة الهيروغليفية وبنيتها","فك رموز الكتابة الماياوية","النقوش الملكية والتاريخية","المخطوطات والكتب المصورة","الأدب والأساطير والرواية الشفوية","النحت والتماثيل واللوحات الحجرية","الرسم الجداري والفخار والفنون التطبيقية","الموسيقى والرقص والأداء والاحتفالات"]),
("07-science-math-astronomy","العلوم والرياضيات والفلك والتقويم",[
"المعرفة الرياضية ونظام العد","مفهوم الصفر والقيمة المكانية","الحسابات الزمنية والدورات العددية","التقويم الطقسي والتقويم الشمسي","العد الطويل والتأريخ التاريخي","رصد الشمس والقمر والكسوف","معرفة الكواكب ودورات الزهرة","العمارة والمحاذاة الفلكية","حدود المعرفة العلمية وتصحيح الأساطير الحديثة"]),
("08-regions-cities-exchange","الأقاليم والمدن الكبرى والتفاعل الحضاري",[
"جغرافية المرتفعات والمنخفضات والسواحل","تيكال ومجالها السياسي والثقافي","كالاكموول والمدن المتنافسة","بالينكي وبنيتها السياسية والفنية","كوبان وكويريغوا","تشيتشن إيتزا ومايابان والمدن الشمالية","العلاقات مع تيوتيهواكان وثقافات أمريكا الوسطى","التجارة والهجرة والتبادل الثقافي","التنوع الإقليمي ووحدة الهوية الماياوية"]),
("09-collapse-modern-research","الانهيارات والتحولات والاكتشافات والبحث الحديث",[
"أزمة المدن الكلاسيكية وتحولاتها","تفسير ما يسمى بانهيار المايا الكلاسيكي","الجفاف والمناخ والموارد والضغط البيئي","الحروب والأزمات السياسية والاجتماعية","استمرار المجتمعات الماياوية بعد تراجع المدن","الغزو الإسباني والتحولات الاستعمارية","اكتشاف المواقع الأثرية وتاريخ البحث العلمي","التقنيات الحديثة: الاستشعار عن بعد والليدار وتحليل النقوش","أحفاد المايا اليوم والهوية والتراث وحقوق المجتمعات الأصلية"])
]

FAMILY_CONTEXT = [
"يركز هذا المحور على تشكل المجتمعات الماياوية وتاريخها المبكر، مع الفصل بين الوجود البشري والاستقرار الزراعي وتبلور السمات الثقافية. تُعامل الحدود الزمنية والهويات المبكرة بوصفها مسائل بحثية قابلة للمراجعة.",
"يتناول هذا المحور تعدد الممالك والمدن المستقلة، وبناء الشرعية والسلالات والتحالفات والصراعات. تُقرأ النقوش الملكية بوصفها مصادر تاريخية مهمة لكنها ذات منظور نخبوي، وتُقارن بالأدلة الأثرية والإقليمية.",
"يعالج هذا المحور العمارة والمدينة بوصفهما نتاجًا اجتماعيًا وتقنيًا وسياسيًا. تُدرس المنشآت في سياقها المكاني والزمني، ولا تُنسب وظيفة دينية أو فلكية إلى مبنى دون قرائن مستقلة.",
"يدرس هذا المحور السكان والإنتاج والعمل والتبادل والحياة اليومية، مع تجاوز التركيز التقليدي على الملوك والمعابد إلى المجتمعات الريفية والحرفيين والنساء والأطفال حيث تسمح الأدلة.",
"يفحص هذا المحور التصورات الكونية والآلهة والأساطير والطقوس من خلال النقوش والمخطوطات واللقى والمصادر الاستعمارية والروايات المعاصرة، مع تجنب إسقاط نص متأخر على جميع العصور.",
"يتناول هذا المحور اللغات والكتابة والنصوص والفنون والأداء. يميز بين قراءة العلامات المؤكدة والقراءات المقترحة، وبين النص القديم ونسخه أو تفسيراته الحديثة.",
"يدرس هذا المحور الرياضيات والتقويم والرصد الفلكي والمعرفة التطبيقية. تُعرض الإنجازات ضمن سياقها التاريخي، وتُفصل الحسابات الموثقة عن الادعاءات الشعبية غير المسندة.",
"يقارن هذا المحور الأقاليم والمدن وشبكات الاتصال والتبادل، ويؤكد التنوع المحلي وعدم تجانس عالم المايا، مع دراسة التفاعل مع ثقافات أمريكا الوسطى المجاورة.",
"يتناول هذا المحور التحولات السياسية والبيئية والاستعمارية وتاريخ البحث الحديث واستمرار شعوب المايا. لا يُستخدم تعبير الانهيار بمعنى اختفاء السكان أو انقطاع الحضارة."
]

GLOBAL_CSS = """
:root{--bg:#f4f0e8;--paper:#fffdf8;--ink:#24251f;--muted:#6c6b60;--line:#ded7c9;--green:#315c4a;--gold:#b68b43;--soft:#e9e3d6}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font-family:Tahoma,Arial,sans-serif;line-height:1.95}
a{color:var(--green);text-decoration:none}a:hover{text-decoration:underline}.shell{max-width:1120px;margin:auto;padding:24px}
header.hero{background:linear-gradient(135deg,#203f35,#426b54);color:#fff;padding:52px 24px 44px;border-bottom:5px solid var(--gold)}
.hero-inner{max-width:1120px;margin:auto}.eyebrow{color:#e8d7ae;font-size:.85rem;letter-spacing:.04em}.hero h1{font-size:clamp(2rem,5vw,3.7rem);line-height:1.3;margin:.35em 0}.hero p{max-width:780px;color:#f0eee7}
.meta{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}.pill{border:1px solid #ffffff55;border-radius:999px;padding:5px 13px;font-size:.86rem}
.panel{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:24px;margin:22px 0;box-shadow:0 8px 28px #3025140a}
h2{font-size:1.5rem;color:var(--green);margin-top:0}h3{font-size:1.1rem;color:#765a2d}.muted{color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:15px}
.family-card,.chapter-card{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:18px;transition:.18s}.family-card:hover,.chapter-card:hover{transform:translateY(-2px);border-color:var(--gold);text-decoration:none}
.num{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:50%;background:var(--soft);color:var(--green);font-weight:bold;margin-left:8px}
.chapter-list{padding:0;list-style:none}.chapter-list li{border-bottom:1px solid var(--line);padding:10px 0}.chapter-list li:last-child{border:0}
.status{display:inline-block;background:#f5ead1;color:#79551d;padding:4px 10px;border-radius:30px;font-size:.8rem}
.prose{font-size:1.04rem}.prose p{margin:0 0 1em}.callout{border-right:4px solid var(--gold);background:#f5f0e4;padding:14px 18px;border-radius:8px}
nav.breadcrumb{font-size:.9rem;color:var(--muted);margin:12px 0 20px}.navrow{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:28px}.navrow a{background:var(--soft);padding:10px 15px;border-radius:9px}
input.search{width:100%;padding:13px 15px;border:1px solid var(--line);border-radius:10px;font:inherit;background:#fff}
footer{max-width:1120px;margin:35px auto;padding:20px 24px;color:var(--muted);border-top:1px solid var(--line);font-size:.88rem}
@media(max-width:600px){.shell{padding:14px}.panel{padding:17px}.hero{padding:35px 16px}}
"""

def page(title, body, desc="موسوعة حضارة المايا"):
    return f'''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{escape(desc)}"><title>{escape(title)} | موسوعة حضارة المايا</title><style>{GLOBAL_CSS}</style></head><body>{body}<footer>موسوعة حضارة المايا · إصدار بحثي قيد التحرير · جميع المواد الحالية مسودات غير معتمدة. يجب مراجعة المراجع والسياقات قبل اعتماد أي فصل.</footer></body></html>'''

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    all_chapters=[]
    for fi,(slug,fname,titles) in enumerate(FAMILIES):
        fdir=OUT/"families"/slug
        fdir.mkdir(parents=True)
        start=fi*9+1
        items=[]
        for ci,title in enumerate(titles):
            n=start+ci
            rel=f"chapters/{n:02d}.html"
            all_chapters.append((n,title,fname,slug,rel,fi,ci))
            items.append(f'<li><a href="../../{rel}"><span class="num">{n:02d}</span>{escape(title)}</a></li>')
        body=f'''<header class="hero"><div class="hero-inner"><div class="eyebrow">العائلة {fi+1:02d} من 09</div><h1>{escape(fname)}</h1><p>{escape(FAMILY_CONTEXT[fi])}</p><div class="meta"><span class="pill">9 فصول</span><span class="pill">مسودة بحثية</span><span class="pill">الموسوعة: 81 فصلًا</span></div></div></header><main class="shell"><nav class="breadcrumb"><a href="../../index.html">الرئيسية</a> / {escape(fname)}</nav><section class="panel"><h2>فهرس العائلة</h2><ul class="chapter-list">{"".join(items)}</ul></section><div class="navrow"><a href="../../index.html">العودة إلى الفهرس الرئيسي</a></div></main>'''
        (fdir/"index.html").write_text(page(fname,body),encoding="utf-8")

    (OUT/"chapters").mkdir(exist_ok=True)
    for idx,(n,title,fname,slug,rel,fi,ci) in enumerate(all_chapters):
        prev=all_chapters[idx-1] if idx else None
        nxt=all_chapters[idx+1] if idx+1<len(all_chapters) else None
        questions=[
            f"ما الأدلة الأولية التي تسمح بإعادة بناء موضوع «{title}»؟",
            "كيف يختلف هذا الموضوع بين الأقاليم والفترات الزمنية؟",
            "ما حدود الاستنتاج، وما الفرضيات التي لا تزال موضع نقاش؟"
        ]
        body=f'''<header class="hero"><div class="hero-inner"><div class="eyebrow">الفصل {n:02d} · العائلة {fi+1:02d}</div><h1>{escape(title)}</h1><p>{escape(fname)}</p><div class="meta"><span class="pill">ملف HTML مستقل</span><span class="pill">مسودة بحثية</span><span class="pill">غير معتمد</span></div></div></header><main class="shell"><nav class="breadcrumb"><a href="../index.html">الرئيسية</a> / <a href="../families/{slug}/index.html">{escape(fname)}</a> / الفصل {n:02d}</nav><section class="panel"><span class="status">قيد التأليف والتحقيق</span><h2>نطاق الفصل</h2><div class="prose"><p>{escape(FAMILY_CONTEXT[fi])}</p><p>يعالج هذا الفصل موضوع «{escape(title)}» ضمن التسلسل التاريخي لحضارة المايا، ويربطه بالسياق الإقليمي والزمني والاجتماعي. لا تُقبل الاستنتاجات إلا بقدر ما تسنده الأدلة المنشورة أو الشواهد الأولية القابلة للفحص.</p></div></section><section class="panel"><h2>أسئلة التحقيق العلمي</h2><ol>{"".join(f"<li>{escape(q)}</li>" for q in questions)}</ol></section><section class="panel"><h2>محاور المعالجة</h2><ul><li>تحديد المصطلحات والنطاق الزمني والجغرافي.</li><li>عرض الأدلة الأثرية أو النصية أو البيئية ذات الصلة.</li><li>مقارنة التفسيرات الأكاديمية وتحديد مواضع الاتفاق والاختلاف.</li><li>تمييز الحقائق المدعومة من الفرضيات والقراءات غير المحسومة.</li><li>خلاصة تركيبية مع توثيق المراجع الأولية والدراسات الحديثة.</li></ul></section><section class="panel"><h2>ضوابط التوثيق والتحرير</h2><div class="callout">لا يُعد هذا الملف فصلًا نهائيًا أو بحثًا مكتملًا. هذه نسخة تحريرية منظمة لبدء التأليف والتحقيق. يجب إدراج إحالات دقيقة إلى المصادر الأصلية والدراسات المحكمة قبل تغيير حالة الفصل إلى «مكتمل» أو «معتمد».</div><p class="muted">مصادر الاستدلال المتوقعة بحسب موضوع الفصل: تقارير الحفريات، قواعد بيانات النقوش، مجموعات المخطوطات، الدراسات المحكمة، التحليلات البيئية، ومصادر المجتمعات الماياوية المعاصرة عند تناول التراث الحي.</p></section><div class="navrow">{f'<a href="../{prev[4]}">← الفصل السابق</a>' if prev else '<a href="../index.html">الفهرس الرئيسي</a>'}{f'<a href="../{nxt[4]}">الفصل التالي →</a>' if nxt else '<a href="../index.html">الفهرس الرئيسي</a>'}</div></main>'''
        (OUT/rel).write_text(page(title,body),encoding="utf-8")

    # Replace the first family's research briefs with authored, source-linked chapter text.
    authored_path = ROOT / "authored_chapters.json"
    if authored_path.exists():
        authored = json.loads(authored_path.read_text(encoding="utf-8"))
        for key, article in authored.items():
            n = int(key)
            record = all_chapters[n-1]
            _, title, fname, slug, rel, fi, ci = record
            prev = all_chapters[n-2] if n > 1 else None
            nxt = all_chapters[n] if n < len(all_chapters) else None
            prev_link = f'<a href="../{prev[4]}">← الفصل السابق</a>' if prev else '<a href="../index.html">الفهرس الرئيسي</a>'
            next_link = f'<a href="../{nxt[4]}">الفصل التالي →</a>' if nxt else '<a href="../index.html">الفهرس الرئيسي</a>'
            nav = f'<div class="navrow">{prev_link}{next_link}</div>'
            authored_body = f'''<header class="hero"><div class="hero-inner"><div class="eyebrow">الفصل {n:02d} · العائلة {fi+1:02d}</div><h1>{escape(title)}</h1><p>{escape(fname)}</p><div class="meta"><span class="pill">بحث موثق</span><span class="pill">مسودة غير معتمدة</span><span class="pill">نسخة تحريرية موسعة</span></div></div></header><main class="shell"><nav class="breadcrumb"><a href="../index.html">الرئيسية</a> / <a href="../families/{slug}/index.html">{escape(fname)}</a> / الفصل {n:02d}</nav><section class="panel"><span class="status">محتوى بحثي أولي · يحتاج مراجعة علمية</span><div class="prose">{article}</div></section>{nav}</main>'''
            (OUT/rel).write_text(page(title, authored_body), encoding="utf-8")

    cards=[]
    for fi,(slug,fname,titles) in enumerate(FAMILIES):
        cards.append(f'<a class="family-card" href="families/{slug}/index.html"><div><span class="num">{fi+1:02d}</span><strong>{escape(fname)}</strong></div><p class="muted">الفصول {fi*9+1}–{fi*9+9} · 9 فصول</p><span class="status">مسودة</span></a>')
    body=f'''<header class="hero"><div class="hero-inner"><div class="eyebrow">مشروع موسوعي مستقل · قسم الحضارات القديمة</div><h1>موسوعة حضارة المايا</h1><p>مرجع عربي منظم لدراسة تاريخ مجتمعات المايا ولغاتها وممالكها ومدنها وعلومها وفنونها وتحولاتها، من الجذور المبكرة إلى المجتمعات المعاصرة.</p><div class="meta"><span class="pill">9 عائلات</span><span class="pill">81 فصلًا</span><span class="pill">HTML يعمل دون اتصال</span><span class="pill">اتجاه RTL</span></div></div></header><main class="shell"><section class="panel"><h2>منهج الموسوعة</h2><p>تعتمد الموسوعة منهجًا تاريخيًا وأثريًا مقارنًا، ويميز بين الأدلة المباشرة والتفسيرات والفرضيات. ولا تُعامل المايا كدولة موحدة أو شعب اختفى؛ بل كمجتمعات متعددة ذات استمرارية تاريخية وثقافية.</p><div class="callout">حالة الإصدار: الفصول 1–9 تحتوي على مسودات بحثية موسعة موثقة، والفصول 10–81 ما زالت هياكل تحريرية أولية. جميع الفصول غير معتمدة علميًا بعد.</div></section><section class="panel"><h2>العائلات التسع</h2><div class="grid">{"".join(cards)}</div></section><section class="panel"><h2>البحث في الفصول</h2><input id="q" class="search" type="search" placeholder="اكتب عنوان الفصل للبحث..." aria-label="بحث في الفصول"><div id="results" class="grid" style="margin-top:15px"></div></section></main><script>const chapters={json.dumps([{"n":n,"t":t,"f":f,"u":r} for n,t,f,s,r,fi,ci in all_chapters],ensure_ascii=False)};const q=document.getElementById('q'),out=document.getElementById('results');function draw(){{const s=q.value.trim();const a=chapters.filter(x=>!s||(x.t+' '+x.f).includes(s)).slice(0,30);out.innerHTML=a.map(x=>'<a class="chapter-card" href="'+x.u+'"><span class="num">'+String(x.n).padStart(2,'0')+'</span><strong>'+x.t+'</strong><p class="muted">'+x.f+'</p></a>').join('')}}q.addEventListener('input',draw);draw();}}</script>'''
    (OUT/"index.html").write_text(page("الفهرس الرئيسي",body),encoding="utf-8")
    readme=OUT/"اقرأني.txt"
    readme.write_text("موسوعة حضارة المايا - إصدار HTML\nافتح index.html في المتصفح. يعمل الإصدار دون اتصال بالإنترنت.\nعدد العائلات: 9\nعدد ملفات الفصول: 81\nالحالة: ملفات تأسيسية قيد التأليف والتحقيق، وليست فصولًا نهائية معتمدة.\n",encoding="utf-8")
    ZIP.parent.mkdir(parents=True,exist_ok=True)
    if ZIP.exists(): ZIP.unlink()
    with zipfile.ZipFile(ZIP,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in OUT.rglob("*"):
            if p.is_file(): z.write(p,p.relative_to(OUT.parent))
    html_count=len(list(OUT.rglob("*.html")))
    assert html_count==91, html_count
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
    print(f"PASS: {html_count} HTML files; 81 chapters; 9 family indexes; 1 master index; ZIP integrity OK")
    print(f"ZIP: {ZIP}")

if __name__=="__main__": main()
