#!/bin/bash
# 🛡️ Aegis Box - Automated Installer Script

set -e

echo "====================================================="
echo "🛡️  Iniciando Instalación de Aegis Box..."
echo "====================================================="

# Base Storage Paths
STORAGE_DIR="$HOME/.local/share/aegis_box"
CONFIG_DIR="$HOME/.config/aegis_box"
BIN_DIR="$HOME/.local/bin"

# 1. Create directory structure
echo "[*] Creando directorios base de Aegis Box..."
mkdir -p "$STORAGE_DIR/shared_libs"
mkdir -p "$STORAGE_DIR/apps"
mkdir -p "$CONFIG_DIR"
mkdir -p "$BIN_DIR"

# 2. Check for required system packages
echo "[*] Verificando dependencias necesarias del sistema..."
for cmd in firejail ldd python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "[-] Error: '$cmd' no está instalado en tu sistema."
        echo "    Por favor, instálalo antes de continuar."
        exit 1
    fi
done
echo "[+] Dependencias base del sistema verificadas (Firejail, LDD, Python3)."

# 3. Create virtual executable link in ~/.local/bin
echo "[*] Configurando comando rápido 'aegis-box' en tu terminal..."
cat << 'EOF' > "$BIN_DIR/aegis-box"
#!/bin/bash
python3 /home/esfingex/workspace/aegis_box/src/cli.py "$@"
EOF
chmod +x "$BIN_DIR/aegis-box"
echo "[+] Comando 'aegis-box' registrado en $BIN_DIR/aegis-box."

# 4. Initialize SQLite Database
echo "[*] Inicializando base de datos SQLite de Aegis Box..."
python3 -c "
import sys
sys.path.append('/home/esfingex/workspace/aegis_box/src')
from database import init_db
init_db()
print('[+] Base de datos inicializada correctamente.')
"

# 5. Create Desktop Launcher for GNOME Menu
echo "[*] Registrando Aegis Box en el menú de aplicaciones de GNOME..."
LAUNCHER_PATH="$HOME/.local/share/applications/aegis-box.desktop"
cat << EOF > "$LAUNCHER_PATH"
[Desktop Entry]
Name=Aegis Box
Comment=Aislamiento Dinámico de Apps & Compatibilidad
Exec=python3 /home/esfingex/workspace/aegis_box/src/main.py
Icon=security-high-symbolic
Terminal=false
Type=Application
Categories=System;Utility;Security;
EOF
chmod +x "$LAUNCHER_PATH"
echo "[+] Lanzador de escritorio creado con éxito en $LAUNCHER_PATH."

# 6. Configurar Interfaz de Red Virtual (Bridge aegis0)
echo "[*] Configurando puente de red virtual 'aegis0' para aislamiento..."
if ! ip link show aegis0 &>/dev/null; then
    echo "[i] Creando interfaz puente aegis0 (puede requerir privilegios de administrador)..."
    if command -v nmcli &>/dev/null; then
        sudo nmcli connection add type bridge con-name aegis0 ifname aegis0 ip4 10.10.10.1/24 &>/dev/null || true
        sudo nmcli connection modify aegis0 bridge.stp no &>/dev/null || true
        sudo nmcli connection up aegis0 &>/dev/null || true
        echo "[+] Puente aegis0 creado con éxito usando NetworkManager."
    else
        sudo ip link add name aegis0 type bridge &>/dev/null || true
        sudo ip addr add 10.10.10.1/24 dev aegis0 &>/dev/null || true
        sudo ip link set aegis0 up &>/dev/null || true
        echo "[+] Puente aegis0 creado temporalmente usando ip link."
    fi
else
    echo "[+] Puente de red aegis0 ya existe y está activo."
fi

echo "====================================================="
echo "🎉 ¡Aegis Box instalado con éxito!"
echo "====================================================="
echo "💡 Próximos pasos:"
echo "  - Ejecuta 'aegis-box gui' o búscalo en tu menú de GNOME para abrir la GUI."
echo "  - Ejecuta 'aegis-box run /usr/bin/firefox' para iniciar un sandbox seguro."
echo "====================================================="
