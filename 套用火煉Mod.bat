@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo 請先關閉遊戲，再按任意鍵套用修補...
pause >nul
python "_ignite_mod\apply_mods.py" --only ignite_no_consume,ignite_changming_triple
if errorlevel 1 pause
else echo 完成。
pause
