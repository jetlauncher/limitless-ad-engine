"""Interactive business intake. No network calls, credentials, or paid generation."""
from datetime import datetime
from pathlib import Path
import re
import uuid
import engine
import student

FONT = student.ROOT / 'fonts' / 'Sarabun-Bold.ttf'


def ask(label, default='', required=False, limit=2000, validate=None, input_fn=input, output=print):
    while True:
        value = input_fn(label + (f' [{default}]' if default else '') + ': ').strip() or default
        if required and not value:
            output('กรอกข้อมูลข้อนี้ก่อน แล้วกด Enter'); continue
        if len(value) > limit:
            output(f'ใช้ไม่เกิน {limit} ตัวอักษร'); continue
        if value and validate and not validate(value):
            output('รูปแบบไม่ถูกต้อง ลองอีกครั้ง'); continue
        return value


def context_file(path):
    p = Path(path).expanduser()
    if p.suffix.lower() not in ('.txt', '.md'):
        raise ValueError('รองรับไฟล์ .txt และ .md เท่านั้น แปลง PDF/Word เป็นข้อความก่อน')
    if p.stat().st_size > 100_000:
        raise ValueError('ไฟล์ต้องไม่เกิน 100 KB')
    return p.read_text(encoding='utf-8-sig')


def interview(input_fn=input, output=print):
    def q(label, **kw):
        return ask(label, input_fn=input_fn, output=output, **kw)
    output('\nสร้างคลังแอดของคุณ — ตอบคำถามครั้งแรก แล้วกลับมาแก้ได้ทุกเมื่อ')
    output('คำตอบเก็บบนเครื่องของคุณ ขั้นตอนนี้ไม่ scrape และไม่ส่งข้อมูลไปหา AI\n')
    brand = {
        'name': q('ชื่อแบรนด์ / ธุรกิจ', required=True, limit=40),
        'audience': q('ลูกค้าของคุณคือใคร', required=True, limit=500),
        'offer': q('ขายอะไร ข้อเสนอ ราคา หรือเงื่อนไขที่มีจริง', required=True, limit=1500),
        'pain': q('ปัญหาหลักที่ลูกค้าอยากแก้', required=True, limit=500),
        'differentiator': q('อะไรทำให้คุณต่างจากตัวเลือกอื่น (ข้ามได้)', limit=1000),
        'proof': q('หลักฐานที่มีจริง เช่น รีวิว / ผลงาน (ข้ามได้)', default='ยังไม่มีหลักฐานที่ตรวจแล้ว'),
        'cta': q('อยากให้ลูกค้าทำอะไรต่อ', default='ดูรายละเอียด', limit=30),
        'destination': q('ลิงก์ปลายทาง HTTPS (ข้ามได้ แต่ต้องเติมก่อนใช้จริง)', default='https://example.com/', validate=engine.https),
        'tone': q('น้ำเสียงแบรนด์', default='เป็นกันเอง ตรงประเด็น'),
        'goal': q('เป้าหมายของแอดชุดแรก', default='ให้ลูกค้าสอบถามรายละเอียด'),
    }
    context = q('บริบทเพิ่มเติมที่อยากให้รู้ (ข้ามได้)', limit=10_000)
    imported = []
    while True:
        path = q('เพิ่มไฟล์บริบท .txt/.md: ใส่ path หรือกด Enter เพื่อไปต่อ')
        if not path:
            break
        try:
            content = context_file(path)
        except (OSError, UnicodeError, ValueError) as exc:
            output(str(exc)); continue
        imported.append({'name': Path(path).name, 'text': content})
        output('อ่านไฟล์แล้ว (เก็บเฉพาะในโปรเจกต์บนเครื่อง)')
        if len(imported) == 10:
            output('ครบ 10 ไฟล์แล้ว'); break
    brand['context'] = {'notes': context, 'documents': imported}
    color = q('สีหลักของแบรนด์ เช่น #c3a172', default='#c3a172',
              validate=lambda v: bool(re.fullmatch(r'#[a-fA-F0-9]{6}', v)))
    country = q('ตลาดที่ศึกษา: รหัสประเทศ เช่น TH, US หรือ ALL', default='TH',
                validate=lambda v: bool(re.fullmatch(r'[A-Z]{2}|ALL', v)))
    watchlist = []
    for relationship, label in [('competitor', 'คู่แข่งโดยตรง'), ('aspiration', 'แบรนด์ที่อยากเรียนรู้')]:
        output('\n' + label + ' — เพิ่มทีละแบรนด์ กด Enter ที่ชื่อเมื่อครบ')
        for i in range(20):
            name = q('ชื่อ' + label + ' (ข้ามได้)', limit=120)
            if not name:
                break
            url = q('ลิงก์เพจ / เว็บไซต์ HTTPS (ข้ามได้)', validate=engine.https)
            why = q('อยากเรียนรู้อะไรจากแบรนด์นี้ (ข้ามได้)', limit=1000)
            page_id = q('Meta page ID ถ้าทราบ (ตัวเลขเท่านั้น ข้ามได้)', validate=lambda v: v.isascii() and v.isdigit())
            verified = False
            if page_id:
                verified = q('ตรวจแล้วว่า ID นี้เป็นของเพจนี้จริงหรือไม่? y/n', default='n',
                             validate=lambda v: v.lower() in ('y', 'n')).lower() == 'y'
            watchlist.append({'id': f'{relationship}-{i+1:02d}', 'name': name,
                              'relationship': relationship, 'url': url, 'notes': why,
                              'country': country, 'page_id': page_id,
                              'identity_verified': verified, 'enabled': verified, 'limit': 30})
    output(f'\nสรุป: {brand["name"]} · {len(watchlist)} แบรนด์อ้างอิง · {len(imported)} ไฟล์บริบท')
    output('จะสร้างภาพข้อความและแคปชั่นร่าง 3 มุมจากคำตอบหลักของคุณ ยังไม่มีการตรวจข้อเสนอหรือสิทธิ์โดยคน')
    if q('บันทึกและสร้างโปรเจกต์? y/n', default='y', validate=lambda v: v.lower() in ('y', 'n')).lower() != 'y':
        return None
    return brand, watchlist, color


