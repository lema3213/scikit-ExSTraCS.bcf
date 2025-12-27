@echo off
setlocal

rem Path to the Python interpreter (your python env)
set "PY=C:\Users\lema\.conda\envs\UCFLCS\python.exe"

rem Path to the training script
set "SCRIPT=.\..\test\test_ExSTraCS_CMD.py"

rem use transfer learning (1) or not (0)
set "USE_TL=1"

rem Loop index from 0 to 9 (10 runs)
for /L %%i in (0,1,9) do (
  rem Args: index dataset learning_iterations N p_spec level use_tl(transfer learning)
  echo start "%SCRIPT%" %%i mpr6 100000 500 0.66 1 %USE_TL%
  start "" "%PY%" "%SCRIPT%" %%i mpr6 100000 500 0.66 1 %USE_TL%

  rem Uncomment below if you want to run other datasets too
  rem start "" "%PY%" "%SCRIPT%" %%i mpr11  100000   1000   0.66 2 %USE_TL%
  rem start "" "%PY%" "%SCRIPT%" %%i mpr20  100000   2000   0.66 3 %USE_TL%
  rem start "" "%PY%" "%SCRIPT%" %%i mpr37  1000000  10000  0.5  4 %USE_TL%
  rem start "" "%PY%" "%SCRIPT%" %%i mpr70  2000000  20000  0.5  5 %USE_TL%
  rem start "" "%PY%" "%SCRIPT%" %%i mpr135 3000000  50000  0.5  6 %USE_TL%
)

echo All jobs started in background.
endlocal
