# Yakuza 6: The Song of Life - Traducción al español v1.0.2 (25-10-2026)
# Instala o quita la traducción. Antes de instalar guarda los archivos originales del juego en «respaldo_original»
# (junto a este instalador); «Quitar» los devuelve. No toca partidas, logros ni horas de Steam.
param([string]$Accion = "")
$ErrorActionPreference = "Stop"
$VERSION = "1.0.2"
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$arch = Join-Path $aqui "archivos"
$resp = Join-Path $aqui "respaldo_original"

function Buscar-Juego {
    $carpetas = @()
    $steam = (Get-ItemProperty "HKCU:\Software\Valve\Steam" -ErrorAction SilentlyContinue).SteamPath
    if ($steam) {
        $carpetas += $steam
        $vdf = Join-Path $steam "steamapps\libraryfolders.vdf"
        if (Test-Path $vdf) {
            foreach ($m in [regex]::Matches((Get-Content $vdf -Raw), '"path"\s+"([^"]+)"')) { $carpetas += $m.Groups[1].Value -replace '\\\\', '\' }
        }
    }
    foreach ($c in ($carpetas | Select-Object -Unique)) {
        $j = Join-Path $c "steamapps\common\Yakuza 6 - The Song of Life"
        if (Test-Path (Join-Path $j "data\talk.par")) { return $j }
    }
    return $null
}

Write-Host "Yakuza 6 - Traducción al español v$VERSION" -ForegroundColor Yellow
if (Get-Process Yakuza6 -ErrorAction SilentlyContinue) { Write-Host "Cierra el juego antes de seguir." -ForegroundColor Red; Read-Host "Enter para salir"; exit 1 }
$juego = Buscar-Juego
if (-not $juego) {
    Write-Host "No encontré el juego automáticamente."
    $juego = Read-Host "Pega la carpeta del juego (la que contiene «data»)"
    if (-not (Test-Path (Join-Path $juego "data\talk.par"))) { Write-Host "Esa carpeta no es la del juego." -ForegroundColor Red; Read-Host "Enter para salir"; exit 1 }
}
$data = Join-Path $juego "data"
Write-Host "Juego: $juego"
if (-not $Accion) { $Accion = Read-Host "Escribe 1 para INSTALAR o 2 para QUITAR la traducción" }

$PARES = @("talk.par", "font.par", "ui.par")
$tablas = Get-ChildItem (Join-Path $arch "db_e") -Filter *.bin
if ($Accion -eq "1") {
    if ((Test-Path (Join-Path $data "traduccion_es_version.txt")) -and -not (Test-Path (Join-Path $resp "talk.par"))) {
        Write-Host "Ya hay una traducción instalada y no encuentro su «respaldo_original» junto a este instalador." -ForegroundColor Red
        Write-Host "Copia aquí la carpeta «respaldo_original» de la versión anterior, o en Steam: clic derecho en el juego >"
        Write-Host "Propiedades > Archivos instalados > Verificar integridad, y vuelve a instalar."
        Read-Host "Enter para salir"; exit 1
    }
    # respaldo archivo por archivo: si ya había uno de la v0.9 (sin ui.par), se completa sin pisar lo guardado
    New-Item -ItemType Directory -Force (Join-Path $resp "db_e") | Out-Null
    Write-Host "Guardando los archivos originales que falten en $resp ..."
    foreach ($f in $PARES) { if (-not (Test-Path (Join-Path $resp $f))) { Copy-Item (Join-Path $data $f) $resp } }
    foreach ($t in $tablas) { if (-not (Test-Path (Join-Path $resp "db_e\$($t.Name)"))) { Copy-Item (Join-Path $data "db\e\$($t.Name)") (Join-Path $resp "db_e") } }
    Write-Host "Instalando..."
    foreach ($f in $PARES) { Copy-Item (Join-Path $arch $f) $data -Force }
    foreach ($t in $tablas) { Copy-Item $t.FullName (Join-Path $data "db\e") -Force }
    Set-Content (Join-Path $data "traduccion_es_version.txt") "Traducción al español v$VERSION" -Encoding UTF8
    Write-Host "¡Listo! Abre el juego con el idioma en inglés." -ForegroundColor Green
} elseif ($Accion -eq "2") {
    if (-not (Test-Path $resp)) { Write-Host "No hay respaldo: usa «Verificar integridad» en Steam para volver al original." -ForegroundColor Red; Read-Host "Enter para salir"; exit 1 }
    foreach ($f in $PARES) { if (Test-Path (Join-Path $resp $f)) { Copy-Item (Join-Path $resp $f) $data -Force } }
    foreach ($t in Get-ChildItem (Join-Path $resp "db_e") -Filter *.bin) { Copy-Item $t.FullName (Join-Path $data "db\e") -Force }
    Remove-Item (Join-Path $data "traduccion_es_version.txt") -ErrorAction SilentlyContinue
    Write-Host "Traducción quitada: el juego vuelve a estar en inglés." -ForegroundColor Green
}
Read-Host "Enter para salir"
