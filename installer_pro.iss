
; Script de instalación para ICAMP
; Versión: 1.1.0

[Setup]
AppId={{ICAMP-1-1-0-PRO}}
AppName=ICAMP
AppVersion=1.1.0
AppPublisher=Mr. Sys
AppPublisherURL=https://github.com/Mrsys-creator/ICAMP
AppSupportURL=https://github.com/Mrsys-creator/ICAMP
AppUpdatesURL=https://github.com/Mrsys-creator/ICAMP
DefaultDirName={pf}\ICAMP
DefaultGroupName=ICAMP
AllowNoIcons=yes
OutputDir=C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\Installer_PRO
OutputBaseFilename=ICAMP_Setup_1.1.0
SetupIconFile=C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\Installer_Files\tu_icono.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\RenombradorPDF.exe
UninstallDisplayName=ICAMP 1.1.0

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
  Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\Installer_Files\RenombradorPDF.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\Installer_Files\version.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\Installer_Files\fondo_iess.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\Installer_Files\fondo_issfa.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ICAMP"; Filename: "{app}\RenombradorPDF.exe"
Name: "{group}\Desinstalar ICAMP"; Filename: "{uninstallexe}"
Name: "{autodesktop}\ICAMP"; Filename: "{app}\RenombradorPDF.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RenombradorPDF.exe"; Description: "{cm:LaunchProgram,ICAMP}"; Flags: postinstall nowait skipifsilent

[Messages]
SpanishWelcomeLabel1=Bienvenido al instalador de ICAMP
SpanishWelcomeLabel2=Este programa instalará ICAMP versión 1.1.0 en tu sistema.
SpanishReadyLabel1=Listo para instalar ICAMP
SpanishReadyLabel2=El programa está listo para ser instalado en tu sistema.

EnglishWelcomeLabel1=Welcome to ICAMP Setup
EnglishWelcomeLabel2=This will install ICAMP version 1.1.0 on your system.
EnglishReadyLabel1=Ready to install ICAMP
EnglishReadyLabel2=The program is ready to be installed on your system.
