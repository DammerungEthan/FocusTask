#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-1.0.0}"
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${2:-$ROOT/dist}"
STAGE="$(mktemp -d "$ROOT/.deb-stage.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p \
  "$STAGE/DEBIAN" \
  "$STAGE/opt/focustask" \
  "$STAGE/usr/bin" \
  "$STAGE/usr/share/applications" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps" \
  "$OUTPUT_DIR"

cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: focustask
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-tk
Maintainer: FocusTask contributors <noreply@github.com>
Description: Lista de tareas con temporizadores individuales
 Aplicación ligera de escritorio para organizar tareas y gestionar
 temporizadores independientes con una interfaz oscura.
CONTROL

install -m 0644 "$ROOT/focus_tasks.py" "$STAGE/opt/focustask/focus_tasks.py"
install -m 0644 "$ROOT/packaging/focustask.svg" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps/focustask.svg"
cat > "$STAGE/usr/bin/focustask" <<'LAUNCHER'
#!/bin/sh
exec /usr/bin/python3 /opt/focustask/focus_tasks.py "$@"
LAUNCHER
chmod 0755 "$STAGE/usr/bin/focustask"
cat > "$STAGE/usr/share/applications/focustask.desktop" <<'DESKTOP'
[Desktop Entry]
Version=1.0
Type=Application
Name=Focus Tasks
Comment=Lista de tareas con temporizadores individuales
Exec=focustask
Icon=focustask
Terminal=false
Categories=Office;
StartupNotify=true
DESKTOP

OUTPUT="$OUTPUT_DIR/focustask_${VERSION}_all.deb"
dpkg-deb --root-owner-group --build "$STAGE" "$OUTPUT"
printf 'Paquete creado: %s\n' "$OUTPUT"
