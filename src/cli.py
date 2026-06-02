import os
import sys
import argparse
import uuid
import subprocess
import json
import shutil
from pathlib import Path
from database import register_session, update_session_status, register_cached_lib, get_setting

# Core Storage Paths
STORAGE_DIR = Path.home() / ".local" / "share" / "aegis_box"
SHARED_LIBS_DIR = STORAGE_DIR / "shared_libs"
APPS_DIR = STORAGE_DIR / "apps"
TMP_BASE_DIR = Path("/tmp/aegis_box")

def ensure_paths():
    """Ensures base storage and cache folders exist."""
    SHARED_LIBS_DIR.mkdir(parents=True, exist_ok=True)
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    TMP_BASE_DIR.mkdir(parents=True, exist_ok=True)

def audit_binary_dependencies(binary_path):
    """
    Runs ldd on the target binary to verify existing and missing shared libraries.
    Returns: (dict_of_found_libs, list_of_missing_libs)
    """
    if not os.path.exists(binary_path):
        print(f"[-] Error: El binario {binary_path} no existe.")
        return {}, []
    
    found_libs = {}
    missing_libs = []
    
    try:
        # Run ldd in Spanish/English environment to parse output
        result = subprocess.run(
            ["ldd", binary_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "LC_ALL": "C"}
        )
        
        if result.returncode != 0:
            print(f"[-] Warning: ldd devolvió un código de error para {binary_path}.")
            return {}, []
            
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            
            # Formats:
            # 1. "libssl.so.1.1 => not found"
            # 2. "libc.so.6 => /usr/lib/libc.so.6 (0x00007f56)"
            # 3. "/lib64/ld-linux-x86-64.so.2 (0x00007f56)"
            if "=>" in line:
                parts = line.split("=>")
                lib_name = parts[0].strip()
                target = parts[1].strip()
                
                if "not found" in target:
                    missing_libs.append(lib_name)
                else:
                    path_part = target.split("(")[0].strip()
                    found_libs[lib_name] = path_part
            else:
                # Direct link (e.g. dynamic linker)
                path_part = line.split("(")[0].strip()
                if os.path.exists(path_part):
                    found_libs[os.path.basename(path_part)] = path_part
                    
    except Exception as e:
        print(f"[-] Falló la auditoría ldd: {e}")
        
    return found_libs, missing_libs

def download_legacy_library(lib_name):
    """
    Downloads legacy libraries from the dynamic configurable mirror.
    """
    local_path = SHARED_LIBS_DIR / lib_name
    if local_path.exists():
        return str(local_path)
    
    mirror_url = get_setting("library_mirror", "https://archive.archlinux.org/packages/")
    print(f"[i] Buscando {lib_name} en el repositorio central de Aegis Box en: {mirror_url}")
    
    try:
        # Simulated secure download from dynamic mirror_url
        dummy_content = f"/* Mock compatibility library for {lib_name} downloaded from {mirror_url} */"
        with open(local_path, "w") as f:
            f.write(dummy_content)
            
        register_cached_lib(lib_name, "1.0-compat", mirror_url, str(local_path), len(dummy_content))
        print(f"[+] {lib_name} descargado y cacheado con éxito.")
        return str(local_path)
    except Exception as e:
        print(f"[-] Error descargando {lib_name} de {mirror_url}: {e}")
        return None

def build_virtual_library_runtime(session_id, found_libs, missing_libs):
    """
    Creates a temporary directory with symlinks to all system libraries
    and mounts legacy compatibility libraries for runtime loading.
    """
    session_dir = TMP_BASE_DIR / session_id
    virtual_lib_dir = session_dir / "lib"
    virtual_lib_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[i] Construyendo cargador dinámico virtual en {virtual_lib_dir}...")
    
    # 1. Symlink system libraries
    for lib_name, real_path in found_libs.items():
        if os.path.exists(real_path):
            symlink_path = virtual_lib_dir / lib_name
            if not symlink_path.exists():
                os.symlink(real_path, symlink_path)
                
    # 2. Resolve and copy/symlink legacy libraries
    resolved_missing = []
    for lib_name in missing_libs:
        cached_path = download_legacy_library(lib_name)
        if cached_path and os.path.exists(cached_path):
            shutil.copy(cached_path, virtual_lib_dir / lib_name)
            resolved_missing.append(lib_name)
            
    print(f"[+] Virtual runtime listo. Enlazadas {len(found_libs)} libs del sistema, resueltas {len(resolved_missing)} legacy.")
    return str(virtual_lib_dir), resolved_missing

