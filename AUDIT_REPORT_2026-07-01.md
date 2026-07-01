# รายงานตรวจสอบโปรเจกต์ LM Co-work — 1 กรกฎาคม 2026

ตรวจ 4 ด้านตามที่ขอ: **ความปลอดภัย / คุณภาพโค้ด / เทสต์+CI / เอกสาร**
วิธีตรวจ: อ่านโค้ดจริงทั้งหมด (`server.py`, `tools.py`, `skills_loader.py`, `agents.py`,
`index.html`, `tests/test_smoke.py`, `.github/workflows/ci.yml`, `README.md`, `AGENTS.md`,
`requirements.txt`) เทียบกับสถานะที่ `IMPROVEMENT_PLAN.md` อ้างไว้

**นี่คือรายงาน — ยังไม่ได้แก้ไขไฟล์ใดๆ** เลือกข้อที่ต้องการให้ลงมือแก้ได้เลย (อ้างอิงรหัส เช่น "แก้ SEC-1, QUAL-2")

---

## สรุปภาพรวม

งานที่ทำไปก่อนหน้านี้ (ใน IMPROVEMENT_PLAN.md) ทำได้ดีและตรวจสอบแล้วว่า **ของจริงตรงกับที่อ้าง**
เกือบทั้งหมด — path jail, SSRF guard, CSRF/same-origin check, XSS escape ใน markdown, skill
confirm-before-run ล้วนมีอยู่จริงในโค้ดและมี test คลุม พบเพิ่มอีก **5 ประเด็นความปลอดภัย
(2 ระดับสูง), 4 ประเด็นคุณภาพโค้ด, 3 ประเด็นเทสต์/CI, 2 ประเด็นเอกสาร**

| ระดับ | จำนวน |
|---|---|
| 🔴 สูง | 2 |
| 🟡 กลาง | 4 |
| ⚪ ต่ำ/ข้อมูล | 7 |

---

## 🔒 ความปลอดภัย (Security)

### SEC-1 🔴 สูง — `import-agent-folder` ไม่กันโฟลเดอร์ระบบ/root ไดรฟ์
**ไฟล์:** `server.py` → `Handler._route_import_agent_folder` (~บรรทัด 865–906)

ทุก endpoint ที่รับ path โฟลเดอร์จากผู้ใช้ (`_route_audio_scan`, `check_audio_integrity`,
`collect_files`) เช็ค `_is_blocked_root` ก่อนเดินไฟล์เสมอ — endpoint นี้ **ไม่เช็ค**
เช็คแค่ `os.path.isdir(folder)` แล้ว `os.walk` ทั้งต้นไม้ทันที อ่านทุกไฟล์ข้อความ
ที่เล็กกว่า 50KB (รวมไม่เกิน 100,000 ตัวอักษร) ฝังเป็น system prompt ของ agent ใหม่

**ผลกระทบ:** ถ้าชี้ไปที่โฟลเดอร์ที่มีข้อมูลอ่อนไหว (เช่น `Documents`, โฟลเดอร์ทั้งไดรฟ์)
เนื้อหาจะถูกฝังในตัว agent แล้วถ้า agent นั้นถูกใช้คุยผ่าน provider ภายนอก (ไม่ใช่ LM
Studio local) ข้อมูลจะถูกส่งออกอินเทอร์เน็ตด้วย — เป็นช่องทาง data exfiltration

**แนะนำ:** เพิ่มเช็ค `T._is_blocked_root(folder)` ก่อน `os.walk` แบบเดียวกับ endpoint อื่น

---

### SEC-2 🔴 สูง — `esc()` เอาไม่อยู่เมื่อใช้ใน inline `onclick` attribute
**ไฟล์:** `index.html` — `renderChats()`, `loadTree()`, `openFile()` (~บรรทัด 602-620)

