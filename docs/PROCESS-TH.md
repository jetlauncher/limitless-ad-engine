# Limitless Ad Engine

## 1. เป้าหมายของระบบ

เปลี่ยนการเปิดดูแอดทีละเพจ ให้เป็นกระบวนการที่นักเรียนทำซ้ำกับธุรกิจของตัวเองได้ ตั้งแต่เลือกคู่แข่งและแบรนด์ต้นแบบ เก็บตัวอย่าง วิเคราะห์มุมขาย สร้างข้อความและภาพใหม่ ไปจนถึงดาวน์โหลดแพ็กที่ทีมตรวจแล้วเพื่อเตรียมยิงแอดด้วยตัวเอง

คุณค่าหลักคือ “จากไอเดียที่เห็น ไปสู่แอดของธุรกิจตัวเอง” นักเรียนต้องได้ทั้งภาพ แคปชั่น หัวข้อ CTA และหน้าปลายทาง พร้อมรู้ว่ามุมนี้กำลังทดสอบอะไร การมีรูปหลายร้อยชิ้นอย่างเดียวไม่ใช่ผลลัพธ์ปลายทาง

ระบบเวอร์ชันนี้เป็น local-first MVP ใช้คอมพิวเตอร์ของผู้ดูแลสร้างแพ็ก แล้วส่งเฉพาะไฟล์แกลเลอรีให้นักเรียนเปิดบนมือถือได้ ยังไม่มีระบบบัญชีนักเรียนหรือพื้นที่ส่วนตัวแยกรายคน

## 2. ผล reverse engineering ที่ตรวจจริง

เว็บต้นทาง: https://limitless-ad-gallery-deploy.vercel.app/

Repo เดิม: https://github.com/jetlauncher/limitless-ad-system

พบ source ในโปรเจกต์ limitless-ad-system และเทียบไฟล์ index.html, app.js, styles.css และ manifest.json กับไฟล์ที่เว็บให้บริการแล้ว ตรงกันทุก byte รายละเอียด hash อยู่ใน docs/source-audit.json

เว็บเป็น static HTML/CSS/JavaScript ไม่ใช้ framework และไม่มี backend โหลดรายการจาก manifest.json แล้วสร้างการ์ดภาพกับ modal แสดงรายละเอียด มีตัวกรอง family และ angle รวมถึงปุ่มคัดลอก caption สำหรับรายการที่มี caption

ข้อมูลที่ตรวจพบ: 675 รายการ แบ่งเป็น Originals 4, Alternatives 664 และ Carousels 7 มี caption 321 รายการ ขาด caption 354 รายการ จำนวนนี้คือรายการใน manifest ไม่ใช่จำนวนแอดที่ยิงจริงหรือจำนวนภาพที่ไม่ซ้ำกัน

ชื่อมุมขายเดิมปนกันทั้งวิธีขาย ชื่อแคมเปญ และวิธีผลิตภาพ จึงควรแยก angle, campaign, format และ generation method ในรุ่นถัดไป การ migrate ครั้งนี้เก็บค่าดั้งเดิมไว้เพื่อไม่ทำให้ข้อมูลหาย

generator เดิมสร้าง primary_text ได้ แต่ตอนเขียน manifest.generated.json ไม่ได้ส่ง field นี้เข้าไป ทำให้ข้อความกับรูปหลุดออกจากกัน อีกทั้งสคริปต์นี้สร้าง concept/copy ไม่ได้สร้างไฟล์ภาพจริง จึงยังต้องมีขั้นผลิตภาพและเช็กไฟล์

ยังไม่พบระบบ scrape ที่เชื่อมกับ manifest ใน source gallery นี้ ไม่พบสถานะอนุมัติที่ผูกกับไฟล์ ไม่พบ ZIP pack และไม่พบการยืนยันสิทธิ์การนำภาพไปใช้ การเห็นแกลเลอรีออนไลน์จึงไม่ได้ยืนยันว่าแต่ละชิ้นพร้อมใช้ยิงแอด

## 3. โครงสร้างระบบใหม่

Watchlist → Scrape / Import → Normalize → Creative brief → Original copy → Render / Canva → Review → ZIP + Gallery → Manual launch → Learn

