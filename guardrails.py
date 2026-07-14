"""guardrails.py — กันเกราะรอบ tool loop (port แนวคิดจาก Mesh LLM, openai-frontend/guardrails)

โมเดล local ตัวเล็กพลาดบ่อยใน 3 แบบ ซึ่งเดิม agent loop เรารับมือไม่ได้เลย:
  1. พ่นบล็อกความคิด <think>...</think> ปนมากับคำตอบ -> ผู้ใช้เห็น reasoning ดิบ
  2. "เล่า" tool call เป็นข้อความ (JSON เปล่า ๆ / ```json / <tool_call> / <function=...>)
     แทนที่จะส่ง tool_calls จริง -> เครื่องมือไม่ถูกเรียก งานไม่เดิน
  3. ตอบว่างเปล่า (โดยเฉพาะหลังตัด think block) -> แชตจบด้วยความว่าง

ที่มา: crates/openai-frontend/src/guardrails/{rescue,retry}.rs ของ Mesh LLM —
เรา port เฉพาะชั้น classification/rescue/nudge มาเป็น Python (ไม่เอา guarded
contract เต็มรูปแบบ เพราะแอปเรายอมรับ plain text เป็นคำตอบปกติอยู่แล้ว)

ข้อแตกต่างจากต้นฉบับที่ตั้งใจ:
  - rescue จาก balanced JSON กลางประโยคทำเฉพาะข้อความสั้น (< _MAX_PROSE_RESCUE_CHARS)
    เพื่อลดโอกาสไปกินตัวอย่าง JSON ในคำตอบยาว ๆ ของ agent สาย coder
  - rescue สำเร็จก็ต่อเมื่อ "ทุกชื่อ tool ที่เจอ" เป็น tool ที่มีจริง — เจอชื่อแปลก
    ปล่อยเป็นข้อความธรรมดา (ของเขา retry แต่ของเราข้อความคือคำตอบที่ valid)
"""

from __future__ import annotations

import json
import re

_MAX_RESCUE_INPUT_CHARS = 64 * 1024   # เท่า MAX_RESCUE_INPUT_BYTES ของต้นฉบับ
_MAX_JSON_CANDIDATES = 32
_MAX_PROSE_RESCUE_CHARS = 2000        # balanced-substring rescue เฉพาะข้อความสั้น

# ---------------------------------------------------------------------------
# 1) ตัดบล็อกความคิด (strip_thinking_blocks)
# ---------------------------------------------------------------------------


def _strip_tag_pairs(content: str, start_tag: str, end_tag: str) -> str:
    """ตัดทุกช่วง start_tag..end_tag ออก; เจอ start_tag ที่ไม่ปิด -> ทิ้งตั้งแต่ตรงนั้นถึงจบ."""
    parts: list[str] = []
    remainder = content
    while True:
        i = remainder.find(start_tag)
        if i < 0:
            break
        parts.append(remainder[:i])
        after = remainder[i + len(start_tag):]
        j = after.find(end_tag)
        if j < 0:                     # ไม่ปิด tag: ถือว่าที่เหลือเป็น reasoning ทั้งหมด
            remainder = ""
            break
        remainder = after[j + len(end_tag):]
    parts.append(remainder)
    return "".join(parts)


def strip_thinking(content: str) -> str:
    """ตัด <think>...</think> และ [THINK]...[/THINK] ออกจากคำตอบโมเดล."""
    if not content:
        return ""
    out = _strip_tag_pairs(content, "<think>", "</think>")
    out = _strip_tag_pairs(out, "[THINK]", "[/THINK]")
    return out.strip()


# ---------------------------------------------------------------------------
# 2) หา JSON candidate จากข้อความ (openai_json_candidates)
# ---------------------------------------------------------------------------


def _balanced_end(text: str, start: int, opening: str, closing: str) -> int | None:
    """หา index ปิดของ {...}/[...] ที่สมดุล โดยไม่นับวงเล็บใน string literal."""
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                return i
    return None


