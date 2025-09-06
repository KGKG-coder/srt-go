@echo off
:: Refresh PATH environment variable
for /f "usebackq tokens=2,*" %%A in (`reg query HKCU\Environment /v PATH`) do set userpath=%%B
for /f "usebackq tokens=2,*" %%A in (`reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH`) do set systempath=%%B
set PATH=%systempath%;%userpath%