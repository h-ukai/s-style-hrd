# GAE Migration Sequential Script
# Process files one by one and pass results to next agent

param(
    [string]$FileListPath = ".\file-list.txt",
    [string]$PromptTemplatePath = ".\migration-prompt-template-v2.txt",
    [string]$MigrationStateFile = ".\GAE_MIGRATION_STATE.md",
    [string]$ProgressStateFile = ".\migration-progress.md",
    [string]$SourceDir = ".\src",
    [string]$OutputDir = ".\migration-src"
)

# Check file existence
if (-not (Test-Path $FileListPath)) {
    Write-Error "File list not found: $FileListPath"
    exit 1
}

if (-not (Test-Path $PromptTemplatePath)) {
    Write-Error "Prompt template not found: $PromptTemplatePath"
    exit 1
}

if (-not (Test-Path $MigrationStateFile)) {
    Write-Error "Migration state file not found: $MigrationStateFile"
    exit 1
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Load prompt template
$promptTemplate = Get-Content -Path $PromptTemplatePath -Raw -Encoding UTF8

# Load file list (exclude empty lines and comments)
$fileList = Get-Content -Path $FileListPath -Encoding UTF8 |
    Where-Object { $_.Trim() -ne "" -and -not $_.Trim().StartsWith("#") }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GAE Migration Sequential Processor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Files to process: $($fileList.Count)" -ForegroundColor Green
Write-Host "Output directory: $OutputDir" -ForegroundColor Green
Write-Host ""

# Create log directory
$logDir = ".\migration-logs\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
Write-Host "Log directory: $logDir" -ForegroundColor Yellow
Write-Host ""

# Initialize progress state file
$progressHeader = @"
# Migration Progress

**Start time**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Total files**: $($fileList.Count)

---

## Completed Files

"@

$progressHeader | Out-File -FilePath $ProgressStateFile -Encoding UTF8

# Record processing results
$results = @()
$fileIndex = 0

foreach ($file in $fileList) {
    $fileIndex++

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "[$fileIndex/$($fileList.Count)] Processing: $file" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # Source file path
    $sourceFilePath = Join-Path $SourceDir $file

    # Output file path (maintain directory structure)
    $outputFilePath = Join-Path $OutputDir $file
    $outputFileDir = Split-Path -Path $outputFilePath -Parent

    # Create output directory
    if (-not (Test-Path $outputFileDir)) {
        New-Item -ItemType Directory -Path $outputFileDir -Force | Out-Null
    }

    # Check source file existence
    if (-not (Test-Path $sourceFilePath)) {
        Write-Host "ERROR: Source file not found: $sourceFilePath" -ForegroundColor Red

        # Record to progress state file
        $errorRecord = @"

### [X] $file
- **Status**: Error (File not found)
- **Time**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Source**: $sourceFilePath

"@
        $errorRecord | Out-File -FilePath $ProgressStateFile -Append -Encoding UTF8

        continue
    }

    # Build prompt
    $fullPrompt = @"
$promptTemplate

---

## Target File Information

**Target file**: $file
**Source path**: $sourceFilePath
**Output path**: $outputFilePath

## Important Additional Instructions

1. **Output destination**
   - Read source file: $sourceFilePath
   - Save migration result to: $outputFilePath
   - Use Write tool to save as new file

2. **Dependency processing**
   - Identify project modules imported by this file
   - Record unprocessed dependencies in migration-progress.md
   - Add comment to dependent module files noting the reference

3. **Result recording**
   - After completion, append to migration-progress.md with Edit tool
   - Format:
     ### [OK] $file
     - **Status**: Completed
     - **Time**: [current time]
     - **Dependencies**: [list of dependent modules]
     - **Notes**: [handover items for next agent if any]

4. **Current progress**
   - Progress: $fileIndex / $($fileList.Count) files
   - Progress state file: $ProgressStateFile

Start migration now.
"@

    # Save prompt to temporary file
    $tempPromptFile = Join-Path $logDir "prompt-$fileIndex-$(Split-Path -Leaf $file).txt"
    $fullPrompt | Out-File -FilePath $tempPromptFile -Encoding UTF8

    # Log file name
    $logFile = Join-Path $logDir "log-$fileIndex-$($file.Replace('/', '-').Replace('\', '-')).txt"

    Write-Host "Prompt: $tempPromptFile" -ForegroundColor DarkGray
    Write-Host "Log: $logFile" -ForegroundColor DarkGray
    Write-Host ""

    # Execute Claude Code
    try {
        Write-Host "Starting Claude Code..." -ForegroundColor Yellow

        # Skip confirmations with environment variables
        $env:CLAUDE_NO_CONFIRM = "1"
        $env:ANTHROPIC_AUTO_APPROVE = "true"

        # Automatically answer yes to all confirmations
        $yesResponses = "y`ny`ny`ny`ny`ny`ny`ny`ny`ny`ny`n"
        $output = $yesResponses | claude-code --no-confirm -f $tempPromptFile 2>&1 | Tee-Object -FilePath $logFile

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Completed: $file" -ForegroundColor Green

            $results += @{
                File = $file
                Index = $fileIndex
                Success = $true
                Time = Get-Date
            }
        } else {
            Write-Host "[X] Failed: $file (Exit Code: $LASTEXITCODE)" -ForegroundColor Red

            $results += @{
                File = $file
                Index = $fileIndex
                Success = $false
                ExitCode = $LASTEXITCODE
                Time = Get-Date
            }

            # Record to progress state file
            $failRecord = @"

### [X] $file
- **Status**: Failed
- **Time**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Exit code**: $LASTEXITCODE
- **Log**: $logFile

"@
            $failRecord | Out-File -FilePath $ProgressStateFile -Append -Encoding UTF8
        }

    } catch {
        Write-Host "[X] Exception: $file" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red

        $results += @{
            File = $file
            Index = $fileIndex
            Success = $false
            Error = $_.Exception.Message
            Time = Get-Date
        }

        # Record to progress state file
        $exceptionRecord = @"

### [X] $file
- **Status**: Exception
- **Time**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Error**: $($_.Exception.Message)

"@
        $exceptionRecord | Out-File -FilePath $ProgressStateFile -Append -Encoding UTF8
    }

    # Wait a bit before next file (reduce load from continuous startup)
    if ($fileIndex -lt $fileList.Count) {
        Write-Host ""
        Write-Host "Waiting 3 seconds before next file..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 3
    }
}

# Append summary to progress state file
$successCount = ($results | Where-Object { $_.Success }).Count
$failCount = $results.Count - $successCount

$summary = @"

---

## Summary

- **Completion time**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Success**: $successCount / $($results.Count)
- **Failed**: $failCount / $($results.Count)
- **Log directory**: $logDir

"@

$summary | Out-File -FilePath $ProgressStateFile -Append -Encoding UTF8

# Display result summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Success: $successCount / $($results.Count)" -ForegroundColor Green
Write-Host "Failed: $failCount / $($results.Count)" -ForegroundColor Red
Write-Host ""
Write-Host "Progress file: $ProgressStateFile" -ForegroundColor Yellow
Write-Host "Log directory: $logDir" -ForegroundColor Yellow
Write-Host ""

# Display failed files
if ($failCount -gt 0) {
    Write-Host "Failed files:" -ForegroundColor Red
    $results | Where-Object { -not $_.Success } | ForEach-Object {
        Write-Host "  - $($_.File)" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "Processing completed!" -ForegroundColor Green
