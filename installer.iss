; ============================================================================
;  LM Co-work — Inno Setup script
;  สร้างตัวติดตั้ง (Setup.exe) แบบ wizard ให้ dist\LM Co-work.exe
;
;  วิธีใช้:
;   1. ติดตั้ง Inno Setup (ฟรี) จาก https://jrsoftware.org/isinfo.php
;   2. เปิดไฟล์นี้ด้วย Inno Setup Compiler (หรือคลิกขวา > Compile)
;   3. ได้ไฟล์ Setup ที่ Output\LM-Co-work-Setup-<version>.exe
;
;  หมายเหตุ: แอปนี้พึ่ง pythonnet/clr + WebView2 (Windows เท่านั้น) จึงทำ
;  installer แบบนี้ให้เฉพาะ Windows — ไม่รองรับ macOS/Linux ด้วยโค้ดชุดนี้
; ============================================================================

#define MyAppName "LM Co-work"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Korakrod"
#define MyAppExeName "LM Co-work.exe"
#define MyAppURL "https://lmstudio.ai"

[Setup]
; GUID คงที่ประจำแอปนี้ (อย่าเปลี่ยนหลังปล่อยเวอร์ชันแรก ไม่งั้น Windows จะมองว่าเป็นโปรแกรมคนละตัว)
AppId={{7C3F9C2E-4B7A-4E1D-9E8B-2A6B1D9E4F31}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}

; ติดตั้งแบบ per-user (ไม่ต้องขอสิทธิ์ admin) เพราะแอปเขียนไฟล์ data\*.json
; ไว้ข้างๆ ตัว .exe เอง — ถ้าติดตั้งลง Program Files แบบ all-user จะเขียนไฟล์ไม่ได้
; ถ้าต้องการให้เลือกได้ทั้ง per-user/all-user ให้เปลี่ยนเป็น PrivilegesRequiredOverridesAllowed=dialog
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

OutputDir=installer_output
OutputBaseFilename=LM-Co-work-Setup-{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableDirPage=no
DisableWelcomePage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; ตัวโปรแกรมหลัก (build แล้วจาก build-ui.bat)
Source: "dist\LM Co-work.exe"; DestDir: "{app}"; Flags: ignoreversion
; skills ที่ build-ui.bat copy ไว้ที่ dist\skills อยู่แล้ว
Source: "dist\skills\*"; DestDir: "{app}\skills"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "*.pyc,__pycache__"
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; ลบไฟล์/โฟลเดอร์ที่แอปสร้างเพิ่มระหว่างใช้งาน (cache ของ python ถ้ามี)
Type: filesandordirs; Name: "{app}\__pycache__"
; หมายเหตุ: ไม่ลบ {app}\data โดยอัตโนมัติ เพื่อกันไม่ให้ประวัติแชต/โปรเจกต์ของผู้ใช้หายตอน uninstall
; ถ้าต้องการให้ลบด้วย ให้เพิ่มบรรทัด: Type: filesandordirs; Name: "{app}\data"

[Code]
function IsWebView2Installed(): Boolean;
var
  Version: String;
begin
  Result :=
    RegQueryStringValue(HKLM64, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) or
    RegQueryStringValue(HKLM32, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) or
    RegQueryStringValue(HKCU, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version);
end;

procedure InitializeWizard();
begin
  if not IsWebView2Installed() then
  begin
    MsgBox('ตรวจไม่พบ Microsoft Edge WebView2 Runtime ในเครื่องนี้' + #13#10 +
           #13#10 +
           'LM Co-work ต้องใช้ WebView2 เพื่อแสดงหน้าต่างโปรแกรม (Windows 11 มีติดตั้งมาให้แล้ว ' +
           'ส่วน Windows 10 บางเครื่องอาจยังไม่มี)' + #13#10 +
           #13#10 +
           'ติดตั้งต่อได้ตามปกติ ถ้าเปิดโปรแกรมแล้วมีข้อความแจ้งเรื่อง WebView2 ให้ไปดาวน์โหลดฟรีที่ ' +
           'https://developer.microsoft.com/microsoft-edge/webview2/',
           mbInformation, MB_OK);
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    // เตือนเรื่อง LM Studio บนหน้าสุดท้ายของ wizard
  end;
end;
