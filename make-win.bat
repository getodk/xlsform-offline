rd /s /q build\xlsform-offline-win 
rd /s /q dist\win
del /s /q *.pyc
pyinstaller pkg\xlsform-offline-win.spec --distpath dist\win --onefile --windowed --noconfirm --clean