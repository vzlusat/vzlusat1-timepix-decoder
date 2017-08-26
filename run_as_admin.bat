@setlocal enableextensions
@cd /d "%~dp0"
pip install --upgrade matplotlib
@echo off

python decoder.py
