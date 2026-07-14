"""agent_runtime.py — ลูปหลักของ agent (tool calling) + การยืนยันเครื่องมือ

แยกออกจาก server.py (refactor 2026-07-10). รับผิดชอบ "สมอง" ของแอป:
เลือก schema เครื่องมือให้แต่ละ agent, จัดการ tool call แต่ละครั้ง (รวมกลไก confirm
สำหรับ skill/MCP/เครื่องมือระบบ), และวนเรียกโมเดลจนได้คำตอบหรือครบจำนวน step.

ไม่ยุ่งกับ HTTP/หน้าต่าง — ชั้นนั้นอยู่ที่ server.py ซึ่ง import ชื่อจากที่นี่ไปใช้ต่อ.
"""

from __future__ import annotations

import json
import logging
import threading

import agent_store as AG
import guardrails as GR
import skills_loader as SL
import tools as T
from agents import AGENTS, DEFAULT_AGENT
from ollama_client import (
    MODEL,
    OLLAMA_BASE,
    OLLAMA_KEY,
    _openai_chat,
    default_model,
    ensure_ollama,
)

_log = logging.getLogger("server")

MAX_STEPS = 8

# ----------------------------- agent core -----------------------------
COWORK_TOOLS = {"list_files", "read_file", "write_file", "fetch_url",
                "check_audio_integrity", "check_ffmpeg", "install_ffmpeg", "remember",
                "search_brain", "read_brain_note"}
# SEC-4: เครื่องมือที่ "เปลี่ยนแปลงระบบ" (ติดตั้งซอฟต์แวร์ ฯลฯ) ต้องผ่านการยืนยันจาก
# ผู้ใช้ก่อนรันจริงเหมือน skill ใหม่ — โมเดลตัดสินใจเรียกเองทันทีไม่ได้อีกต่อไป
CONFIRM_TOOLS = {"install_ffmpeg"}
COWORK_PROMPT = (
    "\n\n[โหมด Co-Work เปิดอยู่] คุณมีสิทธิ์จัดการไฟล์ในโฟลเดอร์งานแล้ว. "
    "ถ้ามีงานที่เกี่ยวข้องกับไฟล์ ให้สำรวจด้วย list_files และอ่านด้วย read_file ก่อนเสมอ "
    "เวลาสร้างหรือแก้ไฟล์ใช้ write_file (ระบบจะแสดงตัวอย่างให้กดยืนยันก่อนบันทึกจริง อย่าเพิ่งบอกว่าทำแล้ว). "
    "อธิบายให้ชัดว่าจะอ่านหรือแก้ไฟล์อะไรบ้างทุกครั้ง."
)
ARTIFACTS_PROMPT = (
    "\n\n[Artifacts] You can present interactive code, UI components, HTML, SVG, or Mermaid diagrams using Artifacts. "
    "To create an Artifact, use the following XML tag format exactly:\n"
    '<antArtifact identifier="unique-id" title="Human-readable Title" type="text/html">\n'
    "// content here\n"
    "</antArtifact>\n"
    "Supported types: text/html, application/javascript, text/css, text/markdown, application/vnd.ant.mermaid, text/plain."
)


def schemas_for(agent: dict, cowork: bool = False) -> list:
    allowed_cats = agent.get("skill_categories")
    base = T.all_tool_schemas(allowed_cats)       # เครื่องมือพื้นฐาน + skills
    allowed = agent.get("tools")
    if allowed is None:
        result = list(base)                # agent นี้ใช้ได้ทุกอย่าง รวม skills
    elif not allowed:
        result = []                        # agent นี้ไม่ใช้เครื่องมือ
    else:
        names = set(allowed)
        # skill tools (และ use_skill) ให้ใช้ได้เสมอถ้า agent ไม่ได้จำกัดเป็น []
        base_names = {s["function"]["name"] for s in T.TOOL_SCHEMAS}
        result = [s for s in base if s["function"]["name"] in names
                  or s["function"]["name"] not in base_names]
    if cowork:
        # Co-Work: file tools ต้องมีเสมอ ไม่ว่า agent จะจำกัดเครื่องมืออย่างไร (รวม tools=[])
        have = {s["function"]["name"] for s in result}
        for s in T.all_tool_schemas():
            n = s["function"]["name"]
            if n in COWORK_TOOLS and n not in have:
                result.append(s)
    return result


def _run(name: str, args: dict) -> str:
    return T.run_tool(name, args)


