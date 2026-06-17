# 🛡️ Aegis Box

**Aegis Box** es un gestor premium de **Sandboxing Dinámico por Diferencias (Diff-Sandboxing)** y aislamiento de librerías dinámicas legacy para **CachyOS / Arch Linux**. 

Permite ejecutar navegadores, juegos de Wine o scripts desconocidos en un entorno efímero en la memoria RAM de forma segura, resolviendo automáticamente dependencias de librerías obsoletas mediante enlaces simbólicos sin contaminar la raíz del sistema operativo.

---

## ✨ Características Principales

* **📦 Aislamiento Efímero en RAM**: Redirige todas las escrituras a un overlay temporal en la memoria RAM (`tmpfs`). Al cerrar la aplicación, puedes decidir si deseas descartar todos los cambios (**Discard**) o guardarlos (**Commit**).
* **🔗 Enlazador Dinámico Virtual**: Audita los binarios al vuelo (`ldd`), enlazando por symlink tus librerías del sistema e inyectando de forma aislada versiones antiguas/legacy (como OpenSSL 1.1) desde una caché central.
* **🌐 Redes Virtuales Dedicadas**: Crea, edita y apaga/enciende interfaces de red virtuales (`aegis0`) mediante NetworkManager de forma nativa para dar soporte de IP/MAC virtuales a los sandboxes de Firejail.
* **🖥️ Interfaz PySide6 (Estilo WingetUI)**: Interfaz gráfica moderna, modular y en modo oscuro que gestiona el ciclo de vida completo de tus apps, perfiles de seguridad y dependencias.
* **⚙️ Perfiles JSON Dinámicos**: Crea o edita en vivo las reglas de aislamiento (RAM, GPU, Red, exclusiones persistentes de Marcadores) sobre la marcha mientras aíslas un programa.

---

## 🚀 Instalación Rápida

Abre una terminal en tu laptop y ejecuta:

```bash
git clone https://github.com/esfingex/aegis_box.git
cd aegis_box
bash install.sh
```

El instalador automático configurará los directorios locales, levantará el puente de red `aegis0` y **creará el lanzador de GNOME automáticamente** para que puedas abrir Aegis Box desde tu cajón de aplicaciones de escritorio.

---

## 💡 Uso Básico

### Interfaz Gráfica (GUI)
Puedes abrirlo buscando **Aegis Box** en el menú de aplicaciones de tu GNOME, o ejecutando:
```bash
aegis-box gui
```

### Línea de Comandos (CLI)
Para correr una aplicación de forma aislada en RAM instantáneamente:
```bash
aegis-box run /usr/bin/vivaldi --profile /home/esfingex/workspace/aegis_box/profiles/vivaldi.json --name "Vivaldi"
```

---

## 🔒 Licencia
Este proyecto es software libre bajo la licencia GNU General Public License v3.0 (GPLv3).
