setlocal

@REM This launcher script is only necessary to rename the wheel to have the correct platform tag
@REM Unlike auditwheel on Linux, delvewheel doesn't automatically rename Wheels.

set THIS_FILE_DIR=%~dp0
set SRC_DIR=%THIS_FILE_DIR%
FOR /F "tokens=* USEBACKQ" %%F IN (`python -c "import sysconfig; print(sysconfig.get_platform())"`) DO (
SET PLAT_NAME=%%F
)
@REM SET PLAT_NAME=win-amd64

@REM https://stackoverflow.com/a/75015323/20785734
python -m build ^
       --no-isolation ^
       --wheel ^
       -C="--global-option=--plat-name" -C="--global-option=%PLAT_NAME%" ^
       %SRC_DIR%