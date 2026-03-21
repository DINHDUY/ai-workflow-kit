@echo off
:: Creates a pull request. Platform is auto-detected from the git remote URL:
::   github.com                         -> gh CLI
::   dev.azure.com / *.visualstudio.com -> az repos pr create  (ADO Services)
::   any other host                     -> REST API + Windows Integrated Auth (ADO Server)
:: Usage: 07-create-pr.bat <base-branch> <title> <body>

setlocal

if "%~1"=="" (
    echo Usage: %~n0 ^<base-branch^> ^<title^> [body] 1>&2
    exit /b 1
)
if "%~2"=="" (
    echo Usage: %~n0 ^<base-branch^> ^<title^> [body] 1>&2
    exit /b 1
)

set "BASE=%~1"
set "TITLE=%~2"
set "BODY=%~3"

for /f "tokens=*" %%i in ('git remote get-url origin 2^>nul') do set "REMOTE_URL=%%i"
if "%REMOTE_URL%"=="" (
    echo Error: no remote 'origin' configured. 1>&2
    exit /b 1
)

for /f "tokens=*" %%i in ('git branch --show-current') do set "SOURCE_BRANCH=%%i"

:: --- Detect platform ---
echo %REMOTE_URL% | findstr /i "github.com" >nul 2>&1
if not errorlevel 1 goto :github

echo %REMOTE_URL% | findstr /i "dev.azure.com visualstudio.com" >nul 2>&1
if not errorlevel 1 goto :ado_services

goto :ado_server


:: -------------------------------------------------------------------------
:github
:: Uses the gh CLI (https://cli.github.com)
where gh >nul 2>&1
if errorlevel 1 (
    echo Error: gh CLI not found. Install with: winget install GitHub.cli 1>&2
    exit /b 1
)

set "BODY_FILE=%TEMP%\pr-body-%RANDOM%.tmp"
echo(%BODY%>"%BODY_FILE%"
gh pr create --base "%BASE%" --title "%TITLE%" --body-file "%BODY_FILE%"
set "RC=%ERRORLEVEL%"
del "%BODY_FILE%"
if %RC% NEQ 0 (
    echo If a PR already exists for this branch, view it with: gh pr view --web 1>&2
)
exit /b %RC%


:: -------------------------------------------------------------------------
:ado_services
:: Uses az repos pr create (azure-devops extension) for Azure DevOps Services.
where az >nul 2>&1
if errorlevel 1 (
    echo Error: Azure CLI not found. Install with: winget install Microsoft.AzureCLI 1>&2
    exit /b 1
)

az repos pr create ^
    --source-branch "%SOURCE_BRANCH%" ^
    --target-branch "%BASE%" ^
    --title "%TITLE%" ^
    --description "%BODY%" ^
    --detect true ^
    --output table
exit /b %ERRORLEVEL%


:: -------------------------------------------------------------------------
:ado_server
:: Azure DevOps Server (on-premises) does not support az repos pr create.
:: Use the REST API with Windows Integrated Authentication (NTLM/Kerberos).
:: Remote URL format: https://<host>/<collection>/<project>/_git/<repo>

set "BODY_FILE=%TEMP%\pr-body-%RANDOM%.tmp"
set "PS_FILE=%TEMP%\adopr-%RANDOM%.ps1"
echo(%BODY%>"%BODY_FILE%"

set "ADO_REMOTE=%REMOTE_URL%"
set "ADO_SOURCE=%SOURCE_BRANCH%"
set "ADO_BASE=%BASE%"
set "ADO_TITLE=%TITLE%"
set "ADO_BODY_FILE=%BODY_FILE%"

(
echo $remote   = $env:ADO_REMOTE
echo $source   = $env:ADO_SOURCE
echo $base     = $env:ADO_BASE
echo $title    = $env:ADO_TITLE
echo $body     = Get-Content $env:ADO_BODY_FILE -Raw
echo $repoName = ($remote -split '/_git/')[1]
echo $projBase = $remote -replace '/_git/.*$', ''
echo $apiUrl   = "$projBase/_apis/git/repositories/$repoName/pullrequests?api-version=5.0"
echo $payload  = @{
echo     title         = $title
echo     description   = $body
echo     sourceRefName = "refs/heads/$source"
echo     targetRefName = "refs/heads/$base"
echo } ^| ConvertTo-Json
echo try {
echo     $r   = Invoke-RestMethod -Uri $apiUrl -Method Post -Body $payload -ContentType 'application/json' -UseDefaultCredentials
echo     $url = "$remote/pullrequest/$($r.pullRequestId)"
echo     Write-Output "PR created: $url"
echo } catch {
echo     $msg = $_.Exception.Response.StatusCode
echo     if ($msg -eq 409^) { Write-Output "A PR already exists for this branch: $projBase/_git/$repoName/pullrequests" }
echo     else { Write-Error $_.Exception.Message; exit 1 }
echo }
)>"%PS_FILE%"

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_FILE%"
set "RC=%ERRORLEVEL%"
del "%BODY_FILE%"
del "%PS_FILE%"
exit /b %RC%
