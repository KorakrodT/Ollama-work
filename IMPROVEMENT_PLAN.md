# แผนปรับปรุง AI Agent

อ้างอิงจากผลตรวจ 26 มิ.ย. 2026 — อัปเดตสถานะ 28 มิ.ย. 2026

---

## สรุปสถานะ (28 มิ.ย. 2026)

| รายการ | สถานะ | หมายเหตุ |
|--------|-------|----------|
| 1.1 ปิดช่อง SSRF ผ่าน redirect | ✅ เสร็จแล้ว | `_is_public_host`, `_SafeRedirectHandler`, `_same_origin()` |
| 2.1 จำกัดขอบเขต `set_workspace` | ✅ เสร็จแล้ว | `_is_blocked_root`, `_is_allowed_workspace` ใน `tools.py` |
| 2.2 อุด XSS ใน Markdown | ✅ เสร็จแล้ว | `esc()` escape `"` และ `'` ครบ + regex ลิงก์จำกัด scheme เป็น http/https เท่านั้น (DOC-2: ไม่ได้ใช้ `new URL()` จริงตามที่เคยเขียนไว้ — regex ก็ป้องกันผลลัพธ์เดียวกันได้) |
| 2.3 Co-Work logic `tools=[]` | ✅ เสร็จแล้ว | cowork block รันหลัง `result=[]` เพิ่ม COWORK_TOOLS ถูกต้อง |
| 2.4 Ollama empty arguments | ✅ เสร็จแล้ว | `raw or "{}"` บรรทัด 441 ใน `server.py` |
| 3.1 `get_current_time(timezone)` | ✅ เสร็จแล้ว | ใช้ `ZoneInfo` จริงแล้ว |
| 3.2 Docstring ล้าสมัย `agents.py` | ✅ เสร็จแล้ว | เพิ่ม `skill_categories`, ลบ field `name` ที่ไม่มีจริง |
| 3.3 ไฟล์ขยะ + `.gitignore` | ✅ เสร็จแล้ว | ไม่มี `.bak*` หลงเหลือ, `.gitignore` ครอบ `__pycache__/`, `*.bak*`, `dist/`, `build/` แล้ว |

---

## ความเสี่ยงที่ยังเปิดอยู่ (ตัดสินใจรับไว้)

### ⚠️ Skill `tool.py` รันโค้ดอิสระ (RCE)
- `skills_loader.py` ใช้ `spec.loader.exec_module()` รัน skill ในโปรเซสเดียวกันโดยไม่มี sandbox
- AI สร้าง skill เองได้ → skill ที่ AI หลอนสร้างขึ้นรันโค้ด Python ใดๆ ได้
- **ยอมรับได้**: แอปใช้งานในเครื่อง local คนเดียว — แต่ควรพิจารณาขอยืนยันก่อนรัน skill ใหม่ครั้งแรก

### ⚠️ `except Exception` แบบกลืน error
- มีหลายจุดใน `server.py` ที่ catch Exception แล้ว pass เงียบ ทำให้ดีบักยาก
- **แนะนำ**: ใส่ `_log.debug(traceback.format_exc())` อย่างน้อยทุกจุด

### ⚠️ ไฟล์ `.py` อาจ truncate จาก OneDrive sync
- เคยพบ 25–26 มิ.ย. — `compileall` ใน CI จะดักได้
- **แนะนำ**: พิจารณาย้าย repo ออกจากโฟลเดอร์ที่ OneDrive sync ตลอดเวลา

---

## ประวัติการแก้ไข

### รอบ 26 มิ.ย. 2026
- แก้บั๊ก `'charmap' codec` (windowed build) — เพิ่ม `_force_utf8_streams()`
- เพิ่ม `pythonnet` + pin เวอร์ชันใน `requirements.txt`
- เปลี่ยน MODEL default `gemma2` → `gemma4`
- เพิ่ม `tests/test_smoke.py` + `.github/workflows/ci.yml`

