@echo off
pythonw -c "from otree_launcher import gui; gui.run()" || goto :error

:error
exit /b %errorlevel%
