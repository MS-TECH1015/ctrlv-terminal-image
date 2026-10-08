import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as os from 'os';
import * as path from 'path';

type Clip =
  | { kind: 'text' }
  | { kind: 'image'; file: string }
  | { kind: 'files'; files: string[] };

let log: vscode.OutputChannel;

export function activate(context: vscode.ExtensionContext) {
  log = vscode.window.createOutputChannel('ctrlv');
  // The version line tells a stale extension host apart from the installed one.
  log.appendLine(`ctrlv ${context.extension.packageJSON.version} activated from ${context.extensionPath}`);
  context.subscriptions.push(
    log,
    vscode.commands.registerCommand('ctrlv.paste', () => paste(context))
  );
}

export function deactivate() {}

async function paste(context: vscode.ExtensionContext) {
  const terminal = vscode.window.activeTerminal;
  if (!terminal) {
    return textPaste();
  }

  // Fast path: plain text in the clipboard means a normal paste, no probe needed.
  // Screenshots and Explorer file copies leave the text slot empty.
  const text = await vscode.env.clipboard.readText();
  if (text.length > 0) {
    return textPaste();
  }

  let clip: Clip;
  try {
    clip = await probeClipboard(context);
  } catch (e) {
    vscode.window.showWarningMessage(`ctrlv: clipboard probe failed, pasting as text. ${String(e)}`);
    return textPaste();
  }

  if (clip.kind === 'text') {
    return textPaste();
  }

  const target = await detectTarget(terminal);
  log.appendLine(`${new Date().toISOString()} clip=${clip.kind} target=${target} shell=${(terminal.creationOptions as vscode.TerminalOptions).shellPath ?? ''}`);
  if (clip.kind === 'image' && process.platform === 'win32' && target === 'local') {
    // Same bytes as pressing Alt+V: Claude Code reads the clipboard image itself and shows [Image #N].
    // A pasted path stays plain text there.
    terminal.sendText('\x1bv', false);
    log.appendLine('  sent Alt+V');
    return;
  }

  const files = clip.kind === 'image' ? [clip.file] : clip.files;
  if (target === 'ssh') {
    vscode.window.showWarningMessage('ctrlv: Remote-SSH terminals are not supported yet; the file stays on this machine.');
  }

  const cfg = vscode.workspace.getConfiguration('ctrlv');
  const quote = cfg.get<boolean>('quotePaths', true);
  const trailing = cfg.get<boolean>('trailingSpace', true);

  const rendered = files
    .map((f) => (target === 'wsl' ? toWslPath(f) : f))
    .map((f) => (quote ? `"${f}"` : f))
    .join(' ');

  // Framed as a bracketed paste: Claude Code turns an image path into [Image #N] only when it arrives as a paste.
  log.appendLine(`  sent path ${rendered}`);
  terminal.sendText(`\x1b[200~${rendered}\x1b[201~` + (trailing ? ' ' : ''), false);
}

function textPaste() {
  return vscode.commands.executeCommand('workbench.action.terminal.paste');
}

function saveDir(): string {
  const configured = vscode.workspace.getConfiguration('ctrlv').get<string>('saveDir', '');
  return configured && configured.trim() ? configured : path.join(os.tmpdir(), 'ctrlv');
}

function newImagePath(): string {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
  return path.join(saveDir(), `img-${stamp}.png`);
}

async function probeClipboard(context: vscode.ExtensionContext): Promise<Clip> {
  switch (process.platform) {
    case 'win32':
      return probeWindows(context);
    case 'darwin':
      return probeMac();
    default:
      return probeLinux();
  }
}

function run(cmd: string, args: string[]): Promise<{ code: number; out: string; err: string }> {
  return new Promise((resolve) => {
    cp.execFile(cmd, args, { windowsHide: true, maxBuffer: 1 << 20 }, (error, stdout, stderr) => {
      const code = error && typeof (error as any).code === 'number' ? (error as any).code : error ? 1 : 0;
      resolve({ code, out: String(stdout), err: String(stderr) });
    });
  });
}

async function probeWindows(context: vscode.ExtensionContext): Promise<Clip> {
  const script = path.join(context.extensionPath, 'media', 'clip.ps1');
  const target = newImagePath();
  // Windows PowerShell 5.1: pwsh 7 cannot read images from the clipboard.
  const r = await run('powershell.exe', [
    '-NoProfile', '-NonInteractive', '-STA', '-ExecutionPolicy', 'Bypass',
    '-File', script, '-SavePath', target,
  ]);
  if (r.code !== 0) {
    throw new Error(r.err.trim() || `powershell exited ${r.code}`);
  }
  const lines = r.out.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const img = lines.find((l) => l.startsWith('IMG:'));
  if (img) {
    return { kind: 'image', file: img.slice(4) };
  }
  const files = lines.filter((l) => l.startsWith('FILES:')).map((l) => l.slice(6));
  if (files.length) {
    return { kind: 'files', files };
  }
  return { kind: 'text' };
}

async function probeMac(): Promise<Clip> {
  const target = newImagePath();
  // pngpaste is the reliable route; fall back to osascript for PNG data.
  let r = await run('pngpaste', [target]);
  if (r.code === 0) {
    return { kind: 'image', file: target };
  }
  r = await run('osascript', [
    '-e', `set f to POSIX file "${target}"`,
    '-e', 'try',
    '-e', 'set d to the clipboard as «class PNGf»',
    '-e', 'set h to open for access f with write permission',
    '-e', 'write d to h',
    '-e', 'close access h',
    '-e', 'return "IMG"',
    '-e', 'on error',
    '-e', 'return "TEXT"',
    '-e', 'end try',
  ]);
  if (r.code === 0 && r.out.trim() === 'IMG') {
    return { kind: 'image', file: target };
  }
  return { kind: 'text' };
}

async function probeLinux(): Promise<Clip> {
  const target = newImagePath();
  const fs = await import('fs');
  fs.mkdirSync(path.dirname(target), { recursive: true });
  const attempts: [string, string[]][] = [
    ['wl-paste', ['--type', 'image/png']],
    ['xclip', ['-selection', 'clipboard', '-t', 'image/png', '-o']],
  ];
  for (const [cmd, args] of attempts) {
    const ok = await new Promise<boolean>((resolve) => {
      const child = cp.execFile(cmd, args, { encoding: 'buffer', maxBuffer: 64 << 20 }, (error, stdout) => {
        if (error || !stdout || (stdout as Buffer).length === 0) {
          return resolve(false);
        }
        fs.writeFileSync(target, stdout as Buffer);
        resolve(true);
      });
      child.on('error', () => resolve(false));
    });
    if (ok) {
      return { kind: 'image', file: target };
    }
  }
  return { kind: 'text' };
}

async function detectTarget(terminal: vscode.Terminal): Promise<'local' | 'wsl' | 'ssh'> {
  const remote = vscode.env.remoteName;
  if (remote === 'wsl') {
    return 'wsl';
  }
  if (remote && remote.startsWith('ssh')) {
    return 'ssh';
  }
  const opts = terminal.creationOptions as vscode.TerminalOptions;
  const shell = (opts.shellPath || '').toLowerCase();
  if (shell.includes('wsl') || shell.includes('bash.exe') && shell.includes('windows\\system32')) {
    return 'wsl';
  }
  return 'local';
}

function toWslPath(winPath: string): string {
  const m = /^([a-zA-Z]):[\\/](.*)$/.exec(winPath);
  if (!m) {
    return winPath;
  }
  return `/mnt/${m[1].toLowerCase()}/${m[2].replace(/\\/g, '/')}`;
}
