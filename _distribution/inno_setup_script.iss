#define MyAppName "Empirix Lab"
#define MyAppVersion "25.1"
#define MyAppPublisher "Empirix.ru"
#define MyAppURL "https://empirix.ru/"
#define MyAppExeName "empirix-lab.exe"

[Setup]
AppId={{41EAD664-F1A8-435A-98D9-0A644A6E7AC2}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\Empirix Lab
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=C:\Users\rsm\Documents\MyProjects\empirix-lab\LICENSE
;PrivilegesRequired=lowest
OutputDir=C:\Users\rsm\Documents\Bundles\empirix-lab_25.1
OutputBaseFilename=empirix-lab-25.1-setup
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\rsm\Documents\Bundles\empirix-lab_25.1\empirix-lab\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\rsm\Documents\Bundles\empirix-lab_25.1\empirix-lab\_internal\*"; DestDir: "{app}/_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent