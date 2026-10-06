param([Parameter(Mandatory = $true)][string]$SavePath)

# Runs under Windows PowerShell 5.1 in STA mode (required for clipboard access).
# Prints one of:
#   IMG:<path>      an image was in the clipboard and was saved to <path>
#   FILES:<path>    one line per copied file (Explorer copy)
#   TEXT            nothing we handle; caller should do a normal text paste
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$clip = [System.Windows.Forms.Clipboard]

if ($clip::ContainsImage()) {
    $img = $clip::GetImage()
    $dir = Split-Path -Parent $SavePath
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $img.Save($SavePath, [System.Drawing.Imaging.ImageFormat]::Png)
    $img.Dispose()
    Write-Output "IMG:$SavePath"
    exit 0
}

if ($clip::ContainsFileDropList()) {
    foreach ($f in $clip::GetFileDropList()) { Write-Output "FILES:$f" }
    exit 0
}

Write-Output "TEXT"
