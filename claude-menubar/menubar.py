#!/usr/bin/env python3
"""
Claude Code macOS menu bar app.

Displays the current 5-hour block usage (%) and remaining time.
When rate-limited, shows the countdown until the limit clears.
"""

import rumps
from datetime import timedelta

from usage import get_usage


def _fmt(td: timedelta) -> str:
    """Format a timedelta as 'Xh Ym' or 'Ym'."""
    total = int(td.total_seconds())
    if total <= 0:
        return "0m"
    h, rem = divmod(total, 3600)
    m = rem // 60
    return f"{h}h {m:02d}m" if h else f"{m}m"


class ClaudeMenuBarApp(rumps.App):
    def __init__(self):
        super().__init__("Claude", quit_button=None)

        self._status_item = rumps.MenuItem("読み込み中...")
        self._token_item = rumps.MenuItem("")

        self.menu = [
            self._status_item,
            self._token_item,
            None,
            rumps.MenuItem("詳細を表示", callback=self._show_detail),
            rumps.MenuItem("今すぐ更新", callback=self._refresh),
            None,
            rumps.MenuItem("終了", callback=rumps.quit_application),
        ]

        self._usage: dict = {}
        self._refresh()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @rumps.timer(60)
    def _auto_refresh(self, _=None):
        self._refresh()

    def _refresh(self, _=None):
        u = get_usage()
        self._usage = u

        if u.get("error"):
            self.title = "Claude ?"
            self._status_item.title = f"エラー: {u['error']}"
            self._token_item.title = ""
            return

        used = u["used_tokens"]
        maxt = u["max_tokens"]
        pct = u["percent"]

        if u["rate_limited"] and u["wait_remaining"]:
            wait = _fmt(u["wait_remaining"])
            self.title = f"⏳ {wait}"
            self._status_item.title = f"制限中 — 解除まで {wait}"
        else:
            remaining = _fmt(u["block_remaining"])
            self.title = f"Claude {pct}% ({remaining})"
            self._status_item.title = f"{pct}% 使用 / 残り {remaining}"

        self._token_item.title = f"  {used:,} / {maxt:,} tokens"

    # ------------------------------------------------------------------ #
    # Menu callbacks
    # ------------------------------------------------------------------ #

    def _show_detail(self, _):
        u = self._usage
        if not u:
            rumps.alert("Claude Code", "データがありません。")
            return
        if u.get("error"):
            rumps.alert("エラー", u["error"])
            return

        lines = [
            f"使用率:     {u['percent']}%",
            f"トークン:   {u['used_tokens']:,} / {u['max_tokens']:,}",
        ]
        if u["rate_limited"]:
            lines.append(f"状態:       制限中")
            lines.append(f"解除まで:   {_fmt(u['wait_remaining'])}")
        else:
            lines.append(f"状態:       通常")
            lines.append(f"ブロック残り: {_fmt(u['block_remaining'])}")

        rumps.alert("Claude Code 使用状況", "\n".join(lines))


if __name__ == "__main__":
    ClaudeMenuBarApp().run()
