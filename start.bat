@echo off
cd /d "D:\OneDrive\Bureau\clean script"
powershell -Command "Start-Process python -ArgumentList 'nettoyage_pc.py' -Verb RunAs"
exit
