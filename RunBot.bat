@echo off

mkdir Voices

python -m venv XLHEnv

call XLHEnv\Scripts\activate

pip install -r piplist.txt

call cls

python XLH.py
