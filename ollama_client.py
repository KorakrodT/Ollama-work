"""ollama_client.py — ตัวเชื่อมกับ Ollama (เซิร์ฟเวอร์ OpenAI-compatible)

แทนที่ lm_studio.py (สลับ backend เป็น Ollama 2026-07-14) — ชั้น "คุยกับโมเดล/จัดการ
process ของ Ollama" อยู่โมดูลเดียวจบ ไม่ปนกับชั้น HTTP/หน้าต่าง (server.py).

ติดตั้ง Ollama จาก https://ollama.com แล้วดึงโมเดลที่รองรับ tool-calling เช่น
  ollama pull qwen2.5    (หรือ llama3.1, mistral-nemo ฯลฯ)
ตัว Ollama เปิด endpoint แบบ OpenAI-compatible ที่ /v1 ให้อยู่แล้ว (พอร์ต 11434).

ตั้งค่าผ่าน env ได้:
  OLLAMA_BASE_URL  (ดีฟอลต์ http://localhost:11434/v1)
  OLLAMA_MODEL     (เว้นว่าง = ใช้โมเดลตัวแรกที่ Ollama มีในเครื่อง)
  OLLAMA_API_KEY   (Ollama ไม่ตรวจ key — ใส่อะไรก็ได้)
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import time
import urllib.request

import winproc  # QUAL-1: no_window_kwargs() ที่ใช้ร่วมกัน

_log = logging.getLogger("server")

OLLAMA_BASE = os.environ.get(
    "OLLAMA_BASE_URL",
    os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1"),
).rstrip("/")
OLLAMA_KEY = os.environ.get("OLLAMA_API_KEY", "ollama")
# โมเดลดีฟอลต์: ถ้าไม่ตั้ง env ไว้ จะ resolve เป็นตัวแรกที่ Ollama มีในเครื่องตอน runtime
MODEL = os.environ.get("OLLAMA_MODEL", "").strip()


def _ollama_get(path: str, timeout: int = 8):
    """GET ไปยัง Ollama (OpenAI-compatible) แล้วคืน JSON (raise ถ้าต่อไม่ได้)."""
    url = OLLAMA_BASE + path
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {OLLAMA_KEY}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def ollama_models() -> list[str]:
    """รายชื่อโมเดลที่ Ollama มีในเครื่อง (GET /models)."""
    try:
        data = _ollama_get("/models")
        out = []
        for m in data.get("data", []) or []:
            mid = m.get("id") if isinstance(m, dict) else None
            if mid:
                out.append(mid)
        return out
    except Exception:  # noqa: BLE001 — Ollama อาจยังไม่เปิด
        return []


def default_model() -> str:
    """โมเดลที่จะใช้: ค่าจาก env ถ้ามี ไม่งั้นเอาตัวแรกที่ Ollama มีในเครื่อง."""
    if MODEL:
        return MODEL
    models = ollama_models()
    return models[0] if models else "qwen2.5"


def _ollama_alive(timeout: int = 3) -> bool:
    """เซิร์ฟเวอร์ Ollama ตอบที่ /models ไหม (ไม่สนว่ามีโมเดลดาวน์โหลดไว้หรือยัง)."""
    try:
        _ollama_get("/models", timeout=timeout)
        return True
    except Exception:  # noqa: BLE001
        return False


# สตาร์ต ollama ได้ครั้งเดียวต่อการรันโปรแกรม — กันการสแปม `ollama serve` ซ้ำ ๆ
_OLLAMA_AUTOSTART_TRIED = False


def _find_ollama() -> str | None:
    """หา path ของ `ollama` CLI (ใช้สตาร์ต server แบบ headless)."""
    exe = shutil.which("ollama")
    if exe:
        return exe
    candidates = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Ollama\ollama.exe"),
        os.path.expanduser("~/.ollama/bin/ollama"),
        "/usr/local/bin/ollama",
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def ensure_ollama(timeout: int = 30) -> bool:
    """ทำให้ Ollama server พร้อมใช้งาน.

    ถ้า server เปิดอยู่แล้ว -> คืน True ทันที
    ถ้ายังไม่เปิด -> เรียก `ollama serve` สตาร์ตแบบ headless แล้วรอจนตอบ
    (โมเดลจะถูกโหลดเข้าหน่วยความจำอัตโนมัติตอนแชตครั้งแรก)
    คืน True ถ้า endpoint พร้อม, False ถ้าหา ollama CLI ไม่เจอ/สตาร์ตไม่ขึ้น
    """
    global _OLLAMA_AUTOSTART_TRIED
    if _ollama_alive():
        return True
    # สตาร์ตแค่ครั้งเดียวตลอดการรัน — ถ้าลองไปแล้วไม่ขึ้น อย่าสแปมเปิด process ซ้ำ
    if _OLLAMA_AUTOSTART_TRIED:
        return False
    _OLLAMA_AUTOSTART_TRIED = True
    exe = _find_ollama()
    if not exe:
        return False

    # `ollama serve` อ่านพอร์ตจาก env OLLAMA_HOST — ส่งต่อจาก OLLAMA_BASE ถ้าไม่ใช่ดีฟอลต์
    env = dict(os.environ)
    host_port = OLLAMA_BASE.split("//", 1)[-1].rsplit("/", 1)[0]
    if host_port and host_port != "localhost:11434":
        env.setdefault("OLLAMA_HOST", host_port)

    # รันเซิร์ฟเวอร์แบบซ่อนหน้าต่าง เพื่อให้ API พร้อมใช้ทันทีโดยไม่ต้องเปิดแอปเอง
    try:
        subprocess.Popen([exe, "serve"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                         env=env, **winproc.no_window_kwargs(detached=True))
    except Exception:  # noqa: BLE001
        # QUAL-3: log ไว้ debug — เคยเกิดเงียบๆ ทำให้ไม่รู้ว่าทำไม server start ไม่ขึ้น
        _log.debug("ensure_ollama: เปิด ollama serve ไม่สำเร็จ", exc_info=True)
        return False

    deadline = time.time() + timeout
    while time.time() < deadline:
        if _ollama_alive():
            return True
        time.sleep(1)
    return False


def _openai_chat(base_url, api_key, model, messages, tools):
    """เรียกโมเดลผ่าน OpenAI-compatible endpoint (Ollama/OpenAI/OpenRouter/Groq/vLLM/...)."""
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {"model": model, "messages": messages, "stream": False}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))
