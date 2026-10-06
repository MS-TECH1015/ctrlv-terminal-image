# Ctrl+V Terminal Image

**Ctrl+V just works in the terminal.** Paste a screenshot into Claude Code, Codex CLI, Gemini CLI or any other agent running in the Cursor / VS Code integrated terminal, with the same key you use for text.

- Text in the clipboard → normal paste, zero added latency.
- Screenshot in the clipboard → on a local Windows terminal it is handed to Claude Code as Alt+V, so it shows up as `[Image #N]`. Elsewhere it is saved as PNG and its path is pasted for the agent to read.
- Files copied in Explorer → their paths are pasted.

No config. One keybinding. Paths work with every CLI that accepts a file path; the Alt+V hand-off on Windows is for Claude Code.

> GIF coming soon.

## Why

Terminals treat Ctrl+V as "paste text". When the clipboard holds an image they paste nothing, silently. Claude Code answers this with Alt+V on Windows, iTerm2 needs Cmd+V, VS Code needs a keybindings.json edit, and WSL and Remote-SSH each need their own tool. Sixteen small repos exist for one slice each. Ctrl+V Terminal Image is one extension for the whole thing: it intercepts Ctrl+V only while the terminal has focus, looks at what is actually in the clipboard, and does the right thing.

## Install

From the `.vsix` on the [releases page](https://github.com/MS-TECH1015/ctrlv-terminal-image/releases):

```sh
cursor --install-extension ctrlv-terminal-image-0.1.1.vsix
# or
code --install-extension ctrlv-terminal-image-0.1.1.vsix
```

Then take a screenshot (Win+Shift+S), click into the terminal running your agent, press Ctrl+V.

After installing a new version over an old one, run `Developer: Restart Extension Host` from the command palette. Until then the old code keeps running. Your terminals stay open.

## Platform status

| Platform | Status |
|---|---|
| Windows, local terminal | Tested in Cursor with Claude Code: Ctrl+V on a screenshot gives `[Image #N]` |
| Windows → WSL terminal | Paths rewritten to `/mnt/c/...`, untested |
| macOS | Backend included (`pngpaste`, falls back to `osascript`), untested |
| Linux | Backend included (`wl-paste`, `xclip`), untested |
| Remote-SSH | Not yet. Falls back to text paste with a warning |

Issues and PRs for the untested rows are very welcome.

## Settings

| Setting | Default | Meaning |
|---|---|---|
| `ctrlv.saveDir` | `<temp>/ctrlv` | Where pasted images are written |
| `ctrlv.quotePaths` | `true` | Wrap paths in double quotes |
| `ctrlv.trailingSpace` | `true` | Add a space after the path so you can keep typing |

## How it works

1. `ctrl+v` (`cmd+v` on macOS) is bound to `ctrlv.paste` with `when: terminalFocus`. Outside the terminal nothing changes.
2. `vscode.env.clipboard.readText()` is checked first. Non-empty text means a plain paste, so normal pasting is never slowed down.
3. Otherwise a tiny probe runs: on Windows a PowerShell 5.1 script in STA mode reads `Clipboard.GetImage()` / `GetFileDropList()`. On a local Windows terminal an image is handed over as Alt+V (`ESC v`), so Claude Code reads the clipboard itself and shows `[Image #N]`. Elsewhere the image is saved as PNG and the path is sent as a bracketed paste with `terminal.sendText`.

The extension runs on the UI side (`extensionKind: ui`), so the clipboard it reads is always the one on the machine you are sitting at.

## Name

The repo and extension are `ctrlv-terminal-image`. Commands and settings keep the short `ctrlv.` prefix.

## Development

```sh
npm install
npm run compile
npx vsce package
```

## License

MIT
