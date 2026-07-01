# วิธีเอา LM Co-work ขึ้น GitHub (public repo ใหม่)

สภาพแวดล้อมที่ผมทำงานอยู่ (sandbox) เข้าไปแก้ไข `.git` ในเครื่องคุณโดยตรงไม่ได้ (กันไว้เพื่อความปลอดภัย
ของประวัติ git) และไม่มีสิทธิ์ login GitHub ของคุณ — ขั้นตอนข้างล่างต้องรันเองบนเครื่องคุณ (PowerShell/Terminal
หรือ GitHub Desktop) แต่ผมเตรียมไฟล์ทุกอย่างที่ต้องใช้ไว้ให้แล้ว

## สิ่งที่เตรียมไว้ให้แล้ว

- ✅ `.gitignore` — เพิ่ม `/data/` (ประวัติแชทจริง + path ส่วนตัว `C:\Users\korak\...` + API key ของ
  provider ที่คุณตั้งไว้ในแอป), `/agents_user.json`, `.ruff_cache/`, `.qodo/`, `.agents/`, `/installer_output/`
  **ห้ามลบบรรทัดพวกนี้ออกก่อน push ขึ้น public repo เด็ดขาด**
- ✅ `LICENSE` — MIT License
- ✅ `README.md`, `.github/workflows/ci.yml` — มีอยู่แล้ว พร้อมใช้

## ขั้นตอน (รันใน PowerShell ที่ `E:\AI Agent`)

### 1. เช็คสถานะ git ปัจจุบันก่อน

```powershell
cd "E:\AI Agent"
git status
```

- ถ้าขึ้น `fatal: not a git repository` → รัน `git init` ก่อน
- ถ้ามีอยู่แล้วและเคย commit `data/` หรือไฟล์ที่มีข้อมูลส่วนตัวไปก่อนหน้านี้ → **บอกผมก่อน push**
  เพราะแค่เพิ่มใน `.gitignore` ตอนนี้ **ไม่ได้ลบมันออกจากประวัติ commit เก่า** ต้องใช้ `git rm -r --cached data`
  + commit ใหม่ (หรือ `git filter-repo` ถ้าอยากลบออกจากประวัติทั้งหมดจริงๆ)

### 2. ตรวจให้ชัวร์ว่าไฟล์ส่วนตัวจะไม่ถูก commit

```powershell
git add .
git status
```

ในลิสต์ "Changes to be committed" **ต้องไม่มี** `data/...` หรือ `agents_user.json` โผล่มา — ถ้ามี ให้หยุดแล้วบอกผม

### 3. Commit แรก

```powershell
git commit -m "Initial commit: LM Co-work"
```

### 4. สร้าง repo บน GitHub แล้ว push

**ถ้ามี GitHub CLI (`gh`) ติดตั้งอยู่และ login แล้ว (`gh auth login`):**

```powershell
gh repo create LM-Co-work --public --source=. --remote=origin --push
```

**ถ้าไม่มี `gh`:**

1. ไปที่ https://github.com/new → ตั้งชื่อ repo เช่น `LM-Co-work` → เลือก **Public**
   → **ห้ามติ๊ก** "Add a README/gitignore/license" (มีอยู่แล้วในเครื่อง จะได้ไม่ชนกัน) → กด Create repository
2. คัดลอกคำสั่งจากหน้า "…or push an existing repository from the command line" ที่ GitHub แสดงให้ ประมาณนี้:

```powershell
git branch -M main
git remote add origin https://github.com/<your-username>/LM-Co-work.git
git push -u origin main
```

## หลัง push แล้ว

- ไฟล์ `dist\LM Co-work.exe` (~40MB) และ `installer_output\*.exe` จะ **ไม่ถูกอัปขึ้นไปด้วย** (ถูก ignore ไว้
  เพราะไบนารีขนาดใหญ่ไม่ควรอยู่ใน git history) — ถ้าอยากแจกไฟล์ .exe ให้คนอื่นโหลด แนะนำใช้
  **GitHub Releases** แทน (Repo → Releases → Draft a new release → แนบไฟล์ .exe/Setup.exe เข้าไป)
- เช็คหน้า repo บน GitHub อีกทีว่าไม่มี `data/` หรือไฟล์ path ส่วนตัวหลุดขึ้นไป
- Actions tab จะรัน CI (`ci.yml`) อัตโนมัติ ให้ดูว่าผ่านไหม
