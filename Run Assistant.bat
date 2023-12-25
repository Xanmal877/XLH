@echo off

REM Activate the virtual environment (Replace 'XLH' with your venv name)
call .\XLH\Scripts\activate

REM Run Python Program in the background
python XLH.py
pause

REM Deactivate the virtual environment
call .\XLH\Scripts\deactivate
