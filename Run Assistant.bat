@echo off

REM Activate Conda Environment
call conda activate XLH

REM Run Python Program in the background
python XLH.py

REM Deactivate Conda Environment (optional, but good practice)
call conda deactivate