โค้ดใช้ `onclick="loadTree('${esc(child)}')"` โดยหวังว่า `esc()` (HTML-entity escape:
`&amp; &lt; &gt; &quot; &#39;`) จะกันการฉีดโค้ดได้ — แต่ browser จะ **decode HTML entity
ก่อน** แล้วค่อยเอาไปแปลเป็น JavaScript ทำให้ `&#39;` กลับเป็น `'` จริงตอนรัน ป้องกันไม่ได้
ถ้าชื่อไฟล์/โฟลเดอร์มีเครื่องหมาย `'` ปนโค้ด เช่น `x'); fetch('http://evil'); //.txt`
จะสามารถหลุดออกจาก string literal แล้วรัน JS อะไรก็ได้ในหน้าต่างแอป (ซึ่งมีสิทธิ์เรียก
`window.pywebview.api` อ่าน/เขียนคลิปบอร์ด และเข้าถึง state ทั้งหมดของแชต)

**เส้นทางโจมตีที่เป็นไปได้:** AI ถูกหลอกด้วย prompt injection (จากเว็บที่ `fetch_url`
ดึงมา หรือไฟล์ที่อ่านเข้ามา) ให้เรียก `write_file` สร้างไฟล์ชื่อแบบข้างบน → ผู้ใช้กด
"ยืนยัน" บันทึกโดยไม่ทันสังเกตชื่อไฟล์ประหลาด → ครั้งถัดไปที่เปิดแท็บ Files แล้วเห็น/คลิก
ไฟล์นั้น โค้ดจะรัน

**แนะนำ:** เลิกสร้าง onclick แบบ string-interpolation ทั้งหมด เปลี่ยนเป็น
`addEventListener` + `dataset` attribute (ปลอดภัยโดยธรรมชาติ ไม่ต้อง escape เลย)
จุดที่ต้องแก้: `loadTree`, `openFile`, `renderChats` (`loadChat`/`delChat` ปลอดภัยอยู่แล้ว
เพราะ `id` มาจาก `uid()` ที่สุ่มเอง ไม่ใช่จากผู้ใช้)

---

### SEC-3 🟡 กลาง — skill ที่ confirm แล้วไม่ถามซ้ำแม้ argument เปลี่ยน
**ไฟล์:** `skills_loader.py` (`_confirmed_skills`), `server.py` (`_handle_tool_call`)

หลัง confirm skill ครั้งแรก ระบบจำไว้ตลอด session โดยไม่ดูว่าครั้งต่อไปจะเรียกด้วย
argument อะไร — ถ้ามี prompt injection สั่งให้เรียก skill ที่เคย confirm ไปแล้วด้วย
argument อันตราย โมเดลเรียกได้เลยไม่ถามอีก (เข้าข่าย LLM06 Excessive Agency)

**แนะนำ:** อย่างน้อยแสดง argument ที่จะใช้ให้เห็นใน UI/log ทุกครั้งที่ skill รัน (ไม่ใช่
แค่ครั้งแรก) ผู้ใช้จะได้สังเกตความผิดปกติได้

---

### SEC-4 🟡 กลาง — `install_ffmpeg` รันจริงทันทีไม่ผ่านการยืนยัน
**ไฟล์:** `tools.py` (`install_ffmpeg`)

เป็นเครื่องมือเดียวที่ "เปลี่ยนแปลงระบบ" (เรียก `winget install`) แต่ไม่อยู่ใน
`WRITE_TOOLS` จึงไม่ผ่านขั้นตอน proposal-confirm เหมือน `write_file`/skill ใหม่ —
โมเดลตัดสินใจเรียกเองได้เลยระหว่างคุย

**แนะนำ:** ใส่เข้า flow ยืนยันแบบเดียวกับ `WRITE_TOOLS` หรืออย่างน้อยแจ้งเตือนชัดเจน
ก่อนรันจริง

---

### SEC-5 ⚪ ข้อมูล (ไม่แนะนำให้แก้) — DNS rebinding TOCTOU ใน `fetch_url`
**ไฟล์:** `tools.py` (`_is_public_host`, `fetch_url`)

