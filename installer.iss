
[Setup]
AppName=ICAMP
AppVersion=1.0.7
DefaultDirName={pf}\ICAMP
DefaultGroupName=ICAMP
UninstallDisplayIcon={app}\RenombradorPDF.exe
Compression=lzma2
SolidCompression=yes
OutputDir=C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\Installer
OutputBaseFilename=ICAMP_Setup_1.0.7

[Files]
Source: "C:/Users/USER/Desktop/PRUEBA/ICAMP 1.0.5\dist\RenombradorPDF.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\ICAMP"; Filename: "{app}\RenombradorPDF.exe"
Name: "{commondesktop}\ICAMP"; Filename: "{app}\RenombradorPDF.exe"

[Run]
Filename: "{app}\RenombradorPDF.exe"; Description: "Iniciar ICAMP"; Flags: postinstall nowait
