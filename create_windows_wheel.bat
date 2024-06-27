setlocal

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%

python -m build ^
       --no-isolation ^
       --wheel ^
       %SRC_DIR%