import sqlite3
import os
from pathlib import Path

DB_DIR = Path.home() / ".config" / "aegis_box"
DB_PATH = DB_DIR / "aegis_box.db"

def init_db():
    """Initializes the database directory and tables if they don't exist."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 1. Sessions table (tracks active or pending sandboxes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            app_name TEXT NOT NULL,
            profile_name TEXT NOT NULL,
            overlay_path TEXT NOT NULL,
            status TEXT NOT NULL, -- 'active', 'pending_commit', 'committed', 'discarded'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP
        )
    """)
    
    # 2. Registered Persistent Apps
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apps (
            app_id TEXT PRIMARY KEY, -- short identifier (e.g., 'chrome-sandbox')
            display_name TEXT NOT NULL,
            binary_path TEXT NOT NULL,
            profile_path TEXT NOT NULL,
            desktop_path TEXT,
            icon_path TEXT,
            status TEXT DEFAULT 'configured', -- 'configured', 'active'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. Shared Libraries Cache
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libs_cache (
            lib_name TEXT PRIMARY KEY, -- e.g., 'libssl.so.1.1'
            version TEXT,
            origin_url TEXT,
            local_path TEXT NOT NULL,
            size_bytes INTEGER,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 4. Global Settings Table for dynamic configurable variables (like library download mirrors)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    # Prefill default library mirror URL
    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value) 
        VALUES ('library_mirror', 'https://archive.archlinux.org/packages/')
    """)
    
    # Auto-detect default bridge connection name on host
    default_bridge = "aegissand"
    try:
        net_dir = Path("/sys/class/net")
        if net_dir.exists():
            for dev in net_dir.iterdir():
                if (dev / "bridge").exists() and dev.name.startswith("aegis"):
                    default_bridge = dev.name
                    break
    except Exception:
        pass

    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value) 
        VALUES ('bridge_interface', ?)
    """, (default_bridge,))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Returns an active SQLite database connection."""
    init_db()
    return sqlite3.connect(str(DB_PATH))

def get_setting(key, default=""):
    """Reads a setting value from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key, value):
    """Saves or updates a setting value in database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

# --- Session Management Functions ---

def register_session(session_id, app_name, profile_name, overlay_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (id, app_name, profile_name, overlay_path, status) VALUES (?, ?, ?, ?, 'active')",
        (session_id, app_name, profile_name, overlay_path)
    )
    conn.commit()
    conn.close()

def update_session_status(session_id, status, finished=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    if finished:
        cursor.execute(
            "UPDATE sessions SET status = ?, finished_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, session_id)
        )
    else:
        cursor.execute(
            "UPDATE sessions SET status = ? WHERE id = ?",
            (status, session_id)
        )
    conn.commit()
    conn.close()

def get_pending_sessions():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE status = 'pending_commit' ORDER BY created_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

# --- Apps Management Functions ---

def register_app(app_id, display_name, binary_path, profile_path, desktop_path=None, icon_path=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO apps (app_id, display_name, binary_path, profile_path, desktop_path, icon_path) VALUES (?, ?, ?, ?, ?, ?)",
        (app_id, display_name, binary_path, profile_path, desktop_path, icon_path)
    )
    conn.commit()
    conn.close()

def get_registered_apps():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apps ORDER BY display_name ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

# --- Libs Cache Functions ---

def register_cached_lib(lib_name, version, origin_url, local_path, size_bytes):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO libs_cache (lib_name, version, origin_url, local_path, size_bytes) VALUES (?, ?, ?, ?, ?)",
        (lib_name, version, origin_url, local_path, size_bytes)
    )
    conn.commit()
    conn.close()

def get_cached_libs():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM libs_cache ORDER BY lib_name ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_session_by_id(session_id):
    """Retrieves a session's details from database by ID."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_app(app_id):
    """Deletes a registered application from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM apps WHERE app_id = ?", (app_id,))
    conn.commit()
    conn.close()

