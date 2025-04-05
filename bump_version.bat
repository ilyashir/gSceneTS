@echo off
echo Обновление версии проекта gSceneTS
if "%1"=="" (
    echo Использование: bump_version.bat [major^|minor^|patch]
    exit /b 1
)

python scripts/bump_version.py %1
if errorlevel 1 (
    echo Произошла ошибка при обновлении версии!
    exit /b 1
)

echo Версия успешно обновлена! 
echo Не забудьте зафиксировать изменения: git push --tags 