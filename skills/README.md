# 🧩 Skills — สร้างความสามารถใหม่ของ agent เอง

วาง 1 skill = 1 โฟลเดอร์ในนี้ โปรแกรมจะโหลดให้อัตโนมัติ (กดปุ่ม "โหลด Skills ใหม่" ใน UI
หรือเปิดโปรแกรมใหม่)

## โครงสร้าง 1 skill

```
skills/
  ชื่อ_skill/
    skill.json     (บังคับ)
    tool.py        (ถ้าเป็น code skill — มีฟังก์ชัน run(**kwargs) -> str)
    prompt.md      (ถ้าเป็น prompt skill — คำสั่ง/ความรู้)
```

## skill.json

```json
{
  "name": "ชื่อเรียกใช้ (อังกฤษ ไม่มีเว้นวรรค)",
  "description": "อธิบายสั้น ๆ ว่า skill ทำอะไร",
  "type": "code",            // code | prompt | both
  "parameters": {            // ใส่เฉพาะ code/both
    "type": "object",
    "properties": { "text": { "type": "string", "description": "..." } },
    "required": ["text"]
  },
  "prompt": "prompt.md"      // ใส่เฉพาะ prompt/both
}
```

## ตัวอย่างในโฟลเดอร์นี้

- **word_count** — code skill: นับคำ/ตัวอักษร/บรรทัด
- **thai_formal_email** — prompt skill: คำสั่งเขียนอีเมลทางการ

## สร้าง skill ใหม่แบบง่าย

เปิด UI เลือก agent **🛠️ Skill Builder** แล้วบอกว่าอยากได้ skill อะไร
มันจะเขียนเนื้อหา `skill.json` / `tool.py` / `prompt.md` ให้ คุณก็อปไปวางเป็นโฟลเดอร์ใหม่ในนี้
แล้วกด "โหลด Skills ใหม่"

> ⚠️ `tool.py` คือโค้ด Python ที่รันบนเครื่องคุณ — อย่าวาง skill จากแหล่งที่ไม่ไว้ใจ
