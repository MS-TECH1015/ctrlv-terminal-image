# Changelog

## 0.1.4 — 2026-10-08

- Warns with a Reload Window button when a newer version is installed but the window still runs the old one. Upgrading without a reload used to leave the old behavior in place with no sign of it.

## 0.1.3 — 2026-10-08

- Ignores Ctrl+V while a paste is still in progress. Holding the key used to paste the same screenshot dozens of times.

## 0.1.2 — 2026-10-08

- Logs to the `ctrlv` output channel: the loaded version and path on activation, and for each paste what was in the clipboard, the detected target and whether Alt+V or a path was sent. This shows when an old version is still running after an upgrade.

## 0.1.1 — 2026-10-06

- Windows local terminal: a clipboard image is now handed over as Alt+V, so Claude Code attaches it as `[Image #N]` instead of showing a file path.
- Pasted paths are framed as a bracketed paste, which Claude Code needs to treat an image path as an attachment.

## 0.1.0 — 2026-10-06

- First release as Ctrl+V Terminal Image (repo `ctrlv-terminal-image`).
- Ctrl+V (Cmd+V on macOS) in the integrated terminal: text pastes as text, a clipboard image is saved as PNG and its path is pasted, copied files paste as their paths.
- Windows: native clipboard via PowerShell 5.1. WSL terminals get `/mnt/c/...` paths.
- macOS and Linux backends included but untested (`pngpaste`/`osascript`, `wl-paste`/`xclip`).
- Remote-SSH: not supported yet; falls back with a warning.
