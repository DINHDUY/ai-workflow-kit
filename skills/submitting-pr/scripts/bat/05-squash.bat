@echo off
:: Soft-resets to origin/<base-branch> and re-commits with a single squash message.
:: No-ops when only one commit exists ahead of the base (squash not needed).
:: Message must follow Commitizen format: <type>[optional scope]: <description>
:: Usage: 05-squash.bat <base-branch> <squash-message>

if "%~1"=="" (
    echo Usage: %~n0 ^<base-branch^> ^<squash-message^> 1>&2
    exit /b 1
)
if "%~2"=="" (
    echo Usage: %~n0 ^<base-branch^> ^<squash-message^> 1>&2
    exit /b 1
)

for /f "tokens=*" %%i in ('git rev-list --count "origin/%~1..HEAD"') do set COMMIT_COUNT=%%i
if "%COMMIT_COUNT%"=="" (
    echo Error: could not count commits against origin/%~1. Verify the base branch is valid. 1>&2
    exit /b 1
)

if %COMMIT_COUNT% LEQ 1 (
    echo Only %COMMIT_COUNT% commit(s) ahead of origin/%~1 -- squash not needed.
    exit /b 0
)

call :validate_commitizen "%~2"
if errorlevel 1 exit /b 1

git reset --soft "origin/%~1"
if errorlevel 1 (
    echo Error: git reset --soft failed. Repository state unchanged. 1>&2
    exit /b 1
)
git commit -m "%~2"
if errorlevel 1 (
    echo Error: commit failed after reset. Run: git commit -m "%~2" to complete manually. 1>&2
    exit /b 1
)
echo Squashed %COMMIT_COUNT% commit(s) into one.
exit /b 0

:validate_commitizen
echo %~1 | findstr /r "^feat[:(] ^fix[:(] ^docs[:(] ^style[:(] ^refactor[:(] ^perf[:(] ^test[:(] ^build[:(] ^ci[:(] ^chore[:(] ^revert[:(]" >nul 2>&1
if errorlevel 1 (
    echo Error: squash message does not follow Commitizen format. 1>&2
    echo   Expected: ^<type^>[optional scope]: ^<description^> 1>&2
    echo   Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert 1>&2
    echo   Example: feat: add dark mode toggle 1>&2
    exit /b 1
)
exit /b 0