def _handle_tool_call(fname, args, used_tools, proposals, skill_names=None):
    """จัดการ tool call หนึ่งครั้ง คืน result string. WRITE_TOOLS เก็บเป็น proposal (ไม่เขียนจริง).

    D1: ถ้า fname เป็น skill ที่ยังไม่ confirm → คืน proposal ประเภท skill_confirm
    ให้ UI แสดง dialog ถามผู้ใช้ก่อน แทนที่จะรัน tool.py ทันที.
    SEC-4: เครื่องมือใน CONFIRM_TOOLS (เปลี่ยนแปลงระบบ เช่น install_ffmpeg) ใช้
    กลไก confirm เดียวกับ skill — is_confirmed()/confirm_skill() เก็บแค่ชื่อ string
    เฉยๆ ไม่ผูกกับ "skill" จริง จึงใช้ร่วมกันได้.
    skill_names: set ของ skill name ทั้งหมดที่โหลดอยู่ (ถ้า None จะดึงจาก T.skills_list())
    """
    used_tools.append(fname)
    if fname in T.WRITE_TOOLS:
        if fname == "remember":
            # F1: แปลง remember(text) เป็น proposal เขียน _memory.md ฉบับเต็ม —
            # ผู้ใช้เห็น preview ความจำทั้งไฟล์ก่อนกดยืนยัน (reuse flow ของ write_file)
            path = T.MEMORY_FILE
            content = T.build_memory_content(args.get("text", ""))
        else:
            path = args.get("path", "untitled.txt")
            content = args.get("content", "")
        proposals.append({"path": path, "content": content, "exists": T.file_exists(path)})
        return (f"เสนอบันทึกไฟล์ '{path}' แล้ว — กำลังรอผู้ใช้กดยืนยันใน UI "
                f"(ยังไม่เขียนจริง)")
    # D1/SEC-4: ตรวจเครื่องมือที่ต้องยืนยันก่อนรัน (skill ใหม่ หรือเครื่องมือระบบใน CONFIRM_TOOLS)
    if skill_names is None:
        skill_names = {s["name"] for s in T.skills_list()}
    is_skill = fname in skill_names
    # SEC-6: MCP tool คือโค้ดภายนอกที่ทำอะไรก็ได้ — ต้องผ่าน confirm ครั้งแรกเหมือน skill
    is_mcp = T.is_mcp_tool(fname)
    if is_skill or is_mcp or fname in CONFIRM_TOOLS:
        if not SL.is_confirmed(fname):
            proposals.append({"type": "skill_confirm", "name": fname, "args": args})
            return (f"⚠️ '{fname}' ยังไม่ได้รับการยืนยัน — "
                    f"กำลังรอผู้ใช้อนุมัติใน UI (จะรันหลังยืนยัน)")
        # SEC-3: หลัง confirm แล้วจะไม่ถูกถามซ้ำอีกในเซสชันนี้ — log argument ทุกครั้งที่รัน
        # (ไม่ใช่แค่ครั้งแรก) ไว้เป็น audit trail กันกรณีมี prompt injection สั่งเรียกด้วย
        # argument ผิดปกติหลังจากที่เคยยืนยันไปแล้ว
        kind = "skill" if is_skill else ("mcp tool" if is_mcp else "system tool")
        _log.warning("%s run (confirmed): %s args=%r", kind, fname, args)
    return _run(fname, args)


def _extract_message(resp: dict) -> dict | None:
    """ดึง assistant message จาก response อย่างปลอดภัย.

    คืน dict ที่มี content/tool_calls (อาจเป็น None) ถ้าเป็น response ปกติ,
    หรือ None ถ้า response ผิดรูปแบบ/เป็น error — ผู้เรียกจะได้สร้างข้อความแจ้งเอง.
    ทนต่อ: response ผิดรูปแบบ, backend คืน {error:{message}}, choices ว่าง ฯลฯ
    (กัน KeyError/TypeError ที่เคยทำให้ agent loop ระเบิดเงียบ).
    """
    if not isinstance(resp, dict):
        return None
    choices = resp.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict) and isinstance(first.get("message"), dict):
            return first["message"]
    return None


