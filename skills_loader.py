"""
skills_loader.py — ระบบ Skills ที่ผู้ใช้สร้างเองได้

Skill หนึ่งตัว = โฟลเดอร์ย่อยใน skills/<ชื่อ>/ ประกอบด้วย:

  skill.json   (บังคับ)  ข้อมูลของ skill
  tool.py      (ถ้าเป็น code skill)  มีฟังก์ชัน  def run(**kwargs) -> str
  prompt.md    (ถ้าเป็น prompt skill)  คำสั่ง/ความรู้ที่จะป้อนให้ agent

ตัวอย่าง skill.json:
{
  "name": "word_count",
  "description": "นับจำนวนคำและตัวอักษรของข้อความ",
  "type": "code",                       // code | prompt | both
  "parameters": {                       // เฉพาะ code/both (JSON schema)
    "type": "object",
    "properties": {"text": {"type": "string", "description": "ข้อความ"}},
    "required": ["text"]
  },
  "prompt": "prompt.md"                  // เฉพาะ prompt/both
}

หมายเหตุความปลอดภัย: tool.py เป็นโค้ด Python ที่ "คุณเขียนเอง" และรันบนเครื่องคุณ
อย่าวาง skill จากแหล่งที่ไม่ไว้ใจ
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import threading

# โหลด skills จากโฟลเดอร์ข้างโปรแกรม:
#  - รันแบบสคริปต์ -> ข้าง ๆ ไฟล์ .py (โฟลเดอร์โปรเจกต์)
#  - รันแบบ .exe   -> ข้าง ๆ ไฟล์ .exe (วาง skill ใหม่ตรงนี้ได้)
if getattr(sys, "frozen", False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(_BASE, "skills")

# D1: set ของ skill ที่ผู้ใช้ confirm แล้ว — เก็บ in-memory (reset เมื่อปิดโปรแกรม)
_confirm_lock = threading.Lock()
_confirmed_skills: set[str] = set()


def confirm_skill(name: str) -> None:
    """D1: ทำเครื่องหมายว่า skill นี้ได้รับการยืนยันจากผู้ใช้แล้ว."""
    with _confirm_lock:
        _confirmed_skills.add(name)


def is_confirmed(name: str) -> bool:
    """D1: คืน True ถ้า skill นี้เคยได้รับการยืนยันจากผู้ใช้แล้ว."""
    with _confirm_lock:
        return name in _confirmed_skills


def reset_confirmed_skills() -> None:
    """D1: ล้าง set (สำหรับ test / เมื่อ reload skills)."""
    with _confirm_lock:
        _confirmed_skills.clear()



def _load_prompt(folder: str, meta: dict) -> str:
    pf = meta.get("prompt")
    if not pf:
        return ""
    path = os.path.join(folder, pf)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def _load_runner(folder: str, name: str):
    """โหลดฟังก์ชัน run() จาก tool.py ของ skill."""
    path = os.path.join(folder, "tool.py")
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location(f"skill_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # noqa: S102 — โค้ดของผู้ใช้เอง
    return getattr(mod, "run", None)


def discover(skills_dir: str = SKILLS_DIR) -> list[dict]:
    """สแกนโฟลเดอร์ skills/ คืนรายการ skill ที่โหลดได้."""
    found: list[dict] = []
    if not os.path.isdir(skills_dir):
        return found
    for name in sorted(os.listdir(skills_dir)):
        folder = os.path.join(skills_dir, name)
        meta_path = os.path.join(folder, "skill.json")
        if not os.path.isdir(folder) or not os.path.isfile(meta_path):
            continue
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            stype = meta.get("type", "code")
            skill = {
                "name": meta.get("name", name),
                "description": meta.get("description", ""),
                "type": stype,
                "category": meta.get("category", "General"),
                "parameters": meta.get("parameters", {"type": "object", "properties": {}}),
                "prompt": _load_prompt(folder, meta) if stype in ("prompt", "both") else "",
                "run": _load_runner(folder, name) if stype in ("code", "both") else None,
                "error": "",
            }
            found.append(skill)
        except Exception as e:  # noqa: BLE001
            found.append({"name": name, "description": "(โหลดไม่สำเร็จ)", "type": "error",
                          "parameters": {}, "prompt": "", "run": None, "error": str(e)})
    return found


def _slug(name: str) -> str:
    import re
    return re.sub(r"[^a-zA-Z0-9_-]", "_", (name or "").strip()).strip("_")


def create_skill(name, description="", stype="code", parameters=None,
                 tool_code=None, prompt_text=None, skills_dir=SKILLS_DIR, category="General", overwrite=False):
    """สร้างโฟลเดอร์ skill ใหม่ (skill.json + tool.py/prompt.md). คืน (ok, message)."""
    slug = _slug(name)
    if not slug:
        return False, "ชื่อ skill ไม่ถูกต้อง (ใช้ a-z, 0-9, _ , -)"
    folder = os.path.join(skills_dir, slug)
    if os.path.exists(folder) and not overwrite:
        return False, f"มี skill ชื่อ '{slug}' อยู่แล้ว"
    os.makedirs(folder, exist_ok=True)

    meta = {"name": slug, "description": description or "", "type": stype, "category": category or "General"}

    if stype in ("code", "both"):
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters) if parameters.strip() else {}
            except Exception:  # noqa: BLE001
                parameters = {"type": "object", "properties": {}}
        meta["parameters"] = parameters or {"type": "object", "properties": {}}
        code = tool_code or "def run(**kwargs):\n    return 'ok'\n"
        with open(os.path.join(folder, "tool.py"), "w", encoding="utf-8") as f:
            f.write(code)

    if stype in ("prompt", "both"):
        meta["prompt"] = "prompt.md"
        with open(os.path.join(folder, "prompt.md"), "w", encoding="utf-8") as f:
            f.write(prompt_text or "")

    with open(os.path.join(folder, "skill.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return True, slug


def delete_skill(name, skills_dir=SKILLS_DIR):
    """ลบโฟลเดอร์ skill (กันลบนอกโฟลเดอร์ skills). คืน (ok, message)."""
    import shutil
    slug = _slug(name)
    folder = os.path.abspath(os.path.join(skills_dir, slug))
    root = os.path.abspath(skills_dir)
    if not slug or not folder.startswith(root + os.sep):
        return False, "path ไม่ถูกต้อง"
    if not os.path.isdir(folder):
        return False, "ไม่พบ skill"
    shutil.rmtree(folder)
    return True, slug


def get_skill_data(name: str, skills_dir=SKILLS_DIR) -> dict | None:
    """อ่านข้อมูลทั้งหมดของ skill สำหรับนำไปแก้ไข"""
    slug = _slug(name)
    folder = os.path.join(skills_dir, slug)
    if not os.path.isdir(folder):
        return None
    
    meta_path = os.path.join(folder, "skill.json")
    if not os.path.isfile(meta_path):
        return None
        
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except Exception:
        meta = {}
        
    data = {
        "name": meta.get("name", slug),
        "description": meta.get("description", ""),
        "type": meta.get("type", "code"),
        "category": meta.get("category", "General"),
        "parameters": json.dumps(meta.get("parameters", {"type": "object", "properties": {}}), ensure_ascii=False, indent=2),
        "tool_code": "",
        "prompt_text": ""
    }
    
    tool_path = os.path.join(folder, "tool.py")
    if os.path.isfile(tool_path):
        try:
            with open(tool_path, "r", encoding="utf-8") as f:
                data["tool_code"] = f.read()
        except Exception:  # noqa: BLE001
            pass

    prompt_path = os.path.join(folder, "prompt.md")
    if os.path.isfile(prompt_path):
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                data["prompt_text"] = f.read()
        except Exception:  # noqa: BLE001
            pass
        
    return data


def _find_skill_md(folder: str) -> str | None:
    """หาไฟล์ SKILL.md ในโฟลเดอร์ (ตัวพิมพ์ใหญ่/เล็กไม่เป็นไร)."""
    for fn in os.listdir(folder):
        if fn.lower() == "skill.md":
            return os.path.join(folder, fn)
    return None


def _parse_skill_md(path: str) -> tuple[dict, str]:
    """แยก YAML frontmatter อย่างง่าย (key: value บรรทัดเดียว) กับเนื้อหา markdown.

    ไม่ใช้ไลบรารี yaml — รองรับแค่ scalar บรรทัดเดียวพอ (name/description/category)
    ซึ่งครอบคลุม SKILL.md ปกติ; key ที่ซับซ้อนกว่านั้นถูกข้ามเฉย ๆ ไม่ error.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    meta: dict = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            for line in text[3:end].splitlines():
                if ":" not in line:
                    continue
                key, _, value = line.partition(":")
                key, value = key.strip(), value.strip().strip("'\"")
                if key and value and "\n" not in value:
                    meta[key] = value
            body = text[end + 4:].lstrip("\n")
    return meta, body


