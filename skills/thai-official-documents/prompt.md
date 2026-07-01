# Knowledge from Folder: thai-official-documents

## SKILL.md
```
---
name: thai-official-documents
description: สร้างหนังสือราชการไทยทุกชนิดเป็นไฟล์ Word (.docx) ตามระเบียบสำนักนายกรัฐมนตรีว่าด้วยงานสารบรรณ พ.ศ. ๒๕๒๖ และที่แก้ไขเพิ่มเติม ใช้ Skill นี้ทุกครั้งที่ผู้ใช้ต้องการร่าง/เขียน/จัดทำ เอกสารราชการ หนังสือราชการ หนังสือภายนอก หนังสือภายใน บันทึกข้อความ หนังสือประทับตรา คำสั่ง ระเบียบ ข้อบังคับ ประกาศ แถลงการณ์ หนังสือรับรอง รายงานการประชุม โครงการ (ขออนุมัติ) หรือคำกล่าวในพิธีการ แม้ผู้ใช้จะไม่ได้พูดคำว่า "หนังสือราชการ" ตรง ๆ เช่น "ร่างหนังสือเชิญประชุม", "ทำบันทึกขออนุมัติจัดซื้อ", "เขียนคำสั่งแต่งตั้งคณะกรรมการ", "ออกประกาศรับสมัครงาน" ก็ให้ใช้ Skill นี้
---

# การเขียนหนังสือราชการไทย (Thai Official Documents)

Skill นี้ช่วยร่างและจัดทำหนังสือราชการไทยให้ถูกต้องตาม **ระเบียบสำนักนายกรัฐมนตรีว่าด้วยงานสารบรรณ พ.ศ. ๒๕๒๖** (แก้ไขเพิ่มเติม ฉบับที่ ๒ พ.ศ. ๒๕๔๘, ฉบับที่ ๓ พ.ศ. ๒๕๖๐, ฉบับที่ ๔ พ.ศ. ๒๕๖๔ เรื่องสารบรรณอิเล็กทรอนิกส์) และผลิตเป็นไฟล์ Word (.docx) ที่จัดรูปแบบครบถ้วน ฟอนต์ **TH SarabunIT๙ ขนาด ๑๖ pt** ตามมาตรฐานราชการ

เป้าหมายคือให้เอกสารที่ได้ "พร้อมใช้" — เปิดใน Word แล้วแก้ไขต่อได้ทันที โดยรูปแบบ ระยะขอบ ครุฑ และตำแหน่งองค์ประกอบถูกต้องตามระเบียบ

## ชนิดของหนังสือราชการ (๖ ชนิด)

ก่อนเริ่ม ให้ระบุว่าผู้ใช้ต้องการหนังสือชนิดใด หากไม่ชัดให้ถามสั้น ๆ:

1. **หนังสือภายนอก** — ติดต่อระหว่างส่วนราชการ หรือถึงบุคคลภายนอก ใช้ครุฑ มีเลขที่หนังสือ คำขึ้นต้น "เรียน" คำลงท้าย "ขอแสดงความนับถือ"
2. **หนังสือภายใน (บันทึกข้อความ)** — ติดต่อภายในส่วนราชการเดียวกัน/กระทรวงเดียวกัน ใช้หัว "บันทึกข้อความ" + ครุฑเล็ก ไม่มีคำลงท้าย
3. **หนังสือประทับตรา** — ใช้ประทับตราแทนการลงชื่อ สำหรับเรื่องไม่สำคัญ เช่น ขอรายละเอียดเพิ่มเติม ตอบรับทราบ
4. **หนังสือสั่งการ** — คำสั่ง / ระเบียบ / ข้อบังคับ
5. **หนังสือประชาสัมพันธ์** — ประกาศ / แถลงการณ์ / ข่าว
6. **หนังสือที่เจ้าหน้าที่ทำขึ้นหรือรับไว้เป็นหลักฐาน** — หนังสือรับรอง / รายงานการประชุม / บันทึก / หนังสืออื่น

นอกจากนี้ยังรองรับเอกสารที่เกี่ยวข้องในงานราชการที่หนังสือต้นทางครอบคลุม: **โครงการเพื่อขออนุมัติ** และ **คำกล่าวในพิธีการ/โอกาสต่าง ๆ**

## ขั้นตอนการทำงาน

1. **ถามชนิดเอกสารก่อนเสมอ** — เปิดงานด้วยการถามผู้ใช้ว่าต้องการหนังสือชนิดใด โดยใช้เครื่องมือถามแบบตัวเลือก (AskUserQuestion) เสนอกลุ่มหลัก: บันทึกข้อความ (ภายใน), หนังสือภายนอก, คำสั่ง/ประกาศ, และอื่น ๆ (ระเบียบ ข้อบังคับ แถลงการณ์ หนังสือรับรอง รายงานการประชุม โครงการ คำกล่าว) ข้ามขั้นนี้ได้ก็ต่อเมื่อผู้ใช้ระบุชนิดมาแล้วอย่างชัดเจน หากผู้ใช้ตอบเป็นกลุ่มกว้าง (เช่น "คำสั่ง/ประกาศ") ให้ถามย่อยต่อว่าเป็นชนิดใดในกลุ่มนั้น
2. **อ่าน `references/formats.md`** เพื่อดูองค์ประกอบที่ต้องมีของเอกสารชนิดนั้น และสเปกรูปแบบ (ระยะขอบ ขนาดครุฑ การจัดวาง)
3. **เก็บข้อมูลที่จำเป็น** — ส่วนราชการเจ้าของหนังสือ, เลขที่, วันที่, เรื่อง, ผู้รับ, เนื้อหา, ผู้ลงนาม/ตำแหน่ง ฯลฯ ข้อมูลที่ผู้ใช้ไม่ได้ให้แต่จำเป็นต่อรูปแบบ ให้ใส่ placeholder ที่แก้ง่าย เช่น `(ระบุส่วนราชการ)` `๐ ๒xxx xxxx` และแจ้งผู้ใช้ว่าใส่ที่ใดไว้บ้าง อย่าแต่งข้อมูลที่เป็นข้อเท็จจริงเฉพาะ (ชื่อคน เลขที่จริง วันที่จริง) ขึ้นเอง
4. **ช่วยเรียบเรียงเนื้อหา** ให้เป็นภาษาราชการที่ถูกต้อง กระชับ สุภาพ ดู `references/formats.md` หัวข้อ "หลักการใช้ภาษาราชการ" และดูตัวอย่างใน `references/examples.md`
5. **สร้างไฟล์ .docx** โดยเขียน JSON spec แล้วเรียกสคริปต์ (ดูหัวข้อถัดไป) — อย่าสร้าง docx ด้วยมือทีละบรรทัด เพราะสคริปต์จัดการฟอนต์ ครุฑ และระยะขอบให้ถูกต้องแล้ว
6. **บันทึกลงโฟลเดอร์ของผู้ใช้** และนำเสนอไฟล์ให้ผู้ใช้เปิด/ดาวน์โหลด

## การสร้างไฟล์ .docx ด้วยสคริปต์

ใช้ `scripts/gen_official_doc.py` ซึ่งรับ JSON spec ทาง stdin หรือไฟล์ แล้วสร้าง .docx ที่จัดรูปแบบครบ:

```bash
python3 scripts/gen_official_doc.py spec.json output.docx
```

โครงสร้าง JSON ขึ้นกับ `doc_type` รายละเอียดฟิลด์ทั้งหมดของแต่ละชนิดอยู่ใน `references/formats.md` (มีตัวอย่าง spec ครบทุกชนิดในไฟล์ `references/examples.md` — คัดลอกมาปรับใช้ได้เลย)

`doc_type` ที่รองรับ: `external` (หนังสือภายนอก), `internal` (บันทึกข้อความ), `seal` (หนังสือประทับตรา), `command` (คำสั่ง), `regulation` (ระเบียบ), `bylaw` (ข้อบังคับ), `announcement` (ประกาศ), `statement` (แถลงการณ์), `certificate` (หนังสือรับรอง), `minutes` (รายงานการประชุม), `project` (โครงการ), `speech` (คำกล่าว)

ตัวอย่าง spec หนังสือภายนอกแบบย่อ:

```json
{
  "doc_type": "external",
  "agency_header": ["ที่ ศธ ๐๔๐๐๑/๑๒๓", "กรมส่งเสริมการเรียนรู้", "ถนนราชดำเนินนอก กทม. ๑๐๓๐๐"],
  "date": "๑๔ มิถุนายน ๒๕๖๙",
  "subject": "ขอเชิญประชุม",
  "salutation": "เรียน ผู้อำนวยการสำนักงานเขตพื้นที่การศึกษา",
  "references": [],
  "enclosures": ["ระเบียบวาระการประชุม จำนวน ๑ ชุด"],
  "body": ["ด้วย...", "จึงเรียนมาเพื่อ..."],
  "closing": "ขอแสดงความนับถือ",
  "signature": {"name": "(นาย...)", "position": "อธิบดีกรมส่งเสริมการเรียนรู้"},
  "contact": {"division": "สำนักอำนวยการ", "phone": "๐ ๒๒๘๐ ๒๙๓๐", "fax": "๐ ๒๒๘๐ ๒๙๓๑"}
}
```

## เรื่องครุฑ (สำคัญ)

หนังสือภายนอก หนังสือสั่งการ ประกาศ ฯลฯ ต้องมี **ตราครุฑ** ที่หัวกระดาษ (สูง ๓ ซม.) บันทึกข้อความใช้ครุฑเล็ก (สูง ๑.๕ ซม.)

- ถ้ามีไฟล์ภาพครุฑ ให้วางไว้ที่ `assets/krut.png` (พื้นหลังโปร่งใส) สคริปต์จะใส่ให้อัตโนมัติ
- ถ้าไม่มีไฟล์ภาพ สคริปต์จะใส่ตัวอักษร "(ตราครุฑ สูง ๓ ซม.)" ไว้แทนที่ เพื่อให้ผู้ใช้นำภาพครุฑจริงไปวางทับภายหลัง — ให้แจ้งผู้ใช้เรื่องนี้
- ตราครุฑเป็นเครื่องหมายราชการ ใช้ได้เฉพาะหนังสือของส่วนราชการจริงเท่านั้น

## หลักสำคัญ

- ฟอนต์มาตรฐานราชการคือ **TH SarabunIT๙ ขนาด ๑๖** (สคริปต์ตั้งให้แล้ว ทั้ง Latin และ Complex Script) หากผู้ใช้ระบุ TH SarabunPSK ก็ปรับได้ผ่านฟิลด์ `font`
- ใช้ **เลขไทย** (๐-๙) ในเนื้อหาหนังสือราชการตามธรรมเนียม เว้นแต่ผู้ใช้ขอเลขอารบิก
- อย่าเดาข้อเท็จจริง (ชื่อ ตำแหน่ง เลขที่ วันที่จริง) — ใช้ placeholder และบอกผู้ใช้
- ดูรายละเอียดรูปแบบทั้งหมดใน `references/formats.md` และตัวอย่างเต็มใน `references/examples.md` ก่อนสร้างเอกสารที่ไม่คุ้นเคย

```

