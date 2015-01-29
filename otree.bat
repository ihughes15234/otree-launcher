@echo off
pythonw run.py || goto :error

:error
exit /b %errorlevel%
