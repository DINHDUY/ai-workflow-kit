@echo off
:: Prints the log of commits on HEAD that are not yet in origin/<base-branch>.
:: Output is used as the PR body and to derive the squash commit message.
:: Usage: 04-collect-commits.bat <base-branch>

if "%~1"=="" (
    echo Usage: %~n0 ^<base-branch^> 1>&2
    exit /b 1
)

git log "origin/%~1..HEAD" --pretty=format:"%%h %%s%%n%%b" --no-merges
