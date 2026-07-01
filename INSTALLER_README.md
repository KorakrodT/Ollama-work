# วิธีสร้างตัวติดตั้ง (Setup.exe) ของ LM Co-work

ไฟล์ `installer.iss` ที่สร้างไว้เป็นสคริปต์สำหรับ **Inno Setup** — ทำตัวติดตั้งแบบ wizard
(หน้าจอถัดไป/ยอมรับ/เลือกโฟลเดอร์/สร้าง shortcut/ปุ่ม uninstall) ให้ `LM Co-work.exe`

ต้องคอมไพล์บนเครื่อง Windows เท่านั้น (Inno Setup เป็นโปรแกรม Windows) — คอมไพล์ในนี้ให้ไม่ได้

## ขั้นตอน (ทำครั้งเดียว)

1. ดาวน์โหลด Inno Setup (ฟรี) จาก https://jrsoftware.org/isdl.php แล้วติดตั้ง
2. เช็คว่ามี `dist\LM Co-work.exe` แล้ว (ถ้ายังไม่มี ให้รัน `build-ui.bat` ก่อน)
3. ดับเบิลคลิก `installer.iss` (จะเปิดด้วย Inno Setup Compiler อัตโนมัติ)
4. กด **Build > Compile** (หรือ Ctrl+F9)
5. ได้ไฟล์ `installer_output\LM-Co-work-Setup-1.0.0.exe` — นี่คือตัวติดตั้งที่แจกจ่ายได้

## ตัวติดตั้งนี้ทำอะไรบ้าง

- ติดตั้งแบบ **per-user** (ไม่ต้องสิทธิ์ admin) ไปที่ `%LocalAppData%\Programs\LM Co-work`
  (เพราะแอปเก็บข้อมูล `data\*.json` ไว้ข้างๆ ตัว .exe — ถ้าลง Program Files แบบ all-user จะเขียนไฟล์ไม่ได้)
- คัดลอก `LM Co-work.exe` + โฟลเดอร์ `skills\` + ไอคอน
- สร้าง shortcut ใน Start Menu และถามว่าจะสร้างบน Desktop ไหม
- มีตัว Uninstall ให้ในตัว (ถอนการติดตั้งได้จาก Settings > Apps หรือ Start Menu)
- **ไม่ลบโฟลเดอร์ `data\`** ตอน uninstall (กันประวัติแชต/โปรเจกต์หาย) — ถ้าอยากให้ลบด้วยตอน uninstall
  ให้แก้ `installer.iss` section `[UninstallDelete]` ตามคอมเมนต์ในไฟล์
- เช็คว่ามี Microsoft Edge WebView2 Runtime ในเครื่องไหม ถ้าไม่มีจะเตือน (Windows 11 มีมาให้แล้ว)

## อัปเดตเวอร์ชันครั้งถัดไป

แก้บรรทัด `#define MyAppVersion "1.0.0"` ในไฟล์ `installer.iss` เป็นเลขเวอร์ชันใหม่ แล้ว build ใหม่
(อย่าแก้ค่า `AppId` เด็ดขาด — ไม่งั้น Windows จะมองเป็นโปรแกรมคนละตัว ติดตั้งซ้อนกันแทนที่จะอัปเดต)

## หมายเหตุเรื่อง macOS

โค้ดของ LM Co-work พึ่ง `pythonnet`/`clr` และ Microsoft Edge WebView2 ซึ่งเป็นเทคโนโลยีเฉพาะ Windows
(ดูใน `requirements.txt` และ `winproc.py`) จึงยังไม่มีทางสร้างตัวติดตั้ง macOS (.pkg/.dmg) จากโค้ดชุดนี้ได้ตรงๆ
ถ้าต้องการรองรับ Mac จริงๆ ต้องปรับ `server.py` ให้ใช้ pywebview backend อื่น (เช่น Cocoa บน macOS แทน edgechromium)
ก่อน แล้วค่อยแพ็กด้วย PyInstaller + เครื่องมือทำ .dmg (เช่น `create-dmg`) แยกต่างหาก — เป็นงานเพิ่มนอกเหนือจาก
ตัวติดตั้ง Windows ที่ทำให้ตอนนี้
