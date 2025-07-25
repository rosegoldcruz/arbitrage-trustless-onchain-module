# 🔒 ATOM Security Check Script
# Verifies no environment files are in the repository

Write-Host "🔍 ATOM Security Check - Environment File Scanner" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

$envPatterns = @(
    "*.env*",
    "*ENV*", 
    "*environment*",
    "*ENVIRONMENT*",
    "config.json",
    "secrets.*",
    "credentials.*",
    "*key*",
    "*secret*",
    "*password*",
    "*token*",
    "*auth*",
    "*private*"
)

$foundFiles = @()
$rootPath = Split-Path -Parent $PSScriptRoot

Write-Host "🔍 Scanning for environment files..." -ForegroundColor Yellow

foreach ($pattern in $envPatterns) {
    $files = Get-ChildItem -Path $rootPath -Recurse -Name $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        # Skip allowed files
        if ($file -notmatch "next-env\.d\.ts|node_modules|\.git|security-check\.ps1|ENVIRONMENT_SETUP\.md") {
            $foundFiles += $file
        }
    }
}

if ($foundFiles.Count -eq 0) {
    Write-Host "✅ SECURITY CHECK PASSED" -ForegroundColor Green
    Write-Host "   No environment files found in repository" -ForegroundColor Green
    Write-Host "   Repository is secure for Git commits" -ForegroundColor Green
} else {
    Write-Host "❌ SECURITY CHECK FAILED" -ForegroundColor Red
    Write-Host "   Found potentially sensitive files:" -ForegroundColor Red
    foreach ($file in $foundFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    Write-Host "   Please remove these files before committing!" -ForegroundColor Red
    exit 1
}

# Check Git status for staged env files
Write-Host ""
Write-Host "🔍 Checking Git staging area..." -ForegroundColor Yellow

$gitStatus = git status --porcelain 2>$null
if ($gitStatus) {
    $envInGit = $gitStatus | Where-Object { $_ -match "env|ENV|secret|password|credential|key|token|auth|private" }
    if ($envInGit) {
        Write-Host "❌ WARNING: Potential sensitive files in Git staging:" -ForegroundColor Red
        foreach ($line in $envInGit) {
            Write-Host "   $line" -ForegroundColor Red
        }
    } else {
        Write-Host "✅ Git staging area is clean" -ForegroundColor Green
    }
} else {
    Write-Host "✅ No files staged for commit" -ForegroundColor Green
}

Write-Host ""
Write-Host "🛡️ Security check complete!" -ForegroundColor Cyan
Write-Host "   Remember: NEVER commit environment files!" -ForegroundColor Yellow
