# GAE Migration Batch Script
# 複数のClaude Codeエージェントを起動してファイルを並列処理

param(
    [string]$FileListPath = ".\file-list.txt",
    [string]$PromptTemplatePath = ".\migration-prompt-template.txt",
    [int]$MaxParallel = 3  # 同時実行数（調整可能）
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
Write-Host "GAE Migration Batch Processor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "処理ファイル数: $($fileList.Count)" -ForegroundColor Green
Write-Host "最大同時実行数: $MaxParallel" -ForegroundColor Green
Write-Host ""

# ログディレクトリ作成
$logDir = ".\migration-logs\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
Write-Host "ログディレクトリ: $logDir" -ForegroundColor Yellow
Write-Host ""

# 処理結果を記録
$results = @()

# ファイルを並列処理
$jobs = @()
$fileIndex = 0

foreach ($file in $fileList) {
    $fileIndex++

    # 同時実行数の制限
    while ((Get-Job -State Running).Count -ge $MaxParallel) {
        Start-Sleep -Seconds 2
    }

    # 完了したジョブの結果を収集
    $completedJobs = Get-Job -State Completed
    foreach ($job in $completedJobs) {
        $jobResult = Receive-Job -Job $job
        $results += $jobResult
        Remove-Job -Job $job
    }

    Write-Host "[$fileIndex/$($fileList.Count)] 処理開始: $file" -ForegroundColor Cyan

    # プロンプトを組み立て
    $fullPrompt = $promptTemplate + "`n`nあなたが処理するファイルは: $file"

    # 一時ファイルにプロンプトを保存
    $tempPromptFile = Join-Path $logDir "prompt-$fileIndex.txt"
    $fullPrompt | Out-File -FilePath $tempPromptFile -Encoding UTF8

    # ログファイル名
    $logFile = Join-Path $logDir "log-$fileIndex-$($file.Replace('/', '-').Replace('\', '-')).txt"

    # バックグラウンドジョブで Claude Code を実行
    $job = Start-Job -ScriptBlock {
        param($prompt, $logFile, $file, $fileIndex)

        $output = @{
            File = $file
            Index = $fileIndex
            StartTime = Get-Date
            Success = $false
            Error = $null
        }

        try {
            # Claude Code を実行（プロンプトを標準入力から渡す）
            $result = $prompt | claude-code --no-confirm 2>&1 | Tee-Object -FilePath $logFile

            $output.Success = $LASTEXITCODE -eq 0
            $output.Output = $result
            $output.EndTime = Get-Date

        } catch {
            $output.Error = $_.Exception.Message
            $output.EndTime = Get-Date
        }

        return $output

    } -ArgumentList $fullPrompt, $logFile, $file, $fileIndex

    $jobs += $job
}

# 残りのジョブが完了するまで待機
Write-Host ""
Write-Host "全ジョブの完了を待機中..." -ForegroundColor Yellow

Wait-Job -Job $jobs | Out-Null

# 全ジョブの結果を収集
foreach ($job in $jobs) {
    $jobResult = Receive-Job -Job $job
    $results += $jobResult
    Remove-Job -Job $job
}

# 結果サマリーを表示
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "処理結果サマリー" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$successCount = ($results | Where-Object { $_.Success }).Count
$failCount = $results.Count - $successCount

Write-Host "成功: $successCount / $($results.Count)" -ForegroundColor Green
Write-Host "失敗: $failCount / $($results.Count)" -ForegroundColor Red
Write-Host ""

# 失敗したファイルを表示
if ($failCount -gt 0) {
    Write-Host "失敗したファイル:" -ForegroundColor Red
    $results | Where-Object { -not $_.Success } | ForEach-Object {
        Write-Host "  - $($_.File)" -ForegroundColor Red
        if ($_.Error) {
            Write-Host "    エラー: $($_.Error)" -ForegroundColor DarkRed
        }
    }
    Write-Host ""
}

# 結果をCSVで保存
$csvPath = Join-Path $logDir "results.csv"
$results | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "詳細結果: $csvPath" -ForegroundColor Yellow

Write-Host ""
Write-Host "処理完了！" -ForegroundColor Green
