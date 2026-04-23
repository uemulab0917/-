#!/bin/bash
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>false</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

# TOKEN_LIMIT: empirically measured upper bound (update when hitting rate limit)
# Time-based limits observed (JST):
#   08:00-13:00 → 10,124,239
#   22:00-03:00 →  8,689,268
TOKEN_LIMIT=10124239

export PATH="/usr/local/bin:/opt/homebrew/bin:$HOME/.nodebrew/current/bin:/usr/bin:/bin:$PATH"

CCUSAGE_JSON=$(npx ccusage@latest blocks --recent --json --offline 2>/dev/null)
export CCUSAGE_JSON
export TOKEN_LIMIT

python3 - <<'PYEOF'
import os, json, sys
from datetime import datetime, timezone, timedelta

TOKEN_LIMIT = int(os.environ.get('TOKEN_LIMIT', '10124239'))
raw = os.environ.get('CCUSAGE_JSON', '').strip()

if not raw:
    print("⚠️ No data")
    print("---")
    print("ccusage からデータを取得できませんでした")
    sys.exit(0)

try:
    data = json.loads(raw)
except json.JSONDecodeError as e:
    print("⚠️ Parse error")
    print("---")
    print(f"JSON parse error: {e}")
    sys.exit(0)

blocks = data.get('blocks', [])
non_gap = [b for b in blocks if not b.get('isGap', True)]

now = datetime.now(timezone.utc)
JST = timezone(timedelta(hours=9))
BLOCK_DURATION = timedelta(hours=5)


def fmt_td(td):
    secs = int(td.total_seconds())
    if secs <= 0:
        return "0m"
    h, rem = divmod(secs, 3600)
    m = rem // 60
    return f"{h}h{m:02d}m" if h else f"{m}m"


def usage_color(pct):
    if pct < 50:
        return "🟢"
    if pct < 70:
        return "🟡"
    if pct < 90:
        return "🟠"
    return "🔴"


if not non_gap:
    print("Claude ✅")
    print("---")
    print("使用データなし")
    sys.exit(0)

by_time = sorted(non_gap, key=lambda b: b['startTime'], reverse=True)
active = next((b for b in by_time if b.get('isActive', False)), None)

if active:
    tokens = active['totalTokens']
    pct = tokens / TOKEN_LIMIT * 100
    start = datetime.fromisoformat(active['startTime'].replace('Z', '+00:00'))
    reset = start + BLOCK_DURATION
    left = reset - now

    # menu bar (single line)
    print(f"{usage_color(pct)}{pct:.0f}% {fmt_td(left)}")
    print("---")

    # dropdown details
    reset_jst = reset.astimezone(JST)
    start_jst = start.astimezone(JST)
    cost = active.get('costUSD', 0)
    models = ', '.join(active.get('models', []))

    print(f"📊 {tokens:,} / {TOKEN_LIMIT:,} tokens ({pct:.1f}%)")
    print("---")
    print(f"🕐 開始: {start_jst.strftime('%m/%d %H:%M JST')}")
    print(f"🔄 リセット: {reset_jst.strftime('%m/%d %H:%M JST')}")
    print(f"⏱ 残り: {fmt_td(left)}")
    print("---")
    print(f"💰 コスト: ${cost:.4f}")
    print(f"🤖 {models}")
    print("---")
    print(f"TOKEN_LIMIT: {TOKEN_LIMIT:,} | font=Menlo size=11 color=#888888")

else:
    # No active block — check if still in rate-limit window
    latest = by_time[0]
    start = datetime.fromisoformat(latest['startTime'].replace('Z', '+00:00'))
    reset = start + BLOCK_DURATION
    left = reset - now

    if left.total_seconds() > 0:
        # Still waiting for the 5-hour window to expire
        print(f"⏳ 解除まで {fmt_td(left)}")
        print("---")
        reset_jst = reset.astimezone(JST)
        print(f"⏳ 制限中")
        print(f"🔓 解除時刻: {reset_jst.strftime('%m/%d %H:%M JST')}")
        print(f"⏱ 残り: {fmt_td(left)}")
    else:
        print("✅ 制限なし")
        print("---")
        print("アクティブブロックなし")

    # Previous block summary
    tokens = latest['totalTokens']
    pct = tokens / TOKEN_LIMIT * 100
    start_jst = start.astimezone(JST)
    reset_jst = reset.astimezone(JST)
    cost = latest.get('costUSD', 0)

    print("---")
    print(f"📋 直前ブロック")
    print(f"🕐 {start_jst.strftime('%m/%d %H:%M')} → {reset_jst.strftime('%H:%M JST')}")
    print(f"📊 {tokens:,} tokens ({pct:.1f}%)")
    print(f"💰 ${cost:.4f}")

PYEOF