Research layer เก็บตัวอย่างจากแหล่ง public พร้อม exact page ID, ad ID, source URL, capture time, run ID และ dataset ID ข้อมูลดิบอยู่ใน runs/ ที่ไม่ขึ้น Git และไม่เข้าไฟล์เว็บ

Creation layer ใช้ brand brief ของนักเรียนเป็นข้อเท็จจริงหลัก ใช้ตัวอย่างคู่แข่งเพื่อศึกษา hook, layout, offer structure และข้อโต้แย้ง สร้าง caption และ visual ใหม่ แล้วบันทึก reference IDs เพื่อย้อนกลับไปดูที่มาได้

Delivery layer ตรวจว่ามีภาพจริง ขนาดตรง caption ไม่ว่าง ปลายทางถูกต้อง และมีการ review ก่อนให้ดาวน์โหลด ZIP ส่วนแกลเลอรีแสดงสถานะชัดเจน นักเรียนไม่ต้องเข้า GitHub เพื่อใช้คลังแอดในแต่ละวัน

## 4. แยกแอดออกเป็นสามประเภท

Reference: แอดคู่แข่งหรือแบรนด์ที่อยากเรียนรู้ ใช้ศึกษาเท่านั้น มี source link แต่ไม่มีปุ่มดาวน์โหลดเป็นแพ็กพร้อมยิง ไม่ยกตัวเลขในโฆษณามาเป็นข้อเท็จจริงของเรา

Original: ผลงานใหม่ของธุรกิจนักเรียน มีภาพและข้อความของตัวเอง อยู่ในสถานะ draft จนกว่าจะตรวจครบ หลังอนุมัติจึงได้ download pack

Legacy: 675 รายการจากคลังเดิม เก็บ caption, title, angle, family และ slug ดั้งเดิมผ่าน source metadata ภาพยังอ้างอิง deployment เดิม ทุกชิ้นเริ่มที่ needs_review ไม่อนุมัติย้อนหลังแบบเหมารวม

Originals ในเว็บเก่าเป็นเพียง family label ไม่ใช่หลักฐานว่าเป็นเจ้าของสิทธิ์ รุ่นใหม่จึงไม่ใช้ชื่อนี้เพื่อข้ามขั้นตรวจ

## 5. ข้อมูลที่นักเรียนต้องเตรียม

ชื่อธุรกิจ สินค้าที่จะขาย ลูกค้าที่ต้องการ ปัญหาในภาษาลูกค้า ข้อเสนอจริง ราคาและเงื่อนไขถ้ามี CTA และหน้าปลายทางที่เปิดใช้งานได้ รวมถึงหลักฐานที่อนุญาตให้ใช้ เช่น รีวิวจริง ผลงานที่ได้รับอนุญาต หรือภาพสาธิตของธุรกิจ

Brand kit: โลโก้ที่มีสิทธิ์ใช้ สี ฟอนต์ ภาพสินค้า ภาพเจ้าของหรือทีมที่ได้รับอนุญาต และตัวอย่างงานที่ชอบ การอ้างอิง style ไม่ใช่การยืมโลโก้ หน้าคน รีวิว หรือ identity ของแบรนด์อื่น

Watchlist แนะนำเริ่ม 3 คู่แข่งโดยตรง และ 2 แบรนด์ที่อยากเรียนรู้ คู่แข่งช่วยให้เห็น pain/offer ในตลาดเดียวกัน ส่วนแบรนด์ต้นแบบช่วยให้เห็นคุณภาพการนำเสนอ ไม่จำเป็นต้องขายของประเภทเดียวกัน

รายการเริ่มต้นใน repo มี SkillLane, Skooldio และ Digital Tips Academy เป็น candidate จากบริบทเดิมเท่านั้น ยังปิดการทำงานและเว้น page ID ไว้ แบรนด์ต้นแบบยังต้องเลือกให้ตรงธุรกิจของผู้เรียน ห้ามใช้ชื่อเพจคล้ายกันแทนโดยไม่ตรวจ

## 6. SOP เก็บแอด

ผู้ดูแลเปิด official Facebook page หรือ Meta Ads Library และตรวจ exact page ID ก่อนตั้ง identity_verified และ enabled เป็น true บันทึก relationship เป็น competitor หรือ aspiration กำหนด country ให้ตรงตลาดที่ต้องการศึกษา

