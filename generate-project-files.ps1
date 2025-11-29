# Generate file list for PROJECT files only (exclude external libraries)
# Outputs only application-specific .py files

param(
    [string]$SourceDir = ".\src",
    [string]$OutputFile = ".\file-list-project.txt"
)

Write-Host "Scanning project Python files in: $SourceDir" -ForegroundColor Cyan

# Define external library patterns to EXCLUDE
$excludePatterns = @(
    "numpy",
    "sendgrid",
    "mapreduce",
    "gaeoauth",
    "lib\\json",
    "lib\\markdown",
    "lib\\",
    "tests?[\\/]",          # test files
    "test_",                # test files
    "_test\.py$"            # test files
)

# Get all .py files recursively
$allFiles = Get-ChildItem -Path $SourceDir -Recurse -Filter "*.py" |
    ForEach-Object { $_.FullName.Substring((Get-Item $SourceDir).FullName.Length + 1) }

# Filter out external libraries
$projectFiles = $allFiles | Where-Object {
    $file = $_
    $isExternal = $false

    foreach ($pattern in $excludePatterns) {
        if ($file -match $pattern) {
            $isExternal = $true
            break
        }
    }

    -not $isExternal
} | Sort-Object

Write-Host "Total Python files: $($allFiles.Count)" -ForegroundColor Gray
Write-Host "Project files (excluding libraries): $($projectFiles.Count)" -ForegroundColor Green
Write-Host ""

# Categorize files by type for better ordering
$configFiles = @()
$modelFiles = @()
$utilFiles = @()
$handlerFiles = @()
$mainFiles = @()
$otherFiles = @()

foreach ($file in $projectFiles) {
    $fileName = [System.IO.Path]::GetFileName($file)
    $fileLower = $file.ToLower()

    if ($fileName -eq "main.py" -or $fileName -eq "app.py") {
        $mainFiles += $file
    }
    elseif ($fileName -match "config|setting") {
        $configFiles += $file
    }
    elseif ($fileLower -match "models?[\\/]" -or $fileName -match "^model") {
        $modelFiles += $file
    }
    elseif ($fileName -match "util|helper|common|base|session|auth") {
        $utilFiles += $file
    }
    elseif ($fileName -match "handler|view|route|endpoint") {
        $handlerFiles += $file
    }
    else {
        $otherFiles += $file
    }
}

# Create ordered list (dependencies first)
$orderedFiles = @()
$orderedFiles += $configFiles | Sort-Object
$orderedFiles += $modelFiles | Sort-Object
$orderedFiles += $utilFiles | Sort-Object
$orderedFiles += $otherFiles | Sort-Object
$orderedFiles += $handlerFiles | Sort-Object
$orderedFiles += $mainFiles | Sort-Object

# Generate file list
$header = @"
# GAE Migration Project File List
# Auto-generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# Total project files: $($orderedFiles.Count)
# (External libraries excluded: numpy, sendgrid, mapreduce, etc.)
#
# Files are ordered by dependency (best effort):
# 1. Config files (setting, config)
# 2. Model files (models/)
# 3. Utility files (util, helper, common, base, session, auth)
# 4. Other application files
# 5. Handler files (handler, view, route)
# 6. Main files (main.py, app.py)

"@

$header | Out-File -FilePath $OutputFile -Encoding UTF8

foreach ($file in $orderedFiles) {
    $file | Out-File -FilePath $OutputFile -Append -Encoding UTF8
}

Write-Host "Project file list generated: $OutputFile" -ForegroundColor Green
Write-Host ""
Write-Host "File breakdown:" -ForegroundColor Yellow
Write-Host "  Config files: $($configFiles.Count)" -ForegroundColor Gray
Write-Host "  Model files: $($modelFiles.Count)" -ForegroundColor Gray
Write-Host "  Utility files: $($utilFiles.Count)" -ForegroundColor Gray
Write-Host "  Handler files: $($handlerFiles.Count)" -ForegroundColor Gray
Write-Host "  Main files: $($mainFiles.Count)" -ForegroundColor Gray
Write-Host "  Other files: $($otherFiles.Count)" -ForegroundColor Gray
Write-Host "  Total: $($orderedFiles.Count)" -ForegroundColor Green
Write-Host ""
Write-Host "Excluded patterns:" -ForegroundColor Yellow
$excludePatterns | ForEach-Object { Write-Host "  - $_" -ForegroundColor DarkGray }
