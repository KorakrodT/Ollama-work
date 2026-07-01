# AGENTS.md — คู่มือบริบทสำหรับ AI Agent / นักพัฒนา ที่แก้โปรเจกต์นี้

โปรเจกต์: **LM Co-work** — แอป AI Agent รันโลคอลทั้งหมด คุยกับโมเดลผ่าน LM Studio
(เซิร์ฟเวอร์ OpenAI-compatible ที่ `http://localhost:1234/v1`) เปิดเป็นหน้าต่างโปรแกรม
จริงด้วย pywebview (WebView2) และแพ็กเป็น `.exe` ได้ ทุกอย่างทำงานในเครื่องผู้ใช้
ไม่มีข้อมูลออกเน็ต

> อ่าน `README.md` สำหรับมุมผู้ใช้ ไฟล์นี้คือมุม "คนที่แก้โค้ด" — สิ่งที่ต้องรู้ก่อนแตะของ

---

## คำสั่งที่ใช้บ่อย

```bash
py -m pip install -r requirements.txt   # ติดตั้ง deps (ใช้ py ไม่ใช่ python — ดูหมายเหตุ)
py server.py                            # รันแอป (เปิดหน้าต่าง pywebview)
py -m pytest tests/ -q                  # รัน smoke tests (ไม่ต้องมี LM Studio)
py -m ruff check --select F server.py tools.py agents.py agent_store.py data_store.py skills_loader.py mcp_client.py knowledge_store.py winproc.py
py -m compileall -q server.py tools.py agents.py agent_store.py data_store.py skills_loader.py mcp_client.py knowledge_store.py winproc.py
build-ui.bat                            # สร้าง dist\LM Co-work.exe (PyInstaller)
```

> **ทำไมต้อง `ruff --select F` ด้วย ไม่ใช่แค่ compileall/pytest:** `compileall` จับแค่
> SyntaxError, `pytest` ไม่ได้เรียก `main()` ตรงๆ (เปิดหน้าต่างจริง) — บั๊กแบบ "import ชื่อ
> ซ้ำในฟังก์ชันเดียวกับที่อ้างชื่อนั้นมาก่อนหน้า" (Python มองว่าเป็น local ทั้งฟังก์ชัน ->
> `UnboundLocalError`) เกิดขึ้นจริงกับ `main()`/`time` เมื่อ 1 ก.ค. 2026 ทำให้ .exe ที่ build
> ออกมาพังทันทีที่เปิด — ไม่มีเครื่องมือไหนข้างบนจับได้ ยกเว้น ruff F823

- **ใช้ `py` ไม่ใช่ `python`** บนเครื่องนี้ — `python` ชี้ไป venv ของแอปอื่น
- ไม่ต้องเปิด LM Studio เอง: แอปสั่ง `lms server start` แบบ headless ให้อัตโนมัติ
  (ต้องมี `lms` CLI + มีโมเดลที่รองรับ tool-calling โหลดไว้ ≥ 1 ตัว)

## แผนผังไฟล์ (ความรับผิดชอบ)

| ไฟล์ | หน้าที่ |
|------|--------|
| `server.py` | เว็บเซิร์ฟเวอร์ (HTTP), agent loop, route table, เชื่อม LM Studio, เปิดหน้าต่าง pywebview |
| `index.html` | UI หน้าเดียว (ไม่มี build step) — ธีม, แชต, Projects, พาเนลไฟล์, จัดการ agent/skill |
| `agents.py` | นิยาม agent ในตัว (persona + system prompt + รายการ tools) |
| `agent_store.py` | merge agent ในตัวกับที่ผู้ใช้สร้าง/แก้ (เก็บ `data/agents.json`) |
| `tools.py` | เครื่องมือที่ agent เรียกได้ + path-jail/SSRF guard + ตรวจไฟล์เสีย/ซ้ำ |
| `skills_loader.py` | โหลด/สร้าง/ลบ skill จากโฟลเดอร์ `skills/` + กลไกยืนยันก่อนรัน (D1) |
| `mcp_client.py` | client เชื่อม MCP server ภายนอก (อ่าน `mcp.json` ถ้ามี) |
| `knowledge_store.py` | RAG อย่างง่าย (Jaccard) เก็บใน `.knowledge_base.json` ในโฟลเดอร์งาน |
| `data_store.py` | เก็บ settings/chats/projects เป็น JSON (whitelist key) |
| `tests/test_smoke.py` | smoke tests — รันเร็ว ดักบั๊กพื้นฐานก่อน build |

## สถาปัตยกรรมโดยย่อ

1. หน้าเว็บ (`index.html`) เรียก HTTP API ของ `server.py` (`/api/*`)
2. `/api/chat` → `run_agent()` วนลูปสูงสุด `MAX_STEPS` ครั้ง: เรียกโมเดล →
   ถ้าโมเดลขอ tool call → รัน tool → ป้อนผลกลับ → ทำซ้ำจนได้คำตอบสุดท้าย
3. เครื่องมือมาจาก 3 แหล่ง รวมใน `tools.all_tool_schemas()`:
   เครื่องมือพื้นฐาน (`TOOL_SCHEMAS`) + skills (`SkillRegistry`) + MCP (`mcp_manager`)
4. `write_file` ไม่เขียนทันที — เก็บเป็น *proposal* ส่งกลับให้ UI ถามผู้ใช้กดยืนยัน
   แล้วค่อยเรียก `/api/apply` เขียนจริง (สำรอง `.bak` อัตโนมัติ)