def _fenced_blocks(text: str) -> list[str]:
    """ดึงเนื้อในบล็อก ``` ... ``` (ตัด prefix ภาษา json/JSON ออก)."""
    blocks = []
    remainder = text
    while True:
        i = remainder.find("```")
        if i < 0:
            break
        after = remainder[i + 3:]
        j = after.find("```")
        if j < 0:
            break
        block = after[:j]
        for prefix in ("json\n", "JSON\n"):
            if block.startswith(prefix):
                block = block[len(prefix):]
                break
        blocks.append(block)
        remainder = after[j + 3:]
    return blocks


def _balanced_json_substrings(text: str) -> list[str]:
    out = []
    for i, ch in enumerate(text):
        if len(out) >= _MAX_JSON_CANDIDATES:
            break
        if ch not in "{[":
            continue
        end = _balanced_end(text, i, ch, "}" if ch == "{" else "]")
        if end is not None:
            out.append(text[i:end + 1])
    return out


def _json_candidates(text: str) -> list[str]:
    """ลำดับความน่าเชื่อ: ทั้งก้อนเป๊ะ -> fenced block -> JSON ฝังในประโยค (เฉพาะข้อความสั้น)."""
    text = text[:_MAX_RESCUE_INPUT_CHARS]
    candidates: list[str] = []

    def push(c: str) -> None:
        c = c.strip()
        if c and c not in candidates and len(candidates) < _MAX_JSON_CANDIDATES:
            candidates.append(c)

    push(text)
    for block in _fenced_blocks(text):
        push(block)
    if len(text) <= _MAX_PROSE_RESCUE_CHARS:
        for sub in _balanced_json_substrings(text):
            push(sub)
    return candidates


# ---------------------------------------------------------------------------
# 3) parser ไวยากรณ์ tool call เฉพาะค่ายที่โมเดล local ชอบพ่น
# ---------------------------------------------------------------------------


def _first_balanced_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None
    end = _balanced_end(text, start, "{", "}")
    return text[start:end + 1] if end is not None else None


def _parse_tool_call_tag(text: str) -> dict | list | None:
    """<tool_call>{...json...}</tool_call> (Qwen3 / Granite / Hermes style)."""
    i = text.find("<tool_call>")
    if i < 0:
        return None
    after = text[i + len("<tool_call>"):]
    j = after.find("</tool_call>")
    if j < 0:
        return None
    try:
        return json.loads(after[:j].strip())
    except ValueError:
        return None


def _parse_function_xml(text: str) -> dict | None:
    """<function=NAME><parameter=K>V</parameter>...</function> (Qwen-coder style)."""
    m = re.search(r"<function=([\"']?)([\w-]+)\1>", text)
    if not m:
        return None
    name = m.group(2)
    body_start = m.end()
    body_end = text.find("</function>", body_start)
    if body_end < 0:
        return None
    body = text[body_start:body_end]
    args: dict = {}
    for pm in re.finditer(r"<parameter=([\"']?)([\w-]+)\1>(.*?)</parameter>", body, re.S):
        raw = pm.group(3).strip()
        try:
            args[pm.group(2)] = json.loads(raw)
        except ValueError:
            args[pm.group(2)] = raw
    return {"name": name, "arguments": args} if args else None


def _parse_paren_call(text: str) -> dict | None:
    """`tool_name({...})` หรือ `tool_name [ARGS] {...}` ที่โมเดลเขียนเลียนแบบโค้ด."""
    marker = text.find("[ARGS]")
    if marker >= 0:
        head, tail = text[:marker], text[marker + len("[ARGS]"):]
    else:
        paren = text.find("(")
        if paren < 0:
            return None
        head, tail = text[:paren], text[paren + 1:]
    name_match = re.search(r"([\w-]+)\s*$", head.strip())
    if not name_match:
        return None
    json_text = _first_balanced_object(tail)
    if not json_text:
        return None
    if marker < 0:                      # รูปแบบวงเล็บ: หลัง JSON ต้องปิดด้วย ')'
        rest = tail[tail.find(json_text) + len(json_text):].lstrip()
        if not rest.startswith(")"):
            return None
    try:
        arguments = json.loads(json_text)
    except ValueError:
        return None
    return {"name": name_match.group(1), "arguments": arguments}


