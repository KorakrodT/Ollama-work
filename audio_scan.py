"""audio_scan.py — งานตรวจไฟล์ (ปุ่มใน UI, ไม่พึ่ง AI)

แยกออกจาก server.py (refactor 2026-07-10).
ตรวจครบในรอบเดียว: สรุปโฟลเดอร์ + ไฟล์ว่าง + ไฟล์ซ้ำ + ไฟล์เสียหาย.
สถานะ (_audio_state) ถูก mutate ในที่ (in-place) ภายใต้ _audio_lock ให้ UI poll ได้.
"""

from __future__ import annotations

import os
import threading

import tools as T


def _blank_scan() -> dict:
    return {"running": False, "finished": False, "total": 0, "done": 0,
            "target": "", "error": "", "ffmpeg": True,
            "summary": {}, "empty": [], "duplicates": [], "corrupt": []}


_audio_state = _blank_scan()
_audio_lock = threading.Lock()


def _audio_worker(folder: str, recursive: bool, ext: str) -> None:
    """สแกนไฟล์ทุกชนิดทีละไฟล์: สรุป/ว่าง/ซ้ำ/เสีย อัปเดต progress ให้ UI poll."""
    info = T.collect_files(folder, recursive, ext)
    if not info["ok"]:
        with _audio_lock:
            _audio_state.update(running=False, finished=True, error=info["error"],
                                target=info.get("target", ""), total=0, done=0)
        return
    exe, files, target = info["ffmpeg"], info["files"], info["target"]

    # รอบที่ 1: เก็บขนาด/ชนิด/จัดกลุ่มตามขนาด (เร็ว ใช้แค่ stat)
    sized: list[tuple[str, int]] = []
    by_type: dict[str, list[int]] = {}
    size_map: dict[int, list[str]] = {}
    total_bytes = 0
    for p in files:
        try:
            sz = os.path.getsize(p)
        except OSError:
            sz = 0
        sized.append((p, sz))
        ek = (os.path.splitext(p)[1].lower() or "(ไม่มีนามสกุล)")
        slot = by_type.setdefault(ek, [0, 0])
        slot[0] += 1
        slot[1] += sz
        total_bytes += sz
        if sz > 0:
            size_map.setdefault(sz, []).append(p)

    with _audio_lock:
        _audio_state.update(running=True, finished=False, total=len(files), done=0,
                            target=target, error="", ffmpeg=bool(exe),
                            summary={}, empty=[], duplicates=[], corrupt=[])

    # ไฟล์ที่ "ขนาดซ้ำกัน" เท่านั้นที่ต้อง hash (ประหยัดเวลา)
    cand = {p for ps in size_map.values() if len(ps) > 1 for p in ps}
    hash_map: dict[str, list[str]] = {}
    empty: list[str] = []
    corrupt: list[dict] = []

    # รอบที่ 2: ตรวจเสีย + hash หาไฟล์ซ้ำ (ส่วนที่ใช้เวลา -> มี progress)
    # หมายเหตุประสิทธิภาพ: ก่อนหน้านี้คัดลอก list(corrupt)/list(empty) ทุกไฟล์ภายใน lock
    # ทำให้สแกนหมื่นไฟล์เป็น O(n²) กระตุก. ตอนนี้อัปเดตเฉพาะ done ทุกไฟล์ (O(1))
    # ส่วน snapshot corrupt/empty คัดลอกเฉพาะรอบที่มีรายการใหม่เข้ามาจริง (จำกัดจำนวนครั้ง).
    for i, (p, sz) in enumerate(sized, 1):
        appended = False
        if sz == 0:
            empty.append(os.path.relpath(p, target))
            appended = True
        reason = T.check_one_file(p, exe)
        if reason is not None:
            corrupt.append({"file": os.path.relpath(p, target), "reason": reason})
            appended = True
        if p in cand:
            h = T.file_sha256(p)
            if h:
                hash_map.setdefault(h, []).append(p)
        with _audio_lock:
            _audio_state["done"] = i
            if appended:
                # คัดลอก snapshot เฉพาะเมื่อมีรายการใหม่ — ไม่ใช่ทุกไฟล์
                _audio_state["corrupt"] = list(corrupt)
                _audio_state["empty"] = list(empty)

    duplicates = []
    for ps in hash_map.values():
        if len(ps) > 1:
            try:
                dsz = os.path.getsize(ps[0])
            except OSError:
                dsz = 0
            duplicates.append({"size": dsz,
                               "files": [os.path.relpath(x, target) for x in sorted(ps)]})
    duplicates.sort(key=lambda d: -d["size"] * (len(d["files"]) - 1))

    by_type_list = sorted(
        [{"ext": k, "count": v[0], "bytes": v[1]} for k, v in by_type.items()],
        key=lambda x: -x["bytes"])
    largest = [{"file": os.path.relpath(p, target), "bytes": sz}
               for p, sz in sorted(sized, key=lambda x: -x[1])[:10] if sz > 0]
    summary = {"count": len(files), "bytes": total_bytes,
               "by_type": by_type_list[:20], "largest": largest,
               "wasted": sum(d["size"] * (len(d["files"]) - 1) for d in duplicates)}

    with _audio_lock:
        _audio_state.update(running=False, finished=True, summary=summary,
                            empty=empty, duplicates=duplicates, corrupt=corrupt)
