from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


GEN_DIR = Path.home() / ".codex" / "generated_images"


def _default_dest() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return GEN_DIR / f"ig_{stamp}.png"


def _resolve_dest(out: str) -> Path:
    if not out:
        return _default_dest()
    p = Path(out).expanduser()
    if p.exists() and p.is_dir():
        return p / _default_dest().name
    if not p.suffix:
        return p / _default_dest().name
    return p


def _known_images() -> dict[Path, float]:
    images: dict[Path, float] = {}
    if GEN_DIR.exists():
        for p in GEN_DIR.glob("ig_*.png"):
            try:
                images[p.resolve()] = p.stat().st_mtime
            except OSError:
                pass
    return images


def _extract_paths(text: str) -> list[Path]:
    matches = re.findall(r"(?:IMAGE:\s*)?((?:[A-Za-z]:[\\/]|/)[^\r\n\"'<>|]+?\.png)", text or "", flags=re.IGNORECASE)
    return [Path(m.strip()).expanduser() for m in matches]


def _find_result(dest: Path, before: dict[Path, float], output: str) -> Path | None:
    if dest.is_file():
        return dest.resolve()

    for p in _extract_paths(output):
        try:
            if p.is_file():
                if p.resolve() != dest.resolve():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, dest)
                    return dest.resolve()
                return p.resolve()
        except OSError:
            continue

    if GEN_DIR.exists():
        candidates: list[Path] = []
        for p in GEN_DIR.glob("ig_*.png"):
            try:
                rp = p.resolve()
                if rp not in before or p.stat().st_mtime > before.get(rp, 0):
                    candidates.append(p)
            except OSError:
                pass
        if candidates:
            newest = max(candidates, key=lambda item: item.stat().st_mtime)
            if newest.resolve() != dest.resolve():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(newest, dest)
                return dest.resolve()
            return newest.resolve()
    return None


def _tail(text: str, max_lines: int = 60) -> str:
    lines = (text or "").splitlines()
    return "\n".join(lines[-max_lines:]).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an image through Codex CLI.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", default="")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    codex = shutil.which("codex")
    if not codex:
        print("ไม่พบคำสั่ง codex ใน PATH; ติดตั้ง Codex CLI แล้วรัน `codex login` ก่อนใช้งาน backend=gpt", file=sys.stderr)
        return 1

    GEN_DIR.mkdir(parents=True, exist_ok=True)
    dest = _resolve_dest(args.out).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    before = _known_images()

    instruction = f"""Generate exactly one PNG image from this user prompt and save it at this exact path:
{dest}

User prompt:
{args.prompt}

Use the available image generation capability in this Codex environment. Do not ask follow-up questions. After saving, confirm the file exists, e.g. list it or check its size, then print exactly this line:
IMAGE: {dest}
"""

    commands = [
        [codex, "exec", "--full-auto", instruction],
        [codex, "exec", instruction],
    ]
    last_proc: subprocess.CompletedProcess[str] | None = None
    combined = ""

    for index, cmd in enumerate(commands):
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(GEN_DIR),
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=max(30, args.timeout),
            )
        except subprocess.TimeoutExpired:
            print(f"Codex timeout หลังรอ {args.timeout} วินาที", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001
            print(f"เรียก codex ไม่สำเร็จ: {exc}", file=sys.stderr)
            return 2

        last_proc = proc
        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        result = _find_result(dest, before, combined)
        if result:
            print(f"IMAGE: {result}")
            return 0

        lowered = combined.lower()
        usage_error = any(token in lowered for token in ["unknown option", "unexpected argument", "unrecognized", "usage:"])
        if index == 0 and usage_error:
            continue
        break

    if last_proc:
        print("Codex ยังสร้างภาพไม่สำเร็จ; ตรวจสอบว่า `codex` ติดตั้งแล้วและ login สำเร็จ (`codex login` หรือคำสั่งสถานะของ Codex CLI)", file=sys.stderr)
        if last_proc.stderr:
            print(_tail(last_proc.stderr), file=sys.stderr)
        if last_proc.stdout:
            print(_tail(last_proc.stdout))
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