ตรวจ DNS แล้วเรียก `urlopen` แยกกันคนละครั้ง เปิดช่อง DNS rebinding ทางทฤษฎีได้ —
ความเสี่ยงต่ำมากสำหรับแอป local ผู้ใช้คนเดียว การแก้ (pin IP เอง) จะซับซ้อนเกินความคุ้มค่า
เมื่อเทียบกับ threat model ปัจจุบัน ใส่ไว้เป็นข้อมูลเฉยๆ

---

## 🧹 คุณภาพโค้ด (Code Quality / Refactor)

### QUAL-1 🟡 กลาง — โค้ดซ้ำ เสี่ยงแก้ไม่ครบ
- `_no_window_kwargs()` นิยามซ้ำเป๊ะทั้งใน `server.py` และ `tools.py`
- การสร้าง system prompt + `schemas_for()` ใน `_route_chat` กับ `_route_chat_stream`
  เกือบเหมือนกันทุกตัวอักษร (เคยเกิดบั๊กจากจุดนี้มาแล้ว: ตอนแรก streaming ลืมใส่
  `ARTIFACTS_PROMPT` ตามที่คอมเมนต์ในโค้ดยอมรับเองบรรทัด 709)

**แนะนำ:** ดึง `_no_window_kwargs` ไปไว้ module ใช้ร่วม, แยกการสร้าง context (system
prompt/tool_schemas/base_url/model) ของ chat ออกเป็นฟังก์ชันเดียวที่ทั้ง `_route_chat`
และ `_route_chat_stream` เรียกใช้ร่วมกัน

### QUAL-2 🟡 กลาง — ไฟล์ขยะ/temp ค้างอยู่ที่ root โปรเจกต์ (ปัญหาเดิมกลับมาใหม่)
พบที่ root: `ziBZ1nXa`, `zizWqTDD` (ไฟล์ ZIP ชื่อสุ่ม ไม่มีนามสกุล — เนื้อหาเป็น backup
ของโปรเจกต์/skill package), `_backup_20260630_130655.zip` (0 bytes, เสีย), `index.html.bak-preui-153804`,
โฟลเดอร์ `ai-native-dev/` และ `ai-native-dev.skill` (0 bytes)

เคยแก้ปัญหานี้ไปแล้วครั้งหนึ่ง (ข้อ 3.3 ใน `IMPROVEMENT_PLAN.md`, 28 มิ.ย.) แต่มีไฟล์ใหม่
เกิดขึ้นอีกจากการทำงานของ session อื่นๆ ในโฟลเดอร์นี้

**แนะนำ:** ลบไฟล์ขยะเหล่านี้ (จะยืนยันทีละไฟล์ก่อนลบให้) และพิจารณาย้าย working
directory ออกจากโฟลเดอร์ที่เครื่องมือ/agent อื่นเขียนถึงบ่อย

### QUAL-3 ⚪ ต่ำ — `except Exception: pass` ที่ยังไม่มี log ตามกฎที่ `AGENTS.md` กำหนดเอง
พบใน `server.py`: fallback ของ `_force_utf8_streams`, `_no_window_kwargs`,
`ensure_lmstudio` (Popen), `JsApi.pick_folder/copy_text/read_text` — `AGENTS.md` เขียน
ไว้เองว่า "อย่า `except: pass` เปล่าๆ" แต่จุดเหล่านี้ยังไม่ทำตาม

**แนะนำ:** เติม `_log.debug(..., exc_info=True)` ให้ครบ

### QUAL-4 ⚪ ต่ำ — placeholder ใน `md()` ใช้ null byte จริง
**ไฟล์:** `index.html` บรรทัด ~386: `return "\x00CB"+i+"\x00"`

ใช้ byte `\x00` เป็นตัวคั่นระหว่างประมวลผล code block — ทำงานได้ในทางปฏิบัติ แต่เปราะ
(เครื่องมือบางตัว เช่น `file`/`grep` ตีความไฟล้งเป็น binary เพราะเจอ null byte) แนะนำ
เปลี่ยนเป็น token ที่ไม่ใช่ control character เช่น `"CB"+i+""` หรือเก็บเป็น
array แทนการฝังใน string

