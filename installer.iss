; ============================================
; Inno Setup script para RunDesk
; Requiere Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
;
; Uso:
;   1. Ejecutar build.bat para generar dist\RunDesk.exe
;   2. Abrir este .iss en Inno Setup Compiler
;   3. Compilar para generar el instalador
;
; Output:
;   installer_output/RunDeskSetup_0.1.1.exe
; ============================================

#define MyAppName "RunDesk"
#define MyAppVersion "0.1.1"
#define MyAppPublisher "MikeDevQH"
#define MyAppExeName "RunDesk.exe"
#define MyAppURL "https://github.com/MikeDevQH/RunDesk"
#define MyAppDescription "A fast, offline text-based command launcher for Windows"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
AppComments={#MyAppDescription}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=RunDeskSetup_{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=LICENSE.txt
VersionInfoVersion=0.1.0.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[CustomMessages]
english.LaunchAfterInstall=Launch RunDesk now
english.StartWithWindows=Start RunDesk when Windows starts
english.AdditionalOptions=Additional options:
spanish.LaunchAfterInstall=Ejecutar RunDesk ahora
spanish.StartWithWindows=Iniciar RunDesk con Windows
spanish.AdditionalOptions=Opciones adicionales:

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "{cm:StartWithWindows}"; GroupDescription: "{cm:AdditionalOptions}"; Flags: checkablealone

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.png"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppDescription}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "{#MyAppDescription}"

[Registry]
; Inicio con Windows — lanza minimizado en segundo plano
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"" --minimized"; Flags: uninsdeletevalue; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchAfterInstall}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden; RunOnceId: "KillRunDesk"

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\RunDesk"
