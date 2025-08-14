@echo off
rem 删除dist和build文件夹
if exist "dist" (
    rmdir /s /q "dist"
    echo dist文件夹已删除
) else (
    echo dist文件夹不存在
)

if exist "build" (
    rmdir /s /q "build"
    echo build文件夹已删除
) else (
    echo build文件夹不存在
)

rem 执行pyinstaller命令
echo 正在执行pyinstaller打包...
"F:\Development\Python\project\WeTransferClient_PY\venv\Scripts\pyinstaller" WeTransferClient.spec

if errorlevel 1 (
    echo pyinstaller执行失败！
    pause
    exit /b 1
) else (
    echo pyinstaller执行成功！
    pause
)