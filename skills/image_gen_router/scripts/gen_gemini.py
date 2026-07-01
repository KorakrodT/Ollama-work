from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


CACHE_DIR = Path.home() / ".cache" / "image_gen_router" / "gemini"


def _default_dest() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return CACHE_DIR / f"ig_{stamp}.png"


def _resolve_dest(out: str) -> Path:
    if not out:
        return _default_dest()
    p = Path(out).expanduser()
    if p.exists() and p.is_dir():
        return p / _default_dest().name
    if not p.suffix:
        return p / _default_dest().name
    return p


def extract_path_from_output(text: str) -> Path | None:
    patterns = [
        r"IMAGE:\s*((?:[A-Za-z]:[\\/]|/)[^\r\n\"'<>|]+?\.png)",
        r"((?:[A-Za-z]:[\\/]|/)[^\r\n\"'<>|]+?\.png)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text or "", flags=re.IGNORECASE)
        if match:
            return Path(match.group(1).strip()).expanduser()
    return None


def _search_roots(dest: Path) -> list[Path]:
    roots = [dest.parent, CACHE_DIR, Path.cwd(), Path.home() / "Downloads", Path.home() / "Desktop", Path.home() / "Pictures"]
    for env_name in ["LOCALAPPDATA", "TEMP", "TMP"]:
        value = os.environ.get(env_name)
        if value:
            temp_root = Path(value)
            roots.append(temp_root if env_name != "LOCALAPPDATA" else temp_root / "Temp")
    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        try:
            key = str(root.resolve())
        except OSError:
            key = str(root)
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return unique


def _snapshot(roots: list[Path]) -> dict[Path, float]:
    before: dict[Path, float] = {}
    for root in roots:
        if not root.exists():
            continue
        try:
            iterator = root.rglob("*.png") if root == CACHE_DIR else root.glob("*.png")
            for p in iterator:
                try:
                    before[p.resolve()] = p.stat().st_mtime
                except OSError:
                    pass
        except OSError:
            pass
    return before


def _find_new_png(dest: Path, before: dict[Path, float], roots: list[Path]) -> Path | None:
    if dest.is_file():
        return dest.resolve()
    candidates: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        try:
            iterator = root.rglob("*.png") if root == CACHE_DIR else root.glob("*.png")
            for p in iterator:
                try:
                    rp = p.resolve()
                    if rp not in before or p.stat().st_mtime > before.get(rp, 0):
                        candidates.append(p)
                except OSError:
                    pass
        except OSError:
            pass
    if not candidates:
        return None
    newest = max(candidates, key=lambda item: item.stat().st_mtime)
    if newest.resolve() != dest.resolve():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(newest, dest)
        return dest.resolve()
    return newest.resolve()


def _tail(text: str, max_lines: int = 60) -> str:
    lines = (text or "").splitlines()
    return "\n".join(lines[-max_lines:]).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an image through agy/Gemini CLI.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", default="")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    agy = shutil.which("agy")
    if not agy:
        print("ไม่พบคำสั่ง agy ใน PATH; ติดตั้ง agy/Gemini CLI และ login ก่อนใช้งาน backend=gemini", file=sys.stderr)
        return 1

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest = _resolve_dest(args.out).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    roots = _search_roots(dest)
    before = _snapshot(roots)

    instruction = f"""Generate exactly one PNG image from this user prompt and save it at this exact path:
{dest}

User prompt:
{args.prompt}

Use the available Gemini image generation capability. Do not ask follow-up questions. After saving, confirm the file exists, e.g. list it or check its size, then print exactly this line:
IMAGE: {dest}
"""

    cmd = [agy, "--dangerously-skip-permissions", "--print-timeout", str(max(30, args.timeout)), "-p", instruction]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(CACHE_DIR),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=max(30, args.timeout) + 10,
        )
    except subprocess.TimeoutExpired:
        print(f"agy timeout หลังรอ {args.timeout} วินาที", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"เรียก agy ไม่สำเร็จ: {exc}", file=sys.stderr)
        return 2

    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    mentioned = extract_path_from_output(combined)
    if mentioned and mentioned.is_file():
        if mentioned.resolve() != dest.resolve():
            shutil.copy2(mentioned, dest)
            print(f"IMAGE: {dest.resolve()}")
        else:
            print(f"IMAGE: {mentioned.resolve()}")
        return 0

    result = _find_new_png(dest, before, roots)
    if result:
        print(f"IMAGE: {result}")
        return 0

    print("agy/Gemini ยังสร้างภาพไม่สำเร็จ; ตรวจสอบว่าติดตั้งและ login แล้ว", file=sys.stderr)
    if proc.stderr:
        print(_tail(proc.stderr), file=sys.stderr)
    if proc.stdout:
        print(_tail(proc.stdout))
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
