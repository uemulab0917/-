#!/bin/bash
# One-command installer for Claude Code macOS menu bar app.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
PLIST_SRC="$SCRIPT_DIR/com.claudecode.menubar.plist"
PLIST_NAME="com.claudecode.menubar.plist"
PLIST_DST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== Claude Code メニューバー インストーラー ==="
echo ""

# ── Python 3 check ────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "❌ python3 が見つかりません。Homebrew でインストール: brew install python"
    exit 1
fi

# ── Virtual environment ───────────────────────────────────────────────────
echo "📦 仮想環境を作成中..."
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

# ── LaunchAgent ───────────────────────────────────────────────────────────
mkdir -p "$HOME/Library/LaunchAgents" "$SCRIPT_DIR/logs"

sed "s|__SCRIPT_DIR__|$SCRIPT_DIR|g" "$PLIST_SRC" > "$PLIST_DST"

# Unload previous instance if running
launchctl unload "$PLIST_DST" 2>/dev/null || true

launchctl load "$PLIST_DST"

echo ""
echo "✅ インストール完了！メニューバーに「Claude XX% (Xh Ym)」が表示されます。"
echo ""
echo "───────────────────────────────────────────"
echo "  ログ:         $SCRIPT_DIR/logs/menubar.log"
echo "  設定ファイル:  ~/.claude/menubar.json"
echo ""
echo "  トークン上限をカスタマイズする場合:"
echo "    echo '{\"max_tokens\": 88000}' > ~/.claude/menubar.json"
echo ""
echo "  アンインストール:"
echo "    launchctl unload \"$PLIST_DST\""
echo "    rm \"$PLIST_DST\""
echo "───────────────────────────────────────────"