เริ่ม 30 ads ต่อแบรนด์ สูงสุดที่สคริปต์ยอมรับคือ 50 active ads ต่อแบรนด์ ใช้ current actor schema ที่ระบุ resultsLimit ไม่ใช้ maxAds จากตัวอย่างเก่า และปิด ecommerce enrichment กับข้อมูลเสริมที่ไม่จำเป็น

รัน dry run ก่อน ระบบจะแสดง input และจำนวนสูงสุดโดยไม่ใช้ token และไม่เสียค่า scrape เมื่อจะรันจริงต้องส่ง --execute และกำหนด --budget-usd เอง ซึ่งเป็นเพดานรวมทั้ง batch แล้วหารให้แต่ละแบรนด์ ไม่ใช่การรับประกันว่าจะได้ครบตามจำนวนเมื่อเงินถึงเพดาน

สคริปต์เก็บ request และ receipt ของแต่ละ run แยกกัน จากนั้นใช้ collect เพื่ออ่านสถานะและ paginate dataset ทีละ 100 แถว หากยัง RUNNING ให้กลับมา collect ใหม่โดยไม่เริ่ม paid run ซ้ำ หาก POST timeout และไม่แน่ใจว่าส่งสำเร็จหรือยัง ให้ตรวจ Apify Runs ก่อนสั่งใหม่

กรณีไม่อยาก scrape ซ้ำ ให้นำ JSON export เดิมเข้า normalize พร้อมข้อมูลแบรนด์ที่ตรวจแล้ว ข้อมูลทดสอบใน examples เป็น synthetic fixture ไม่ใช่ตัวอย่างแอดจริง

## 7. ทำความสะอาดและเก็บหลักฐาน

Deduplicate ด้วย Meta ad archive ID ตรวจ page ID ให้ตรงกับแบรนด์ที่ร้องขอ แถวที่ไม่มี ID หรือมาจากอีกเพจจะไป rejected report เก็บ caption พร้อม line breaks ตาม source โดยไม่เรียบเรียงทับต้นฉบับ

เก็บแยก unknown, zero และ failure: ไม่ทราบสถานะ active ให้เป็น null การ scrape สำเร็จแต่ได้ศูนย์แถวแปลว่า zero results ใน run นี้ ส่วน FAILED/TIMED-OUT ไม่ใช่หลักฐานว่าแบรนด์ไม่มีแอด

จำนวน ads ที่กำลังรัน วันเริ่มรัน หรือรูปแบบที่เห็นซ้ำเป็นเพียงสัญญาณสำหรับตั้งสมมติฐาน ไม่ใช่ ROAS, CPA หรือกำไร ห้ามเรียก “winning ad” เพียงเพราะเห็นรันมานาน

URL ภาพและวิดีโอจากแพลตฟอร์มอาจหมดอายุ รุ่นนี้เก็บ link และ source เพื่ออ้างอิง ไม่ได้ทำระบบสำรองสื่อคู่แข่งทั้งคลัง ถ้ารูปเปิดไม่ได้แกลเลอรีจะแจ้งให้ทราบ งานจริงที่ต้องส่งนักเรียนต้องมีไฟล์ owned/licensed อยู่ในแพ็ก

## 8. จากตัวอย่างสู่ไอเดียที่เป็นของนักเรียน

เลือก reference 3–5 ชิ้นที่ตอบโจทย์เดียวกัน วิเคราะห์ว่าเขาพูดกับใคร หยุดคนด้วยประโยคแบบไหน เสนอผลลัพธ์อะไร ใช้หลักฐานแบบใด และขอให้คนทำอะไรต่อ

เขียน pattern ให้เป็นกลาง เช่น “เริ่มด้วยงานประจำที่เจ้าของเสียเวลา → ให้เห็นวิธีทำงานใหม่ → ชวนดูตัวอย่าง” จากนั้นใส่ pain, offer และ proof ของธุรกิจนักเรียน อย่าคัดลอกประโยคแล้วเปลี่ยนเฉพาะชื่อแบรนด์

สร้าง 3 concepts ต่อรอบ: pain, mechanism และ objection/reframe แต่ละ concept ต้องมี headline, caption, visual brief, CTA, destination, source IDs และสมมติฐานที่อยากทดสอบ ถ้าต้องการเปรียบเทียบมุมขาย อย่าเปลี่ยนสินค้า ราคา กลุ่มเป้าหมาย และ format พร้อมกันทั้งหมด