def _format_error_reply(resp: dict) -> str:
    """สร้างข้อความที่อ่านรู้เรื่องจาก response ที่ไม่มี choices (เช่น {error:...})."""
    err = resp.get("error") if isinstance(resp, dict) else None
    if isinstance(err, dict):
        msg = err.get("message") or err.get("code") or str(err)
        return f"⚠️ โมเดลส่งกลับข้อผิดพลาด: {msg}"
    if err:
        return f"⚠️ โมเดลส่งกลับข้อผิดพลาด: {err}"
    return ("⚠️ โมเดลตอบกลับมาผิดรูปแบบ (อาจเป็นเพราะ context เกิน โมเดลโหลดไม่ติด "
            "หรือ provider ไม่รองรับ tool calling) — ลองเปลี่ยนโมเดลหรือถามใหม่อีกครั้ง")


# ---- cancel flag สำหรับ B2: ปุ่มหยุด ----
_cancel_lock = threading.Lock()
_cancel_requested = False


def request_cancel() -> None:
    """Set flag ให้ run_agent หยุดทำงาน (ปุ่ม Stop ฝั่ง UI)."""
    global _cancel_requested
    with _cancel_lock:
        _cancel_requested = True


def _clear_cancel() -> None:
    global _cancel_requested
    with _cancel_lock:
        _cancel_requested = False


def _is_cancelled() -> bool:
    with _cancel_lock:
        return _cancel_requested


