"""scheduler.py — งานตามเวลา (Scheduled tasks) รันตอนแอปเปิดอยู่

แยกออกจาก server.py (refactor 2026-07-10).

เก็บใน data/schedules.json (ผ่าน data_store key "schedules") รูปแบบรายการละ dict:
  {id, title, time:"HH:MM", days:[0-6]?, prompt, agent, workspace, enabled,
   last_run:"YYYY-MM-DD", last_result}
ข้อจำกัดที่ตั้งใจ: รันเฉพาะตอนแอปเปิดอยู่ (ไม่ใช่ Windows service) และรันทีละงาน.
"""

from __future__ import annotations

import datetime as _dt
import logging
import re as _re
import threading
import time

import data_store as DS
import tools as T
from agent_runtime import run_agent
from agents import DEFAULT_AGENT

_log = logging.getLogger("server")

_sched_running = threading.Lock()


def _sched_due(s: dict, now: _dt.datetime | None = None) -> bool:
    """งานถึงกำหนดหรือยัง: enabled + เลยเวลา HH:MM ของวันนี้ + วันตรง + ยังไม่รันวันนี้."""
    if not s.get("enabled", True):
        return False
    now = now or _dt.datetime.now()
    if s.get("last_run") == now.strftime("%Y-%m-%d"):
        return False
    days = s.get("days")
    if days and now.weekday() not in days:
        return False
    t = (s.get("time") or "").strip()
    if not _re.fullmatch(r"\d{1,2}:\d{2}", t):
        return False
    hh, mm = t.split(":")
    return now.hour * 60 + now.minute >= int(hh) * 60 + int(mm)


def _run_schedule(s: dict) -> str:
    """รันงานหนึ่งรายการแบบ headless แล้วเขียนรายงานลง reports/ ในโฟลเดอร์งานของงานนั้น.

    write_file proposals จากตัว agent จะไม่ถูกเขียน (ไม่มีใครกดยืนยัน) — รายงานจะบอก
    ผู้ใช้แทน. ผลลัพธ์หลัก (reply) ถูกเขียนตรงโดย server เพราะผู้ใช้ opt-in ตอนตั้งงานแล้ว.
    """
    title = (s.get("title") or s.get("id") or "งาน").strip()
    _log.info("scheduled task start: %s", title)
    T.set_cowork(True)   # ให้ตั้ง workspace ที่ผู้ใช้เลือกไว้ได้ (ยังกัน root/ระบบเสมอ)
    T.set_workspace(s.get("workspace") or None)
    res = run_agent(s.get("agent") or DEFAULT_AGENT,
                    [{"role": "user", "content": s.get("prompt") or ""}],
                    "", cowork=True)
    reply = res.get("reply", "")
    note = ""
    if res.get("proposals"):
        note = ("\n\n---\n⚠️ งานนี้พยายามสร้าง/แก้ไฟล์ "
                f"{len(res['proposals'])} รายการ แต่โหมดอัตโนมัติไม่เขียนไฟล์ให้ — "
                "เปิดแอปแล้วสั่งเองถ้าต้องการ")
    stamp = _dt.datetime.now().strftime("%Y-%m-%d")
    slug = _re.sub(r"[^0-9A-Za-zก-๙_-]", "_", title)[:40] or "task"
    path = f"reports/{stamp}-{slug}.md"
    T.write_file(path, f"# {title} — {stamp}\n\n{reply}{note}\n")
    _log.info("scheduled task done: %s -> %s", title, path)
    return path


def _scheduler_loop() -> None:
    """เช็คทุก 30 วิ — งานไหนถึงกำหนดก็รัน (ทีละงาน) แล้วบันทึก last_run/last_result."""
    while True:
        time.sleep(30)
        try:
            items = DS.load("schedules", []) or []
            changed = False
            for s in items:
                if not isinstance(s, dict) or not _sched_due(s):
                    continue
                if not _sched_running.acquire(blocking=False):
                    break            # มีงานกำลังรันอยู่ — รอรอบหน้า
                try:
                    s["last_run"] = _dt.datetime.now().strftime("%Y-%m-%d")
                    s["last_result"] = _run_schedule(s)
                except Exception as e:  # noqa: BLE001
                    s["last_result"] = f"ผิดพลาด: {e}"
                    _log.warning("scheduled task '%s' failed", s.get("title"), exc_info=True)
                finally:
                    _sched_running.release()
                changed = True
            if changed:
                DS.save("schedules", items)
        except Exception:  # noqa: BLE001
            _log.warning("scheduler loop error", exc_info=True)
