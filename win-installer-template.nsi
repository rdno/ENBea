#Include Modern UI
!include "MUI2.nsh"
# define name of installer
Name "ENBea"
OutFile "enbea-installer.exe"
 
# define installation directory
InstallDir "$PROGRAMFILES\Enbea"

Var StartMenuFolder
 
#Request application privileges for Windows Vista
RequestExecutionLevel user

#Pages
!insertmacro MUI_PAGE_LICENSE "COPYING"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

#Languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Turkish"
  

# start default section
Section

    # set the installation directory as the destination for the following actions
    SetOutPath $INSTDIR
    
    #Store installation folder
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Enbea" \
                 "DisplayName" "ENBea - Episode Name Beautifier"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Enbea" \
                 "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    
    # create the uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
 
    # create a shortcut named "new shortcut" in the start menu programs directory
    # point the new shortcut at the program uninstaller
    #INCLUDE_FILES#
    
    CreateShortCut "$DESKTOP\ENBea.lnk" "$INSTDIR\enbea.exe"
    #Start Menu
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\ENBea.lnk" "$INSTDIR\enbea.exe"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd
 
# uninstaller section start
Section "uninstall"
 
    # first, delete the uninstaller
    Delete "$INSTDIR\uninstall.exe"
    Delete "$DESKTOP\ENBea.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\ENBea.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" 
    RMDir "$SMPROGRAMS\$StartMenuFolder"    
    #DELETE_FILES#
    
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Enbea"
# uninstaller section end
SectionEnd