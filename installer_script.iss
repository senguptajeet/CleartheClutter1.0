[Setup]
; A unique identifier for your app so Windows knows how to uninstall or update it
AppId={{C1B5F8A9-9B2D-4C3A-8F7E-2D4E6A8B9C0D}
AppName=Clear The Clutter
AppVersion=1.0.0
AppPublisher=Jeet Sengupta
; Installs into C:\Program Files\Clear The Clutter
DefaultDirName={autopf}\Clear The Clutter
DisableProgramGroupPage=yes
; Requires administrator rights to install into Program Files
PrivilegesRequired=admin
; The folder where your final setup.exe will be saved
OutputDir=Output
OutputBaseFilename=ClearTheClutter_Setup_v1.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; If you successfully created the app_icon.ico earlier, remove the semicolon (;) from the beginning of the next line to apply it to the installer wizard:
; SetupIconFile=assets\app_icon.ico

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Grabs the executable we built using PyInstaller
Source: "dist\ClearTheClutter.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Creates the Start Menu shortcut
Name: "{autoprograms}\Clear The Clutter"; Filename: "{app}\ClearTheClutter.exe"
; Creates the Desktop shortcut if the user checks the box
Name: "{autodesktop}\Clear The Clutter"; Filename: "{app}\ClearTheClutter.exe"; Tasks: desktopicon

[Run]
; Offers a checkbox to launch the app immediately after installation finishes
Filename: "{app}\ClearTheClutter.exe"; Description: "{cm:LaunchProgram,Clear The Clutter}"; Flags: nowait postinstall skipifsilent