## assets\README.md
```
# assets

วางไฟล์ภาพ **ตราครุฑ** ชื่อ `krut.png` (พื้นหลังโปร่งใส) ไว้ในโฟลเดอร์นี้
สคริปต์ `gen_official_doc.py` จะนำไปวางที่หัวกระดาษให้อัตโนมัติ:
- หนังสือภายนอก / คำสั่ง / ระเบียบ / ประกาศ ฯลฯ → ครุฑสูง ๓ ซม. กึ่งกลาง
- บันทึกข้อความ → ครุฑสูง ๑.๕ ซม. มุมบนซ้าย

หากไม่มีไฟล์ `krut.png` สคริปต์จะใส่ข้อความ "(ตราครุฑ สูง ๓ ซม.)" ไว้แทน
เพื่อให้นำภาพครุฑจริงไปวางทับในภายหลัง

ตราครุฑเป็นเครื่องหมายราชการ ใช้กับหนังสือของส่วนราชการจริงเท่านั้น

```

## references\examples.md
```
# ตัวอย่าง JSON spec ครบทุกชนิด

คัดลอกและปรับค่าตามเรื่องจริง แล้วบันทึกเป็น `spec.json` รันด้วย
`python3 scripts/gen_official_doc.py spec.json output.docx`
ค่าที่ยังไม่ทราบให้ใส่ placeholder เช่น `(ระบุชื่อ)` `(...)`

## หนังสือภายนอก
```json
{
  "doc_type": "external",
  "agency_header": ["ที่ ศธ ๐๔๐๐๑/ว ๑๒๓", "กรมส่งเสริมการเรียนรู้", "ถนนราชดำเนินนอก เขตดุสิต กรุงเทพมหานคร ๑๐๓๐๐"],
  "date": "๑๔ มิถุนายน ๒๕๖๙",
  "subject": "ขอเชิญประชุมคณะกรรมการพัฒนาหลักสูตร",
  "salutation": "เรียน  ผู้อำนวยการสำนักงานเขตพื้นที่การศึกษาประถมศึกษา ทุกเขต",
  "references": ["หนังสือกรมส่งเสริมการเรียนรู้ ที่ ศธ ๐๔๐๐๑/ว ๑๐๐ ลงวันที่ ๑ พฤษภาคม ๒๕๖๙"],
  "enclosures": ["ระเบียบวาระการประชุม จำนวน ๑ ชุด"],
  "body": [
    "ด้วยกรมส่งเสริมการเรียนรู้กำหนดจัดประชุมคณะกรรมการพัฒนาหลักสูตร เพื่อพิจารณาแนวทางการปรับปรุงหลักสูตรให้สอดคล้องกับนโยบายของกระทรวง ในวันที่ ๒๕ มิถุนายน ๒๕๖๙ เวลา ๐๙.๐๐ น. ณ ห้องประชุม ๑ กรมส่งเสริมการเรียนรู้",
    "ในการนี้ จึงขอเชิญท่านหรือผู้แทนเข้าร่วมประชุมตามวัน เวลา และสถานที่ดังกล่าว และขอความกรุณาแจ้งรายชื่อผู้เข้าร่วมประชุมภายในวันที่ ๒๐ มิถุนายน ๒๕๖๙",
    "จึงเรียนมาเพื่อโปรดพิจารณาเข้าร่วมประชุมตามวัน เวลา และสถานที่ดังกล่าวด้วย จะขอบคุณยิ่ง"
  ],
  "closing": "ขอแสดงความนับถือ",
  "signature": {"name": "(นาย................................)", "position": "อธิบดีกรมส่งเสริมการเรียนรู้"},
  "contact": {"division": "สำนักอำนวยการ  กลุ่มบริหารงานทั่วไป", "phone": "๐ ๒๒๘๐ ๒๙๓๐", "fax": "๐ ๒๒๘๐ ๒๙๓๑"}
}
```

## บันทึกข้อความ (หนังสือภายใน)
```json
{
  "doc_type": "internal",
  "agency": "กลุ่มบริหารงานบุคคล  สำนักอำนวยการ",
  "phone": "๐ ๒๒๘๐ ๒๙๓๕",
  "doc_no": "ศธ ๐๔๐๐๑.๑/๔๕",
  "date": "๑๔ มิถุนายน ๒๕๖๙",
  "subject": "ขออนุมัติจัดซื้อวัสดุสำนักงาน",
  "salutation": "เรียน  ผู้อำนวยการสำนักอำนวยการ",
  "body": [
    "ด้วยกลุ่มบริหารงานบุคคลมีความจำเป็นต้องจัดซื้อวัสดุสำนักงานเพื่อใช้ในการปฏิบัติงาน เนื่องจากวัสดุคงเหลือไม่เพียงพอ รวมเป็นเงินทั้งสิ้น ๑๕,๐๐๐ บาท (หนึ่งหมื่นห้าพันบาทถ้วน) รายละเอียดตามเอกสารแนบ",
    "จึงเรียนมาเพื่อโปรดพิจารณาอนุมัติ"
  ],
  "signature": {"name": "(นาง................................)", "position": "หัวหน้ากลุ่มบริหารงานบุคคล"}
}
```

## หนังสือประทับตรา
```json
{
  "doc_type": "seal",
  "agency_header": ["ที่ ศธ ๐๔๐๐๑/๒๒๒"],
  "to": "ผู้อำนวยการโรงเรียนบ้านหนองแก",
  "body": [
    "ตามที่โรงเรียนได้ส่งรายงานผลการดำเนินงานประจำปีมายังกรมส่งเสริมการเรียนรู้นั้น กรมขอให้ส่งเอกสารหลักฐานการเบิกจ่ายเพิ่มเติม เพื่อประกอบการตรวจสอบ ภายในวันที่ ๓๐ มิถุนายน ๒๕๖๙"
  ],
  "agency_name": "กรมส่งเสริมการเรียนรู้",
  "date": "๑๔ มิถุนายน ๒๕๖๙",
  "contact": {"division": "สำนักอำนวยการ", "phone": "๐ ๒๒๘๐ ๒๙๓๐"}
}
```

## คำสั่ง
```json
{
  "doc_type": "command",
  "agency_name": "กรมส่งเสริมการเรียนรู้",
  "doc_no": "ที่ ๑๒๓/๒๕๖๙",
  "subject": "แต่งตั้งคณะกรรมการพัฒนาหลักสูตร",
  "preamble": [
    "เพื่อให้การพัฒนาหลักสูตรของกรมส่งเสริมการเรียนรู้เป็นไปด้วยความเรียบร้อยและมีประสิทธิภาพ อาศัยอำนาจตามความในมาตรา ๓๒ แห่งพระราชบัญญัติระเบียบบริหารราชการแผ่นดิน พ.ศ. ๒๕๓๔ จึงแต่งตั้งคณะกรรมการพัฒนาหลักสูตร ดังนี้"
  ],
  "clauses": [
    {"no": "๑", "text": "นาย............................  อธิบดีกรมส่งเสริมการเรียนรู้  เป็นประธานกรรมการ"},
    {"no": "๒", "text": "นาง............................  รองอธิบดี  เป็นรองประธานกรรมการ"},
    {"no": "๓", "text": "ผู้อำนวยการสำนักวิชาการ  เป็นกรรมการและเลขานุการ"}
  ],
  "effective": "ทั้งนี้ ตั้งแต่บัดนี้เป็นต้นไป",
  "ordered_date": "สั่ง ณ วันที่ ๑๔ มิถุนายน พ.ศ. ๒๕๖๙",
  "signature": {"name": "(นาย................................)", "position": "อธิบดีกรมส่งเสริมการเรียนรู้"}
}
```

## ระเบียบ
```json
{
  "doc_type": "regulation",
  "agency_name": "กรมส่งเสริมการเรียนรู้",
  "title": "การใช้ห้องสมุดประชาชน",
  "year": "๒๕๖๙",
  "preamble": [
    "โดยที่เป็นการสมควรกำหนดระเบียบการใช้ห้องสมุดประชาชนให้เหมาะสม อาศัยอำนาจตามความในมาตรา ๓๒ แห่งพระราชบัญญัติระเบียบบริหารราชการแผ่นดิน พ.ศ. ๒๕๓๔ จึงวางระเบียบไว้ ดังต่อไปนี้"
  ],
  "clauses": [
    {"no": "๑", "text": "ระเบียบนี้เรียกว่า \"ระเบียบกรมส่งเสริมการเรียนรู้ ว่าด้วยการใช้ห้องสมุดประชาชน พ.ศ. ๒๕๖๙\""},
    {"no": "๒", "text": "ระเบียบนี้ให้ใช้บังคับตั้งแต่วันถัดจากวันประกาศเป็นต้นไป"},
    {"no": "๓", "text": "ผู้ใช้บริการต้องแต่งกายสุภาพ และปฏิบัติตามคำแนะนำของเจ้าหน้าที่"}
  ],
  "announced_date": "ประกาศ ณ วันที่ ๑๔ มิถุนายน พ.ศ. ๒๕๖๙",
  "signature": {"name": "(นาย................................)", "position": "อธิบดีกรมส่งเสริมการเรียนรู้"}
}
```

## ข้อบังคับ
ใช้โครงสร้างเดียวกับ "ระเบียบ" เปลี่ยน `"doc_type": "bylaw"`

## ประกาศ
```json
{
  "doc_type": "announcement",
  "agency_name": "กรมส่งเสริมการเรียนรู้",
  "subject": "รับสมัครบุคคลเพื่อเลือกสรรเป็นพนักงานราชการทั่วไป",
  "body": [
    "ด้วยกรมส่งเสริมการเรียนรู้ประสงค์จะรับสมัครบุคคลเพื่อจัดจ้างเป็นพนักงานราชการทั่วไป ฉะนั้น อาศัยอำนาจตามประกาศคณะกรรมการบริหารพนักงานราชการ จึงประกาศรับสมัครบุคคล ดังรายละเอียดต่อไปนี้",
    "๑. ตำแหน่งที่รับสมัคร  นักวิชาการศึกษา จำนวน ๒ อัตรา",
    "๒. ผู้สมัครต้องสำเร็จการศึกษาระดับปริญญาตรีทุกสาขา",
    "๓. กำหนดรับสมัครตั้งแต่วันที่ ๒๐ – ๓๐ มิถุนายน ๒๕๖๙ ในวันและเวลาราชการ"
  ],
  "announced_date": "ประกาศ ณ วันที่ ๑๔ มิถุนายน พ.ศ. ๒๕๖๙",
  "signature": {"name": "(นาย................................)", "position": "อธิบดีกรมส่งเสริมการเรียนรู้"}
}
```

## แถลงการณ์
```json
{
  "doc_type": "statement",
  "agency_name": "กรมส่งเสริมการเรียนรู้",
  "subject": "ชี้แจงกรณีข่าวการปรับหลักสูตร",
  "body": [
    "ตามที่มีการเผยแพร่ข้อมูลเกี่ยวกับการปรับหลักสูตรของกรมส่งเสริมการเรียนรู้นั้น กรมขอเรียนชี้แจงข้อเท็จจริงเพื่อความเข้าใจที่ถูกต้อง ดังนี้"
  ],
  "announced_date": "วันที่ ๑๔ มิถุนายน ๒๕๖๙"
}
```

## หนังสือรับรอง
```json
{
  "doc_type": "certificate",
  "agency_header": ["ที่ ศธ ๐๔๐๐๑/๓๓๓"],
  "doc_no": "เลขที่ ๓๓๓/๒๕๖๙",
  "body": [
    "หนังสือฉบับนี้ให้ไว้เพื่อรับรองว่า นาย............................ เป็นข้าราชการพลเรือนสามัญ ตำแหน่งนักวิชาการศึกษาชำนาญการ สังกัดกรมส่งเสริมการเรียนรู้ ได้รับเงินเดือนในอัตราเดือนละ ........ บาท จริง",
    "ให้ไว้เพื่อใช้เป็นหลักฐานประกอบการขอสินเชื่อกับสถาบันการเงิน"
  ],
  "given_date": "ให้ไว้ ณ วันที่ ๑๔ มิถุนายน พ.ศ. ๒๕๖๙",
  "signature": {"name": "(นาง................................)", "position": "ผู้อำนวยการสำนักอำนวยการ"}
}
```

## รายงานการประชุม
```json
{
  "doc_type": "minutes",
  "meeting_name": "คณะกรรมการพัฒนาหลักสูตร",
  "time": ["ครั้งที่ ๓/๒๕๖๙", "เมื่อวันที่ ๒๕ มิถุนายน ๒๕๖๙ เวลา ๐๙.๐๐ น.", "ณ ห้องประชุม ๑ กรมส่งเสริมการเรียนรู้"],
  "attendees": [
    "นาย............................  อธิบดี  ประธานกรรมการ",
    "นาง............................  รองอธิบดี  รองประธานกรรมการ",
    "ผู้อำนวยการสำนักวิชาการ  กรรมการและเลขานุการ"
  ],
  "absentees": ["นาย............................  ติดราชการ"],
  "start_time": "๐๙.๐๐ น.",
  "agenda": [
    {"no": "๑", "title": "เรื่องที่ประธานแจ้งให้ที่ประชุมทราบ", "content": ["ประธานแจ้งว่า..."]},
    {"no": "๒", "title": "เรื่องรับรองรายงานการประชุมครั้งที่ ๒/๒๕๖๙", "content": ["ที่ประชุมมีมติรับรองรายงานการประชุมโดยไม่มีการแก้ไข"]},
    {"no": "๓", "title": "เรื่องเพื่อพิจารณา", "content": ["ที่ประชุมพิจารณาแนวทางการปรับปรุงหลักสูตร และมีมติ..."]},
    {"no": "๔", "title": "เรื่องอื่น ๆ", "content": ["ไม่มี"]}
  ],
  "end_time": "๑๒.๐๐ น.",
  "recorder": {"name": "นางสาว............................", "position": "ผู้จดรายงานการประชุม"},
  "checker": {"name": "นาง............................", "position": "ผู้ตรวจรายงานการประชุม"}
}
```

## โครงการ
```json
{
  "doc_type": "project",
  "project_name": "ส่งเสริมการอ่านสำหรับชุมชน ประจำปีงบประมาณ ๒๕๖๙",
  "principle": ["ด้วยกรมส่งเสริมการเรียนรู้ตระหนักถึงความสำคัญของการอ่าน จึงจัดทำโครงการนี้เพื่อ..."],
  "objectives": ["เพื่อส่งเสริมนิสัยรักการอ่านของประชาชนในชุมชน", "เพื่อเพิ่มจำนวนผู้ใช้บริการห้องสมุดประชาชน"],
  "targets": ["เชิงปริมาณ: ประชาชนเข้าร่วมไม่น้อยกว่า ๕๐๐ คน", "เชิงคุณภาพ: ผู้เข้าร่วมมีความพึงพอใจไม่น้อยกว่าร้อยละ ๘๐"],
  "methods": ["จัดกิจกรรมส่งเสริมการอ่านในห้องสมุดประชาชน", "จัดนิทรรศการหนังสือ"],
  "duration": "เดือนกรกฎาคม – กันยายน ๒๕๖๙",
  "place": "ห้องสมุดประชาชนประจำอำเภอ",
  "budget": "๑๐๐,๐๐๐ บาท (หนึ่งแสนบาทถ้วน)",
  "responsible": "กลุ่มส่งเสริมการเรียนรู้",
  "evaluation": ["แบบสอบถามความพึงพอใจ", "สถิติจำนวนผู้เข้าร่วม"],
  "outcomes": ["ประชาชนมีนิสัยรักการอ่านเพิ่มขึ้น", "ห้องสมุดประชาชนมีผู้ใช้บริการเพิ่มขึ้น"]
}
```

## คำกล่าวในพิธีการ
```json
{
  "doc_type": "speech",
  "title": "คำกล่าวรายงานในพิธีเปิดโครงการส่งเสริมการอ่านสำหรับชุมชน",
  "greeting": ["เรียน  ท่านประธานในพิธีที่เคารพ", "และท่านผู้มีเกียรติทุกท่าน"],
  "body": [
    "กระผมในนามของคณะกรรมการจัดงาน ขอขอบพระคุณท่านประธานที่ได้ให้เกียรติมาเป็นประธานในพิธีเปิดโครงการในวันนี้",
    "โครงการนี้จัดขึ้นโดยมีวัตถุประสงค์เพื่อ..."
  ],
  "closing": ["บัดนี้ ได้เวลาอันสมควรแล้ว กระผมขอเรียนเชิญท่านประธานกล่าวเปิดโครงการ และให้โอวาทแก่ผู้เข้าร่วมงาน ต่อไป"]
}
```

```

