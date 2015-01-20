@echo off
pythonw run.py --gui || goto :error

:error
exit /b %errorlevel%
