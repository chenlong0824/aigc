#!/usr/bin/env python3
"""
咸阳文旅 AIGC — 服务端自动化测试脚本
=====================================
用法（服务器上直接运行）:
  python scripts/test_api.py                    # 完整测试（含 AI）
  python scripts/test_api.py --fast              # 仅冒烟测试（21个 GET + 错误处理）
  python scripts/test_api.py --skip-ai           # 跳过 AI 测试（CI 无 API Key 时用）

用法（本地远程测试，需 paramiko）:
  python scripts/test_api.py --remote --host HOST --user root --password PASS

测试覆盖:
  [1] 登录认证
  [2] 健康检查 + 18个 GET 端点
  [3] 错误处理（404/400）
  [4] 数据完整性（Media 32条 + Templates + Accounts）
  [5] CRUD（创建/删除账号）
  [6] AI 功能（脚本生成 + 客服对话）

退出码: 0=全部通过, 1=存在失败
"""
import subprocess
import json
import sys
import os
import argparse
import time

# ============================================================
# Config
# ============================================================
BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")
ADMIN_USER = os.getenv("TEST_USER", "admin")
ADMIN_PASS = os.getenv("TEST_PASS", "admin123")

PASS = 0
FAIL = 0
FAILURES = []
TOKEN = ""


# ============================================================
# Helpers
# ============================================================
def curl(*args, timeout=30):
    """在服务器上执行 curl 命令，返回 (exit_code, stdout)"""
    cmd = ["curl", "-s", "--max-time", str(timeout)] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        out = result.stdout.strip()
        # 尝试从最后一行提取 HTTP 状态码（如果用了 -w "\n%{http_code}"）
        if result.returncode != 0:
            return result.returncode, out
        return 0, out
    except Exception as e:
        return -1, str(e)


def http_code(path, method="GET", body=None, timeout=30):
    """获取 HTTP 状态码"""
    args = ["-o", "/dev/null", "-w", "%{http_code}", "-X", method]
    if TOKEN and path not in ("/api/health", "/", "/api/auth/login"):
        args.extend(["-H", f"Authorization: Bearer {TOKEN}"])
    if body:
        args.extend(["-H", "Content-Type: application/json", "-d", body])
    args.append(f"{BASE_URL}{path}")
    ec, out = curl(*args, timeout=timeout)
    return out.strip()


def http_body(path, method="GET", body=None, timeout=30):
    """获取 JSON 响应体"""
    args = ["-X", method]
    if TOKEN and path not in ("/api/health", "/", "/api/auth/login"):
        args.extend(["-H", f"Authorization: Bearer {TOKEN}"])
    if body:
        args.extend(["-H", "Content-Type: application/json", "-d", body])
    args.append(f"{BASE_URL}{path}")
    ec, out = curl(*args, timeout=timeout)
    return out


def login():
    global TOKEN
    body = http_body("/api/auth/login", method="POST",
                     body=json.dumps({"username": ADMIN_USER, "password": ADMIN_PASS}))
    try:
        data = json.loads(body)
        TOKEN = data.get("access_token", "")
    except:
        TOKEN = ""
    return bool(TOKEN)


def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}{' — ' + detail if detail else ''}")
    else:
        FAIL += 1
        FAILURES.append(name)
        print(f"  [FAIL] {name}{' — ' + detail if detail else ''}")


# ============================================================
# Test Suites
# ============================================================
def step_login():
    print("\n[Login]")
    ok = login()
    test("Auth login", ok, f"token={'...' if ok else 'NONE'}")
    return ok


def step_smoke():
    print("\n[GET 冒烟测试 — 18 endpoints]")
    endpoints = [
        ("01-Health", "/api/health"),
        ("02-Root", "/"),
        ("03-Templates", "/api/content/templates"),
        ("04-Media", "/api/content/media"),
        ("05-Tasks", "/api/content/tasks"),
        ("06-Avatars", "/api/content/digital-human/avatars"),
        ("07-Accounts", "/api/accounts"),
        ("08-PublishLogs", "/api/accounts/publish-logs"),
        ("09-ReportOverview", "/api/reports/overview"),
        ("10-ReportAnomaly", "/api/reports/anomalies"),
        ("11-ReportRanking", "/api/reports/rankings"),
        ("12-ChatHistory", "/api/chat/history/test"),
        ("13-Funnel", "/api/analytics/funnel"),
        ("14-Attribution", "/api/analytics/attribution"),
        ("15-ROI", "/api/analytics/roi"),
        ("16-Profiles", "/api/insight/profiles"),
        ("17-DashSummary", "/api/dashboard/summary"),
        ("18-DashTrends", "/api/dashboard/trends"),
    ]
    for name, path in endpoints:
        code = http_code(path)
        test(name, code.startswith("2"), f"[{code}]")


def step_errors():
    print("\n[Error Handling]")
    code = http_code("/api/accounts/99999", method="PUT", body='{"followers":1}')
    test("404 Account", code.startswith("4"), f"[{code}]")

    code = http_code("/api/content/tasks/99999/download")
    test("404 Download", code.startswith("4"), f"[{code}]")

    code = http_code("/api/accounts/schedule-publish", method="POST",
                     body='{"account_id":1,"content_title":"Bad","scheduled_at":"not-a-date"}')
    test("400 Schedule", code.startswith("4"), f"[{code}]")