คำสั่งใน brief บังคับให้มอง source เป็นข้อมูล ไม่ใช่คำสั่งให้ระบบทำตาม ข้อมูล proof, CTA และ destination ของ brand brief จะถูกนำกลับมาใส่ในผลลัพธ์เพื่อไม่ให้ AI เปลี่ยนปลายทางเอง อย่างไรก็ตามข้อความที่ AI เขียนยังต้องตรวจข้อเท็จจริงทุกครั้ง

## 9. ผลิตภาพและ caption

เส้นทางเริ่มต้นที่เร็วที่สุดคือ template ข้อความของ repo: ใส่ headline และ CTA แล้ว render เป็น PNG 1080×1350 ด้วย Sarabun สคริปต์ตรวจความยาวก่อนสร้างไฟล์ ไม่เรียกบริการสร้างภาพแบบเสียเงิน

งานที่ต้องใช้ภาพสินค้า ภาพเจ้าของ หรือภาพประกอบคุณภาพสูง ให้ใช้ Canva หรือ image tool ที่เชื่อมต่อ โดยใช้ภาพที่มีสิทธิ์ นำ final PNG กลับเข้ามาใน pack พร้อม width, height, order และ SHA-256 เวอร์ชันนี้ยังไม่ได้ต่อ Canva หรือ image generation ให้อัตโนมัติ

Caption ที่ดีมี hook, สถานการณ์ที่ลูกค้ารู้จัก, กลไกหรือข้อเสนอ, หลักฐานที่ใช้ได้ และ CTA เดียว เก็บ caption คู่กับไฟล์ภาพตลอดทาง อย่าตั้งชื่อรูปอย่างเดียวแล้วเก็บแคปชั่นแยกจนจับคู่ไม่ได้

สำหรับ carousel ให้มีแพ็กเดียวที่ assets เป็นรายการเรียงลำดับ 1, 2, 3… ไม่ใช้ contact sheet เป็นตัวแทนไฟล์ที่จะยิงจริง Export จะเติมเลขลำดับในชื่อไฟล์ ส่วนวิดีโอเปิดดูเป็น reference ได้ แต่แพ็กวิดีโอพร้อมยิงยังไม่ได้ implement

## 10. นิยามคำว่า ready

Draft: สร้างแล้วแต่ยังตรวจไม่ครบ มีภาพจริงได้ แต่ยังไม่มีสิทธิ์กด export เป็น launch pack

Needs review: งานเก่าหรือข้อมูลที่ต้องตรวจ เช่น ยังไม่มี caption ราคาเก่า หรือยังไม่รู้สิทธิ์ภาพ

Approved: ผู้ตรวจที่ระบุชื่อได้ตรวจภาพ ข้อเสนอ คำกล่าวอ้าง สิทธิ์ และหน้าปลายทางแล้ว การอนุมัติผูกกับ hash ของเนื้อหาและไฟล์ในแพ็ก ถ้าเปลี่ยน caption หรือเปลี่ยนภาพต้อง review ใหม่

Exported for manual launch: มี ZIP ที่ตรวจโครงสร้างและอ่านไฟล์ได้ พร้อมให้ผู้เรียนไปตั้งค่าใน Ads Manager เอง สถานะนี้ไม่เท่ากับ live หรือได้รับอนุมัติจากแพลตฟอร์ม และไม่ได้ยืนยันว่าจะได้ผลตอบแทน

Checklist ก่อนอนุมัติ: อ่านบนมือถือออก ภาพไม่แตก ภาษาไทยและวรรณยุกต์ถูก ข้อความในภาพตรงกับ caption ไม่มีราคาหรือวันหมดอายุที่เก่า ไม่มีผลลัพธ์ที่พิสูจน์ไม่ได้ CTA ตรงกับ landing page สิทธิ์ภาพชัด และเปิด destination จริงแล้ว

## 11. สิ่งที่อยู่ใน ZIP

ไฟล์ PNG จริงเรียงลำดับ, caption.txt ที่คง line breaks, headline.txt, launch-details.json ระบุ CTA/destination/proof/approval และ manifest.json ระบุข้อมูลแพ็กกับ hash ระบบตรวจ CRC ของ ZIP หลังสร้าง

