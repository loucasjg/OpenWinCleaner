@echo off
powershell -Command "Start-Process python -ArgumentList 'nettoyage_pc.py' -Verb RunAs"
exit