## ค่าคงที่ความปลอดภัย (อย่าทำพัง)

- **Path jail:** อ่าน/เขียนไฟล์ผ่าน `tools._resolve()` เท่านั้น — กันหลุดออกนอกโฟลเดอร์งาน
- **ขอบเขต workspace:** `set_workspace` จำกัดใต้ project/home/temp; โหมด Co-Work ปลดล็อก
  ได้ แต่ยังกัน root ไดรฟ์/โฟลเดอร์ระบบเสมอ (`_is_blocked_root`)
- **SSRF guard:** `fetch_url` อนุญาตเฉพาะ host สาธารณะ (`_is_public_host`) และตรวจซ้ำ
  ทุก redirect (`_SafeRedirectHandler`)
- **Same-origin (CSRF):** ทุก `/api/*` ผ่าน `Handler._same_origin()` — ใช้ `ACTUAL_PORT`
  (พอร์ตจริงที่ bind สำเร็จ อาจเลื่อนจาก 11500)
- **ยืนยัน skill (D1):** skill ที่ผู้ใช้สร้างใหม่ต้องผ่าน `confirm_skill()` ก่อน `run()`
  ครั้งแรก — server คืน proposal `type="skill_confirm"` ให้ UI ถามก่อน
- มี test รองรับค่าคงที่เหล่านี้ใน `tests/test_smoke.py` — ถ้าแก้ตรงนี้ ต้องอัปเดต test ด้วย

## ความเสี่ยงที่ยังเปิดอยู่ (ยอมรับไว้ — แอป local คนเดียว)

- **RCE จาก skill:** `skills_loader._load_runner` ใช้ `exec_module()` รัน `tool.py` ใน
  โปรเซสเดียวกันโดยไม่มี sandbox และโค้ดระดับโมดูลรันตั้งแต่ตอน `discover()` (ก่อน
  ยืนยัน) — กลไก D1 กันแค่ตอนเรียก `run()` ไม่ได้กัน side-effect ตอน import
- **OneDrive sync:** ถ้า repo อยู่ในโฟลเดอร์ที่ OneDrive sync ไฟล์ `.py` เคย truncate/
  เป็น cloud-placeholder ได้ → CI มี `compileall` ดักก่อน build (ดูด้านล่าง)

## กฎ/ธรรมเนียมการเขียนโค้ด

- เพิ่ม tool ใหม่: เขียนฟังก์ชันใน `tools.py` → ลงใน `TOOLS` → เพิ่ม schema ใน
  `TOOL_SCHEMAS` (ถ้าเป็นเครื่องมือเขียนไฟล์ ให้ใส่ใน `WRITE_TOOLS` ด้วย)
- เพิ่ม agent ใหม่: ก็อปบล็อกใน `agents.AGENTS` (`tools: None`=ทุกอย่าง, `[]`=ไม่ใช้,
  `[...]`=เฉพาะที่ระบุ); `skill_categories` กรองหมวด skill ได้
- เพิ่ม route: เพิ่ม method `_route_*` ใน `Handler` แล้วลง `_POST_ROUTE_TABLE`
  (มี test `test_post_route_table_has_all_known_routes` ตรวจความครบ)
- **อย่านิยามฟังก์ชันชื่อซ้ำในไฟล์เดียว** — Python ผูกชื่อกับ def ตัวท้ายสุด def ก่อน
  หน้าจะกลายเป็น dead code เงียบ ๆ (เคยมีบั๊กแบบนี้: stub `check_ffmpeg`/`install_ffmpeg`
  ตัวล่างทับตัวจริง ทำให้ auto-install ใช้ไม่ได้)
- `except Exception` ที่จำเป็นต้องเงียบ ให้ใส่ `_log.debug(..., exc_info=True)` อย่างน้อย
  อย่า `except: pass` เปล่า ๆ (กลืน error ทำให้ดีบักยาก + จับ KeyboardInterrupt โดยไม่ตั้งใจ)
- ตอบผู้ใช้เป็นภาษาไทย โค้ด/ชื่อ identifier เป็นอังกฤษ

## ก่อนส่ง / ก่อน build

1. `py -m pytest tests/ -q` ให้ผ่านครบ
2. `py -m compileall ...` (รายการไฟล์เต็มด้านบน) — ดักไฟล์ truncate/SyntaxError
3. CI (`.github/workflows/ci.yml`) รัน 3 ขั้นนี้ (dependency audit + compileall + pytest)
   บน `windows-latest` อัตโนมัติ
4. ทดสอบด้วยมือ: แชตปกติ, โหมด Co-Work (สร้าง/แก้ไฟล์ + กดยืนยัน), `fetch_url`
5. **TEST-3 — QA มือสำหรับ escaping ใน `index.html`** (ยังไม่มี automated test ฝั่ง JS):
   สร้างไฟล์/โฟลเดอร์ในโฟลเดอร์งานที่ชื่อมีเครื่องหมาย `'` หรือ `"` ปน (เช่น
   `it's a test'.txt`) แล้วเปิดแท็บ Files ให้ทั้ง list ขึ้นและกดเปิดไฟล์นั้น — ต้องไม่มี
   JS error/alert popup ใดๆ โผล่ขึ้นมา (ถ้ามี แปลว่า escaping ใน `loadTree`/`openFile`/
   `renderChats` พังอีก — ดู SEC-2 ใน `AUDIT_REPORT_2026-07-01.md`) เช็คคู่กับชื่อแชตที่พิมพ์
   อักขระพิเศษด้วยเช่นกัน
