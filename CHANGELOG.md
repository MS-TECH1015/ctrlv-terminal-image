# Changelog

## 0.1.0 — 2026-10-06

- First release as Ctrl+V Terminal Image (repo `ctrlv-terminal-image`).
- Ctrl+V (Cmd+V on macOS) in the integrated terminal: text pastes as text, a clipboard image is saved as PNG and its path is pasted, copied files paste as their paths.
- Windows: native clipboard via PowerShell 5.1. WSL terminals get `/mnt/c/...` paths.
- macOS and Linux backends included but untested (`pngpaste`/`osascript`, `wl-paste`/`xclip`).
- Remote-SSH: not supported yet; falls back with a warning.
