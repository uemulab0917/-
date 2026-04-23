#!/bin/bash
# Setup script for claude-usage SwiftBar plugin (macOS)
set -e

PLUGIN_DIR="$HOME/Library/Application Support/SwiftBar/Plugins"
SCRIPT_NAME="claude-usage.1m.sh"
SCRIPT_SRC="$(cd "$(dirname "$0")" && pwd)/$SCRIPT_NAME"
SCRIPT_DEST="$PLUGIN_DIR/$SCRIPT_NAME"

echo "=== Claude Code Usage - SwiftBar Plugin Setup ==="
echo

# 1. Check dependencies
echo "[1/4] Checking dependencies..."

if ! command -v swiftbar &>/dev/null && [ ! -d /Applications/SwiftBar.app ]; then
  echo "  SwiftBar not found. Install with:"
  echo "    brew install --cask swiftbar"
  exit 1
fi

NPX_PATH=$(command -v npx 2>/dev/null)
if [ -z "$NPX_PATH" ]; then
  echo "  npx not found. Install Node.js with:"
  echo "    brew install nodebrew"
  echo "    nodebrew install stable && nodebrew use stable"
  echo "    echo 'export PATH=\$HOME/.nodebrew/current/bin:\$PATH' >> ~/.zshrc"
  exit 1
fi
echo "  ✅ npx: $NPX_PATH"
echo "  ✅ SwiftBar found"

# 2. Create plugin directory
echo "[2/4] Creating plugin directory..."
mkdir -p "$PLUGIN_DIR"
echo "  ✅ $PLUGIN_DIR"

# 3. Copy and enable plugin
echo "[3/4] Installing plugin..."
cp "$SCRIPT_SRC" "$SCRIPT_DEST"
chmod +x "$SCRIPT_DEST"
echo "  ✅ Installed: $SCRIPT_DEST"

# 4. Configure SwiftBar and restart
echo "[4/4] Configuring SwiftBar..."
defaults write com.ameba.SwiftBar PluginDirectory "$PLUGIN_DIR"
killall SwiftBar 2>/dev/null || true
sleep 1
open /Applications/SwiftBar.app
echo "  ✅ SwiftBar restarted"

echo
echo "Done! Claude usage will appear in your menu bar within 1 minute."
echo
echo "TOKEN_LIMIT is currently set to 10,124,239."
echo "To update after hitting the rate limit, edit TOKEN_LIMIT in:"
echo "  $SCRIPT_DEST"