### รอบ 28 มิ.ย. 2026
- ตรวจสอบทุกรายการในแผน — พบว่าแก้ไขครบหมดแล้วทุกข้อ (ลำดับ 1–3)
- แก้ docstring ใน `agents.py` ให้ตรงกับ dict fields จริง (เพิ่ม `skill_categories`)

### รอบ 1 ก.ค. 2026 — ตรวจสอบเต็ม 4 ด้าน (security/คุณภาพโค้ด/เทสต์+CI/เอกสาร)
รายละเอียดเต็มอยู่ใน `AUDIT_REPORT_2026-07-01.md` — สรุปที่แก้ไปแล้วทั้งหมด:

- **SEC-1**: `_route_import_agent_folder` (server.py) ไม่เคยเช็ค `_is_blocked_root` มาก่อน
  ต่างจาก endpoint รับโฟลเดอร์อื่นๆ — เพิ่มเช็คแล้ว + มี test คุ้มครอง
- **SEC-2**: `index.html` ใช้ `esc()` (HTML-entity) ใน inline `onclick="fn('...')"` ซึ่ง
  เอาไม่อยู่จริง (entity ถูก decode ก่อนแปลเป็น JS) — เปลี่ยน `renderChats`/`loadTree`
  เป็น data-attribute + `addEventListener` ทั้งหมด
- **SEC-3**: skill ที่ confirm แล้วไม่ถูกถามซ้ำ — เพิ่ม log argument ทุกครั้งที่รัน (audit trail)
- **SEC-4**: `install_ffmpeg` เดิมรันทันทีไม่ผ่านการยืนยัน — เพิ่ม `CONFIRM_TOOLS` ให้ใช้
  กลไก confirm เดียวกับ skill ใหม่
- **QUAL-1**: รวม `_no_window_kwargs()` ที่ซ้ำกันใน server.py/tools.py ไปไว้ที่ `winproc.py`
  ที่เดียว (parametrize `detached=`)
- **QUAL-2**: ลบไฟล์ขยะที่ root โปรเจกต์ (`ziBZ1nXa`, `zizWqTDD`, `_backup_*.zip`,
  `index.html.bak-preui-*`, `ai-native-dev/`)
- **QUAL-3**: เติม `_log.debug(..., exc_info=True)` ในจุดที่ `except Exception: pass`
  แบบเงียบสนิทใน server.py (ตามกฎที่ตัวเองประกาศไว้แต่ยังทำไม่ครบ)
- **QUAL-4**: เปลี่ยน placeholder ใน `md()` (index.html) จาก null byte จริง (`\x00`) เป็น
  อักขระ Unicode invisible separator แทน (กันเครื่องมือตีความไฟล์เป็น binary)
- **TEST-1**: เพิ่ม test สำหรับ SEC-1 และ SEC-4 (`test_import_agent_folder_rejects_blocked_root`,
  `test_install_ffmpeg_requires_confirmation`, `test_install_ffmpeg_runs_after_confirmed`)
- **TEST-2**: เพิ่ม step `pip-audit -r requirements.txt` ใน CI
- **TEST-3**: เพิ่ม manual QA checklist สำหรับ escaping ใน `index.html` ที่ `AGENTS.md`
  (ยังไม่มี automated test ฝั่ง JS)
- **DOC-1**: เพิ่ม `pystray`/`keyboard`/`Pillow` ที่ขาดหายใน `requirements.txt`
  (ใช้จริงใน `start_tray()` แต่ไม่เคยประกาศไว้)