def concepts_for(brand):
    # Deterministic drafts, not claims of AI analysis of the attached documents.
    footer = '\n\n' + brand['cta']
    value = '\n\n' + brand['differentiator'] if brand.get('differentiator') else ''
    texts = [
        ('Pain', 'กำลังเจอปัญหานี้\nอยู่หรือเปล่า', brand['pain'] + '\n\nสำหรับ ' + brand['audience'] + '\n\n' + brand['offer']),
        ('Offer', 'ลองรู้จัก\n' + brand['name'], brand['offer'] + value + '\n\nสำหรับ ' + brand['audience']),
        ('Consideration', 'ก่อนตัดสินใจ\nมาดูรายละเอียด', 'กำลังมองหาตัวเลือกสำหรับ ' + brand['pain'] + '\n\nลองดูข้อเสนอจาก ' + brand['name'] + '\n' + brand['offer']),
    ]
    return [dict(id=f'my-ad-{i:02d}', title=headline.replace('\n', ' '), headline=headline,
                 angle=angle, caption=caption+footer, brand=brand['name'],
                 kind='original', status='draft', demo=False, cta=brand['cta'],
                 destination=brand['destination'], proof=brand['proof'], source_ids=[],
                 visual_brief='Original typography draft from user-supplied facts',
                 generation_method='local_template',
                 notes='ร่างจากแบบข้อความบนเครื่อง ตรวจภาพ ข้อเสนอ คำกล่าวอ้าง และปลายทางก่อนใช้')
            for i, (angle, headline, caption) in enumerate(texts, 1)]


def create_project(brand, watchlist, color, out):
    from scripts.render_pack import render
    out = Path(out)
    if out.exists():
        raise ValueError('Project exists; choose a new folder. Existing work is preserved.')
    site = student.load_site(student.ROOT / 'student')
    site.update(name=brand['name'], headline='คลังแอด\n' + brand['name'],
                description='ภาพและข้อความร่างสำหรับธุรกิจของคุณ เปิดแต่ละชิ้นเพื่อตรวจและปรับต่อ',
                footer=brand['name'] + ' · ตรวจทุกชิ้นก่อนนำไปใช้')
    site['colors']['gold'] = color
    # Render in a sibling staging directory. Only expose a complete project on success.
    import tempfile
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.intake-', dir=out.parent) as tmp:
        stage = Path(tmp)
        packs = render(concepts_for(brand), stage / 'assets', FONT, site['colors'])
        ads = [dict(p, images=[a['path'] for a in p['assets']]) for p in packs]
        for ad in ads:
            ad.pop('assets', None)
        brief = engine.brief([], brand)
        brief['watchlist'] = watchlist
        brief['research_status'] = 'not_collected'
        brief['context_status'] = 'retained_verbatim_not_analyzed'
        for name, data in [('brand', brand), ('site', site), ('ads', ads),
                           ('watchlist', watchlist), ('references', []), ('creative-brief', brief)]:
            engine.write(stage / (name + '.json'), data)
        student.prepare(stage)
        # The destination was checked above; rename refuses a nonempty destination.
        if out.exists():
            raise ValueError('Project destination appeared during setup; choose another folder')
        stage.rename(out)
    return out


def new_project_path():
    return student.ROOT / 'private' / 'projects' / (datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6])