def step_data_validation():
    print("\n[Data Validation]")

    # Media count
    body = http_body("/api/content/media")
    try:
        data = json.loads(body)
        count = len(data.get("data", []))
        test("Media count", count == 32, f"got {count}, expected 32")
    except:
        test("Media JSON parse", False)

    # Templates count
    body = http_body("/api/content/templates")
    try:
        data = json.loads(body)
        count = len(data.get("data", []))
        test("Templates > 0", count > 0, f"got {count}")
    except:
        test("Templates JSON parse", False)

    # Accounts count
    body = http_body("/api/accounts")
    try:
        data = json.loads(body)
        count = len(data.get("data", []))
        test("Accounts > 0", count > 0, f"got {count}")
    except:
        test("Accounts JSON parse", False)

    # DB Media count (direct sqlite check)
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "db", "aigc.db")
    try:
        conn = sqlite3.connect(db_path)
        db_count = conn.execute("SELECT count(*) FROM media").fetchone()[0]
        conn.close()
        test("DB Media count", db_count == 32, f"got {db_count}, expected 32")
    except Exception as e:
        test("DB check", False, str(e)[:80])


def step_crud():
    print("\n[CRUD]")

    code = http_code("/api/accounts", method="POST",
                     body='{"name":"__TEST__","platform":"Douyin","group_name":"Test","followers":100}')
    test("Create Account", code == "200", f"[{code}]")

    body = http_body("/api/accounts")
    try:
        data = json.loads(body)
        test_id = None
        for a in data.get("data", []):
            if a.get("name") == "__TEST__":
                test_id = a["id"]
                break
        if test_id:
            code = http_code(f"/api/accounts/{test_id}", method="DELETE")
            test("Delete Account", code == "200", f"[{code}]")
        else:
            test("Find created", False, "not found in list")
    except:
        test("CRUD JSON parse", False)


def step_ai():
    print("\n[AI Tests — Qwen Cloud]")

    print("  ... script generation (~10-30s) ...", end=" ", flush=True)
    code = http_code("/api/content/generate-script", method="POST",
                     body='{"topic":"Xianyang Qianling","style":"Explore"}', timeout=120)
    test("Generate Script", code == "200", f"[{code}]")

    print("  ... AI chat (~5-15s) ...", end=" ", flush=True)
    code = http_code("/api/chat/ask", method="POST",
                     body='{"message":"Tell me about Qianling","session_id":"auto_test"}', timeout=120)
    test("AI Chat", code == "200", f"[{code}]")


# ============================================================
# Remote mode (SSH into server and run this script there)
# ============================================================
def run_remote(host, user, password):
    try:
        import paramiko
    except ImportError:
        print("[ERROR] Remote mode requires paramiko: pip install paramiko")
        sys.exit(2)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=30)

    flags = ""
    if args.fast:
        flags = " --fast"
    if args.skip_ai:
        flags += " --skip-ai"

    cmd = f"cd /opt/aigc && backend/venv/bin/python scripts/test_api.py{flags}"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    for line in iter(stdout.readline, ""):
        print(line, end="")
    for line in iter(stderr.readline, ""):
        print(line, end="", file=sys.stderr)
    ec = stdout.channel.recv_exit_status()
    ssh.close()
    return ec


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIGC API 自动化测试")
    parser.add_argument("--fast", action="store_true", help="仅冒烟测试 + 错误处理")
    parser.add_argument("--skip-ai", action="store_true", help="跳过 AI 测试")
    parser.add_argument("--remote", action="store_true", help="SSH 远程模式")
    parser.add_argument("--host", default=os.getenv("TEST_HOST", ""))
    parser.add_argument("--user", default=os.getenv("TEST_USER", "root"))
    parser.add_argument("--password", default=os.getenv("TEST_PASS", ""))
    args = parser.parse_args()

    if args.remote:
        if not args.host or not args.password:
            print("[ERROR] Remote mode requires --host and --password")
            sys.exit(2)
        sys.exit(run_remote(args.host, args.user, args.password))

    print("=" * 60)
    print(f"  咸阳文旅 AIGC — API 自动化测试")
    print(f"  Target: {BASE_URL}")
    print("=" * 60)

    if not step_login():
        print("\n[FAIL] 登录失败，无法继续测试")
        sys.exit(1)

    step_smoke()
    step_errors()

    if not args.fast:
        step_data_validation()
        step_crud()
        if not args.skip_ai:
            step_ai()
        else:
            print("\n[AI Tests] — SKIPPED (--skip-ai)")

    total = PASS + FAIL
    print()
    print("=" * 60)
    print(f"  SUMMARY: total={total}  |  PASS={PASS}  |  FAIL={FAIL}")
    if FAILURES:
        print(f"\n  Failures ({len(FAILURES)}):")
        for f in FAILURES:
            print(f"    - {f}")
        print()
    else:
        print("  ALL PASSED")
    print("=" * 60)

    sys.exit(0 if FAIL == 0 else 1)
