@echo off
echo ========================================
echo  劳动法AI维权助手 - 打包工具
echo ========================================
echo.

REM 检查前端静态文件
if not exist "..\web-app\out\" (
    echo [错误] 前端静态文件不存在，请先构建前端:
    echo   cd ..\web-app ^&^& npm run build
    pause
    exit /b 1
)

echo [1/3] 安装 PyInstaller...
pip install pyinstaller -q

echo [2/3] 开始打包（预计 3-5 分钟）...
pyinstaller --clean labor-law-ai.spec

echo [3/3] 打包完成！
echo.
echo 输出文件: dist\劳动法AI维权助手.exe
echo 启动方式: 双击 exe 或运行 dist\劳动法AI维权助手.exe
pause
