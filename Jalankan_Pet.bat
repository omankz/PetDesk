@echo off
REM ===== PetDex Desktop Pet launcher =====
cd /d "%~dp0"

REM pythonw = jalan tanpa jendela konsol hitam
where pythonw >nul 2>nul
if %errorlevel%==0 (
  start "" pythonw "desktop_pet.py"
) else (
  start "" python "desktop_pet.py"
)
