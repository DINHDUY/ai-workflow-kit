@echo off
:: Resolves the upstream default branch (HEAD branch) from the remote.
:: Prints the branch name to stdout; falls back to "main" if unresolvable.

git fetch origin >nul 2>&1

set BASE_BRANCH=
for /f "tokens=3" %%i in ('git remote show origin 2^>nul ^| findstr "HEAD branch"') do set BASE_BRANCH=%%i

if "%BASE_BRANCH%"=="" (
    echo Warning: could not resolve remote HEAD branch -- falling back to 'main'. 1>&2
    set BASE_BRANCH=main
)

echo %BASE_BRANCH%
