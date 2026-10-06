# ctrlv

**Ctrl+V just works in the terminal.** Paste a screenshot into Claude Code, Codex CLI, Gemini CLI or any other agent running in the Cursor / VS Code integrated terminal, with the same key you use for text.

- Text in the clipboard → normal paste, zero added latency.
- Screenshot in the clipboard → saved as PNG, its path is pasted. The agent reads the image.
- Files copied in Explorer → their paths are pasted.

No config. One keybinding. Works with every CLI that accepts a file path.

> GIF coming soon.

## Why

Terminals treat Ctrl+V as "paste text". When the clipboard holds an image they paste nothing, silently. Claude Code answers this with Alt+V on Windows, iTerm2 needs Cmd+V, VS Code needs a keybindings.json edit, and WSL and Remote-SSH each need their own tool. Sixteen small repos exist for one slice each. ctrlv is one extension for the whole thing: it intercepts Ctrl+V only while the terminal has focus, looks at what is actually in the clipboard, and does the right thing.

## Install

From the `.vsix` on the [releases page](https://github.com/MS-TECH1015/ctrlv/releases):

```sh
cursor --install-extension ctrlv-0.1.0.vsix
# or
code --install-extension ctrlv-0.1.0.vsix
```

Then take a screenshot (Win+Shift+S), click into the terminal running your agent, press Ctrl+V.

## Platform status

| Platform | Status |
|---|---|
| Windows, local terminal | Tested |
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
3. Otherwise a tiny probe runs: on Windows a PowerShell 5.1 script in STA mode reads `Clipboard.GetImage()` / `GetFileDropList()`. The image is saved as PNG and the path is sent to the terminal with `terminal.sendText`.

The extension runs on the UI side (`extensionKind: ui`), so the clipboard it reads is always the one on the machine you are sitting at.

## Development

```sh
npm install
npm run compile
npx vsce package
```

## License

MIT