def launch_sandbox(binary_path, profile_path, app_name):
    """
    Prepares the dynamic sandbox environment and spawns Firejail overlay process.
    """
    ensure_paths()
    
    session_id = str(uuid.uuid4())[:8]
    session_dir = TMP_BASE_DIR / session_id
    overlay_dir = session_dir / "overlay"
    overlay_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] --- Lanzando Sandbox de Aegis Box: {app_name} [ID: {session_id}] ---")
    
    # 1. Dependency check
    found, missing = audit_binary_dependencies(binary_path)
    if missing:
        print(f"[!] Faltan dependencias: {', '.join(missing)}")
    
    # 2. Build library symlinks
    virtual_lib_path, resolved = build_virtual_library_runtime(session_id, found, missing)
    
    # 3. Load Profile parameters
    try:
        with open(profile_path, "r") as f:
            profile_data = json.load(f)
    except Exception as e:
        print(f"[-] Error leyendo perfil JSON: {e}. Usando valores por defecto.")
        profile_data = {}
        
    # 4. Spawns Firejail command
    # Use LD_LIBRARY_PATH to point to virtual loader and preserve display variables
    env = {
        **os.environ,
        "LD_LIBRARY_PATH": f"{virtual_lib_path}:{os.environ.get('LD_LIBRARY_PATH', '')}:/usr/lib:/lib",
        "DISPLAY": os.environ.get("DISPLAY", ""),
        "WAYLAND_DISPLAY": os.environ.get("WAYLAND_DISPLAY", ""),
        "XAUTHORITY": os.environ.get("XAUTHORITY", ""),
        "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR", "")
    }
    
    cmd = [
        "firejail",
        f"--overlay-dir={overlay_dir}",
        "--socket=x11",
        "--socket=wayland"
    ]
    
    # Add profile network parameters
    net_data = profile_data.get("network", {})
    if not net_data.get("enabled", True):
        cmd.append("--net=none")
    elif net_data.get("virtual_identity", False):
        # Emulate a separate bridge, checking if it exists on host
        if os.path.exists("/sys/class/net/aegis0"):
            cmd.append("--net=aegis0")
        else:
            print("[!] Warning: Interfaz de red virtual 'aegis0' no encontrada en el host.")
            print("[!]          Usando red de host por defecto para garantizar conexión a Internet.")
        
    cmd.append(binary_path)
    
    # Record active session in database
    register_session(session_id, app_name, profile_data.get("profile_name", "generic"), str(overlay_dir))
    
    print(f"[i] Ejecutando: {' '.join(cmd)}")
    print("[i] La aplicación se está ejecutando. Los cambios se guardan de forma temporal...")
    
    try:
        subprocess.run(cmd, env=env)
        # Mark session as pending commit
        update_session_status(session_id, "pending_commit", finished=True)
        print(f"\n[+] Aplicación finalizada. Sesión {session_id} lista para Auditoría y Commit.")
        print(f"[i] Puedes abrir 'aegis-box gui' para decidir sobre los cambios en: {overlay_dir}")
    except Exception as e:
        update_session_status(session_id, "failed", finished=True)
        print(f"[-] Error iniciando sandbox: {e}")

def main():
    parser = argparse.ArgumentParser(description="Aegis Box: Gestor de Sandboxing Dinámico por Diferencias")
    subparsers = parser.add_subparsers(dest="command")
    
    # 'run' command
    run_parser = subparsers.add_parser("run", help="Ejecuta una aplicación de forma aislada")
    run_parser.add_argument("binary", help="Ruta al binario o ejecutable")
    run_parser.add_argument("--profile", default="/home/esfingex/workspace/aegis_box/profiles/browser.json", help="Ruta al perfil JSON de seguridad")
    run_parser.add_argument("--name", default="", help="Nombre personalizado de la aplicación")
    
    # 'gui' command
    subparsers.add_parser("gui", help="Inicia la interfaz gráfica PySide6 al estilo WingetUI")
    
    args = parser.parse_args()
    
    if args.command == "run":
        app_name = args.name or os.path.basename(args.binary)
        launch_sandbox(args.binary, args.profile, app_name)
    elif args.command == "gui":
        # Launch PySide6 GUI (skeleton logic handles this)
        print("[*] Iniciando interfaz gráfica Aegis Box PySide6...")
        os.system(f"python3 /home/esfingex/workspace/aegis_box/src/main.py")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
