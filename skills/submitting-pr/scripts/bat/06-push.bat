@echo off
:: Pushes the current branch to origin.
:: Pass --force to use --force-with-lease (required after a squash).
:: Refuses to push (or force-push) to main or master.
:: Usage: 06-push.bat [--force]

for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i

if "%BRANCH%"=="main" (
    echo Error: refusing to push to 'main'. Switch to a feature branch first. 1>&2
    exit /b 1
)
if "%BRANCH%"=="master" (
    echo Error: refusing to push to 'master'. Switch to a feature branch first. 1>&2
    exit /b 1
)

if "%~1"=="--force" (
    git push --force-with-lease origin HEAD
) else (
    git push -u origin HEAD
)
