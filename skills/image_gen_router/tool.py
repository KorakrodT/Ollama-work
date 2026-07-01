from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SCRIPT_BY_BACKEND = {
    "gpt": BASE_DIR / "scripts" / "gen_gpt.py",
    "gemini": BASE_DIR / "scripts" / "gen_gemini.py",
}


def _tail(text: str, max_lines: int = 30) -> str:
    lines = (text or "").splitlines()
    return "\n".join(lines[-max_lines:]).strip()


def _extract_image(stdout: str) -> str:
    for line in (stdout or "").splitlines():
        m = re.match(r"\s*IMAGE:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip().strip('"')
    return ""


def run(prompt: str, backend: str, out: str = "", timeout: int = 600, **kwargs) -> str:
    backend = (backend or "").strip().lower()
    if backend not in SCRIPT_BY_BACKEND:
        return "ต้องระบุ backend เป็น 'gpt' หรือ 'gemini' ก่อนเรียกใช้ image_gen_router; ถ้าผู้ใช้ยังไม่เลือก ให้ถามผู้ใช้ก่อน"

    prompt = (prompt or "").strip()
    if not prompt:
        return "ต้องระบุ prompt สำหรับสร้างภาพ"

    try:
        timeout = int(timeout or 600)
    except (TypeError, ValueError):
        timeout = 600
    timeout = max(30, timeout)

    script = SCRIPT_BY_BACKEND[backend]
    if not script.is_file():
        return f"ไม่พบ runner script: {script}"

    cmd = [sys.executable, str(script), "--prompt", prompt, "--timeout", str(timeout)]
    if out:
        cmd.extend(["--out", str(Path(out).expanduser())])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout + 20,
        )
    except subprocess.TimeoutExpired:
        return f"image_gen_router timeout หลังรอ {timeout} วินาที ({backend})"
    except Exception as exc:  # noqa: BLE001
        return f"image_gen_router เรียก runner ไม่สำเร็จ ({backend}): {exc}"

    image = _extract_image(proc.stdout)
    if proc.returncode == 0 and image:
        return f"สร้างภาพสำเร็จ ({backend}): {image}"

    stdout_tail = _tail(proc.stdout)
    stderr_tail = _tail(proc.stderr)
    detail_parts = [f"image_gen_router สร้างภาพไม่สำเร็จ ({backend}), exit code {proc.returncode}"]
    if stderr_tail:
        detail_parts.append("stderr:\n" + stderr_tail)
    if stdout_tail:
        detail_parts.append("stdout:\n" + stdout_tail)
    if not stderr_tail and not stdout_tail:
        detail_parts.append("ไม่มี output จาก backend; ตรวจสอบว่าติดตั้งและ login CLI แล้ว")
    return "\n\n".join(detail_parts)
