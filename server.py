"""
server.py — UI แบบหน้าต่างสไตล์ Claude desktop (ธีมน้ำเงิน) + Co-Work

ฟีเจอร์:
  - หลาย agent + tool calling (ผ่าน Ollama — OpenAI-compatible server)
  - โฟลเดอร์งาน (workspace) ที่ตั้งค่าได้ — อ่าน/เขียนไฟล์เฉพาะในนี้
  - Co-Work: AI เสนอการสร้าง/แก้ไฟล์ -> ผู้ใช้กด "บันทึก" ยืนยันก่อนเขียนจริง
  - แนบไฟล์: อัปโหลดไฟล์ข้อความเข้าโฟลเดอร์งานให้ AI อ่าน

รัน:   py server.py    (หรือดับเบิลคลิก run-ui.bat)
"""

from __future__ import annotations

import io
import json
import logging
import os
import re as _re
import sys
import threading
import time
import traceback
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# logging พื้นฐาน: แสดง warning+ บนคอนโซล พร้อม timestamp
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
_log = logging.getLogger("server")


def _force_utf8_streams() -> None:
    """กันปัญหา 'charmap' codec บน Windows ภาษาไทย.

    เมื่อ build แบบ --windowed (console=False) ตัว stdout/stderr อาจเป็น None
    หรือเป็น cp874 ('charmap') ทำให้พอมีโค้ด/ไลบรารี (เช่น pywebview) พิมพ์ log
    ภาษาไทยหรืออีโมจิตอนเปิดหน้าต่าง จะเกิด UnicodeEncodeError แล้ว crash
    (ซึ่งก่อนหน้านี้ถูกเดาผิดว่าเป็นเพราะไม่มี WebView2 Runtime).
    ฟังก์ชันนี้บังคับให้ทุก stream เป็น utf-8 และไม่ล้มแม้เจอตัวอักษรแปลก ๆ.
    """
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is None:
            # โหมดหน้าต่างไม่มี console: ใส่ sink รองรับ utf-8 กันโค้ดที่ print แล้วพัง
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8", errors="replace"))
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            try:
                setattr(sys, name, io.TextIOWrapper(
                    stream.buffer, encoding="utf-8", errors="replace", line_buffering=True))
            except Exception:  # noqa: BLE001
                # QUAL-3: อย่างน้อย log ไว้ debug ระดับ (ไม่ raise ต่อเพราะเป็น fallback สุดท้ายจริงๆ)
                _log.debug("_force_utf8_streams: ตั้ง utf-8 stream ไม่สำเร็จ (%s)", name, exc_info=True)


_force_utf8_streams()

from agents import DEFAULT_AGENT  # noqa: E402  # ต้องอยู่หลัง _force_utf8_streams()
import tools as T  # noqa: E402
import skills_loader as SL  # noqa: E402
import agent_store as AG  # noqa: E402
import data_store as DS  # noqa: E402

# OBS-1: log ลงไฟล์ data/app.log ด้วย — โหมด .exe (--windowed) ไม่มีคอนโซล
# ถ้าไม่มีไฟล์ log แปลว่า warning/audit trail (SEC-3) และ traceback (D2) หายเงียบหมด
_FILE_LOG_READY = False


def _setup_file_logging() -> None:
    """เพิ่ม RotatingFileHandler ที่ data/app.log (1MB × เก็บย้อนหลัง 3 ไฟล์).

    คอนโซลยังแสดงเฉพาะ WARNING+ เหมือนเดิม แต่ไฟล์เก็บตั้งแต่ INFO ขึ้นไป.
    """
    global _FILE_LOG_READY
    if _FILE_LOG_READY:
        return
    try:
        from logging.handlers import RotatingFileHandler
        os.makedirs(DS.DATA_DIR, exist_ok=True)
        fh = RotatingFileHandler(
            os.path.join(DS.DATA_DIR, "app.log"),
            maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        root = logging.getLogger()
        for h in root.handlers:          # handler คอนโซลเดิม: คุมระดับไว้ที่ WARNING+
            h.setLevel(logging.WARNING)
        root.addHandler(fh)
        root.setLevel(logging.INFO)      # ให้ INFO ไหลถึง file handler ได้
        _FILE_LOG_READY = True
    except Exception:  # noqa: BLE001 — log ไฟล์เป็นของเสริม อย่าทำแอปพังเพราะมัน
        _log.debug("_setup_file_logging: ตั้ง file logging ไม่สำเร็จ", exc_info=True)


_setup_file_logging()

# ----------------------------- backend / services -----------------------------
# refactor 2026-07-10: โค้ดชั้น "คุยกับโมเดล / agent loop / ตัวจัดตารางเวลา / สแกนไฟล์"
# ถูกแยกออกเป็นโมดูลของตัวเอง — server.py เหลือหน้าที่หลักคือ HTTP + หน้าต่างแอป.
# ยัง import ชื่อเดิมกลับเข้ามาที่นี่ (re-export) เพื่อให้โค้ด/เทสต์ที่อ้าง server.<ชื่อ>
# ใช้ได้เหมือนเดิมทุกตัว ไม่ต้องแก้ตาม.
import ollama_client as OL  # noqa: E402
import agent_runtime as AR  # noqa: E402
import scheduler as SCHED  # noqa: E402
import audio_scan as AUDIO  # noqa: E402

# --- Ollama client (ดูรายละเอียดใน ollama_client.py) ---
OLLAMA_BASE = OL.OLLAMA_BASE
OLLAMA_KEY = OL.OLLAMA_KEY
MODEL = OL.MODEL
ollama_models = OL.ollama_models
default_model = OL.default_model
ensure_ollama = OL.ensure_ollama
_ollama_get = OL._ollama_get
_ollama_alive = OL._ollama_alive
_openai_chat = OL._openai_chat

# --- agent runtime / tool calling (ดู agent_runtime.py) ---
MAX_STEPS = AR.MAX_STEPS
COWORK_TOOLS = AR.COWORK_TOOLS
CONFIRM_TOOLS = AR.CONFIRM_TOOLS
schemas_for = AR.schemas_for
run_agent = AR.run_agent
request_cancel = AR.request_cancel
_clear_cancel = AR._clear_cancel
_is_cancelled = AR._is_cancelled
_handle_tool_call = AR._handle_tool_call
_extract_message = AR._extract_message
_format_error_reply = AR._format_error_reply
_run = AR._run

# --- งานตามเวลา (ดู scheduler.py) ---
_sched_due = SCHED._sched_due
_run_schedule = SCHED._run_schedule
_scheduler_loop = SCHED._scheduler_loop
_sched_running = SCHED._sched_running

# --- งานตรวจไฟล์/สแกน (ดู audio_scan.py) ---
# _audio_state/_audio_lock อ้างถึง object เดียวกับใน audio_scan (mutate ในที่ ไม่ rebind)
# จึงแชร์สถานะกันได้ระหว่าง Handler (อ่าน/รีเซ็ต) กับ _audio_worker (เขียน progress)
_blank_scan = AUDIO._blank_scan
_audio_worker = AUDIO._audio_worker
_audio_lock = AUDIO._audio_lock
_audio_state = AUDIO._audio_state

# --- ค่าคงที่ของเซิร์ฟเวอร์/หน้าต่าง (คงไว้ที่ server.py) ---
HOST, PORT = "127.0.0.1", 11500
# พอร์ตจริงที่ bind สำเร็จ (อาจเลื่อนจาก PORT ถ้าชน) — _same_origin/URL ต้องใช้ค่านี้
ACTUAL_PORT = PORT
HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))