Reference และ demo export เป็น launch pack ไม่ได้ ภาพหาย ขนาดผิด hash ไม่ตรง caption ว่าง placeholder ค้าง หรือ approval ไม่ตรงกับเนื้อหาปัจจุบันจะถูกปฏิเสธ การแก้ไขต้องบันทึกเป็นไฟล์ใหม่เพื่อรักษาของเดิม

## 12. ประสบการณ์นักเรียนใน gallery

เปิดหน้าเว็บบนมือถือ → เลือกแอดต้นฉบับ แอดอ้างอิง หรือคลังเดิม → ค้นหาด้วยคำหรือแบรนด์ → กรองมุมขาย/สถานะ → เปิดภาพกับ caption → คัดลอกข้อความ → ดาวน์โหลดแพ็กที่ผ่านการตรวจแล้ว

หน้าใหม่แบ่งแสดงครั้งละ 36 รายการ เพื่อลดการสร้างการ์ดพร้อมกันจำนวนมาก มีปุ่มดูเพิ่ม สถานะไม่มีข้อมูล และข้อความแจ้งภาพอ้างอิงที่เปิดไม่ได้ หน้า modal ใช้ dialog และกลับ focus ไปการ์ดเดิมเมื่อปิด

การค้นหาเป็น client-side และอ่าน catalog ทั้งชุด เหมาะกับ MVP ระดับนี้ แต่เมื่อคลังโตมากควรแยก index/search service และ paginate ที่ฝั่ง server ต้องเพิ่มบัญชีผู้ใช้และสิทธิ์ก่อนเก็บข้อมูลส่วนตัวนักเรียนร่วมกัน

## 13. คู่มือรันสำหรับผู้ดูแล

คำสั่งติดตั้ง รัน scrape/import, generate copy, render, validate, approve, export และ build อยู่ใน README.md ของ repo แบบคัดลอกไปใช้ได้ ต้องใช้ Python 3.11 ขึ้นไป Core ไม่ต้องลง package เพิ่ม ส่วน render ใช้ Pillow และไฟล์ Sarabun ที่ผู้ดูแลจัดเตรียม

เก็บ token ใน environment เท่านั้น ไม่ใส่ในเว็บ ไม่ใส่ใน manifest และไม่ส่งในแชท ตัวอย่าง .env.example เป็นรายการชื่อที่ต้องตั้ง ไม่ถูกโหลดอัตโนมัติ สคริปต์ AI ต้องระบุ TEXT_MODEL เองตามโมเดลที่บัญชีใช้งานได้

ทุก build ต้องใช้ output directory ใหม่ ถ้าชื่อซ้ำระบบหยุดแทนการเขียนทับไฟล์เดิม เก็บ brand brief และข้อมูล client ใน private/ ซึ่งถูก ignore จาก Git

Static deploy ใช้เฉพาะ output directory ระบบ build คัดเฉพาะ field สำหรับ gallery และ media ของแพ็ก ไม่รวม raw scrape หรือ token ห้าม deploy repository root

Private GitHub ไม่ได้แปลว่าเว็บ Vercel เป็น private ถ้าคลังมีข้อมูลเฉพาะนักเรียนต้องใช้ hosting access control หรือเพิ่ม authentication ก่อนเปิดใช้งานร่วมกัน รุ่นที่ส่งนี้ยังไม่ deploy และไม่แก้ production เดิม

## 14. การย้ายคลังเดิม

เก็บไฟล์ source เดิมและ manifest ทั้ง 675 รายการใน legacy/ พร้อม source audit จากเว็บจริง Migration สร้าง ID ใหม่แบบคงที่และเก็บ legacy_slug เดิมไว้ ไม่เปลี่ยน caption ดั้งเดิม และไม่ถือ family Originals เป็นการอนุมัติสิทธิ์

เพื่อให้ clone repo เบา ภาพ legacy ยังอ่านจาก URL เดิม ไม่ใช่ archive แบบ offline ทั้งหมด ถ้า deployment ต้นทางหยุดทำงาน ภาพส่วนนี้จะไม่โหลด แม้ metadata ยังอยู่ครบ

