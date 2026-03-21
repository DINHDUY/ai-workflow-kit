@echo off
:: Stages all changes and creates a commit with the provided message.
:: Message must follow Commitizen format: <type>[optional scope]: <description>
:: Usage: 02-commit.bat <commit-message>

if "%~1"=="" (
    echo Usage: %~n0 ^<commit-message^> 1>&2
    exit /b 1
)

call :validate_commitizen "%~1"
if errorlevel 1 exit /b 1

git add -A
if errorlevel 1 (
    echo Error: git add failed. 1>&2
    exit /b 1
)
git commit -m "%~1"
if errorlevel 1 (
    echo Error: git commit failed. 1>&2
    exit /b 1
)
exit /b 0

:validate_commitizen
echo %~1 | findstr /r "^feat[:(] ^fix[:(] ^docs[:(] ^style[:(] ^refactor[:(] ^perf[:(] ^test[:(] ^build[:(] ^ci[:(] ^chore[:(] ^revert[:(]" >nul 2>&1
if errorlevel 1 (
    echo Error: commit message does not follow Commitizen format. 1>&2
    echo   Expected: ^<type^>[optional scope]: ^<description^> 1>&2
    echo   Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert 1>&2
    echo   Example: feat^(auth^): add OAuth2 login 1>&2
    exit /b 1
)
exit /b 0
