# Full API Test Script (PowerShell)
$ErrorActionPreference = "Continue"
$BASE = "http://localhost:8000"
$PASS = 0
$FAIL = 0
$FAILURES = @()

function Test-API {
    param($Name, $Method, $Path, $Body, $ExpectSuccess=$true)
    $url = "$BASE$Path"
    try {
        if ($Body) {
            $json = $Body | ConvertTo-Json -Compress
            $resp = Invoke-RestMethod -Uri $url -Method $Method -Body $json -ContentType "application/json" -TimeoutSec 60
        } else {
            $resp = Invoke-RestMethod -Uri $url -Method $Method -TimeoutSec 60
        }
        if ($ExpectSuccess) {
            if ($resp.success) {
                Write-Host "  PASS: $Name"
                $script:PASS++
            } else {
                Write-Host "  FAIL: $Name - success=False"
                $script:FAIL++
                $script:FAILURES += $Name
            }
        } else {
            Write-Host "  FAIL: $Name - expected failure but got success"
            $script:FAIL++
            $script:FAILURES += $Name
        }
        return $resp
    } catch {
        if (-not $ExpectSuccess) {
            Write-Host "  PASS: $Name - expected failure"
            $script:PASS++
        } else {
            Write-Host "  FAIL: $Name - $_"
            $script:FAIL++
            $script:FAILURES += $Name
        }
        return $null
    }
}

function Check-Field {
    param($Result, $Name, $Path, $Label)
    $val = $Result
    foreach ($p in $Path) {
        if ($val -is [System.Collections.IDictionary]) {
            $val = $val[$p]
        } else { $val = $null; break }
    }
    if ($val -and (-not ($val -is [Array]) -or $val.Count -gt 0)) {
        Write-Host "  PASS: $Name"
        $script:PASS++
    } else {
        Write-Host "  FAIL: $Name - $Label is empty/null"
        $script:FAIL++
        $script:FAILURES += $Name
    }
}

# ============ 1. Health ============
Write-Host "`n[1] Health Check"
Test-API "GET /api/health" "GET" "/api/health"
Test-API "GET / (root)" "GET" "/"

# ============ 2. Content Factory ============
Write-Host "`n[2] Content Factory"

$r = Test-API "GET /api/content/templates" "GET" "/api/content/templates"
if ($r) { Check-Field $r "templates data" @("data") "data" }

Write-Host "  ... Generating script via Ollama (may take 10-30s)..."
$r = Test-API "POST /api/content/generate-script" "POST" "/api/content/generate-script" @{topic="XianYang Spring"; style="探店"}
if ($r) {
    Check-Field $r "script title" @("data","title") "title"
    Check-Field $r "script scenes" @("data","scenes") "scenes"
}

Test-API "GET /api/content/media" "GET" "/api/content/media"

Write-Host "  ... Composing video via Ollama+FFmpeg (may take 15-40s)..."
$r = Test-API "POST /api/content/compose-video" "POST" "/api/content/compose-video" @{topic="XianYang Qianling"; template_id=1; style="航拍"}
$taskId = $null
if ($r) {
    $taskId = $r.data.task_id
    Check-Field $r "compose task_id" @("data","task_id") "task_id"
    Check-Field $r "compose output_path" @("data","output_path") "output_path"
    $outPath = $r.data.output_path
    if (Test-Path $outPath) {
        $size = (Get-Item $outPath).Length
        Write-Host "  PASS: output file exists ($size bytes)"
        $script:PASS++
    } else {
        Write-Host "  FAIL: output file missing: $outPath"
        $script:FAIL++
        $script:FAILURES += "output file check"
    }
}

Test-API "GET /api/content/tasks" "GET" "/api/content/tasks"

# ============ 3. Digital Human ============
Write-Host "`n[3] Digital Human"
Test-API "GET /api/content/digital-human/avatars" "GET" "/api/content/digital-human/avatars"

Write-Host "  ... Generating digital human video (may take 5-15s)..."
$r = Test-API "POST /api/content/digital-human/generate" "POST" "/api/content/digital-human/generate" @{avatar_id="avatar_1"; script="Weather alert for XianYang"}
if ($r) {
    Check-Field $r "digital-human task_id" @("data","task_id") "task_id"
    $dhOut = $r.data.output_path
    if (Test-Path $dhOut) {
        Write-Host "  PASS: digital-human file exists ($((Get-Item $dhOut).Length) bytes)"
        $script:PASS++
    } else {
        Write-Host "  FAIL: digital-human file missing: $dhOut"
        $script:FAIL++
        $script:FAILURES += "digital-human file"
    }
}

