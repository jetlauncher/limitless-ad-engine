# คลังแอดของคุณ — Limitless Ad Engine

**นักเรียนแต่ละคนสร้าง repo ของตัวเอง แล้วแก้แบรนด์ ภาพ แคปชั่น และหน้าตาเว็บได้ทั้งหมด** เริ่มด้วยแอดตัวอย่าง 3 ชิ้น ใช้งานบนเครื่องได้โดยไม่ต้องมี API key

[สร้าง repo ของฉันจาก Template](https://github.com/new?template_name=limitless-ad-engine&template_owner=jetlauncher) · [Google Doc คู่มือฉบับเต็ม](https://docs.google.com/document/d/1YpCwbuapteto5hN3khbKXZSGM7SilnHIjr4s4B4REbc/edit) · [คู่มือกระบวนการใน repo](docs/PROCESS-TH.md)

## Clone → Install → Run

ติดตั้ง Git และ Python 3.11 ขึ้นไปก่อน จากนั้นรันบน macOS / Linux:

```sh
git clone https://github.com/jetlauncher/limitless-ad-engine.git
cd limitless-ad-engine
python3 install.py
python3 start.py
```

Windows ใช้ `py install.py` และ `py start.py` แทน `python3` การติดตั้งใช้ Internet โหลด Pillow ลง `.venv` แยกจาก Python หลัก ฟอนต์ Sarabun พร้อม license รวมไว้แล้ว

ครั้งแรกโปรแกรมจะถามชื่อธุรกิจ ลูกค้า สินค้า ข้อเสนอ ปัญหาลูกค้า จุดต่าง หลักฐาน CTA ลิงก์ปลายทาง น้ำเสียง และเป้าหมาย จากนั้นให้เพิ่มบริบทที่มีอยู่ นำเข้าไฟล์ `.txt` / `.md` เลือกสีแบรนด์ ตลาด คู่แข่ง และแบรนด์ที่อยากเรียนรู้ได้

ตอบครบแล้วจะสร้าง **ภาพ PNG และแคปชั่นร่าง 3 ชิ้น** ด้วยแบบข้อความบนเครื่อง และเปิด gallery ใน browser อัตโนมัติ ขั้นตอนนี้ไม่ใช้ AI และไม่เรียก paid scraper ไฟล์บริบทเก็บครบใน `creative-brief.json` เพื่อส่งต่อให้ AI เมื่อคุณเลือกใช้ แต่ยังไม่ได้วิเคราะห์ไฟล์เหล่านั้น

คำตอบอยู่ใน `private/projects/…` ซึ่งไม่ขึ้น Git โดยอัตโนมัติ Raw context ไม่เข้าไฟล์เว็บที่ build เมื่อเปิด `python3 start.py` อีกครั้ง จะใช้โปรเจกต์ล่าสุดโดยไม่ถามใหม่ กด Ctrl+C เพื่อหยุด แก้ไฟล์แล้วรันใหม่เพื่อดูการเปลี่ยนแปลง

```sh
# สร้างอีกแบรนด์ โดยเก็บโปรเจกต์เก่าไว้
python3 start.py --new

# เปิดโปรเจกต์ที่เลือกเอง
python3 start.py --project private/projects/YOUR-PROJECT

# ตอบคำถามและบันทึก โดยยังไม่เปิดเว็บ
python3 start.py --new --setup-only
```

หาก port 8767 ไม่ว่าง โปรแกรมจะเลือก port ถัดไปให้ ภาพเดิมจะไม่เปลี่ยนตามการแก้ caption ต้อง render ใหม่เมื่อแก้ตัวหนังสือบนภาพ ทุกชิ้นเริ่มเป็น draft ให้เติมปลายทางจริงแทน example.com แล้วตรวจภาพ ข้อเสนอและหลักฐานก่อน review/export

## สร้าง repo ของตัวเอง / เปิดตัวอย่างเดิม

1. กด **Use this template → Create a new repository** เลือกบัญชีตัวเอง ตั้งชื่อ เช่น `my-ad-library` และเลือก Private หากไม่ต้องการเปิด source ให้คนอื่น
2. เปิด repo ของคุณใน Codex / Claude Code หรือ clone ลงเครื่อง ใช้ Python 3.11 ขึ้นไป
3. เปิด terminal ในโฟลเดอร์ repo แล้วรัน:

```sh
python3 student.py preview
```

4. เปิด **http://localhost:8767** จะเห็นตัวอย่าง 3 ชิ้น กด Ctrl+C เพื่อหยุด แก้ไฟล์ แล้วรันคำสั่งเดิมเพื่อดูเวอร์ชันใหม่

คุณเป็นเจ้าของสำเนานี้ การแก้ไขจะไม่กระทบ repo ของครูหรือเพื่อน คุณเพิ่มไฟล์ เปลี่ยนระบบ และนำไปใช้กับธุรกิจตัวเองได้ตาม MIT license

## อยากเปลี่ยนอะไร แก้ตรงไหน

ตารางนี้อ้างอิงตัวอย่างใน `student/` หากใช้ guided setup ให้แก้ไฟล์ชื่อเดียวกันใน `private/projects/YOUR-PROJECT/` แทน ทุกคำสั่ง `student.py` รองรับ `--project private/projects/YOUR-PROJECT`

| สิ่งที่ต้องการ | ไฟล์ |
| --- | --- |
| ชื่อธุรกิจ ลูกค้า ข้อเสนอ CTA ลิงก์ปลายทาง หลักฐาน | `student/brand.json` |
| ชื่อเว็บ ข้อความหน้าแรก สี | `student/site.json` |
| หัวข้อ มุมขาย แคปชั่น และรายชื่อภาพแต่ละแอด | `student/ads.json` |
| ภาพของคุณ | `student/assets/` |
| คู่แข่งและแบรนด์ต้นแบบ | `student/watchlist.json` |
| แอดอ้างอิงที่ผ่าน normalize | `student/references.json` |
| จัดหน้าและเพิ่มปุ่ม | `web/index.html` |
| รูปแบบ สี ขนาดตัวอักษร | `web/styles.css` |
| ค้นหา ตัวกรอง และการทำงานของหน้าเว็บ | `web/app.js` |
| ขั้นตอนเก็บแอด สร้างแพ็ก และส่งออก | `engine.py`, `student.py`, `scripts/` |

ชื่อบนหน้าเว็บอยู่ใน `site.json` ส่วนชื่อที่ใช้ผลิตแอดอยู่ใน `brand.json` แก้ให้ตรงกัน เปลี่ยนข้อความในไฟล์ JSON ใช้ `\n` เพื่อขึ้นบรรทัดใหม่ อย่าลืมเครื่องหมายคำพูดและ comma

**Prompt พร้อมใช้กับ AI coding assistant:**

> อ่าน README.md และ AGENTS.md ก่อน ช่วยปรับโปรเจกต์นี้เป็นคลังแอดของธุรกิจ [ชื่อธุรกิจ] ขาย [สินค้า/บริการ] ให้ [ลูกค้า] ใช้สี [สี] และลิงก์ [URL] แก้ student/brand.json, site.json และ ads.json ให้สอดคล้องกัน ถ้าข้อมูลข้อเสนอหรือหลักฐานไม่พอให้ถามฉัน สร้างข้อความใหม่ 3 มุมขายโดยไม่แต่งรีวิวหรือผลลัพธ์ลูกค้า จากนั้นรัน python3 student.py check และเปิด preview ให้ฉันตรวจ

## เพิ่มแอดและเปลี่ยนภาพ

คัดลอกหนึ่ง object ใน `student/ads.json` ตั้ง `id` ใหม่ เช่น `my-ad-04` เปลี่ยน `title`, `headline`, `angle`, `caption` และ `images` ให้เป็นไฟล์ของคุณ ใส่ PNG ใน `student/assets/` เช่น `my-ad-04.png`

รองรับ PNG ขนาด 1080×1080, 1080×1350 และ 1080×1920 สำหรับหลายภาพ ใส่ชื่อไฟล์ตามลำดับใน `images` ระบบคำนวณขนาดและ hash ให้เอง

```json
"images": ["my-ad-04-01.png", "my-ad-04-02.png"]
```

การแก้ headline หรือสีเว็บ **ไม่เปลี่ยนตัวหนังสือที่อยู่ในภาพเดิม** ต้องเปลี่ยนภาพจาก Canva หรือ render ใหม่ด้วยคำสั่งด้านล่าง

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python student.py render --font /absolute/path/Sarabun-Bold.ttf --out runs/my-new-project
python3 student.py preview --project runs/my-new-project
```

ดาวน์โหลดฟอนต์ Sarabun จาก [Google Fonts](https://fonts.google.com/specimen/Sarabun) แล้วใช้ path ของไฟล์ TTF จริง คำสั่งนี้สร้างสำเนาโปรเจกต์ใหม่พร้อมภาพ 1080×1350 ใช้ชื่อธุรกิจ headline CTA และสีที่คุณตั้งไว้ ตรวจคำตัดบรรทัดและความอ่านง่ายก่อนใช้ เลือกโฟลเดอร์ใหม่ทุกครั้ง

## จากตัวอย่างสู่แพ็กแอดจริง

ตัวอย่างตั้ง `demo: true` ไว้เพื่อฝึกใช้งาน เมื่อเปลี่ยนเป็นข้อเสนอจริง ภาพที่มีสิทธิ์ใช้ แคปชั่นจริง และลิงก์จริงครบแล้ว จึงตั้ง `demo: false` พร้อมแก้ `rights` และ `rights_evidence` ให้ตรงกับงาน ห้ามใช้หลักฐานสิทธิ์ของตัวอย่างกับภาพที่เพิ่งนำเข้ามา

```sh
python3 student.py check
python3 student.py pack --id my-ad-04 --out runs/my-ad-04.json
python3 engine.py validate --pack runs/my-ad-04.json --root student/assets
```

ให้ผู้ตรวจเปิดภาพและอ่าน caption ข้อเสนอ หลักฐาน CTA และปลายทางจริงก่อนบันทึก review:

```sh
python3 scripts/approve_pack.py --pack runs/my-ad-04.json --root student/assets --out runs/my-ad-04-approved.json --reviewer "ชื่อผู้ตรวจจริง" --confirm-reviewed
python3 engine.py export --pack runs/my-ad-04-approved.json --root student/assets --out runs/my-ad-04-launch-pack.zip
```

ZIP มีภาพตามลำดับ แคปชั่น หัวข้อ และข้อมูลสำหรับตั้งแอด การแก้เนื้อหาหลัง review ทำให้ approval เดิมใช้ไม่ได้ หากใช้ `--project` อื่น ให้ใช้โฟลเดอร์ `assets` ของโปรเจกต์นั้นเป็น `--root`

หน้า preview สำหรับแก้ไขจะสร้างทุกแอดเป็น **draft** เสมอ หากต้องการหน้าแจกนักเรียนที่มีปุ่มดาวน์โหลด ให้รวม approved pack JSON เป็น array แล้วใช้คำสั่ง build ใน [คู่มือผู้ดูแล](docs/OPERATOR-GUIDE.md) ระบบไม่เปิดแคมเปญหรือใช้เงินยิงแอดให้เอง

## เก็บแอดคู่แข่งและแบรนด์ต้นแบบ

เริ่มจากคู่แข่ง 3 รายและแบรนด์ต้นแบบ 2 รายใน `student/watchlist.json` ตรวจ exact Meta page ID ก่อนเปิด `enabled` และ `identity_verified` รายการเริ่มต้นยังปิดอยู่และไม่มี page ID

```sh
# แสดงแผนเท่านั้น ไม่เรียก paid scrape
python3 engine.py scrape --watchlist student/watchlist.json
```

ขั้นตอน scrape จริงพร้อมงบสูงสุด, collect, import JSON, normalize และสร้าง brief อยู่ใน [คู่มือผู้ดูแล](docs/OPERATOR-GUIDE.md) ใส่ผล normalize เป็น JSON array ใน `student/references.json` แอดอ้างอิงใช้ศึกษา hook/mุมขาย แล้วสร้างภาพและข้อความของธุรกิจคุณเอง

## นำเว็บของตัวเองขึ้น Vercel

สำหรับโปรเจกต์ส่วนตัวจาก setup ใช้ `python3 student.py build --project private/projects/YOUR-PROJECT --out builds/my-gallery` แล้ว deploy เฉพาะโฟลเดอร์ผลลัพธ์ อย่า push ไฟล์บริบททั้งหมดขึ้น public repo ขั้นตอน import repo ด้านล่างใช้ข้อมูลใน `student/`

รัน `python3 student.py check` ก่อน จากนั้น import **repo ของคุณ** เข้า Vercel ค่าที่เตรียมไว้จะ build จาก `student/` ไปยัง `dist/` โดยอัตโนมัติ ดู Preview Deployment แล้วค่อยเลือกเผยแพร่ เมื่อแก้ไฟล์และ push Vercel จะ build ตามการตั้งค่าของคุณ

```sh
python3 student.py build --out builds/my-gallery
```

build ต้องใช้โฟลเดอร์ใหม่ เว็บที่เผยแพร่เป็น static ไม่มี login นักเรียนหรือพื้นที่ส่วนตัว ใช้ข้อมูลที่ตั้งใจให้ผู้เปิดเว็บเห็น Private GitHub repo ไม่ได้ทำให้เว็บ Vercel เป็น private

## สำหรับคนอยากต่อยอด

- เพิ่มฟอร์มแก้แคปชั่น เพิ่มหมวดธุรกิจ หรือเปลี่ยน layout ใน `web/` ได้ทั้งหมด
- คลังเดิม 675 รายการเก็บแยกใน `legacy/` เพื่อศึกษาและ migrate ไม่ถูกโหลดในเว็บของนักเรียนโดยอัตโนมัติ
- รัน `python3 -m unittest discover -s tests -v` ก่อน push ทุกครั้ง GitHub Actions ตรวจระบบและแนบ static build ให้ด้วย
- เก็บ API keys ใน environment เท่านั้น โฟลเดอร์ `private/`, `runs/`, `builds/` และไฟล์ `.env` ไม่ขึ้น Git ตาม `.gitignore`
- Paid Apify/OpenAI adapters ยังไม่ได้ทดสอบด้วยการใช้เงินจริงในชุดส่งมอบนี้ ไม่มีระบบ refresh ตามเวลา แคมเปญอัตโนมัติ หรือการวัด ROAS

## License

ฟอนต์ Sarabun มาจาก [Google Fonts](https://github.com/google/fonts/tree/main/ofl/sarabun) ภายใต้ [SIL Open Font License](fonts/OFL.txt) แยกจาก source code

Source และเอกสารใช้ [MIT](LICENSE) นักเรียนแก้ไขและต่อยอดเชิงพาณิชย์ได้โดยเก็บ license notice ไว้ สิทธิ์นี้ไม่ครอบคลุมสื่อแบรนด์อื่น ภาพในคลังเก่า โลโก้ หน้าคน หรือฟอนต์ของบุคคลที่สาม
