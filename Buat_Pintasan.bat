@echo off
REM Membuat shortcut "PetDesk" di Desktop, lengkap dengan ikon.
REM (File .bat tidak bisa punya ikon sendiri, jadi pakai shortcut ini.)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$lnk = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\PetDesk.lnk');" ^
  "$lnk.TargetPath = '%~dp0Jalankan_Pet.bat';" ^
  "$lnk.WorkingDirectory = '%~dp0';" ^
  "$lnk.IconLocation = '%~dp0assets\icon.ico';" ^
  "$lnk.Description = 'PetDesk - pet virtual di desktop';" ^
  "$lnk.Save()"
echo.
echo Shortcut "PetDesk" sudah dibuat di Desktop (dengan ikon).
pause