# ============ 4. Video Download ============
Write-Host "`n[4] Video Download"
if ($taskId) {
    Test-API "GET /api/content/tasks/$taskId/download" "GET" "/api/content/tasks/$taskId/download"
}
Test-API "GET non-existent download (404)" "GET" "/api/content/tasks/99999/download" -ExpectSuccess:$false

# ============ 5. Distribution ============
Write-Host "`n[5] Distribution Network"
Test-API "GET /api/accounts" "GET" "/api/accounts"
Test-API "POST /api/accounts" "POST" "/api/accounts" @{name="TestAccount"; platform="抖音"; group_name="Test"; followers=100}
Test-API "PUT /api/accounts/1" "PUT" "/api/accounts/1" @{followers=99999}
Test-API "PUT non-existent (404)" "PUT" "/api/accounts/99999" @{followers=1} -ExpectSuccess:$false

# Clean up
$accs = Test-API "GET accounts for cleanup" "GET" "/api/accounts"
if ($accs) {
    foreach ($a in $accs.data) {
        if ($a.name -eq "TestAccount") {
            Test-API "DELETE /api/accounts/$($a.id)" "DELETE" "/api/accounts/$($a.id)"
        }
    }
}

$futureTime = (Get-Date).AddHours(1).ToString("o")
Test-API "POST schedule-publish" "POST" "/api/accounts/schedule-publish" @{account_id=1; content_title="Test"; scheduled_at=$futureTime}
Test-API "POST bad date (400)" "POST" "/api/accounts/schedule-publish" @{account_id=1; content_title="Bad"; scheduled_at="not-a-date"} -ExpectSuccess:$false
Test-API "GET publish-logs" "GET" "/api/accounts/publish-logs"

Test-API "GET /api/reports/overview" "GET" "/api/reports/overview"
Test-API "GET /api/reports/anomalies" "GET" "/api/reports/anomalies"
Test-API "GET /api/reports/rankings" "GET" "/api/reports/rankings"

# ============ 6. Conversion ============
Write-Host "`n[6] Conversion"
Write-Host "  ... AI chat (may take 5-15s)..."
$r = Test-API "POST chat/scenic" "POST" "/api/chat/ask" @{message="What is Qianling?"; session_id="t1"}
$r2 = Test-API "POST chat/booking" "POST" "/api/chat/ask" @{message="I want to book tickets"; session_id="t2"}
if ($r2) { Check-Field $r2 "booking intent" @("data","has_booking_intent") "has_booking_intent" }

Test-API "GET chat/history/t1" "GET" "/api/chat/history/t1"
Test-API "GET chat/history/nonexistent" "GET" "/api/chat/history/nonexistent"

Test-API "GET /api/analytics/funnel" "GET" "/api/analytics/funnel"
Test-API "GET /api/analytics/attribution" "GET" "/api/analytics/attribution"
Test-API "GET /api/analytics/roi" "GET" "/api/analytics/roi"

# ============ 7. Insight ============
Write-Host "`n[7] Insight"
Test-API "GET /api/insight/profiles" "GET" "/api/insight/profiles"
Test-API "POST adopt topic" "POST" "/api/insight/topics/adopt" @{title="Test"; reason="T"; audience="T"; publish_time="Fri"; score=80}

# ============ 8. Dashboard ============
Write-Host "`n[8] Dashboard"
Test-API "GET /api/dashboard/summary" "GET" "/api/dashboard/summary"
Test-API "GET /api/dashboard/trends" "GET" "/api/dashboard/trends"

# ============ 9. Frontend Proxy ============
Write-Host "`n[9] Frontend Proxy"
try {
    $resp = Invoke-RestMethod -Uri "http://localhost:3000/api/health" -TimeoutSec 5
    if ($resp.status -eq "ok") {
        Write-Host "  PASS: Vite proxy works"
        $script:PASS++
    } else {
        Write-Host "  FAIL: Vite proxy unexpected"
        $script:FAIL++
    }
} catch {
    Write-Host "  FAIL: Vite proxy error: $_"
    $script:FAIL++
    $script:FAILURES += "Vite proxy"
}

# ============ Results ============
Write-Host "`n" + ("=" * 60)
$total = $PASS + $FAIL
Write-Host "  Total: $total  |  PASS: $PASS  |  FAIL: $FAIL"
if ($FAILURES.Count -gt 0) {
    Write-Host "`n  Failures:"
    foreach ($f in $FAILURES) { Write-Host "    - $f" }
} else {
    Write-Host "  All tests passed!"
}
Write-Host ("=" * 60)

if ($FAIL -gt 0) { exit 1 }
