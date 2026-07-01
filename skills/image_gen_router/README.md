# image_gen_router

Skill นี้เพิ่ม tool สำหรับสร้างภาพผ่าน backend ที่ผู้ใช้เลือกเอง:

- `backend=gpt` ใช้ Codex/OpenAI CLI (`codex`)
- `backend=gemini` ใช้ agy/Gemini CLI (`agy`)

ดัดแปลงแนวคิดจาก `andrewii23/ii23-skills` ให้เข้ากับระบบ `skills_loader.py` ของแอป `E:\AI Agent` บน Windows โดยไม่ต้องแก้ `skills_loader.py`, `server.py`, หรือ `tools.py`.

## วิธีใช้

เรียก skill `image_gen_router` พร้อมพารามิเตอร์:

- `prompt`: คำบรรยายภาพที่ต้องการ
- `backend`: `gpt` หรือ `gemini`
- `out`: path ปลายทาง optional เช่น `~/Pictures/my-image.png`
- `timeout`: เวลารอเป็นวินาที default `600`

ถ้าผู้ใช้พูดว่า GPT, OpenAI, ChatGPT หรือ Codex ให้ใช้ `backend=gpt`.
ถ้าผู้ใช้พูดว่า Gemini, Google หรือ agy ให้ใช้ `backend=gemini`.
ถ้าผู้ใช้ไม่ได้ระบุ backend ให้ agent ถามก่อนว่าจะใช้ `gpt` หรือ `gemini` แล้วค่อยเรียก tool.

## ข้อกำหนด

Skill นี้ติดตั้งเฉพาะตัว router และ runner scripts เท่านั้น ยังไม่ได้ติดตั้ง backend CLI ให้โดยอัตโนมัติ.

สำหรับ GPT/Codex:

1. ติดตั้ง `codex`
2. login ให้เรียบร้อย เช่น `codex login`
3. ตรวจสอบว่าคำสั่ง `codex` อยู่ใน `PATH`

สำหรับ Gemini/agy:

1. ติดตั้ง `agy`
2. login ให้เรียบร้อยตามวิธีของ CLI
3. ตรวจสอบว่าคำสั่ง `agy` อยู่ใน `PATH`

หากยังไม่ได้ติดตั้งหรือ login การสร้างภาพจริงจะ fail พร้อมข้อความแนะนำในผลลัพธ์ของ tool.

## หมายเหตุ Windows

- runner ใช้ `shutil.which()` เพื่อหา `codex`/`agy` และส่ง full path เข้า `subprocess.run()` จึงรองรับ CLI ที่ติดตั้งผ่าน npm หรือ wrapper `.cmd` ได้ดีขึ้น
- ใช้ `encoding="utf-8", errors="replace"` เพื่อลดปัญหา output encoding บน Windows
- รองรับ path แบบ `C:\...\file.png`, `C:/.../file.png`, Unix-style path และ `~`
- output default ของ `backend=gpt` อยู่ที่ `%USERPROFILE%\.codex\generated_images`
- output default ของ `backend=gemini` อยู่ที่ `%USERPROFILE%\.cache\image_gen_router\gemini`

## Reload

หลังติดตั้ง ให้กดปุ่มโหลด Skills ใหม่ (⟳) ใน UI หรือเปิดแอปใหม่ เพื่อให้ loader เห็น skill ใหม่.

ครั้งแรกที่ agent เรียก skill นี้ แอปจะขึ้น confirm gate ให้กดยืนยันก่อนรัน `tool.py` ซึ่งเป็นพฤติกรรมมาตรฐานของ code skill.