ขั้นเปลี่ยน legacy เป็น original pack: เลือกชิ้นที่มีสิทธิ์ → นำ final PNG เข้า local pack → เติม caption ที่ขาด → ตรวจ offer/claims ใหม่ → เก็บหลักฐานสิทธิ์ → อนุมัติเฉพาะชิ้น → build เข้า cohort gallery

ไม่แนะนำเติม caption 354 รายการโดยเดา offer จากรูป ควรเริ่มจากชุดที่ยังขายจริงและมี source ของข้อความที่ตรวจแล้วก่อน

## 15. แผนสอนหนึ่งรอบ

ช่วงที่ 1: นักเรียนเขียน brand brief และเลือกหนึ่งสินค้าที่จะทำแอด ทีมช่วยตรวจว่าปลายทางและข้อเสนอพร้อมจริง

ช่วงที่ 2: แยกคู่แข่งกับแบรนด์ต้นแบบ ตรวจ page ID และ import sample ที่เตรียมไว้ เพื่อไม่ให้ทั้งห้องรอ scrape พร้อมกัน

ช่วงที่ 3: นักเรียนเลือก pattern หนึ่งแบบ แล้วเขียน 3 angles ด้วย pain และ proof ของตัวเอง ห้ามเอา reference ไปใช้ตรง ๆ

ช่วงที่ 4: ผลิตภาพและ caption อย่างน้อยหนึ่งแพ็ก ตรวจบนมือถือ ปรับภาษาและรายละเอียดธุรกิจ แล้วให้เพื่อนหรือผู้ดูแลตรวจตาม checklist

ช่วงที่ 5: Export ZIP เปิดทุกไฟล์และทดสอบ copy caption จาก gallery ก่อนจบคลาส ผลงานขั้นต่ำคือหนึ่งแพ็กที่นำไปตั้งค่าแคมเปญได้ ไม่ใช่แค่ prompt หรือภาพ preview

ช่วงติดตาม: นักเรียนบันทึกว่าลองมุมไหน ใช้เงินจริงเท่าไร และได้ qualified lead หรือยอดขายเท่าไร โดยแนบข้อมูลจากบัญชีของตน ไม่ใช้ค่าของคู่แข่งแทนผลลัพธ์

## 16. งานทีมและจังหวะทำซ้ำ

Research owner: ดูแล watchlist, source identity, scrape receipts และ rejection report

Creative owner: เลือก pattern เขียน brief และผลิตภาพ/caption โดยรักษา brand facts

Reviewer: ตรวจ offer, claims, rights, Thai readability และ destination แล้วระบุชื่อก่อน approve

Gallery owner: สร้าง static build ใหม่ ตรวจลิงก์และ ZIP แล้วส่ง URL ของ cohort ที่ถูกต้อง หลังได้รับอนุมัติให้เผยแพร่

รอบแรกเริ่มด้วยหนึ่งธุรกิจ 3–5 แบรนด์อ้างอิง และ 3 original concepts รอบถัดไปค่อยเพิ่มจำนวนตามเวลาตรวจของทีม ไม่เร่งผลิต 100 ภาพถ้าตรวจ caption และสิทธิ์ไม่ทัน

## 17. แผนต่อยอด 30 วัน

สัปดาห์ 1: รันกับธุรกิจจริงหนึ่งราย ตรวจ live Apify adapter ด้วยวงเงินที่กำหนด ตรวจ paid text adapter ถ้าจะใช้ และทำหนึ่งแพ็กผ่าน review ให้ครบเส้นทาง

สัปดาห์ 2: ทำชุดตัวอย่างรายอุตสาหกรรม แยก brand profile และ assets ให้ชัด เก็บเวลาตั้งแต่ brief ถึง approved pack เพื่อวัดคอขวดจริง

สัปดาห์ 3: เพิ่ม editable Canva template, formats 1:1 และ 9:16 ตาม placement ที่จะใช้ และปรับวิธี wrap ภาษาไทยจากผล QA เพิ่ม video export เมื่อมี use case จริง

สัปดาห์ 4: เพิ่ม student login กับ storage แยกผู้เรียน ถ้าต้องการคลัง private ร่วมกัน และเพิ่ม scheduled research เฉพาะเมื่อทีมกำหนดผู้รับผิดชอบและงบแล้ว เวอร์ชันนี้ไม่มี schedule ที่เปิดใช้งานอยู่

