# ファイルリストから個別のClaude Codeコマンドを生成するスクリプト
# 生成されたコマンドを手動で実行したり、バッチファイルとして保存できます

param(
    [string]$FileListPath = ".\file-list.txt",
    [string]$PromptTemplatePath = ".\migration-prompt-template.txt",
    [string]$OutputBatchPath = ".\run-migrations.bat"
)

# ファイルの存在確認
if (-not (Test-Path $FileListPath)) {
    Write-Error "ファイルリストが見つかりません: $FileListPath"
    exit 1
}

if (-not (Test-Path $PromptTemplatePath)) {
    Write-Error "プロンプトテンプレートが見つかりません: $PromptTemplatePath"
    exit 1
}

# プロンプトテンプレートを読み込み
$promptTemplate = Get-Content -Path $PromptTemplatePath -Raw -Encoding UTF8

# ファイルリストを読み込み（空行とコメント行を除外）
$fileList = Get-Content -Path $FileListPath -Encoding UTF8 |
    Where-Object { $_.Trim() -ne "" -and -not $_.Trim().StartsWith("#") }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Batch Command Generator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "処理ファイル数: $($fileList.Count)" -ForegroundColor Green
Write-Host ""

# バッチコマンドを格納
$batchCommands = @()
$batchCommands += "@echo off"
$batchCommands += "REM GAE Migration Batch Commands"
$batchCommands += "REM Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$batchCommands += ""
$batchCommands += "setlocal enabledelayedexpansion"
$batchCommands += ""

# 一時ディレクトリ作成
$tempDir = ".\migration-prompts"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$fileIndex = 0
foreach ($file in $fileList) {
    $fileIndex++

    Write-Host "[$fileIndex/$($fileList.Count)] コマンド生成: $file" -ForegroundColor Cyan

    # プロンプトを組み立て
    $fullPrompt = $promptTemplate + "`n`nあなたが処理するファイルは: $file"

    # 一時ファイルにプロンプトを保存
    $promptFileName = "prompt-$fileIndex.txt"
    $promptFilePath = Join-Path $tempDir $promptFileName
    $fullPrompt | Out-File -FilePath $promptFilePath -Encoding UTF8

    # バッチコマンドを追加
    $batchCommands += "echo [$fileIndex/$($fileList.Count)] Processing: $file"
    $batchCommands += "type `"$promptFilePath`" | claude-code --no-confirm"
    $batchCommands += "if errorlevel 1 ("
    $batchCommands += "    echo ERROR: Failed to process $file"
    $batchCommands += "    pause"
    $batchCommands += ")"
    $batchCommands += "echo."
    $batchCommands += ""
}

$batchCommands += "echo ========================================"
$batchCommands += "echo All migrations completed!"
$batchCommands += "echo ========================================"
$batchCommands += "pause"

# バッチファイルに保存
$batchCommands | Out-File -FilePath $OutputBatchPath -Encoding Default

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "バッチファイルを生成しました！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "出力ファイル: $OutputBatchPath" -ForegroundColor Yellow
Write-Host "プロンプト保存先: $tempDir" -ForegroundColor Yellow
Write-Host ""
Write-Host "実行方法:" -ForegroundColor Cyan
Write-Host "  $OutputBatchPath" -ForegroundColor White
Write-Host ""
