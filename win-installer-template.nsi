# define name of installer
OutFile "installer.exe"
 
# define installation directory
InstallDir "$PROGRAMFILES\Enbea"
 
# start default section
Section

    # set the installation directory as the destination for the following actions
    SetOutPath $INSTDIR
 
    # create the uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
 
    # create a shortcut named "new shortcut" in the start menu programs directory
    # point the new shortcut at the program uninstaller
    #INCLUDE_FILES#
    CreateShortCut "$DESKTOP\ENBea.lnk" "$INSTDIR\enbea.exe"
SectionEnd
 
# uninstaller section start
Section "uninstall"
 
    # first, delete the uninstaller
    Delete "$INSTDIR\uninstall.exe"
    Delete "$DESKTOP\ENBea.lnk"
    #DELETE_FILES#
# uninstaller section end
SectionEnd