## references\formats.md
```
# รูปแบบหนังสือราชการตามระเบียบงานสารบรรณ

อ้างอิง: ระเบียบสำนักนายกรัฐมนตรีว่าด้วยงานสารบรรณ พ.ศ. ๒๕๒๖ และที่แก้ไขเพิ่มเติม (ฉบับที่ ๒ พ.ศ. ๒๕๔๘, ฉบับที่ ๓ พ.ศ. ๒๕๖๐, ฉบับที่ ๔ พ.ศ. ๒๕๖๔) ประกอบกับหนังสือ "การเขียนในงานราชการไทย" (ผศ.ว่าที่ร้อยเอก ดร.ธนู ทดแทนคุณ)

## สารบัญ
1. สเปกรูปแบบมาตรฐาน (ทุกชนิด)
2. หนังสือภายนอก (external)
3. หนังสือภายใน / บันทึกข้อความ (internal)
4. หนังสือประทับตรา (seal)
5. คำสั่ง (command)
6. ระเบียบ (regulation)
7. ข้อบังคับ (bylaw)
8. ประกาศ (announcement)
9. แถลงการณ์ (statement)
10. หนังสือรับรอง (certificate)
11. รายงานการประชุม (minutes)
12. โครงการ (project)
13. คำกล่าวในพิธีการ (speech)
14. หลักการใช้ภาษาราชการ
15. คำขึ้นต้น–สรรพนาม–คำลงท้าย ตามฐานะผู้รับ
16. การแยกคำ / ตัดคำท้ายบรรทัด (ยัติภังค์)

---

## ๑. สเปกรูปแบบมาตรฐาน (ทุกชนิด)

- **กระดาษ:** A4 (๒๑๐ x ๒๙๗ มม.)
- **ฟอนต์:** TH SarabunIT๙ (หรือ TH SarabunPSK) ขนาด ๑๖ pt เป็นมาตรฐาน หัวเรื่องบางส่วน เช่น คำว่า "บันทึกข้อความ" "ประกาศ" "คำสั่ง" ใช้ขนาดใหญ่ขึ้น (๒๙–๓๖ pt ตามระเบียบ)
- **ระยะขอบ:** ขอบบน ~๑.๕ นิ้ว (ระยะจากขอบบนถึงครุฑ ๓ ซม. / ถึงตัวอักษรแรก ~๒.๕ ซม.), ขอบซ้าย ๓ ซม., ขอบขวา ๒ ซม., ขอบล่าง ~๒ ซม.
- **ระยะบรรทัด:** ๑ เท่า (single) โดยมีระยะก่อนย่อหน้าพอเหมาะ; ระหว่างหัวเรื่องต่าง ๆ เว้น ๑ บรรทัดเปล่า (ขนาด ๖ pt ตามระเบียบกำหนด "บรรทัด ๖ พอยต์")
- **ครุฑ:** หนังสือภายนอก/สั่งการ/ประชาสัมพันธ์ ใช้ครุฑสูง ๓ ซม. กึ่งกลางหน้ากระดาษด้านบน; บันทึกข้อความใช้ครุฑสูง ๑.๕ ซม. มุมบนซ้าย
- **เลข:** ใช้เลขไทย ๐๑๒๓๔๕๖๗๘๙ ในตัวเนื้อหา
- **การย่อหน้า:** ย่อหน้าแรกของแต่ละข้อความเยื้องเข้าจากกั้นหน้า (~๒.๕ ซม. / ๑ Tab)

---

## ๒. หนังสือภายนอก (doc_type: external)

หนังสือติดต่อราชการที่เป็นแบบพิธี ใช้กระดาษครุฑ องค์ประกอบเรียงตามลำดับ:

1. **ที่** — เลขที่หนังสือ (มุมบนซ้าย) เช่น `ที่ ศธ ๐๔๐๐๑/ว ๑๒๓`
2. **ส่วนราชการเจ้าของหนังสือ** — ใต้ครุฑ กึ่งกลาง บรรทัดถัดมาเป็นที่ตั้ง/ที่อยู่ (ชิดขวาของกลางหน้า หรือจัดตามแบบ) — ในสคริปต์ใส่เป็น `agency_header` (อาร์เรย์: บรรทัด ที่/ชื่อส่วนราชการ/ที่อยู่)
3. **วัน เดือน ปี** — กึ่งกลาง ไม่มีคำว่า "วันที่" เช่น `๑๔ มิถุนายน ๒๕๖๙`
4. **เรื่อง** — `เรื่อง  ...` (ย่อ กระชับ เป็นใจความสำคัญ)
5. **คำขึ้นต้น** — `เรียน  ...` (ตามฐานะผู้รับ ดูข้อ ๑๕)
6. **อ้างถึง** (ถ้ามี) — อ้างหนังสือที่เคยติดต่อกันมาก่อน
7. **สิ่งที่ส่งมาด้วย** (ถ้ามี) — ระบุสิ่งที่ส่งแนบและจำนวน
8. **ข้อความ (เนื้อหา)** — แบ่งเป็นย่อหน้า โดยทั่วไป: เหตุที่มีหนังสือ → รายละเอียด → จุดประสงค์/คำขอ และปิดท้ายด้วย "จึงเรียนมาเพื่อ..."
9. **คำลงท้าย** — `ขอแสดงความนับถือ` (กึ่งกลางค่อนไปทางขวา) ตามฐานะผู้รับ (ดูข้อ ๑๕)
10. **ลงชื่อ** — ชื่อผู้ลงนาม (อยู่ในวงเล็บ) และ **ตำแหน่ง** ใต้ชื่อ
11. **ส่วนราชการเจ้าของเรื่อง** — ชื่อหน่วยงานย่อยที่รับผิดชอบ + **โทร./โทรสาร** (มุมล่างซ้าย ขนาดเล็กลงได้)
12. **สำเนาส่ง** (ถ้ามี)

JSON fields: `agency_header[]`, `date`, `subject`, `salutation`, `references[]`, `enclosures[]`, `body[]`, `closing`, `signature{name,position}`, `contact{division,phone,fax}`, `cc[]`(optional), `font`(optional), `use_arabic`(optional)

---

## ๓. หนังสือภายใน / บันทึกข้อความ (doc_type: internal)

ใช้ติดต่อภายในกระทรวง/กรม/หน่วยงานเดียวกัน หัวกระดาษเป็นแบบ "บันทึกข้อความ"

โครงสร้างหัว:
- ครุฑเล็ก (๑.๕ ซม.) มุมบนซ้าย ใต้ครุฑมีคำว่า **บันทึกข้อความ** (ตัวใหญ่ กึ่งกลาง)
- **ส่วนราชการ** ........ (ชื่อหน่วยงานเจ้าของบันทึก + โทร.)
- **ที่** ........  **วันที่** ........
- **เรื่อง** ........
- **คำขึ้นต้น** `เรียน  ...`
- **ข้อความ** — เนื้อหา ปิดท้าย "จึงเรียนมาเพื่อโปรด..." (เช่น เพื่อโปรดทราบ / พิจารณา / อนุมัติ)
- **ลงชื่อ + ตำแหน่ง** (ไม่มีคำลงท้ายแบบ "ขอแสดงความนับถือ")

JSON fields: `agency` (ส่วนราชการ), `phone`(optional), `doc_no` (ที่), `date`, `subject`, `salutation`, `body[]`, `signature{name,position}`, `font`(optional)

---

## ๔. หนังสือประทับตรา (doc_type: seal)

ใช้ประทับตราส่วนราชการแทนการลงชื่อ สำหรับเรื่องที่ไม่สำคัญ เช่น ขอรายละเอียดเพิ่มเติม ส่งสำเนา ตอบรับ ใช้ครุฑ
องค์ประกอบ:
- ครุฑ + คำว่า "ที่" (เลขที่)
- ข้อความขึ้นต้น `ถึง  ...` (ใช้ "ถึง" ไม่ใช่ "เรียน")
- ข้อความ (เนื้อหา)
- ชื่อส่วนราชการที่ส่ง
- ที่ประทับตราชื่อส่วนราชการ + ลงชื่อย่อกำกับตรา
- วัน เดือน ปี
- ส่วนราชการเจ้าของเรื่อง + โทร.

JSON fields: `agency_header[]`, `to` (ถึง...), `body[]`, `agency_name`, `date`, `contact{division,phone}`

---

## ๕. คำสั่ง (doc_type: command)

หนังสือสั่งการให้ปฏิบัติ ใช้ครุฑ
องค์ประกอบ:
- ครุฑ กึ่งกลาง
- **คำสั่ง**(ชื่อส่วนราชการ) — กึ่งกลาง
- **ที่** .../(พ.ศ.) — กึ่งกลาง
- **เรื่อง** ........ — กึ่งกลาง
- บรรทัดคั่น (เส้นใต้/เว้นวรรค)
- ข้อความนำ (อ้างเหตุ/อำนาจตามกฎหมาย) เช่น "อาศัยอำนาจตามความใน..."
- เนื้อหาคำสั่ง (มักแบ่งเป็นข้อ ๑, ๒, ๓)
- "ทั้งนี้ ตั้งแต่..." (วันที่มีผลบังคับ)
- "สั่ง ณ วันที่ ........"
- ลงชื่อ + ตำแหน่ง

JSON fields: `agency_name`, `doc_no` (ที่...), `subject`, `preamble[]`, `clauses[]`, `effective` (ทั้งนี้ ตั้งแต่...), `ordered_date` (สั่ง ณ วันที่...), `signature{name,position}`

---

## ๖. ระเบียบ (doc_type: regulation)

โครงสร้างคล้ายคำสั่ง แต่หัวเป็น **ระเบียบ**(ส่วนราชการ) **ว่าด้วย** ........ **พ.ศ.** ....
- ข้อความนำ "โดยที่เป็นการสมควร..." + "อาศัยอำนาจตาม..."
- แบ่งเป็น **ข้อ** มีข้อ ๑ ชื่อระเบียบ, ข้อ ๒ วันใช้บังคับ, ข้อถัดไปเป็นสาระ
- "ประกาศ ณ วันที่ ........"
- ลงชื่อ + ตำแหน่ง

JSON fields: `agency_name`, `title` (ว่าด้วย...), `year` (พ.ศ.), `preamble[]`, `clauses[]` (แต่ละข้อ {no, text}), `announced_date`, `signature{name,position}`

---

## ๗. ข้อบังคับ (doc_type: bylaw)

เหมือนระเบียบ แต่หัวเป็น **ข้อบังคับ**(ส่วนราชการ/องค์กร) **ว่าด้วย** .... **พ.ศ.** .... ใช้ JSON fields เดียวกับ regulation

---

## ๘. ประกาศ (doc_type: announcement)

หนังสือประชาสัมพันธ์ ใช้ครุฑ
- ครุฑ กึ่งกลาง
- **ประกาศ**(ส่วนราชการ) — กึ่งกลาง
- **เรื่อง** ........ — กึ่งกลาง
- ข้อความ (เนื้อหา) อาจแบ่งเป็นข้อ
- "ประกาศ ณ วันที่ ........"
- ลงชื่อ + ตำแหน่ง

JSON fields: `agency_name`, `subject`, `body[]`, `announced_date`, `signature{name,position}`

---

## ๙. แถลงการณ์ (doc_type: statement)

ชี้แจง/ทำความเข้าใจเรื่องใดเรื่องหนึ่งต่อประชาชน
- ครุฑ + **แถลงการณ์**(ส่วนราชการ)
- **เรื่อง** ........
- ข้อความ
- ส่วนราชการที่ออกแถลงการณ์ + วัน เดือน ปี

JSON fields: `agency_name`, `subject`, `body[]`, `announced_date`

---

## ๑๐. หนังสือรับรอง (doc_type: certificate)

รับรองบุคคล/นิติบุคคล/ข้อเท็จจริง ใช้ครุฑ
- ครุฑ + **ที่** (เลขที่หนังสือรับรอง)
- **หนังสือฉบับนี้ให้ไว้เพื่อรับรองว่า** ........
- ข้อความรายละเอียด
- "ให้ไว้ ณ วันที่ ........"
- ลงชื่อ + ตำแหน่ง
- (รูปถ่าย/ลายมือชื่อผู้ได้รับการรับรอง ถ้าเป็นการรับรองบุคคล)

JSON fields: `agency_header[]`, `doc_no`, `body[]`, `given_date`, `signature{name,position}`

---

## ๑๑. รายงานการประชุม (doc_type: minutes)

องค์ประกอบ:
- **รายงานการประชุม** ........ (ชื่อการประชุม) — กึ่งกลาง
- **ครั้งที่** ..../.... 
- **เมื่อ** วัน เดือน ปี เวลา
- **ณ** สถานที่
- **ผู้มาประชุม** (รายชื่อ + ตำแหน่ง เรียงลำดับ)
- **ผู้ไม่มาประชุม** (ถ้ามี พร้อมเหตุผล)
- **ผู้เข้าร่วมประชุม** (ถ้ามี)
- **เริ่มประชุมเวลา** ........
- **ระเบียบวาระ** เรียงเป็นวาระ: วาระที่ ๑ เรื่องที่ประธานแจ้งให้ทราบ, วาระที่ ๒ รับรองรายงานการประชุมครั้งก่อน, วาระที่ ๓ เรื่องสืบเนื่อง, วาระที่ ๔ เรื่องเพื่อพิจารณา, วาระที่ ๕ เรื่องอื่น ๆ
- **เลิกประชุมเวลา** ........
- **ผู้จดรายงานการประชุม** (ลงชื่อ)
- **ผู้ตรวจรายงานการประชุม** (ลงชื่อ)

JSON fields: `meeting_name`, `time` (ครั้งที่/เมื่อ/ณ), `attendees[]`, `absentees[]`, `participants[]`, `start_time`, `agenda[]` (แต่ละวาระ {no, title, content[]}), `end_time`, `recorder{name,position}`, `checker{name,position}`

---

## ๑๒. โครงการ (doc_type: project)

โครงการเพื่อเสนอขออนุมัติ องค์ประกอบหลัก:
1. ชื่อโครงการ
2. หลักการและเหตุผล
3. วัตถุประสงค์
4. เป้าหมาย (เชิงปริมาณ/คุณภาพ)
5. วิธีดำเนินการ / ขั้นตอน
6. ระยะเวลาดำเนินการ
7. สถานที่
8. งบประมาณ
9. ผู้รับผิดชอบโครงการ
10. การประเมินผล
11. ผลที่คาดว่าจะได้รับ

JSON fields: `project_name`, `principle[]`, `objectives[]`, `targets[]`, `methods[]`, `duration`, `place`, `budget`, `responsible`, `evaluation[]`, `outcomes[]`

---

## ๑๓. คำกล่าวในพิธีการ (doc_type: speech)

เช่น คำกล่าวรายงาน คำกล่าวเปิด-ปิดงาน สุนทรพจน์ องค์ประกอบ:
- คำขึ้นต้นทักทายผู้มีเกียรติ (เรียงตามลำดับอาวุโส/ตำแหน่ง)
- อารัมภบท / ที่มา
- เนื้อหาสาระ
- คำลงท้าย / อวยพร / กล่าวเปิด-ปิด

JSON fields: `title`, `greeting[]`, `body[]`, `closing[]`

---

## ๑๔. หลักการใช้ภาษาราชการ

- ใช้ภาษาสุภาพ เป็นทางการ กระชับ ชัดเจน ตรงประเด็น หลีกเลี่ยงคำฟุ่มเฟือยและภาษาพูด
- ใช้คำราชาศัพท์ให้ถูกต้องเมื่อเกี่ยวข้องกับสถาบันพระมหากษัตริย์/พระบรมวงศานุวงศ์
- ขึ้นต้นเนื้อหาด้วยเหตุ ("ด้วย" / "เนื่องด้วย" / "ตามที่...นั้น") แล้วจึงเข้าสู่รายละเอียดและจุดประสงค์
- ปิดเนื้อหาด้วยประโยคแสดงความประสงค์: หนังสือภายนอก "จึงเรียนมาเพื่อโปรดพิจารณา/ทราบ"; บันทึกข้อความ "จึงเรียนมาเพื่อโปรดทราบ/พิจารณา/อนุมัติ"
- เรื่อง (subject) ต้องสั้น เป็นนามวลี จับใจความได้ว่าหนังสือเกี่ยวกับอะไร
- ใช้คำว่า "ข้าพเจ้า/กระผม/ดิฉัน" ตามความเหมาะสม แต่ในหนังสือราชการมักใช้ในนามส่วนราชการ

---

## ๑๕. คำขึ้นต้น–สรรพนาม–คำลงท้าย ตามฐานะผู้รับ

(สรุปจากระเบียบงานสารบรรณ ภาคผนวก) ปรับตามฐานะของผู้รับ:

| ผู้รับ | คำขึ้นต้น | สรรพนามแทนผู้รับ | คำลงท้าย |
|---|---|---|---|
| บุคคลทั่วไป / ข้าราชการทั่วไป | เรียน | ท่าน | ขอแสดงความนับถือ |
| ผู้ดำรงตำแหน่งสูง (รัฐมนตรี ปลัดฯ อธิบดี ฯลฯ) | เรียน | ท่าน | ขอแสดงความนับถืออย่างยิ่ง (กรณีให้เกียรติสูง) |
| ประธานองคมนตรี/นายกรัฐมนตรี/ประธานรัฐสภา/ประธานศาลฎีกา ฯลฯ | กราบเรียน | ท่าน | ขอแสดงความนับถืออย่างยิ่ง |
| พระภิกษุทั่วไป | นมัสการ | พระคุณเจ้า/ท่าน | ขอนมัสการด้วยความเคารพ |
| สมเด็จพระสังฆราช | กราบทูล | ฝ่าพระบาท | ควรมิควรแล้วแต่จะโปรด |

หมายเหตุ: กรณีกราบบังคมทูล/กราบทูลพระบรมวงศานุวงศ์ มีแบบเฉพาะ ให้ตรวจสอบภาคผนวกระเบียบงานสารบรรณและราชาศัพท์เป็นกรณีไป

---

## ๑๖. การแยกคำ / ตัดคำท้ายบรรทัด (ยัติภังค์)

เมื่อคำหรือชื่อยาวพิมพ์ไม่พอในบรรทัดเดียวและต้องขึ้นบรรทัดใหม่ มี ๒ กรณี:

- **ก. แยกได้โดยไม่ต้องใช้ยัติภังค์** — เมื่อแยกออกเป็น "นามทั่วไป + นามเฉพาะ" แล้วแต่ละส่วนมีความหมายสมบูรณ์ในตัว ขึ้นบรรทัดใหม่ได้เลย ไม่ต้องมี `-` เช่น มหาวิทยาลัย / นเรศวร · กระทรวง / มหาดไทย · สำนัก / งบประมาณกรุงเทพมหานคร
- **ข. ต้องใช้ยัติภังค์ (-)** — เมื่อคำนั้นแยกแล้วความหมายไม่สมบูรณ์ คือต่อพยางค์หรือเป็นคำสมาส ให้เขียน `-` ไว้ท้ายบรรทัดเพื่อแสดงว่าต่อคำ เช่น ...ศาลาว่าการ- / กรุงเทพมหานคร เขตพระนคร

**ข้อควรระวังเมื่อสร้าง/แก้ไข .docx (สำคัญ):** เนื้อหาจัดแบบ Thai Distributed ซึ่งใช้ "ช่องว่าง" เป็นจุดตัดคำ —

1. อย่าใส่ช่องว่างคั่นกลางคำหรือชื่อเฉพาะภาษาไทย เพราะ Word จะตัดคำผิดตำแหน่ง
2. อย่าฮาร์ดโค้ดยัติภังค์หรือขึ้นบรรทัดใหม่กลางชื่อ ให้ Word ตัดบรรทัดเอง แล้วตรวจทานตามกฎ ก./ข.
3. เวลาทำ find-replace ข้าม run ให้ตรวจว่าคำไม่ขาดครึ่ง ไม่มีช่องว่างค้าง และไม่มีช่องว่างซ้อน

```

