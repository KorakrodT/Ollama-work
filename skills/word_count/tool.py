"""Skill: word_count — นับคำ/ตัวอักษร/บรรทัด"""


def run(text: str = "") -> str:
    chars = len(text)
    chars_no_space = len(text.replace(" ", "").replace("\n", ""))
    words = len(text.split())
    lines = len(text.splitlines()) or (1 if text else 0)
    return (f"ผลการนับ:\n"
            f"- คำ: {words}\n"
            f"- ตัวอักษร (รวมเว้นวรรค): {chars}\n"
            f"- ตัวอักษร (ไม่รวมเว้นวรรค): {chars_no_space}\n"
            f"- บรรทัด: {lines}")
