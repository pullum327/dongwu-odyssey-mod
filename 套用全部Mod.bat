@echo off
chcp 65001 >nul
cd /d "%~dp0.."
python "_ignite_mod\apply_mods.py"
pause