## scripts\gen_official_doc.py
```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สร้างหนังสือราชการไทยเป็นไฟล์ .docx ตามระเบียบงานสารบรรณ

วิธีใช้:
    python3 gen_official_doc.py spec.json output.docx
    cat spec.json | python3 gen_official_doc.py - output.docx

spec.json คือ JSON object ที่มีฟิลด์ "doc_type" และฟิลด์อื่น ๆ ตาม references/formats.md
รองรับ doc_type: external, internal, seal, command, regulation, bylaw,
               announcement, statement, certificate, minutes, project, speech
"""
import sys
import json
import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DEFAULT_FONT = "TH SarabunIT9"   # มาตรฐานราชการ (TH SarabunIT๙)
BODY_SIZE = 16
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KRUT_PATH = os.path.join(SCRIPT_DIR, "..", "assets", "krut.png")


# ---------- low-level helpers ----------

def set_run_font(run, font_name, size=None, bold=False):
    run.font.name = font_name
    run.font.bold = bold
    if size is not None:
        run.font.size = Pt(size)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    # ตั้งทั้ง ascii/hAnsi/cs ให้ไทยและละตินใช้ฟอนต์เดียวกัน
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rfonts.set(qn(attr), font_name)


def add_par(doc, text="", font=DEFAULT_FONT, size=BODY_SIZE, bold=False,
            align=WD_ALIGN_PARAGRAPH.LEFT, indent_cm=None, space_after=0,
            space_before=0, line_spacing=1.0):
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing = line_spacing
    if indent_cm is not None:
        pf.first_line_indent = Cm(indent_cm)
    if text != "" or True:
        run = p.add_run(text)
        set_run_font(run, font, size, bold)
    return p


def add_runs(doc, segments, align=WD_ALIGN_PARAGRAPH.LEFT, font=DEFAULT_FONT,
             size=BODY_SIZE, indent_cm=None, space_after=0):
    """segments: list of (text, bold)"""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.0
    if indent_cm is not None:
        p.paragraph_format.first_line_indent = Cm(indent_cm)
    for text, bold in segments:
        r = p.add_run(text)
        set_run_font(r, font, size, bold)
    return p


def setup_page(doc):
    sec = doc.sections[0]
    sec.page_height = Cm(29.7)
    sec.page_width = Cm(21.0)
    sec.top_margin = Cm(2.5)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(3.0)
    sec.right_margin = Cm(2.0)
    # base style font
    style = doc.styles['Normal']
    style.font.name = DEFAULT_FONT
    style.font.size = Pt(BODY_SIZE)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rfonts.set(qn(attr), DEFAULT_FONT)


def add_krut(doc, height_cm=3.0, align=WD_ALIGN_PARAGRAPH.CENTER):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(0)
    if os.path.exists(KRUT_PATH):
        run = p.add_run()
        run.add_picture(KRUT_PATH, height=Cm(height_cm))
    else:
        run = p.add_run("(ตราครุฑ สูง %.1f ซม.)" % height_cm)
        set_run_font(run, DEFAULT_FONT, 14)
        run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    return p


def blank(doc, size=6):
    add_par(doc, "", size=size)


L = WD_ALIGN_PARAGRAPH.LEFT
C = WD_ALIGN_PARAGRAPH.CENTER
R = WD_ALIGN_PARAGRAPH.RIGHT
J = WD_ALIGN_PARAGRAPH.JUSTIFY


# ---------- signature block ----------

def add_signature(doc, sig, extra_top=True):
    if not sig:
        return
    if extra_top:
        blank(doc)
        blank(doc)
    name = sig.get("name", "(ลงชื่อ)")
    pos = sig.get("position", "")
    # ลงชื่อ จัดให้อยู่ค่อนไปทางขวา
    add_par(doc, name, align=C, indent_cm=None, space_after=0).paragraph_format.left_indent = Cm(8)
    if pos:
        add_par(doc, pos, align=C).paragraph_format.left_indent = Cm(8)


def add_signature_right(doc, sig):
    """ลายเซ็นแบบหนังสือภายนอก: ขอแสดงความนับถือ + ชื่อ + ตำแหน่ง กึ่งกลางฝั่งขวา"""
    if not sig:
        return
    name = sig.get("name", "(ลงชื่อ)")
    pos = sig.get("position", "")
    for txt in [name, pos]:
        if txt:
            p = add_par(doc, txt, align=C)
            p.paragraph_format.left_indent = Cm(8)


# ---------- document builders ----------

def build_external(doc, s):
    font = s.get("font", DEFAULT_FONT)
    add_krut(doc, 3.0)
    blank(doc)
    header = s.get("agency_header", [])
    # บรรทัดแรก = ที่ (ชิดซ้าย), ที่เหลือ = ชื่อ/ที่อยู่ (กึ่งกลางค่อนขวา)
    if header:
        add_par(doc, header[0], font=font, align=L, space_after=0)
        for line in header[1:]:
            p = add_par(doc, line, font=font, align=C, space_after=0)
            p.paragraph_format.left_indent = Cm(7)
    if s.get("date"):
        p = add_par(doc, s["date"], font=font, align=C, space_before=4, space_after=4)
        p.paragraph_format.left_indent = Cm(7)
    if s.get("subject"):
        add_runs(doc, [("เรื่อง  ", True), (s["subject"], False)], font=font, space_after=2)
    if s.get("salutation"):
        add_par(doc, s["salutation"], font=font, space_after=2)
    for ref in s.get("references", []):
        add_runs(doc, [("อ้างถึง  ", True), (ref, False)], font=font, space_after=0)
    encl = s.get("enclosures", [])
    if encl:
        if len(encl) == 1:
            add_runs(doc, [("สิ่งที่ส่งมาด้วย  ", True), (encl[0], False)], font=font, space_after=2)
        else:
            add_par(doc, "สิ่งที่ส่งมาด้วย", font=font, bold=True, space_after=0)
            for i, e in enumerate(encl, 1):
                add_par(doc, "%d. %s" % (i, e), font=font, indent_cm=1.5, space_after=0)
    blank(doc)
    for para in s.get("body", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4, line_spacing=1.0)
    blank(doc)
    closing = s.get("closing", "ขอแสดงความนับถือ")
    p = add_par(doc, closing, font=font, align=C)
    p.paragraph_format.left_indent = Cm(8)
    blank(doc)
    blank(doc)
    add_signature_right(doc, s.get("signature"))
    # contact
    c = s.get("contact")
    if c:
        blank(doc)
        if c.get("division"):
            add_par(doc, c["division"], font=font, size=14, space_after=0)
        line = []
        if c.get("phone"):
            line.append("โทร. " + c["phone"])
        if c.get("fax"):
            line.append("โทรสาร " + c["fax"])
        if line:
            add_par(doc, "  ".join(line), font=font, size=14, space_after=0)
    for cc in s.get("cc", []):
        add_par(doc, "สำเนาส่ง  " + cc, font=font, size=14, space_after=0)


def build_internal(doc, s):
    font = s.get("font", DEFAULT_FONT)
    # ครุฑเล็กมุมซ้าย + บันทึกข้อความ
    add_krut(doc, 1.5, align=L)
    add_par(doc, "บันทึกข้อความ", font=font, size=29, bold=True, align=C, space_after=6)
    seg = [("ส่วนราชการ  ", True), (s.get("agency", ""), False)]
    if s.get("phone"):
        seg.append(("  โทร. " + s["phone"], False))
    add_runs(doc, seg, font=font, space_after=0)
    add_runs(doc, [("ที่  ", True), (s.get("doc_no", ""), False),
                   ("          วันที่  ", True), (s.get("date", ""), False)],
             font=font, space_after=0)
    add_runs(doc, [("เรื่อง  ", True), (s.get("subject", ""), False)], font=font, space_after=4)
    add_par(doc, s.get("salutation", ""), font=font, space_after=4)
    for para in s.get("body", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)
    add_signature(doc, s.get("signature"))


def build_seal(doc, s):
    font = s.get("font", DEFAULT_FONT)
    add_krut(doc, 3.0)
    blank(doc)
    for line in s.get("agency_header", []):
        add_par(doc, line, font=font, align=L, space_after=0)
    blank(doc)
    add_runs(doc, [("ถึง  ", True), (s.get("to", ""), False)], font=font, space_after=4)
    for para in s.get("body", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)
    blank(doc)
    add_par(doc, s.get("agency_name", ""), font=font, align=C, space_after=0)
    add_par(doc, "(ประทับตราส่วนราชการ)", font=font, size=14, align=C, space_after=0)
    if s.get("date"):
        add_par(doc, s["date"], font=font, align=C, space_after=0)
    c = s.get("contact")
    if c:
        blank(doc)
        if c.get("division"):
            add_par(doc, c["division"], font=font, size=14, space_after=0)
        if c.get("phone"):
            add_par(doc, "โทร. " + c["phone"], font=font, size=14, space_after=0)


def _titled_directive(doc, s, head_word):
    """ใช้ร่วมกัน: คำสั่ง / ประกาศ / แถลงการณ์ (มีครุฑ + หัวกลาง)"""
    font = s.get("font", DEFAULT_FONT)
    add_krut(doc, 3.0)
    title = head_word + s.get("agency_name", "")
    add_par(doc, title, font=font, size=22, bold=True, align=C, space_after=0)
    if s.get("doc_no"):
        add_par(doc, s["doc_no"], font=font, align=C, space_after=0)
    if s.get("subject"):
        add_runs(doc, [("เรื่อง  ", True), (s["subject"], False)], font=font, align=C, space_after=4)
    add_par(doc, "_______________", font=font, align=C, space_after=4)
    return font


def build_command(doc, s):
    font = _titled_directive(doc, s, "คำสั่ง")
    for para in s.get("preamble", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)
    for i, cl in enumerate(s.get("clauses", []), 1):
        if isinstance(cl, dict):
            no = cl.get("no", str(i))
            txt = cl.get("text", "")
        else:
            no, txt = str(i), cl
        add_par(doc, "ข้อ %s  %s" % (no, txt), font=font, align=J, indent_cm=2.5, space_after=4)
    if s.get("effective"):
        add_par(doc, s["effective"], font=font, align=J, indent_cm=2.5, space_after=4)
    blank(doc)
    if s.get("ordered_date"):
        p = add_par(doc, s["ordered_date"], font=font, align=C)
        p.paragraph_format.left_indent = Cm(6)
    blank(doc)
    add_signature_right(doc, s.get("signature"))


def build_regulation(doc, s, head="ระเบียบ"):
    font = s.get("font", DEFAULT_FONT)
    add_krut(doc, 3.0)
    add_par(doc, head + s.get("agency_name", ""), font=font, size=22, bold=True, align=C, space_after=0)
    title = "ว่าด้วย" + s.get("title", "")
    add_par(doc, title, font=font, size=18, bold=True, align=C, space_after=0)
    if s.get("year"):
        add_par(doc, "พ.ศ. " + s["year"], font=font, size=18, bold=True, align=C, space_after=4)
    add_par(doc, "_______________", font=font, align=C, space_after=4)
    for para in s.get("preamble", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)
    for i, cl in enumerate(s.get("clauses", []), 1):
        if isinstance(cl, dict):
            no = cl.get("no", str(i)); txt = cl.get("text", "")
        else:
            no, txt = str(i), cl
        add_par(doc, "ข้อ %s  %s" % (no, txt), font=font, align=J, indent_cm=2.5, space_after=4)
    blank(doc)
    if s.get("announced_date"):
        p = add_par(doc, s["announced_date"], font=font, align=C)
        p.paragraph_format.left_indent = Cm(6)
    blank(doc)
    add_signature_right(doc, s.get("signature"))


def build_bylaw(doc, s):
    build_regulation(doc, s, head="ข้อบังคับ")


def build_announcement(doc, s):
    font = _titled_directive(doc, s, "ประกาศ")
    for para in s.get("body", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)
    blank(doc)
    if s.get("announced_date"):
        p = add_par(doc, s["announced_date"], font=font, align=C)
        p.paragraph_format.left_indent = Cm(6)
    blank(doc)
    add_signature_right(doc, s.get("signature"))


def build_statement(doc, s):
    font = _titled_directive(doc, s, "แถลงการณ์")
    for para in s.get("body", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)
    blank(doc)
    add_par(doc, s.get("agency_name", ""), font=font, align=C, space_after=0)
    if s.get("announced_date"):
        add_par(doc, s["announced_date"], font=font, align=C, space_after=0)


def build_certificate(doc, s):
    font = s.get("font", DEFAULT_FONT)
    add_krut(doc, 3.0)
    blank(doc)
    if s.get("doc_no"):
        add_par(doc, s["doc_no"], font=font, align=C, space_after=4)
    add_par(doc, "หนังสือรับรอง", font=font, size=20, bold=True, align=C, space_after=4)
    for para in s.get("body", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)
    blank(doc)
    if s.get("given_date"):
        p = add_par(doc, s["given_date"], font=font, align=C)
        p.paragraph_format.left_indent = Cm(6)
    blank(doc)
    add_signature_right(doc, s.get("signature"))


def build_minutes(doc, s):
    font = s.get("font", DEFAULT_FONT)
    add_par(doc, "รายงานการประชุม" + s.get("meeting_name", ""), font=font, size=18, bold=True, align=C, space_after=0)
    for t in s.get("time", []) if isinstance(s.get("time"), list) else ([s["time"]] if s.get("time") else []):
        add_par(doc, t, font=font, align=C, space_after=0)
    add_par(doc, "_______________", font=font, align=C, space_after=4)

    def name_list(label, items):
        if not items:
            return
        add_par(doc, label, font=font, bold=True, space_after=0)
        for i, it in enumerate(items, 1):
            add_par(doc, "%d. %s" % (i, it), font=font, indent_cm=1.0, space_after=0)

    name_list("ผู้มาประชุม", s.get("attendees", []))
    name_list("ผู้ไม่มาประชุม", s.get("absentees", []))
    name_list("ผู้เข้าร่วมประชุม", s.get("participants", []))
    if s.get("start_time"):
        add_par(doc, "เริ่มประชุมเวลา  " + s["start_time"], font=font, space_before=4, space_after=4)
    for ag in s.get("agenda", []):
        no = ag.get("no", "")
        title = ag.get("title", "")
        add_par(doc, "ระเบียบวาระที่ %s  %s" % (no, title), font=font, bold=True, space_after=2)
        for c in ag.get("content", []):
            add_par(doc, c, font=font, align=J, indent_cm=2.5, space_after=2)
    if s.get("end_time"):
        add_par(doc, "เลิกประชุมเวลา  " + s["end_time"], font=font, space_before=4, space_after=6)
    blank(doc)
    rec = s.get("recorder")
    chk = s.get("checker")
    if rec:
        add_par(doc, "(%s)" % rec.get("name", ""), font=font, align=C).paragraph_format.left_indent = Cm(8)
        add_par(doc, rec.get("position", "ผู้จดรายงานการประชุม"), font=font, align=C).paragraph_format.left_indent = Cm(8)
    if chk:
        blank(doc)
        add_par(doc, "(%s)" % chk.get("name", ""), font=font, align=C).paragraph_format.left_indent = Cm(8)
        add_par(doc, chk.get("position", "ผู้ตรวจรายงานการประชุม"), font=font, align=C).paragraph_format.left_indent = Cm(8)


def build_project(doc, s):
    font = s.get("font", DEFAULT_FONT)
    add_par(doc, "โครงการ" + s.get("project_name", ""), font=font, size=18, bold=True, align=C, space_after=6)

    def section(title, items):
        if not items:
            return
        add_par(doc, title, font=font, bold=True, space_after=0)
        if isinstance(items, str):
            add_par(doc, items, font=font, align=J, indent_cm=2.5, space_after=4)
        else:
            for i, it in enumerate(items, 1):
                add_par(doc, "%d. %s" % (i, it), font=font, align=J, indent_cm=1.0, space_after=0)
            blank(doc)

    section("๑. หลักการและเหตุผล", s.get("principle", []))
    section("๒. วัตถุประสงค์", s.get("objectives", []))
    section("๓. เป้าหมาย", s.get("targets", []))
    section("๔. วิธีดำเนินการ", s.get("methods", []))
    if s.get("duration"):
        add_par(doc, "๕. ระยะเวลาดำเนินการ  " + s["duration"], font=font, space_after=4)
    if s.get("place"):
        add_par(doc, "๖. สถานที่ดำเนินการ  " + s["place"], font=font, space_after=4)
    if s.get("budget"):
        add_par(doc, "๗. งบประมาณ  " + s["budget"], font=font, space_after=4)
    if s.get("responsible"):
        add_par(doc, "๘. ผู้รับผิดชอบโครงการ  " + s["responsible"], font=font, space_after=4)
    section("๙. การประเมินผล", s.get("evaluation", []))
    section("๑๐. ผลที่คาดว่าจะได้รับ", s.get("outcomes", []))


def build_speech(doc, s):
    font = s.get("font", DEFAULT_FONT)
    if s.get("title"):
        add_par(doc, s["title"], font=font, size=18, bold=True, align=C, space_after=6)
    for g in s.get("greeting", []):
        add_par(doc, g, font=font, align=C, space_after=0)
    blank(doc)
    for para in s.get("body", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)
    for para in s.get("closing", []):
        add_par(doc, para, font=font, align=J, indent_cm=2.5, space_after=4)


BUILDERS = {
    "external": build_external,
    "internal": build_internal,
    "seal": build_seal,
    "command": build_command,
    "regulation": build_regulation,
    "bylaw": build_bylaw,
    "announcement": build_announcement,
    "statement": build_statement,
    "certificate": build_certificate,
    "minutes": build_minutes,
    "project": build_project,
    "speech": build_speech,
}


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: gen_official_doc.py <spec.json|-> <output.docx>")
    spec_arg, out_path = sys.argv[1], sys.argv[2]
    raw = sys.stdin.read() if spec_arg == "-" else open(spec_arg, encoding="utf-8").read()
    spec = json.loads(raw)

    dtype = spec.get("doc_type")
    if dtype not in BUILDERS:
        sys.exit("unknown doc_type: %r (valid: %s)" % (dtype, ", ".join(BUILDERS)))

    # อนุญาตให้ override ฟอนต์มาตรฐานทั้งเอกสาร
    global DEFAULT_FONT
    if spec.get("font"):
        DEFAULT_FONT = spec["font"]

    doc = Document()
    setup_page(doc)
    BUILDERS[dtype](doc, spec)
    doc.save(out_path)
    print("saved:", out_path)


if __name__ == "__main__":
    main()

```