def import_or_convert_skill(src_folder: str, skills_dir=SKILLS_DIR) -> tuple[bool, str]:
    """นำเข้าหรือแปลงโฟลเดอร์ให้เป็น Skill"""
    if not os.path.isdir(src_folder):
        return False, "ไม่พบโฟลเดอร์"
    
    import shutil
    slug = _slug(os.path.basename(src_folder))
    if not slug:
        slug = "imported_skill"
    
    # วนลูปหาชื่อที่ไม่ซ้ำ
    dest_folder = os.path.join(skills_dir, slug)
    counter = 1
    orig_slug = slug
    while os.path.exists(dest_folder):
        slug = f"{orig_slug}_{counter}"
        dest_folder = os.path.join(skills_dir, slug)
        counter += 1

    # แบบที่ 1: เป็น Skill อยู่แล้ว
    if os.path.isfile(os.path.join(src_folder, "skill.json")):
        try:
            shutil.copytree(src_folder, dest_folder)
            return True, f"นำเข้า Skill '{slug}' สำเร็จ"
        except Exception as e:
            return False, f"เกิดข้อผิดพลาดในการนำเข้า: {e}"

    # แบบที่ 1.5: โฟลเดอร์รูปแบบ SKILL.md (มาตรฐานที่ Claude Code / Mesh LLM ใช้)
    # — frontmatter (name/description) + เนื้อหา markdown -> แปลงเป็น Prompt Skill
    skill_md = _find_skill_md(src_folder)
    if skill_md:
        try:
            meta_fm, body = _parse_skill_md(skill_md)
            name = _slug(meta_fm.get("name", "")) or slug
            # ชื่อจาก frontmatter อาจชนกับ skill เดิม -> วนหาชื่อว่างเหมือน slug ข้างบน
            dest_folder = os.path.join(skills_dir, name)
            counter = 1
            while os.path.exists(dest_folder):
                dest_folder = os.path.join(skills_dir, f"{name}_{counter}")
                name = os.path.basename(dest_folder)
                counter += 1
            os.makedirs(dest_folder, exist_ok=True)
            meta = {
                "name": name,
                "description": meta_fm.get("description")
                or f"skill จาก SKILL.md ({os.path.basename(src_folder)})",
                "type": "prompt",
                "category": meta_fm.get("category", "Imported"),
                "prompt": "prompt.md",
            }
            with open(os.path.join(dest_folder, "prompt.md"), "w", encoding="utf-8") as f:
                f.write(body)
            with open(os.path.join(dest_folder, "skill.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            return True, f"นำเข้า SKILL.md เป็น Skill '{name}' สำเร็จ"
        except Exception as e:  # noqa: BLE001
            return False, f"เกิดข้อผิดพลาดในการนำเข้า SKILL.md: {e}"

    # แบบที่ 2: แปลงโฟลเดอร์ธรรมดาเป็น Prompt Skill
    try:
        os.makedirs(dest_folder, exist_ok=True)
        prompt_lines = [f"# Knowledge from Folder: {os.path.basename(src_folder)}\n"]
        
        for root, dirs, files in os.walk(src_folder):
            for f in files:
                # ข้ามไฟล์ซ่อนและไฟล์ Binary ทั่วไป
                if f.startswith('.') or f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.exe', '.dll', '.so', '.pyc', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.wav', '.pdf')):
                    continue
                path = os.path.join(root, f)
                try:
                    # จำกัดขนาดไฟล์ที่อ่านไม่เกิน 50KB
                    if os.path.getsize(path) < 50000:
                        with open(path, "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                            if content.strip():
                                rel_path = os.path.relpath(path, src_folder)
                                prompt_lines.append(f"## {rel_path}\n```\n{content}\n```\n")
                except Exception:
                    pass
                    
        prompt_text = "\n".join(prompt_lines)[:100000] # จำกัดรวมไม่เกิน ~100KB เพื่อไม่ให้ Context ล้น
        
        meta = {
            "name": slug,
            "description": f"ความรู้และซอร์สโค้ดจากโฟลเดอร์ {os.path.basename(src_folder)}",
            "type": "prompt",
            "category": "Imported",
            "prompt": "prompt.md"
        }
        
        with open(os.path.join(dest_folder, "prompt.md"), "w", encoding="utf-8") as f:
            f.write(prompt_text)
        with open(os.path.join(dest_folder, "skill.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
            
        return True, f"แปลงโฟลเดอร์เป็น Skill '{slug}' สำเร็จ"
    except Exception as e:
        if os.path.exists(dest_folder):
            shutil.rmtree(dest_folder, ignore_errors=True)
        return False, f"เกิดข้อผิดพลาดในการแปลง: {e}"


class SkillRegistry:
    """รวม skills แล้วทำให้พร้อมเสียบเข้ากับระบบ tool calling."""

    def __init__(self, skills_dir: str = SKILLS_DIR):
        self.skills_dir = skills_dir
        self.skills: list[dict] = []
        self.reload()

    def reload(self) -> int:
        self.skills = discover(self.skills_dir)
        return len(self.skills)

    def _is_allowed(self, s: dict, allowed_categories: list[str] | None) -> bool:
        if not allowed_categories or "*" in allowed_categories:
            return True
        return s.get("category", "General") in allowed_categories

    # ---- tools (code skills) ----
    def tool_schemas(self, allowed_categories=None) -> list[dict]:
        out = []
        has_prompt = False
        for s in self.skills:
            if s["type"] == "error":
                continue
            if not self._is_allowed(s, allowed_categories):
                continue

            if s["type"] in ("code", "both") and s["run"]:
                out.append({"type": "function", "function": {
                    "name": s["name"],
                    "description": s["description"] + " (skill)",
                    "parameters": s["parameters"] or {"type": "object", "properties": {}},
                }})
            if s["type"] in ("prompt", "both"):
                has_prompt = True

        # ถ้ามี prompt skill ในหมวดที่อนุญาต -> เพิ่มเครื่องมือ use_skill
        if has_prompt:
            out.append({"type": "function", "function": {
                "name": "use_skill",
                "description": "ดึงคำสั่ง/ความรู้ของ skill มาใช้ ก่อนทำงานที่เกี่ยวข้อง",
                "parameters": {"type": "object", "properties": {
                    "name": {"type": "string", "description": "ชื่อ skill"}},
                    "required": ["name"]},
            }})
        return out

    def tool_map(self) -> dict:
        """ชื่อ -> ฟังก์ชัน สำหรับเรียกใช้ (ดึงมาทั้งหมดเพื่อเตรียมให้ server เรียก)."""
        m = {}
        for s in self.skills:
            if s["type"] in ("code", "both") and s["run"]:
                m[s["name"]] = s["run"]
        if any(s["type"] in ("prompt", "both") for s in self.skills):
            m["use_skill"] = self._use_skill
        return m

    def _use_skill(self, name: str) -> str:
        for s in self.skills:
            if s["name"] == name and s["prompt"]:
                return s["prompt"]
        return f"ไม่พบคำสั่งของ skill '{name}'"

    def catalog(self, allowed_categories=None) -> str:
        if not self.skills:
            return ""
        
        filtered = [s for s in self.skills if s["type"] != "error" and self._is_allowed(s, allowed_categories)]
        if not filtered:
            return ""

        groups = {}
        for s in filtered:
            cat = s.get("category", "General")
            if cat not in groups:
                groups[cat] = []
            groups[cat].append(s)

        lines = ["คุณมี Skills พิเศษที่ผู้ใช้ติดตั้งไว้ดังนี้ (ให้พิจารณาเลือกใช้ให้เหมาะสม):"]
        for cat, items in groups.items():
            lines.append(f"\n[หมวดหมู่: {cat}]")
            for s in items:
                kind = {"code": "เครื่องมือ", "prompt": "คู่มือคำสั่ง", "both": "เครื่องมือและคู่มือ"}.get(s["type"], "")
                lines.append(f"- {s['name']} ({kind}): {s['description']}")
                
        lines.append("\n[คำแนะนำการใช้ Skills]")
        lines.append("1. Skill ประเภทเครื่องมือ (code): สามารถเรียกใช้งาน (Tool calling) ได้ทันทีเหมือนเครื่องมือปกติ")
        lines.append("2. Skill ประเภทคู่มือคำสั่ง (prompt): คุณต้องเรียกใช้เครื่องมือ `use_skill(name=\"...\")` ก่อนเพื่ออ่านคำสั่ง จากนั้นให้นำคำสั่งหรือความรู้ที่ได้รับมาปฏิบัติตามทันทีในการตอบผู้ใช้")
        return "\n".join(lines)

    def public_list(self) -> list[dict]:
        """ข้อมูลย่อสำหรับแสดงใน UI."""
        return [{"name": s["name"], "description": s["description"], "type": s["type"],
                 "category": s.get("category", "General"), "error": s.get("error", "")} for s in self.skills]