- **DOC-2**: แก้คำอธิบายข้อ 2.2 ด้านบนให้ตรงกับโค้ดจริง
- **SEC-5** (ตอนแรกแนะนำให้ข้าม แต่ผู้ใช้ขอให้แก้ด้วย): DNS-rebinding TOCTOU ใน `fetch_url`
  — เพิ่ม `_resolve_public_ip()` + `_PinnedIPResolver` + `_PinnedHTTPConnection`/
  `_PinnedHTTPSConnection`/`_PinnedHTTPHandler`/`_PinnedHTTPSHandler` ใน `tools.py`:
  resolve host ครั้งเดียว validate ว่าทุก IP เป็นสาธารณะ แล้ว "pin" การเชื่อมต่อจริงไปยัง
  IP นั้นตรงๆ (HTTPS ยังตรวจ cert/SNI กับ hostname เดิมตามปกติ) ไม่ resolve DNS ซ้ำตอน
  connect อีก รองรับ redirect ด้วย (resolve+pin ใหม่ต่อ host ที่ redirect ไป) มี test คุม
  ทั้ง cache-per-host (`test_pinned_ip_resolver_caches_per_host`) และ round-trip ผ่าน
  เซิร์ฟเวอร์ HTTP จริง (`test_fetch_url_pinned_connection_roundtrip`)

⚠️ **พบเพิ่มระหว่างแก้ไข (ไม่ได้อยู่ในรายงานเดิม แต่แก้ไปด้วยเพราะเจอจริง):**
`server.py` และ `index.html` เกิดไฟล์ถูก **truncate กลางไฟล์** ระหว่างเซสชันแก้ไขนี้
(อาการตรงกับความเสี่ยง "ไฟล์ .py อาจ truncate จาก OneDrive sync" ที่บันทึกไว้ด้านบนแล้ว
แต่รอบนี้ลามไปโดน `.html` ด้วย) ตรวจพบเพราะ `compileall`/`node --check` จับไม่ผ่านหลังแก้
— กู้เนื้อหาที่หายคืนสำเร็จและ verify แล้วว่าไม่มี byte เพี้ยน/ซ้ำ **แนะนำอย่างจริงจัง:
ย้าย repo ออกจากโฟลเดอร์ที่มีการ sync กับระบบอื่นอยู่เบื้องหลัง** เพราะเกิดขึ้นจริงระหว่าง
เซสชันนี้ ไม่ใช่แค่ความเสี่ยงทางทฤษฎีอีกต่อไป

### รอบ 1 ก.ค. 2026 (ต่อ) — บั๊กจริงที่พบหลัง build .exe แล้วรันจริง
หลัง build `LM Co-work.exe` รอบใหม่ (หลังแก้ 15 ข้อข้างบน) รันแล้ว **crash ทันที**:
```
UnboundLocalError: cannot access local variable 'time' where it is not associated with a value
File "server.py", line 1121, in main
```
**สาเหตุ:** `main()` มี `import time` ซ้ำอยู่ในบล็อก `try/except` ท้ายฟังก์ชัน (fallback
เปิดเบราว์เซอร์ตอน pywebview ใช้ไม่ได้) — แค่มี `import time` ที่ไหนก็ตามในฟังก์ชัน ทำให้
Python ตีความ `time` เป็น **local variable ของทั้งฟังก์ชัน** ตั้งแต่ต้น ไม่ว่า branch นั้น
จะได้รันจริงหรือไม่ ทำให้บรรทัดก่อนหน้า `url = f"...{int(time.time())}"` (ที่ตั้งใจใช้
`time` module-level ที่ import ไว้บนสุดไฟล์) กลาย เป็น `UnboundLocalError` **ทุกครั้งที่
เรียก `main()`** — เป็นบั๊กที่มีอยู่ก่อนแล้วในโค้ดต้นฉบับ (ไม่ได้เกิดจากการแก้ 15 ข้อรอบนี้)
แต่ไม่มีใครสังเกตเพราะไม่มีใคร build+รัน .exe ตัวใหม่มาก่อนหน้านี้

**แก้แล้ว:** ลบ `import time` ที่ซ้ำใน `main()` ออก (ใช้ตัว module-level แทน)