## 18. วัดประโยชน์จากงานที่เสร็จ

ตัวชี้วัดหลัก: เวลาจาก brief ถึง approved pack, สัดส่วนแพ็กที่ผ่าน QA รอบแรก, จำนวนแพ็กที่มี caption+ภาพครบ, อัตราลิงก์เสีย, ค่า scrape ต่อ reference ที่ใช้จริง และต้นทุนผลิตต่อแพ็กที่ผ่าน review

ฝั่งการตลาด: จำนวนแพ็กที่ถูกนำไปทดสอบจริง, qualified leads, cost per qualified lead และ sales ตามข้อมูลบัญชีผู้เรียน การเปรียบเทียบต้องระบุช่วงเวลา กลุ่มเป้าหมาย งบ และ conversion definition ให้ตรงกัน

ตัวอย่างเป้าทดลอง ไม่ใช่ผลวัดแล้ว: ถ้าเดิมใช้ 180 นาทีต่อแพ็ก และระบบใหม่ใช้ 45 นาที จะประหยัด 135 นาทีต่อแพ็ก หรือ 22.5 ชั่วโมงต่อ 10 แพ็ก ให้เก็บเวลาจริงอย่างน้อยหนึ่งรอบก่อนอ้างเป็นผลลัพธ์ของระบบ

งบรวมควรคิดจากค่า scrape + ค่า AI text/image + hosting/storage + เวลา review ยังไม่มีราคาปัจจุบันที่ยืนยันสำหรับทุกบริการในเอกสารนี้ งบตัวอย่างในคำสั่งเป็นเพดานที่ operator เลือก ไม่ใช่ราคาเหมาจ่ายของระบบ

## 19. สถานะส่งมอบและข้อจำกัด

สร้างแล้ว: engine CLI, import/normalize/dedupe, brief builder, optional AI copy adapter, typography PNG renderer, human approval receipt, ZIP export, static gallery, legacy migration, synthetic examples และ CI checks

ทดสอบแบบ offline แล้ว: caption line breaks, identity rejection, dedupe, dry-run ไม่เรียก paid API, quota bounds, approval invalidation, missing/corrupt asset handling, path traversal protection, safe catalog build, ZIP integrity และ no-overwrite behavior

ยังไม่รันแบบเสียเงินจริง: live Apify scrape และ OpenAI text generation จึงยังไม่เรียก provider integration ว่า live-verified ข้อมูล actor input และ API endpoint ตรวจจาก documentation ปัจจุบัน แต่ไม่มี output schema จาก connector ในรอบตรวจนี้ ต้องทดลองกับ sample ของ actor ก่อน scale

ยังไม่เปิดใช้: automatic image generation, Canva integration, video launch packs, authentication, per-student storage, schedule, analytics ingestion และ automatic ad launch งานผลิตภาพระดับ photo direction ยังเป็นขั้น manual ด้วยเครื่องมือที่ทีมเลือก

ตัวอย่าง 3 แพ็กเป็นงานสาธิตพร้อมภาพจริงและ caption แต่ตั้งใจล็อกไม่ให้ approved เพราะใช้ธุรกิจสมมติ ส่วน 675 legacy entries เป็น inventory ที่ต้องตรวจใหม่ ไม่มีการอ้างว่า approve หรือยิงแอดครบแล้ว

## 20. แหล่งอ้างอิงและจุดเปิดงาน

เว็บเดิม: https://limitless-ad-gallery-deploy.vercel.app/

Repo เดิม: https://github.com/jetlauncher/limitless-ad-system

Repo กระบวนการใหม่: https://github.com/jetlauncher/limitless-ad-engine

Apify Actor input: https://apify.com/apify/facebook-ads-scraper/input

Run Actor API และ spend cap: https://docs.apify.com/api/v2/actors-runs-post

Dataset pagination: https://docs.apify.com/api/v2/dataset-items-get

อ่าน README.md เพื่อเริ่มรัน ดู docs/source-audit.json เมื่อต้องตรวจ provenance และดู tests/test_engine.py เมื่อต้องขยายระบบโดยไม่ทำให้ขั้นตรวจเสีย