# ----------------------------- web server -----------------------------

# C1: Route table สำหรับ do_POST — แต่ละ entry คือ (handler_method)
# handler เป็น method ของ Handler รับ (body: dict) คืน None (เรียก self._send เอง)
# สร้างทีหลัง class ผ่าน _register_routes() เพื่อให้ method binding ทำงานถูกต้อง
_POST_ROUTES: dict[str, str] = {}   # path -> method name (จะ bind ใน do_POST)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8", no_cache=False):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if no_cache:
            # กัน WebView2 หยิบ index.html เก่าจาก cache (เปิดแล้ว "ไม่เห็นเปลี่ยน")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def _json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def _same_origin(self) -> bool:
        """กันคำสั่งข้ามเว็บ (CSRF): อนุญาตเฉพาะคำขอจากหน้าตัวเอง.

        pywebview/หน้าเว็บของแอปเองจะส่ง Origin/Referer เป็น http://127.0.0.1:<ACTUAL_PORT>
        หรือไม่ส่งมาเลย ส่วนเว็บภายนอกในเบราว์เซอร์จะมี Origin เป็นโดเมนอื่น -> ปฏิเสธ.
        ใช้ ACTUAL_PORT (อาจเลื่อนจาก PORT ตอน bind) ไม่ใช่ค่าคงที่ตายตัว.
        """
        port = ACTUAL_PORT
        allowed = f"http://{HOST}:{port}"
        allowed_host = f"{HOST}:{port}"
        host = (self.headers.get("Host") or "").lower()
        if host and host != allowed_host:
            return False
        origin = self.headers.get("Origin")
        if origin is not None:
            return origin == allowed
        ref = self.headers.get("Referer")
        if ref is not None:
            parsed = urllib.parse.urlparse(ref)
            return f"{parsed.scheme}://{parsed.netloc}" == allowed
        return True  # ไม่มี Origin/Referer (เช่น pywebview) -> ถือว่าปลอดภัย

    # ------------------------------------------------------------------
    # GET routes
    # ------------------------------------------------------------------
    def do_GET(self):
        path0 = self.path.split("?", 1)[0]   # ตัด query (?v=cache-buster) ออกก่อน match
        if path0.startswith("/api/") and not self._same_origin():
            self._send(403, json.dumps({"error": "ปฏิเสธ: คำขอข้ามต้นทาง (cross-origin)"},
                                       ensure_ascii=False))
            return
        if path0 in ("/", "/index.html"):
            try:
                with open(os.path.join(HERE, "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8", no_cache=True)
            except FileNotFoundError:
                self._send(404, "index.html not found", "text/plain; charset=utf-8")
        elif self.path == "/api/agents":
            self._send(200, json.dumps({
                "model": default_model(),
                "default": DEFAULT_AGENT,
                "workspace": T.WORKSPACE,
                "agents": AG.list_agents(),
                "tools_available": AG.AVAILABLE_TOOLS,
                "skills": T.skills_list(),
            }, ensure_ascii=False))
        elif self.path == "/api/models":
            names = ollama_models()          # ดึงรายชื่อโมเดลจาก Ollama
            if MODEL and MODEL not in names:
                names.insert(0, MODEL)
            self._send(200, json.dumps({"models": names}, ensure_ascii=False))
        elif self.path == "/api/audio-scan-status":
            with _audio_lock:
                self._send(200, json.dumps(dict(_audio_state), ensure_ascii=False))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    # ------------------------------------------------------------------
    # POST route handlers (C1: แยกแต่ละ route เป็นฟังก์ชัน)
    # ------------------------------------------------------------------

    def _route_audio_scan(self, p: dict) -> None:
        with _audio_lock:
            if _audio_state["running"]:
                self._send(200, json.dumps({"ok": False, "error": "กำลังตรวจอยู่แล้ว"},
                                           ensure_ascii=False))
                return
            _audio_state.clear()
            _audio_state.update(_blank_scan())
            _audio_state["running"] = True
        threading.Thread(
            target=_audio_worker,
            args=(p.get("folder", ""), p.get("recursive", True), p.get("ext", "")),
            daemon=True).start()
        self._send(200, json.dumps({"ok": True}, ensure_ascii=False))

    def _route_chat(self, p: dict) -> None:
        T.set_cowork(p.get("cowork", False))
        if p.get("workspace"):
            T.set_workspace(p["workspace"])
        result = run_agent(p.get("agent", DEFAULT_AGENT),
                           p.get("messages", []),
                           p.get("model", MODEL),
                           cowork=p.get("cowork", False),
                           provider=p.get("provider"))
        self._send(200, json.dumps(result, ensure_ascii=False))

    def _route_cancel(self, p: dict) -> None:  # noqa: ARG002
        """B2: หยุด run_agent ที่กำลังทำงานอยู่."""
        request_cancel()
        self._send(200, json.dumps({"ok": True}, ensure_ascii=False))

    def _route_apply(self, p: dict) -> None:
        # ผู้ใช้กดยืนยัน -> เขียนไฟล์จริง (สำรอง .bak ให้อัตโนมัติ)
        if p.get("workspace"):
            T.set_workspace(p["workspace"])
        msg = T.write_file(p.get("path", "untitled.txt"), p.get("content", ""))
        self._send(200, json.dumps({"ok": True, "message": msg}, ensure_ascii=False))

    def _route_upload(self, p: dict) -> None:
        # แนบไฟล์ -> เซฟลงโฟลเดอร์งาน
        if p.get("workspace"):
            T.set_workspace(p["workspace"])
        name = os.path.basename(p.get("name", "upload.txt"))
        msg = T.write_file(name, p.get("content", ""))
        self._send(200, json.dumps({"ok": True, "name": name, "message": msg},
                                   ensure_ascii=False))

    def _route_setdir(self, p: dict) -> None:
        T.set_cowork(p.get("cowork", False))
        actual = T.set_workspace(p.get("path"))
        self._send(200, json.dumps({"ok": True, "workspace": actual}, ensure_ascii=False))

    def _route_reload_skills(self, p: dict) -> None:  # noqa: ARG002
        n = T.reload_skills()
        self._send(200, json.dumps({"ok": True, "count": n, "skills": T.skills_list()},
                                   ensure_ascii=False))

    def _route_create_skill(self, p: dict) -> None:
        ok, msg = SL.create_skill(
            p.get("name", ""), p.get("description", ""), p.get("type", "code"),
            p.get("parameters"), p.get("tool_code"), p.get("prompt_text"),
            category=p.get("category", "General"), overwrite=p.get("is_edit", False))
        if ok:
            T.reload_skills()
        self._send(200, json.dumps({"ok": ok, "message": msg, "skills": T.skills_list()},
                                   ensure_ascii=False))

    def _route_get_skill(self, p: dict) -> None:
        data = SL.get_skill_data(p.get("name", ""))
        if data:
            self._send(200, json.dumps({"ok": True, "data": data}, ensure_ascii=False))
        else:
            self._send(200, json.dumps({"ok": False, "message": "ไม่พบข้อมูล skill"},
                                       ensure_ascii=False))

    def _route_delete_skill(self, p: dict) -> None:
        ok, msg = SL.delete_skill(p.get("name", ""))
        if ok:
            T.reload_skills()
        self._send(200, json.dumps({"ok": ok, "message": msg, "skills": T.skills_list()},
                                   ensure_ascii=False))

    def _route_import_skill(self, p: dict) -> None:
        ok, msg = SL.import_or_convert_skill(p.get("path", ""))
        if ok:
            T.reload_skills()
        self._send(200, json.dumps({"ok": ok, "message": msg, "skills": T.skills_list()},
                                   ensure_ascii=False))

    def _route_files(self, p: dict) -> None:
        if p.get("workspace"):
            T.set_workspace(p["workspace"])
        base = os.path.abspath(T.WORKSPACE)
        sub = p.get("path", "") or ""
        full = os.path.abspath(os.path.join(base, sub))
        if not (full == base or full.startswith(base + os.sep)):
            full, sub = base, ""
        items = []
        if os.path.isdir(full):
            for name in sorted(os.listdir(full), key=lambda s: s.lower()):
                fp = os.path.join(full, name)
                is_dir = os.path.isdir(fp)
                items.append({"name": name, "dir": is_dir,
                              "size": 0 if is_dir else os.path.getsize(fp)})
        items.sort(key=lambda x: (not x["dir"], x["name"].lower()))
        self._send(200, json.dumps({"workspace": base, "path": sub, "files": items},
                                   ensure_ascii=False))

    def _route_readfile(self, p: dict) -> None:
        if p.get("workspace"):
            T.set_workspace(p["workspace"])
        content = T.read_file(p.get("path", ""))
        self._send(200, json.dumps({"content": content}, ensure_ascii=False))

    def _route_get_agent(self, p: dict) -> None:
        data = AG.get_agent(p.get("key", ""))
        if data:
            out = dict(data)
            out["key"] = p.get("key", "")
            self._send(200, json.dumps({"ok": True, "data": out}, ensure_ascii=False))
        else:
            self._send(200, json.dumps({"ok": False, "message": "ไม่พบ agent"},
                                       ensure_ascii=False))

    def _route_save_agent(self, p: dict) -> None:
        data = {
            "title": p.get("title", ""),
            "description": p.get("description", ""),
            "system": p.get("system", ""),
            "tools": p.get("tools", None),
            "skill_categories": p.get("skill_categories"),
        }
        ok, msg = AG.save_agent(p.get("key", ""), data, is_new=bool(p.get("is_new")))
        self._send(200, json.dumps(
            {"ok": ok, "message": msg, "agents": AG.list_agents()}, ensure_ascii=False))

    def _route_delete_agent(self, p: dict) -> None:
        ok, msg = AG.delete_agent(p.get("key", ""))
        self._send(200, json.dumps(
            {"ok": ok, "message": msg, "agents": AG.list_agents()}, ensure_ascii=False))

    def _route_import_agent_folder(self, p: dict) -> None:
        folder = p.get("path", "")
        if not os.path.isdir(folder):
            self._send(200, json.dumps({"ok": False, "message": "ไม่พบโฟลเดอร์"},
                                       ensure_ascii=False))
            return
        # SEC-1: กันไม่ให้เดินไฟล์ทั้ง root ไดรฟ์/โฟลเดอร์ระบบ (เช่น C:\ หรือ C:\Windows)
        # ที่นี่จะอ่านไฟล์ข้อความทุกไฟล์ในโฟลเดอร์แล้วฝังเป็น system prompt ของ agent
        # ใหม่ — เหมือนกับที่ _route_audio_scan/collect_files กันไว้อยู่แล้ว
        if T._is_blocked_root(os.path.abspath(folder)):
            self._send(200, json.dumps(
                {"ok": False, "message": "ปฏิเสธ: นำเข้าจาก root ไดรฟ์หรือโฟลเดอร์ระบบไม่ได้"},
                ensure_ascii=False))
            return
        base = os.path.basename(os.path.normpath(folder)) or "imported_agent"
        skip = (".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll", ".so", ".pyc",
                ".zip", ".tar", ".gz", ".mp4", ".mp3", ".wav", ".pdf")
        chunks = []
        for root, dirs, files in os.walk(folder):
            for fn in files:
                if fn.startswith("."):
                    continue
                if fn.lower().endswith(skip):
                    continue
                fp = os.path.join(root, fn)
                try:
                    if os.path.getsize(fp) < 50000:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                            c = fh.read()
                        if c.strip():
                            rel = os.path.relpath(fp, folder)
                            chunks.append(f"## {rel}\n{c}")
                except Exception:  # noqa: BLE001
                    _log.debug("import-agent-folder: skip unreadable file", exc_info=True)
        text = ("\n\n".join(chunks))[:100000]
        existing = set(AG.all_agents().keys())
        slug = _re.sub(r"[^a-zA-Z0-9_-]", "_", base).strip("_").lower() or "imported_agent"
        key, i = slug, 1
        while key in existing:
            key = f"{slug}_{i}"
            i += 1
        sysp = (f"คุณคือผู้ช่วยที่มีความรู้จากโฟลเดอร์ '{base}' ตอบเป็นภาษาไทย.\n\n"
                f"[ความรู้อ้างอิง]\n{text}")
        ok, msg = AG.save_agent(key, {
            "title": f"📁 {base}", "description": f"agent จากโฟลเดอร์ {base}",
            "system": sysp, "tools": None, "skill_categories": None}, is_new=True)
        self._send(200, json.dumps({
            "ok": ok,
            "message": (f"นำเข้าเป็น agent '{key}' แล้ว") if ok else msg,
            "agents": AG.list_agents()}, ensure_ascii=False))

    def _route_init_workspace(self, p: dict) -> None:
        """F3: จัดโครงสร้างโฟลเดอร์งานเริ่มต้น (สร้างเฉพาะที่ยังไม่มี — ไม่ทับของเดิม).

        เขียนตรงได้โดยไม่ผ่าน proposal flow เพราะ trigger คือผู้ใช้กดปุ่มเอง
        (ไม่ใช่ AI ตัดสินใจ) และไม่ overwrite ไฟล์ใดๆ ที่มีอยู่แล้ว.
        """
        if p.get("workspace"):
            T.set_workspace(p["workspace"])
        base = os.path.abspath(T.WORKSPACE)
        created: list[str] = []
        skipped: list[str] = []
        for d in ("inbox", "projects", "archive"):
            full = os.path.join(base, d)
            if os.path.isdir(full):
                skipped.append(d + "/")
            else:
                os.makedirs(full, exist_ok=True)
                created.append(d + "/")
        templates = {
            T.AGENT_FILE: (
                "# คำสั่งประจำโฟลเดอร์งาน\n\n"
                "AI อ่านไฟล์นี้อัตโนมัติทุกครั้งก่อนเริ่มตอบในโฟลเดอร์นี้ — เขียนกฎ/บริบทของงาน เช่น\n\n"
                "- ตอบภาษาไทย กระชับ ตรงประเด็น\n"
                "- งานในโฟลเดอร์นี้คือ: (เติมเอง)\n"
                "- ไฟล์งานใหม่เข้าที่ inbox/ งานที่ทำอยู่ใน projects/ งานจบแล้วย้ายไป archive/\n\n"
                f"(อ่านสูงสุด {T.AGENT_MAX_CHARS} ตัวอักษรแรก — เขียนเรื่องสำคัญไว้บนสุด)\n"
            ),
            T.MEMORY_FILE: (
                "# ความจำของโฟลเดอร์นี้\n\n"
                "AI เพิ่มบันทึกที่นี่ผ่านเครื่องมือ remember (ถามยืนยันก่อนทุกครั้ง) "
                "และคุณแก้/ลบเองได้ตามใจ\n"
            ),
        }
        for name, content in templates.items():
            full = os.path.join(base, name)
            if os.path.isfile(full):
                skipped.append(name)
            else:
                with open(full, "w", encoding="utf-8") as f:
                    f.write(content)
                created.append(name)
        self._send(200, json.dumps({"ok": True, "created": created, "skipped": skipped},
                                   ensure_ascii=False))

    # ------------------------------------------------------------------
    # F4: MCP Connectors — จัดการ mcp.json ผ่าน UI
    # ------------------------------------------------------------------

    @staticmethod
    def _load_mcp_config() -> dict:
        if os.path.isfile(T.MCP_CONFIG_PATH):
            try:
                with open(T.MCP_CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if isinstance(cfg, dict):
                    return cfg
            except Exception:  # noqa: BLE001
                _log.warning("mcp.json อ่านไม่ได้/ผิดรูปแบบ — เริ่มจาก config ว่าง", exc_info=True)
        return {}

    @staticmethod
    def _save_mcp_config(cfg: dict) -> None:
        # เขียนแบบ atomic (tmp + os.replace) — ดับกลางคันไฟล์ไม่พัง
        tmp = T.MCP_CONFIG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        os.replace(tmp, T.MCP_CONFIG_PATH)

    def _route_mcp_status(self, p: dict) -> None:  # noqa: ARG002
        self._send(200, json.dumps({
            "ok": True,
            "config_path": T.MCP_CONFIG_PATH,
            "exists": os.path.isfile(T.MCP_CONFIG_PATH),
            "servers": T.mcp_manager.status(),
        }, ensure_ascii=False))

    def _route_mcp_reload(self, p: dict) -> None:  # noqa: ARG002
        n = T.init_mcp()
        self._send(200, json.dumps({"ok": True, "tools": n,
                                    "servers": T.mcp_manager.status()}, ensure_ascii=False))

    def _route_mcp_save(self, p: dict) -> None:
        """เพิ่ม/แก้ MCP server หนึ่งตัวใน mcp.json แล้ว reload."""
        sid = _re.sub(r"[^a-zA-Z0-9_-]", "_", (p.get("id") or "").strip()).strip("_")
        command = (p.get("command") or "").strip()
        if not sid or not command:
            self._send(200, json.dumps({"ok": False, "message": "ต้องระบุ id และ command"},
                                       ensure_ascii=False))
            return
        args = p.get("args") or []
        if isinstance(args, str):
            args = args.split()
        env = p.get("env") if isinstance(p.get("env"), dict) else {}
        cfg = self._load_mcp_config()
        cfg.setdefault("mcpServers", {})[sid] = {
            "command": command, "args": [str(a) for a in args], "env": env}
        self._save_mcp_config(cfg)
        n = T.init_mcp()
        self._send(200, json.dumps({
            "ok": True, "id": sid, "tools": n, "servers": T.mcp_manager.status(),
            "message": (f"บันทึก '{sid}' แล้ว — เครื่องมือของ connector "
                        f"จะถูกถามยืนยันก่อนใช้ครั้งแรกเสมอ")}, ensure_ascii=False))

    def _route_mcp_delete(self, p: dict) -> None:
        sid = (p.get("id") or "").strip()
        cfg = self._load_mcp_config()
        servers = cfg.get("mcpServers", {})
        if sid not in servers:
            self._send(200, json.dumps({"ok": False, "message": f"ไม่พบ connector '{sid}'"},
                                       ensure_ascii=False))
            return
        del servers[sid]
        self._save_mcp_config(cfg)
        n = T.init_mcp()
        self._send(200, json.dumps({"ok": True, "tools": n,
                                    "servers": T.mcp_manager.status()}, ensure_ascii=False))

    def _route_schedule_run(self, p: dict) -> None:
        """F5: รันงานตามเวลาทันที (ปุ่ม ▶ ใน UI) — รันใน background ไม่บล็อก request.

        ไม่แตะ last_run (การทดสอบด้วยมือไม่ควรทำให้รอบอัตโนมัติของวันนี้ถูกข้าม).
        """
        sid = p.get("id") or ""
        items = DS.load("schedules", []) or []
        s = next((x for x in items if isinstance(x, dict) and x.get("id") == sid), None)
        if s is None:
            self._send(200, json.dumps({"ok": False, "message": "ไม่พบงานนี้"},
                                       ensure_ascii=False))
            return

        def _bg(job: dict):
            with _sched_running:
                try:
                    result = _run_schedule(job)
                except Exception as e:  # noqa: BLE001
                    result = f"ผิดพลาด: {e}"
                    _log.warning("schedule-run '%s' failed", job.get("title"), exc_info=True)
                cur_items = DS.load("schedules", []) or []
                for x in cur_items:
                    if isinstance(x, dict) and x.get("id") == sid:
                        x["last_result"] = result
                DS.save("schedules", cur_items)

        threading.Thread(target=_bg, args=(dict(s),), daemon=True).start()
        self._send(200, json.dumps(
            {"ok": True, "message": "เริ่มรันแล้ว — ผลจะอยู่ในโฟลเดอร์ reports/ ของโฟลเดอร์งาน"},
            ensure_ascii=False))

    def _route_confirm_skill(self, p: dict) -> None:
        """D1: ผู้ใช้กด 'อนุมัติ' skill ใหม่ → confirm แล้วรันจริง คืนผล."""
        name = p.get("name", "")
        args = p.get("args") or {}
        if not name:
            self._send(200, json.dumps({"ok": False, "message": "ต้องระบุชื่อ skill"},
                                       ensure_ascii=False))
            return
        SL.confirm_skill(name)
        result = _run(name, args)
        self._send(200, json.dumps({"ok": True, "result": result}, ensure_ascii=False))

    def _route_get_data(self, p: dict) -> None:
        self._send(200, json.dumps({"ok": True, "data": DS.load(p.get("key", ""))},
                                   ensure_ascii=False))

    def _route_set_data(self, p: dict) -> None:
        ok = DS.save(p.get("key", ""), p.get("data"))
        self._send(200, json.dumps({"ok": ok}, ensure_ascii=False))

    def _route_model_info(self, p: dict) -> None:
        name = p.get("model") or default_model()
        info: dict = {"context": None}
        try:
            data = _ollama_get("/models")
            for m in data.get("data", []) or []:
                if isinstance(m, dict) and m.get("id") == name:
                    ctx = (m.get("context_length")
                           or m.get("max_context_length")
                           or m.get("loaded_context_length"))
                    if ctx:
                        try:
                            info["context"] = int(ctx)
                        except Exception:  # noqa: BLE001
                            _log.debug("model-info: bad context value", exc_info=True)
                    info["family"] = m.get("type") or m.get("object")
                    break
        except Exception as e:  # noqa: BLE001
            _log.warning("model-info: %s", e)
            info["error"] = str(e)
        self._send(200, json.dumps({"ok": True, "info": info}, ensure_ascii=False))

    # ------------------------------------------------------------------
    # C1: Route dispatch (do_POST ใหม่ — ใช้ route table)
    # ------------------------------------------------------------------

    # POST_ROUTES: map path -> method name
    _POST_ROUTE_TABLE: dict[str, str] = {
        "/api/audio-scan":           "_route_audio_scan",
        "/api/chat":                 "_route_chat",
        "/api/cancel":               "_route_cancel",
        "/api/apply":                "_route_apply",
        "/api/upload":               "_route_upload",
        "/api/setdir":               "_route_setdir",
        "/api/reload-skills":        "_route_reload_skills",
        "/api/create-skill":         "_route_create_skill",
        "/api/get-skill":            "_route_get_skill",
        "/api/delete-skill":         "_route_delete_skill",
        "/api/import-skill":         "_route_import_skill",
        "/api/files":                "_route_files",
        "/api/readfile":             "_route_readfile",
        "/api/get-agent":            "_route_get_agent",
        "/api/save-agent":           "_route_save_agent",
        "/api/delete-agent":         "_route_delete_agent",
        "/api/import-agent-folder":  "_route_import_agent_folder",
        "/api/get-data":             "_route_get_data",
        "/api/set-data":             "_route_set_data",
        "/api/model-info":           "_route_model_info",
        "/api/confirm-skill":        "_route_confirm_skill",   # D1
        "/api/init-workspace":       "_route_init_workspace",  # F3
        "/api/mcp-status":           "_route_mcp_status",      # F4
        "/api/mcp-reload":           "_route_mcp_reload",      # F4
        "/api/mcp-save":             "_route_mcp_save",        # F4
        "/api/mcp-delete":           "_route_mcp_delete",      # F4
        "/api/schedule-run":         "_route_schedule_run",    # F5
    }

    def do_POST(self) -> None:
        if not self._same_origin():
            self._send(403, json.dumps({"error": "ปฏิเสธ: คำขอข้ามต้นทาง (cross-origin)"},
                                       ensure_ascii=False))
            return
        method_name = self._POST_ROUTE_TABLE.get(self.path)
        if method_name is None:
            self._send(404, json.dumps({"error": "not found"}))
            return
        # D2: log traceback แทนกลืนเงียบ
        try:
            body = self._json()
            getattr(self, method_name)(body)
        except Exception as e:  # noqa: BLE001
            _log.error("POST %s raised: %s\n%s", self.path, e, traceback.format_exc())
            try:
                self._send(500, json.dumps({"reply": f"เกิดข้อผิดพลาด: {e}",
                                            "error": str(e),
                                            "tools": [], "proposals": []},
                                           ensure_ascii=False))
            except Exception:  # noqa: BLE001  — อาจ send ซ้ำถ้า header ส่งไปแล้ว
                pass


class JsApi:
    """API ที่ฝั่งหน้าเว็บเรียกผ่าน window.pywebview.api เพื่อเปิดกล่องเลือกโฟลเดอร์จริง."""
    def pick_folder(self):
        try:
            import webview
            win = webview.windows[0]
            res = win.create_file_dialog(webview.FOLDER_DIALOG)
            if res:
                return res[0] if isinstance(res, (list, tuple)) else res
        except Exception:  # noqa: BLE001
            # QUAL-3: log ไว้ debug — เดิมกลืนเงียบทำให้ debug ไม่ได้ว่าทำไมเลือกโฟลเดอร์ไม่ได้
            _log.debug("pick_folder: เปิด file dialog ไม่สำเร็จ", exc_info=True)
        return ""

    def copy_text(self, text):
        """คัดลอกข้อความลงคลิปบอร์ดฝั่ง Python (fallback เมื่อ WebView2 บล็อก clipboard ของ JS)."""
        # 1) ลองใช้ tkinter (มีใน stdlib ไม่ต้องติดตั้งเพิ่ม)
        try:
            import tkinter
            r = tkinter.Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(text)
            r.update()  # ค้างค่าไว้ในคลิปบอร์ด
            r.destroy()
            return True
        except Exception:  # noqa: BLE001
            # QUAL-3: tkinter ใช้ไม่ได้เป็นเรื่องปกติในบางเครื่อง (ไม่มี Tcl/Tk) — log debug แล้วลอง pyperclip ต่อ
            _log.debug("copy_text: tkinter ใช้ไม่ได้ ลอง pyperclip ต่อ", exc_info=True)
        # 2) สำรอง: pyperclip ถ้ามีติดตั้ง
        try:
            import pyperclip
            pyperclip.copy(text)
            return True
        except Exception:  # noqa: BLE001
            _log.debug("copy_text: pyperclip ก็ใช้ไม่ได้ — คัดลอกไม่สำเร็จ", exc_info=True)
            return False

    def read_text(self):
        """อ่านข้อความจากคลิปบอร์ดฝั่ง Python (fallback สำหรับ Paste เมื่อ WebView2 บล็อก clipboard ของ JS)."""
        # 1) tkinter (stdlib)
        try:
            import tkinter
            r = tkinter.Tk()
            r.withdraw()
            try:
                data = r.clipboard_get()
            except Exception:  # noqa: BLE001 - คลิปบอร์ดว่าง/ไม่ใช่ข้อความ
                data = ""
            r.destroy()
            return data
        except Exception:  # noqa: BLE001
            # QUAL-3: tkinter ใช้ไม่ได้เป็นเรื่องปกติในบางเครื่อง (ไม่มี Tcl/Tk) — log debug แล้วลอง pyperclip ต่อ
            _log.debug("read_text: tkinter ใช้ไม่ได้ ลอง pyperclip ต่อ", exc_info=True)
        # 2) สำรอง: pyperclip
        try:
            import pyperclip
            return pyperclip.paste() or ""
        except Exception:  # noqa: BLE001
            _log.debug("read_text: pyperclip ก็ใช้ไม่ได้ — อ่านคลิปบอร์ดไม่สำเร็จ", exc_info=True)
            return ""


def _bind_server() -> ThreadingHTTPServer | None:
    """สร้างเซิร์ฟเวอร์ — ลอง bind พอร์ตเริ่มต้น ถ้าชนเลื่อนไปพอร์ตถัดไป (สูงสุด 10 พอร์ต).

    อัปเดต global ACTUAL_PORT เป็นพอร์ตที่ bind สำเร็จ คืน server หรือ None ถ้าทุกพอร์ตไม่ว่าง
    (กันแอป crash ตอนเปิดเมื่อมีอินสแตนซ์เดิมค้างอยู่ / พอร์ตถูกใช้).
    """
    global ACTUAL_PORT
    for offset in range(10):
        port = PORT + offset
        try:
            srv = ThreadingHTTPServer((HOST, port), Handler)
            ACTUAL_PORT = port
            return srv
        except OSError:
            continue
    return None


def _apply_window_icon(title: str = "LM Co-work") -> None:
    """ตั้งไอคอนหน้าต่าง/taskbar บน Windows.

    ทำไมต้องมี: `icon=` ใน PyInstaller spec ตั้งไอคอนให้ "ตัวไฟล์ .exe" เท่านั้น
    แต่หน้าต่างที่ pywebview สร้าง (WinForms) ใช้ไอคอน generic ของตัวเอง ทำให้
    ไอคอนบน taskbar ตอนรันไม่ใช่โลโก้แอป — ต้องยิง WM_SETICON ใส่ hwnd เอง.
    รันใน background thread: รอหน้าต่างโผล่ก่อน (โพลสูงสุด 10 วิ) แล้วค่อยตั้ง.
    """
    if os.name != "nt":
        return
    ico = os.path.join(HERE, "icon.ico")
    if not os.path.isfile(ico):
        _log.debug("_apply_window_icon: ไม่พบ icon.ico ที่ %s", ico)
        return
    try:
        import ctypes
        hwnd = 0
        deadline = time.time() + 10
        while not hwnd and time.time() < deadline:
            hwnd = ctypes.windll.user32.FindWindowW(None, title)
            if not hwnd:
                time.sleep(0.3)
        if not hwnd:
            _log.debug("_apply_window_icon: หา hwnd ของหน้าต่าง '%s' ไม่เจอ", title)
            return
        IMAGE_ICON, LR_LOADFROMFILE = 1, 0x0010
        WM_SETICON, ICON_SMALL, ICON_BIG = 0x0080, 0, 1
        for size, which in ((16, ICON_SMALL), (32, ICON_BIG)):
            hicon = ctypes.windll.user32.LoadImageW(
                None, ico, IMAGE_ICON, size, size, LR_LOADFROMFILE)
            if hicon:
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, which, hicon)
    except Exception:  # noqa: BLE001
        _log.debug("_apply_window_icon: ตั้งไอคอนไม่สำเร็จ", exc_info=True)


def main():
    # ให้ Windows มองแอปนี้เป็นแอปของตัวเอง (ไม่จัดกลุ่ม/ใช้ไอคอนของ host process อื่น)
    # ต้องเรียกก่อนสร้างหน้าต่าง — มีผลกับไอคอน+การ pin บน taskbar
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("LMCoWork.App")
        except Exception:  # noqa: BLE001
            _log.debug("SetCurrentProcessExplicitAppUserModelID ไม่สำเร็จ", exc_info=True)
    T.set_workspace(None)  # สร้างโฟลเดอร์งานเริ่มต้น

    # QUAL-5: โหลด MCP servers ใน background — ไม่บล็อกการเปิดหน้าต่าง
    def _mcp_boot():
        try:
            n = T.init_mcp()
            if n:
                _log.info("MCP พร้อม: %d tools จาก %d server", n, len(T.mcp_manager.clients))
        except Exception:  # noqa: BLE001
            _log.warning("โหลด MCP ไม่สำเร็จ", exc_info=True)

    threading.Thread(target=_mcp_boot, daemon=True).start()

    # F5: scheduler งานตามเวลา (รันเฉพาะตอนแอปเปิดอยู่)
    threading.Thread(target=_scheduler_loop, daemon=True).start()

    # สตาร์ต Ollama server แบบ headless อัตโนมัติ (ไม่ต้องเปิดแอป Ollama เอง)
    # ทำใน background thread เพื่อไม่บล็อกการเปิดหน้าต่าง และสตาร์ตแค่ครั้งเดียว
    if not _ollama_alive():
        print("⏳ กำลังสตาร์ต Ollama server แบบ headless (เบื้องหลัง) ...")
        threading.Thread(target=ensure_ollama, daemon=True).start()
    else:
        print(f"✅ Ollama server พร้อม ({OLLAMA_BASE})")

    server = _bind_server()
    if server is None:
        # ทุกพอร์ตไม่ว่าง -> แจ้งเตือนชัด (อย่า crash เงียบ)
        msg = (f"เปิดเซิร์ฟเวอร์ไม่ได้: พอร์ต {PORT}–{PORT + 9} ทั้งหมดถูกใช้อยู่ "
               f"(อาจมี LM Co-work เปิดค้างอยู่อินสแตนซ์เดิม) ปิดโปรแกรมเดิมแล้วลองอีกครั้ง")
        frozen = getattr(sys, "frozen", False)
        if frozen:
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, msg, "LM Co-work", 0x10)
            except Exception:  # noqa: BLE001
                print(msg, file=sys.stderr)
        else:
            print(msg, file=sys.stderr)
        return

    # cache-buster ?v=<เวลาเปิด> ทำให้ URL ไม่ซ้ำเดิม -> WebView2 โหลด index.html ใหม่เสมอ
    url = f"http://{HOST}:{ACTUAL_PORT}/?v={int(time.time())}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    frozen = getattr(sys, "frozen", False)   # True เมื่อรันเป็น .exe
    print(f"🤖 LM Co-work พร้อมแล้ว -> {url}"
          + (f"  (พอร์ต {PORT} ชน เลื่อนไปใช้ {ACTUAL_PORT})" if ACTUAL_PORT != PORT else ""))
    print(f"   โฟลเดอร์งานเริ่มต้น: {T.WORKSPACE}")

    # เปิดเป็นหน้าต่างโปรแกรมจริง (pywebview)
    try:
        import webview  # type: ignore
        
        # System Tray & Hotkey logic
        def start_tray(window):
            try:
                import pystray
                from PIL import Image, ImageDraw
                import keyboard
                import os
                
                # Create a simple icon
                image = Image.new('RGB', (64, 64), color=(37, 99, 235))
                d = ImageDraw.Draw(image)
                d.text((10,20), "LM", fill=(255,255,255))
                
                def show_window(icon, item):
                    window.show()
                    window.restore()
                    
                def quit_app(icon, item):
                    icon.stop()
                    window.destroy()
                    os._exit(0)
                    
                icon = pystray.Icon("LM Co-work", image, "LM Co-work", menu=pystray.Menu(
                    pystray.MenuItem("Show", show_window, default=True),
                    pystray.MenuItem("Quit", quit_app)
                ))
                
                # Global hotkey to summon
                def summon():
                    window.show()
                    window.restore()
                    
                keyboard.add_hotkey('ctrl+alt+space', summon)
                
                icon.run()
            except Exception as e:
                print(f"System tray/Hotkey not available: {e}")

        window = webview.create_window("LM Co-work", url, js_api=JsApi(), width=1180, height=800,
                              min_size=(860, 580), text_select=True)
                              
        threading.Thread(target=start_tray, args=(window,), daemon=True).start()
        # ตั้งไอคอนหน้าต่าง/taskbar หลังหน้าต่างโผล่ (WinForms ใช้ไอคอน generic ถ้าไม่ตั้งเอง)
        threading.Thread(target=_apply_window_icon, daemon=True).start()

        webview.start()
        print("\nปิดโปรแกรมแล้ว 👋")
        return
    except Exception as e:  # noqa: BLE001
        import traceback
        detail = traceback.format_exc()
        # แนะนำติดตั้ง WebView2 เฉพาะเมื่ออาการเข้าข่ายจริง (อย่าเดามั่ว)
        looks_like_webview2 = any(
            k in detail.lower()
            for k in ("webview2", "edgechromium", "edge", "clr", "pythonnet", "winrt", "0x80")
        )
        if frozen:
            # โหมด .exe: ไม่เปิดเบราว์เซอร์ — แจ้งเตือนแล้วปิด
            hint = ("ต้องติดตั้ง Microsoft Edge WebView2 Runtime ก่อน "
                    "(ดาวน์โหลดฟรีจากเว็บ Microsoft)"
                    if looks_like_webview2 else
                    "เกิดข้อผิดพลาดระหว่างเปิดหน้าต่าง โปรดส่งข้อความด้านล่างนี้ให้ผู้พัฒนา")
            msg = f"เปิดหน้าต่างโปรแกรมไม่ได้:\n{e!r}\n\n{hint}"
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, msg, "LM Co-work", 0x10)
            except Exception:  # noqa: BLE001
                print(msg)
            print(detail, file=sys.stderr)
            return
        # โหมดสคริปต์ (dev): เปิดเบราว์เซอร์ให้สะดวก
        print(f"   (ไม่พบ pywebview จึงเปิดในเบราว์เซอร์แทน: {e})")
        webbrowser.open(url)
        try:
            # BUG-FIX: เดิม import time ซ้ำตรงนี้ ทำให้ Python ตีความ `time` เป็น
            # local variable ของทั้งฟังก์ชัน main() -> บรรทัด int(time.time()) ด้านบน
            # (ตอนสร้าง url) กลาย เป็น UnboundLocalError ทุกครั้งที่เรียก main() เลย
            # (ไม่ต้องรอให้ pywebview ล้มก่อนด้วยซ้ำ) ตัดออก ใช้ time ที่ import ไว้
            # module-level บรรทัดบนสุดของไฟล์แทน
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nปิดเซิร์ฟเวอร์แล้ว 👋")


if __name__ == "__main__":
    main()