def run_agent(agent_key: str, history: list, model: str,
              cowork: bool = False, provider: dict | None = None) -> dict:
    """
    รันลูป agent. WRITE_TOOLS ถูกเก็บเป็น 'proposals' ให้ผู้ใช้ยืนยันก่อนเขียนจริง.
    provider: ถ้ามี base_url -> route ไป endpoint นั้นแทน Ollama (ดีฟอลต์).
    ตรวจ _cancel_requested ทุก step — ถ้าถูก cancel คืนผลบางส่วนที่ได้ทันที.
    """
    _clear_cancel()  # ล้าง flag เก่าทุกครั้งที่เริ่ม run ใหม่
    _agents = AG.all_agents()
    agent = _agents.get(agent_key) or _agents.get(DEFAULT_AGENT) or AGENTS[DEFAULT_AGENT]
    sys_prompt = agent["system"]
    sys_prompt += ARTIFACTS_PROMPT
    if cowork:
        sys_prompt += COWORK_PROMPT
    allowed_cats = agent.get("skill_categories")
    catalog = T.skills_catalog(allowed_cats)
    if catalog:
        sys_prompt += "\n\n" + catalog
    # SI-1: ผูกงานปัจจุบันกับ decision trail + ป้อนประสบการณ์ skill กลับให้โมเดล
    try:
        import skill_intelligence as SI
        _last_user = next((h.get("content", "") for h in reversed(history)
                           if h.get("role", "user") == "user"), "")
        SI.set_current_task(_last_user)
        if catalog:  # มี skills ให้เลือก จึงค่อยใส่สถิติ (ไม่มี skill = ไม่เปลืองบริบท)
            _exp = SI.experience_context(_last_user)
            if _exp:
                sys_prompt += "\n\n" + _exp
    except Exception:  # noqa: BLE001
        pass
    # F1: บริบทประจำโฟลเดอร์งาน (_agent.md/_memory.md) — ว่าง = ไม่เปลืองบริบทโมเดล
    ws_ctx = T.workspace_context()
    if ws_ctx:
        sys_prompt += "\n\n" + ws_ctx
    tool_schemas = schemas_for(agent, cowork)
    used_tools: list[str] = []
    proposals: list[dict] = []
    # D1: คำนวณ skill names ครั้งเดียว (ประหยัดการเรียก skills_list ทุก tool call)
    skill_names = {s["name"] for s in T.skills_list()}

    # backend: Ollama (ดีฟอลต์) หรือ provider ภายนอกที่ส่ง base_url มาเอง
    if provider and provider.get("base_url"):
        base_url = provider.get("base_url").rstrip("/")
        api_key = provider.get("api_key", "")
    else:
        base_url = OLLAMA_BASE
        api_key = OLLAMA_KEY
    if not model:
        model = default_model()

    is_ollama = base_url == OLLAMA_BASE
    tried_autostart = False
    messages = [{"role": "system", "content": sys_prompt}]
    messages += [{"role": h.get("role", "user"), "content": h.get("content", "")}
                 for h in history]
    # GR: ชื่อ tool ทั้งหมดที่ agent นี้เรียกได้จริง — ใช้ตัดสินว่า rescue ข้อความได้ไหม
    schema_names = {s["function"]["name"] for s in tool_schemas}
    guard_retries = 0
    pending_nudge: list[dict] = []   # system nudge แนบเฉพาะ request รอบ retry
    for _ in range(MAX_STEPS):
        if _is_cancelled():
            return {"reply": "⛔ ยกเลิกแล้ว", "tools": used_tools, "proposals": proposals,
                    "cancelled": True}
        try:
            resp = _openai_chat(base_url, api_key, model, messages + pending_nudge,
                                tool_schemas)
        except Exception as e:  # noqa: BLE001 — Ollama ยังไม่เปิด/ไม่มีโมเดล
            _log.warning("_openai_chat failed: %s", e, exc_info=True)
            # self-healing: ถ้าเป็น backend Ollama ลองสตาร์ต headless แล้วลองใหม่ครั้งเดียว
            if is_ollama and not tried_autostart:
                tried_autostart = True
                if ensure_ollama():
                    if not MODEL:
                        model = default_model()
                    continue
            return {"reply": (f"⚠️ ต่อ Ollama ไม่ได้ ({e}).\n"
                              f"ตรวจว่าติดตั้ง Ollama แล้ว (ดาวน์โหลดจาก https://ollama.com) "
                              f"และดึงโมเดลที่รองรับ tool calling ไว้อย่างน้อย 1 ตัว เช่น "
                              f"`ollama pull qwen2.5` นะครับ"),
                    "tools": used_tools, "proposals": proposals}
        msg = _extract_message(resp)
        if msg is None:
            # response ผิดรูปแบบ/เป็น error (เช่น context เกิน, โมเดลไม่โหลด) -> แจ้งให้ชัด
            return {"reply": _format_error_reply(resp), "tools": used_tools, "proposals": proposals}
        pending_nudge = []
        calls = msg.get("tool_calls")
        # GR-1: ตัดบล็อกความคิด (<think>/[THINK]) ออกจากข้อความที่ผู้ใช้จะเห็น
        visible = GR.strip_thinking(msg.get("content") or "")
        # GR-2: โมเดล "เล่า" tool call เป็นข้อความ -> กู้กลับเป็น tool call จริง
        if not calls and visible:
            rescued = GR.rescue_tool_calls(visible, schema_names)
            if rescued:
                _log.info("guardrails: rescued %d tool call(s) from plain text", len(rescued))
                calls = rescued
                visible = ""            # ข้อความคือ tool call ที่หลงรูป — ไม่ใช่คำตอบ
        # GR-3: ตอบว่างเปล่า (มักเพราะทั้งก้อนเป็น think block) -> retry พร้อม nudge
        if not calls and not visible:
            if guard_retries < GR.MAX_GUARDRAIL_RETRIES:
                guard_retries += 1
                pending_nudge = [GR.nudge_message("empty_output")]
                _log.info("guardrails: empty output, retry %d/%d",
                          guard_retries, GR.MAX_GUARDRAIL_RETRIES)
                continue
            return {"reply": "⚠️ โมเดลตอบกลับมาว่างเปล่า — ลองถามใหม่หรือเปลี่ยนโมเดลดูนะครับ",
                    "tools": used_tools, "proposals": proposals}
        am = {"role": "assistant", "content": visible}
        if calls:
            am["tool_calls"] = calls
        messages.append(am)
        if not calls:
            return {"reply": visible, "tools": used_tools, "proposals": proposals}
        for tc in calls:
            if _is_cancelled():
                return {"reply": "⛔ ยกเลิกแล้ว", "tools": used_tools, "proposals": proposals,
                        "cancelled": True}
            fn = tc.get("function", {})
            fname = fn.get("name", "")
            raw = fn.get("arguments") or "{}"
            try:
                args = raw if isinstance(raw, dict) else json.loads(raw or "{}")
            except ValueError as e:
                # GR: บอกโมเดลชัด ๆ ว่าพลาดอะไร + contract ที่ต้องทำ (แบบ retry_nudge ของ mesh)
                err_msg = (f"⚠️ Error parsing tool arguments: {e}. "
                           + GR.nudge_message("invalid_arguments")["content"])
                messages.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": err_msg})
                continue
            result = _handle_tool_call(fname, args, used_tools, proposals, skill_names)
            messages.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": result})
    return {"reply": "ทำงานหลายขั้นเกินกำหนด", "tools": used_tools, "proposals": proposals}
