param(
    [Parameter(Mandatory=$true)][string]$Src,
    [Parameter(Mandatory=$true)][string]$Console,
    [int]$FtpPort = 2121,
    [string]$InstallRoot = '/mnt/ext1/etaHEN/games'
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path $Src).Path.TrimEnd([char[]]'\/')
if (!(Test-Path "$root/eboot.bin")) { throw 'eboot.bin is missing' }
$files = Get-ChildItem -LiteralPath $root -Recurse -File | Sort-Object @{Expression={ $_.Name -eq 'eboot.bin' }}, FullName
foreach ($file in $files) {
    $rel = $file.FullName.Substring($root.Length + 1).Replace('\','/')
    & curl.exe --fail --silent --show-error --ftp-create-dirs --connect-timeout 15 -u 'anonymous:' -T $file.FullName "ftp://${Console}:${FtpPort}${InstallRoot}/PPSA99621/$rel"
    if ($LASTEXITCODE -ne 0) { throw "Upload failed: $rel" }
    Write-Host "Uploaded $rel"
}
Write-Host "Register/mount $InstallRoot/PPSA99621 with ShadowMountPlus."
