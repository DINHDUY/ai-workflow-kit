@echo off
:: Prints the current branch name and working-tree status.
:: Exits non-zero if on a protected branch (main or master).
:: Outputs machine-parseable keys so callers can branch on results.

for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
echo current-branch: %BRANCH%

if "%BRANCH%"=="" (
    echo Error: not on a branch (detached HEAD). Check out a feature branch before submitting a PR. 1>&2
    exit /b 1
)

if "%BRANCH%"=="main" (
    echo Error: current branch is 'main'. Switch to a feature branch before submitting a PR. 1>&2
    exit /b 1
)
if "%BRANCH%"=="master" (
    echo Error: current branch is 'master'. Switch to a feature branch before submitting a PR. 1>&2
    exit /b 1
)

set STATUS_FILE=%TEMP%\git-status-%RANDOM%.tmp
git status --short > "%STATUS_FILE%" 2>&1

for %%F in ("%STATUS_FILE%") do set SIZE=%%~zF
if %SIZE% EQU 0 (
    echo working-tree: clean
) else (
    echo working-tree: dirty
    type "%STATUS_FILE%"
)
del "%STATUS_FILE%"
