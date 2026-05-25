@echo off
chcp 65001 >nul
cd /d "%~dp0.."
python "_ignite_mod\apply_mods.py" --only ignite_no_consume,ignite_changming_triple
pause
