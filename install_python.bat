<# :
@echo off
setlocal
if not "%1"=="am_admin" (
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0' -ArgumentList 'am_admin'"
    exit /b
)
powershell -exec Bypass -noprofile -nologo "iex (${%~f0} | out-string)"
goto :EOF
#>

$added_to_path = $false

function Main {
    CheckAdmin
    UI
    Write-Host "Testing python" -ForegroundColor Green
    RemoveAlias
    PythonAppstore

    Add-Python-To-Path

    Write-Host "Python seems to be working now!" -ForegroundColor Green

    if ($added_to_path) {
        Write-Host "Please restart script" -ForegroundColor Green
        Read-Host "Press enter to quit"
        exit 0
    }

    Write-Host "Press enter to quit" -ForegroundColor Green -NoNewline
    Read-Host
}

function Write-Centered {
    param (
        [Parameter(Mandatory=$true)]
        [string]$Text
    )
    $console_width = $host.ui.rawui.WindowSize.Width
    $text_length = $Text.Length
    $spaces = ($console_width - $text_length) / 2
    $spaces = [math]::Round($spaces)
    $spaces = " " * $spaces
    Write-Host "$spaces$Text" -ForegroundColor Green
}

function UI {
    $banner = @"
d8888b. db    db d888888b db   db  .d88b.  d8b   db      d88888b d888888b db    db d88888b d8888b.
88  ``8D ``8b  d8' ``~~88~~' 88   88 .8P  Y8. 888o  88      88'       ``88'   ``8b  d8' 88'     88  ``8D
88oodD'  ``8bd8'     88    88ooo88 88    88 88V8o 88      88ooo      88     ``8bd8'  88ooooo 88oobY'
88~~~      88       88    88~~~88 88    88 88 V8o88      88~~~      88     .dPYb.  88~~~~~ 88``8b  
88         88       88    88   88 ``8b  d8' 88  V888      88        .88.   .8P  Y8. 88.     88 ``88.
88         YP       YP    YP   YP  ``Y88P'  VP   V8P      YP      Y888888P YP    YP Y88888P 88   YD
Made by KDot227 and Godfather
"@
    $banner_segments = $banner.Split("`n")

    $banner_segments | ForEach-Object {
        Write-Centered -Text $_
    }
}

function DownloadPython {
    Write-Host "Downloading Python" -ForegroundColor Green
    $download_ver = Invoke-WebRequest "https://www.python.org/ftp/python/" -UseBasicParsing | Select-String -Pattern '3.11.[0-9]{1,2}' -AllMatches | Select-Object -ExpandProperty Matches | Select-Object -ExpandProperty Value | Sort-Object -Descending -Unique | Select-Object -First 1
    Write-Host "Downloading version $download_ver" -ForegroundColor Green
    $download_link = "https://www.python.org/ftp/python/$download_ver/python-$download_ver-amd64.exe"
    $python_exe = "$env:TEMP\python-installer.exe"

    #Invoke-WebRequest $download_link -OutFile $python_exe -UseBasicParsing
    Start-BitsTransfer -Source $download_link -Destination $python_exe

    Write-Host "Installing Python. (This may take awhile)" -ForegroundColor Green

    Start-Process $python_exe -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Incude_pip=1" -Wait

    Write-Host "Python downloaded and Installed. Please restart script." -ForegroundColor Green
    Write-Host "Press enter to quit" -ForegroundColor Green -NoNewline
    Read-Host " " 
    exit 0
}

function PythonAppstore {
    #see if python is installed from the appstore
    $python = Get-AppxPackage -AllUsers | Where-Object {$_.Name -like "Python*"}
    if ($python) {
        Write-Host "Python is installed from the appstore. Please uninstall it and try again" -ForegroundColor Green
        Read-Host "Press enter to quit"
        exit 1
    }
}

function FindPython {
    $python = Get-Command python -ErrorAction SilentlyContinue
    #check if multiple versions of python are installed. If so, warn the user and tell them to delete one
    if ($python.Count -gt 1) {
        Write-Host "Multiple versions of python found. Please delete one" -ForegroundColor Green
        Read-Host "Press enter to quit"
        exit 1
    }
    $pattern = 'Python\d+\\python\.exe'
    if ($python -and $python.Path -match $pattern) {
        Write-Host "Found python at $($python.Path)" -ForegroundColor Green
    } else {
        $installedmaybe = Get-Package -Name "*Python 3.*" -ErrorAction SilentlyContinue
        if ($installedmaybe) {
            $python1 = Get-ChildItem -Path "$env:Programfiles" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue | Where-Object {$_.FullName -match $pattern} | Select-Object -ExpandProperty FullName
            $python2 = Get-ChildItem -Path "$env:LOCALAPPDATA" -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue | Where-Object {$_.FullName -match $pattern} | Select-Object -ExpandProperty FullName
            if ($python1 -or $python2) {
                Write-Host "Found python at '$python1' or '$python2'" -ForegroundColor Green
                if ($python1) {
                    return $python1
                } else {
                    return $python2
                }
            } else {
                Write-Host "Python not found. Downloading" -ForegroundColor Green
                DownloadPython
            }
        } else {
            Write-Host "Python not found. Downloading" -ForegroundColor Green
            DownloadPython
        }
    }
    return $python.Path
}

function RemoveAlias {
    Remove-Item $env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe -ErrorAction SilentlyContinue
    Remove-Item $env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe -ErrorAction SilentlyContinue
}

function Add-Python-To-Path {
    $path = FindPython
    $new_path = $path.Substring(0, $path.LastIndexOf("\"))
    $scripts_path = "$new_path\Scripts"
    $full_path = $env:Path
    #see if path is in full_path
    if ($full_path -match $new_path.Replace('\', '\\')) {
        Write-Host "Python is already in path" -ForegroundColor Green
        return
    }
    Backup-Environment-Variables
    $answer = Read-Host "Do you want to add python to path? (y/n) NOTE THIS SHOULD WORK BUT IF IT DOESN'T DON'T KEEP RETRYING OR IT CAN MESSUP ENV VARS"
    if ($answer -eq "y" -or $answer -eq "Y") {
        [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";$new_path;$scripts_path", "User")
        Write-Host "Added python to path" -ForegroundColor Green
        $added_to_path = $true
    }
}

function Backup-Environment-Variables {
    #output to dir of script
    $env:Path | Out-File -FilePath $PSScriptRoot\path.txt
}

function CheckAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    $isElevated = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (!$isElevated) {
        Get-Admin-Privileges
        exit 1
    }
}

function Get-Admin-Privileges {
    $path = $PSScriptRoot + "\main.ps1"
    try {
        Start-Process powershell -Verb runAs -ArgumentList "-NoExit -File $path"
    }
    catch {
        Write-Error "Failed to get admin privileges"
        Read-Host
        exit 1
    }
    
}

Main
