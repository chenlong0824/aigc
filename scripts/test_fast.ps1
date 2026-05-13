$PASS=0; $FAIL=0; $B="http://localhost:8000"
$tests = @(
    @{N="01-health"; M="GET"; P="/api/health"},
    @{N="02-root"; M="GET"; P="/"},
    @{N="03-templates"; M="GET"; P="/api/content/templates"},
    @{N="04-media"; M="GET"; P="/api/content/media"},
    @{N="05-tasks"; M="GET"; P="/api/content/tasks"},
    @{N="06-avatars"; M="GET"; P="/api/content/digital-human/avatars"},
    @{N="07-accounts"; M="GET"; P="/api/accounts"},
    @{N="08-publish-logs"; M="GET"; P="/api/accounts/publish-logs"},
    @{N="09-reports-overview"; M="GET"; P="/api/reports/overview"},
    @{N="10-reports-anomalies"; M="GET"; P="/api/reports/anomalies"},
    @{N="11-reports-rankings"; M="GET"; P="/api/reports/rankings"},
    @{N="12-chat-history"; M="GET"; P="/api/chat/history/test"},
    @{N="13-funnel"; M="GET"; P="/api/analytics/funnel"},
    @{N="14-attribution"; M="GET"; P="/api/analytics/attribution"},
    @{N="15-roi"; M="GET"; P="/api/analytics/roi"},
    @{N="16-insight-profiles"; M="GET"; P="/api/insight/profiles"},
    @{N="17-dashboard-summary"; M="GET"; P="/api/dashboard/summary"},
    @{N="18-dashboard-trends"; M="GET"; P="/api/dashboard/trends"},
    @{N="19-404-account"; M="PUT"; P="/api/accounts/99999"; B='{"followers":1}'; E=$false},
    @{N="20-404-download"; M="GET"; P="/api/content/tasks/99999/download"; E=$false},
    @{N="21-400-schedule"; M="POST"; P="/api/accounts/schedule-publish"; B='{"account_id":1,"content_title":"B","scheduled_at":"not-a-date"}'; E=$false}
)

foreach ($t in $tests) {
    $expect = if ($null -eq $t.E) { $true } else { $t.E }
    try {
        $body = $t.B
        if ($body) {
            $r = Invoke-RestMethod -Uri "$B$($t.P)" -Method $t.M -Body $body -ContentType "application/json" -TimeoutSec 15
        } else {
            $r = Invoke-RestMethod -Uri "$B$($t.P)" -Method $t.M -TimeoutSec 15
        }
        if ($expect) {
            if ($r.success) { Write-Output "PASS $($t.N)"; $global:PASS++ } else { Write-Output "FAIL $($t.N) success=False"; $global:FAIL++ }
        } else { Write-Output "FAIL $($t.N) expected-fail-got-success"; $global:FAIL++ }
    } catch {
        if (-not $expect) { Write-Output "PASS $($t.N) got-error"; $global:PASS++ }
        else { Write-Output "FAIL $($t.N) $_"; $global:FAIL++ }
    }
}
Write-Output "=== Fast Tests: PASS=$PASS FAIL=$FAIL ==="
if ($FAIL -gt 0) { exit 1 }
