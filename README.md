# Focus Tasks

Aplicación de escritorio para Linux y Windows, sencilla y oscura, con temporizadores independientes, guardado automático, tareas completadas y aviso al terminar cada temporizador.

## Descarga

Abre la sección **Releases** de este repositorio y descarga:

- Debian/Ubuntu: `focustask_<versión>_all.deb`
- Windows: `FocusTasks.exe`

En Debian/Ubuntu, instala el `.deb` con doble clic o desde una terminal:

```bash
sudo apt install ./focustask_1.0.0_all.deb
```

En Windows, abre `FocusTasks.exe` con doble clic. No necesitas instalar Python.

## Ejecutar desde el código fuente

Requiere Python 3 y Tkinter. En Debian/Ubuntu, si Tkinter no está instalado:

```bash
sudo apt install python3-tk
```

En Linux puedes ejecutar `./FocusTasks.sh`. En Windows abre PowerShell en esta carpeta y ejecuta:

```powershell
py focus_tasks.py
```

## Archivos del proyecto

- `focus_tasks.py`: aplicación y lógica compartida.
- `FocusTasks.sh`, `FocusTasks.desktop`: lanzadores de Linux.
- `packaging/build_deb.sh`: genera el instalador Debian/Ubuntu.
- `packaging/build_windows.ps1`: genera el ejecutable de Windows.
- `.github/workflows/release.yml`: compila los dos instaladores y crea una Release de GitHub.
- `LICENSE`: licencia MIT.

## Subir el proyecto desde el navegador de GitHub

1. En GitHub, crea un repositorio nuevo llamado `FocusTask` y selecciona **Public**. No marques las opciones para crear README, `.gitignore` ni licencia: esos archivos ya están en este proyecto.
2. Abre el repositorio y elige **Add file → Upload files**.
3. Desde la carpeta `FocusTask` de tu PC, sube estos archivos de la raíz: `.gitignore`, `FocusTasks.desktop`, `FocusTasks.sh`, `LEEME.txt`, `LICENSE`, `README.md`, `focus_tasks.py` y `requirements-build.txt`.
4. Sube también las carpetas completas `.github` y `packaging`. En el selector de archivos de Linux, pulsa **Ctrl+H** para mostrar las carpetas y el archivo ocultos que empiezan con punto.
5. **No subas** `data/` (puede tener tu lista personal), `dist/` (son paquetes generados) ni `.git/` (no hace falta y puede no existir).
6. Escribe el mensaje `Publica Focus Tasks` y selecciona **Commit directly to the main branch**. Presiona **Commit changes**.

En el repositorio deben aparecer `.github/workflows/release.yml` y `.gitignore`. La primera activa la compilación; la segunda evita incluir tus tareas personales en futuras subidas.

## Crear la descarga de Windows y Linux desde GitHub

No hace falta compilar en tu PC ni crear etiquetas locales. Después de subir los archivos del proyecto al repositorio:

1. Abre la pestaña **Actions**.
2. Selecciona **Build and release** en la lista de la izquierda. Si GitHub muestra un botón para habilitar Actions, presiónalo.
3. Presiona **Run workflow**, elige la rama `main` y deja la versión `1.0.0`.
4. Presiona de nuevo **Run workflow**. Cuando termine con éxito, abre **Releases**: encontrarás el `.deb` y el `.exe` allí.

Deja `1.0.0` en el campo de versión para mantener esa versión fija. Ejecuta este flujo una sola vez; si la Release ya existe, no vuelvas a crearla con el mismo número.

## Datos y privacidad

Las tareas se guardan en el equipo del usuario:

- Linux: `$XDG_DATA_HOME/focus-tasks/tasks.json` o, si no se define `XDG_DATA_HOME`, `~/.local/share/focus-tasks/tasks.json`.
- Windows: `%LOCALAPPDATA%\focus-tasks\tasks.json`.

El repositorio ignora `data/tasks.json`, que puede contener tareas personales. La app migra automáticamente ese archivo heredado en su primer inicio.

## Licencia

MIT. Consulta [LICENSE](LICENSE).
