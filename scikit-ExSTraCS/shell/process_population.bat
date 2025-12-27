@echo off
setlocal

rem Path to the Python interpreter (your conda env)
set "PY=C:\Users\lema\.conda\envs\UCFLCS\python.exe"

rem Path to the training script
set "SCRIPT=.\..\utils\ProcessPopulation.py"

rem Loop index from 0 to 9 (ten runs)
for /L %%i in (0,1,1) do (
  rem Args: index dataset
  echo start "%SCRIPT%" %%i mpr6
  start "" "%PY%" "%SCRIPT%" %%i mpr6

  rem Uncomment below if you want to run other datasets too
  rem start "" "%PY%" "%SCRIPT%" %%i mpr11
  rem start "" "%PY%" "%SCRIPT%" %%i mpr20
  rem start "" "%PY%" "%SCRIPT%" %%i mpr37
  rem start "" "%PY%" "%SCRIPT%" %%i mpr70
  rem start "" "%PY%" "%SCRIPT%" %%i mpr135
)

echo All jobs started in background.
endlocal