**ป้องกันไม่ให้เกิดซ้ำ:** เพิ่มขั้นตอน **`ruff check --select F`** (rule `F823`: "local
variable referenced before assignment") ใน `.github/workflows/ci.yml`, `build-ui.bat`,
และ `AGENTS.md` — เป็นเครื่องมือเดียวที่จับ pattern นี้ได้แบบ static โดยไม่ต้องรันโค้ดจริง
(`compileall` จับแค่ SyntaxError, ไม่มี test ไหนเรียก `main()` ตรงๆ เพราะมันเปิดหน้าต่างจริง)


---

## ลำดับ 1 — แก้ก่อน (ความปลอดภัย + บั๊กที่กระทบการใช้งานจริง)

### 1.1 ปิดช่อง SSRF ผ่าน redirect ใน `fetch_url`
- **แนวทาง:** ใน `do_POST`/`do_GET` ตรวจ header `Origin`/`Referer` ให้เป็น `http://127.0.0.1:11500` หรือว่าง (pywebview) เท่านั้น ถ้าไม่ตรง → ตอบ 403. เสริมด้วย token สุ่มฝังตอนเสิร์ฟ `index.html` แล้วเช็คทุก request ได้ยิ่งดี
- **ไฟล์:** `server.py` (`Handler`)
- **แรง:** ~30 นาที

---

## ลำดับ 2 — ควรแก้ (ลดความเสี่ยง + ความถูกต้อง)

### 2.1 จำกัดขอบเขต `set_workspace`
- **ปัญหา:** ตั้ง workspace เป็น absolute path ใดก็ได้ (เช่น `C:\`) ทำให้ขอบเขตอ่านไฟล์กว้างเกิน เมื่อรวมกับข้อ 1.3
- **แนวทาง:** จำกัดให้อยู่ใต้ไดเรกทอรีฐานที่อนุญาต (เช่น home หรือโฟลเดอร์โปรเจกต์ที่ตั้งไว้) หรืออย่างน้อยกันพาธระบบ (`C:\Windows`, `C:\`) — เลือกได้ตามที่ผู้ใช้ตั้งใจ
- **ไฟล์:** `tools.py` (`set_workspace`)
- **แรง:** ~20 นาที

### 2.2 อุด XSS ในการเรนเดอร์ลิงก์ Markdown
- **ปัญหา:** `esc()` แปลงแค่ `< > &` ไม่แปลง `"` และ regex ลิงก์ `[^)]+` ยอม `"` → แทรก attribute ใน `href` ได้
- **แนวทาง:** ให้ `esc()` แปลง `"` และ `'` ด้วย หรือ encode `"` ใน URL ตอนสร้าง `<a href>`
- **ไฟล์:** `index.html` (`esc`, `md`)
- **แรง:** ~10 นาที

### 2.3 แก้ logic Co-Work ที่ไม่ให้ file tools กับ agent `tools=[]`
- **ปัญหา:** `schemas_for()` เติม file tools เข้า `base` แล้วถูก `if not allowed: return []` ทิ้ง — ขัดกับคอมเมนต์ที่ว่า "รวม file tools เสมอ"
- **แนวทาง:** ตัดสินใจพฤติกรรมที่ต้องการ แล้วทำให้ตรง: ถ้า Co-Work เปิด ให้คืนรายการ COWORK_TOOLS เสมอแม้ `tools=[]` (ย้ายเงื่อนไข cowork มาก่อน `if not allowed`)
- **ไฟล์:** `server.py` (`schemas_for`)
- **แรง:** ~15 นาที

### 2.4 กัน arguments ว่างฝั่ง Ollama
- **ปัญหา:** `json.loads(raw)` ถ้า `raw==""` จะ error (ฝั่ง OpenAI กันด้วย `raw or "{}"` แล้ว)
- **แนวทาง:** ใช้ `json.loads(raw or "{}")` ให้เหมือนกันทั้งสองเส้นทาง
- **ไฟล์:** `server.py` (`run_agent`, Ollama loop)
- **แรง:** 5 นาที

---

## ลำดับ 3 — เก็บงาน (คุณภาพ/ความสะอาด ไม่กระทบการทำงาน)

### 3.1 ทำ `get_current_time(timezone)` ให้ใช้พารามิเตอร์จริง
รองรับ timezone ด้วย `zoneinfo` หรือถ้าไม่ต้องการก็ถอด argument ออกจาก schema ให้ตรงพฤติกรรม — `tools.py`

### 3.2 แก้ docstring ที่ล้าสมัย
`agents.py` อ้างฟิลด์ `name` ที่ agent ไม่มีจริง — ปรับคอมเมนต์ให้ตรง

### 3.3 เก็บกวาดไฟล์ขยะ
ลบ `*.bak-*` (server.py 5 ตัว, tools/agent_store/index.html) และ `__pycache__` ที่ปนเวอร์ชัน 310/314 — แนะนำเพิ่ม `.gitignore` ครอบ `__pycache__/`, `*.bak*`, `dist/`, `build/`

---

## หมายเหตุ
- ทุกข้อใน "ลำดับ 1" แก้ได้ภายในครึ่งวัน และครอบคลุมความเสี่ยงหลักทั้งหมด
- แนะนำทำ backup/commit ก่อนเริ่ม และทดสอบ `fetch_url`, การแชตปกติ, และโหมด Co-Work หลังแก้

---

## รอบตรวจเพิ่มเติม 26 มิ.ย. 2026 (charmap crash)

### ✅ แก้แล้วในรอบนี้
- **บั๊ก `'charmap' codec`** ตอนเปิดหน้าต่าง (build `--windowed`): เพิ่ม `_force_utf8_streams()`
  บนสุดของ `server.py` บังคับ stdout/stderr เป็น utf-8 (รองรับเคส None/cp874). ข้อความ
  error เดิมเดาผิดว่า "ต้องติดตั้ง WebView2" — แก้ให้แสดง exception จริงและแนะนำ WebView2
  เฉพาะเมื่อเข้าข่าย
- เติม `pythonnet` + pin เวอร์ชันใน `requirements.txt`; ใส่ `PYTHONUTF8=1`/`chcp 65001` ใน `.bat`
- เปลี่ยน MODEL ดีฟอลต์ `gemma2` → `gemma4` (ให้ตรง README) + คอมเมนต์เตือนเรื่อง tool-calling
- เพิ่ม `tests/test_smoke.py` + `.github/workflows/ci.yml` (มี `compileall` ดักไฟล์ truncate)

### ⚠️ ยังไม่แก้ — ความเสี่ยงที่ควรพิจารณา
- **Skill `tool.py` รันโค้ดอิสระ (RCE):** `skills_loader.py` ใช้ `spec.loader.exec_module()`
  รัน skill ในโปรเซสเดียวกันโดยไม่มี sandbox และ AI สร้าง skill เองได้ → skill ที่ AI หลอน
  สร้างขึ้นรันโค้ด Python ใด ๆ ได้ (ไม่ถูกจำกัดใน workspace). ถ้าตั้งใจเป็นแอป local คนเดียว
  พอรับได้ แต่ควรอย่างน้อย: ขอยืนยันก่อนรัน skill ใหม่ครั้งแรก / จำกัด import
- **`except Exception` แบบกลืน error ~9 จุดใน `server.py`** (หลายอันเป็น `pass` เงียบ) ทำให้
  ดีบักยาก — บั๊ก charmap นี้ก็เกิดจากการกลืน+เดาสาเหตุผิด ควรอย่างน้อย log `traceback` ทุกจุด
- **ไฟล์ `.py` เคย truncate/corrupt (เห็นซ้ำ 25–26 มิ.ย.)** อาจเกี่ยวกับ OneDrive sync ระหว่าง
  เขียนไฟล์ — `compileall` ใน CI จะดักได้ แต่ควรเฝ้าระวัง และพิจารณาย้าย repo ออกจากโฟลเดอร์
  ที่ OneDrive sync ตลอดเวลา