---

## 🧪 เทสต์ + CI/CD

### TEST-1 🟡 กลาง — ไม่มี test คลุม `_route_import_agent_folder`
จุดที่พบช่องโหว่ SEC-1 ไม่มี test เลย ทั้งที่ endpoint รับ path โฟลเดอร์คล้าย
`_route_audio_scan` ที่มี test คลุมอยู่แล้ว (`test_audio_check_rejects_outside_workspace`)

**แนะนำ:** เพิ่ม test ยืนยันว่าถูกปฏิเสธเมื่อชี้ไป blocked root (พร้อมกับแก้ SEC-1)

### TEST-2 ⚪ ต่ำ — CI ไม่มีขั้น dependency audit / lint
`.github/workflows/ci.yml` รันแค่ `compileall` + `pytest` บน `windows-latest` — ไม่มี
`pip-audit` (เช็ค CVE ของ `pywebview`/`pythonnet`) หรือ lint (`ruff`/`flake8`)

**แนะนำ:** เพิ่ม step `pip-audit` อย่างน้อย เพราะโปรเจกต์พึ่งพา native library

### TEST-3 ⚪ ต่ำ — ไม่มี test ฝั่ง frontend (JS)
`pytest` ทดสอบแต่ backend Python ทั้งหมด — ฟังก์ชัน `esc()`/`md()` ใน `index.html`
(จุดที่พบ SEC-2) ไม่มี regression test เลย

**แนะนำ:** ถ้าแก้ SEC-2 แล้ว ควรมีอย่างน้อย manual QA checklist หรือ Playwright test
ง่ายๆ ยืนยันว่าชื่อไฟล์แปลกๆ render ปลอดภัย

---

## 📄 เอกสาร

### DOC-1 🟡 กลาง — `requirements.txt` ขาด dependency ที่ใช้จริง
`server.py` ฟังก์ชัน `start_tray` (~บรรทัด 1119-1154) ใช้ `pystray`, `keyboard`, `PIL`
(Pillow) จริง — ไม่มีอยู่ใน `requirements.txt` เลย ผู้ใช้ที่ติดตั้งตาม README/AGENTS.md
จะไม่ได้ฟีเจอร์ system tray/global hotkey โดยไม่รู้ตัว (error ถูกกลืนแล้ว print
ข้อความที่ไม่มีใครเห็นเพราะ build แบบ `--windowed`)

**แนะนำ:** เพิ่ม `pystray`, `keyboard`, `Pillow` ลง `requirements.txt` (หรือทำเป็น
optional extra พร้อมคอมเมนต์บอกชัดว่าไม่มีก็ใช้แอปได้ปกติ แค่ไม่มี tray icon)

### DOC-2 ⚪ ต่ำ — `IMPROVEMENT_PLAN.md` อ้างการแก้ที่ไม่ตรงกับโค้ดจริง 100%
ข้อ 2.2 เขียนว่าเสร็จแล้วพร้อม "`new URL()` validate href" — ตรวจโค้ดจริงไม่พบการเรียก
`new URL()` ที่จุดนี้ มีแค่ regex จำกัด scheme เป็น http/https ซึ่งป้องกันผลลัพธ์
เดียวกันได้ในทางปฏิบัติ (ไม่ใช่บั๊ก แค่ changelog เขียนเกินจริงไปหน่อย)

**แนะนำ:** แก้คำอธิบายให้ตรงของจริง กันคนอ่านเข้าใจผิดว่ามี validation ที่ไม่มีจริง

---

## ขั้นตอนถัดไป

บอกได้เลยว่าจะให้แก้ข้อไหนบ้าง (อ้างรหัส เช่น "แก้ SEC-1 กับ SEC-2 ก่อน" หรือ "แก้ทุกข้อ
ยกเว้น SEC-5") จะลงมือแก้ทีละจุดพร้อมอัปเดต `IMPROVEMENT_PLAN.md` และเพิ่ม test ตามที่
เกี่ยวข้อง