# ---------------------------------------------------------------------------
# 4) normalize -> OpenAI-style tool_calls (raw_tool_calls_from_value + parse_tool_call)
# ---------------------------------------------------------------------------


def _normalize_one(value) -> dict | None:
    """แปลง dict หน้าตาต่าง ๆ ให้เป็น {"name": str, "arguments": dict} หรือ None."""
    if not isinstance(value, dict):
        return None
    if isinstance(value.get("function"), dict):     # {"function": {"name","arguments"}}
        value = value["function"]
    name = value.get("name")
    if not isinstance(name, str) or not name:
        return None
    args = value.get("arguments", value.get("parameters", {}))
    if isinstance(args, str):
        try:
            args = json.loads(args) if args.strip() else {}
        except ValueError:
            return None
    if args is None:
        args = {}
    if not isinstance(args, dict):
        return None
    return {"name": name, "arguments": args}


def _normalize_calls(value) -> list[dict] | None:
    """รับ JSON ที่ parse ได้ -> list ของ call ปกติ; คืน None ถ้ารูปร่างไม่ใช่ tool call."""
    if isinstance(value, dict) and isinstance(value.get("tool_calls"), list):
        value = value["tool_calls"]
    items = value if isinstance(value, list) else [value]
    calls = []
    for item in items:
        call = _normalize_one(item)
        if call is None:
            return None                  # มีชิ้นที่ไม่ใช่ tool call -> ทั้งก้อนไม่ใช่
        calls.append(call)
    return calls or None


def rescue_tool_calls(content: str, known_tools: set[str]) -> list[dict] | None:
    """พยายามกู้ tool call จากข้อความธรรมดาที่โมเดลพ่นมา.

    คืน tool_calls รูปแบบ OpenAI (arguments เป็น JSON string) เมื่อกู้ได้และ
    "ทุกชื่อ" เป็น tool ที่มีจริงเท่านั้น — ไม่งั้นคืน None (ปล่อยเป็นคำตอบข้อความ).
    """
    if not content or not known_tools:
        return None

    parsed_values = []
    for candidate in _json_candidates(content):
        try:
            parsed_values.append(json.loads(candidate))
        except ValueError:
            continue
    for parser in (_parse_tool_call_tag, _parse_function_xml, _parse_paren_call):
        value = parser(content)
        if value is not None:
            parsed_values.append(value)

    for value in parsed_values:
        calls = _normalize_calls(value)
        if not calls:
            continue
        if all(c["name"] in known_tools for c in calls):
            return [{"id": f"rescue_{i}", "type": "function",
                     "function": {"name": c["name"],
                                  "arguments": json.dumps(c["arguments"], ensure_ascii=False)}}
                    for i, c in enumerate(calls)]
    return None


# ---------------------------------------------------------------------------
# 5) retry nudge (retry.rs::retry_nudge) — ข้อความสะกิดให้โมเดลแก้ตัวรอบถัดไป
# ---------------------------------------------------------------------------

MAX_GUARDRAIL_RETRIES = 2   # เท่า default budget ฝั่ง mesh (max_tool_retries)

_NUDGES = {
    "empty_output": ("Your previous reply was empty after hidden reasoning was stripped. "
                     "Reply with your answer text, or exactly one valid tool call. "
                     "Do not add extra text."),
    "invalid_arguments": ("Your previous reply used invalid JSON tool arguments. "
                          "Reply with exactly one valid tool call using only the provided "
                          "tools and valid JSON arguments. Do not add extra text."),
}


def nudge_message(category: str) -> dict:
    """system message สั้น ๆ แนบท้าย request รอบ retry (ไม่บันทึกถาวรลง history)."""
    return {"role": "system", "content": _NUDGES.get(category, _NUDGES["empty_output"])}
