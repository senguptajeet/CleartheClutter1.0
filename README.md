# Clear The Clutter

**Organize Your Files. Simplify Your Digital Life.**

Clear The Clutter is a Windows-focused desktop utility that scans a selected folder, previews files, and moves them into category folders based on their file extensions. It combines a Python file-management backend with a Flask-powered interface displayed in a native desktop window through PyWebView.

> **Important:** Organizing files moves them from the source folder to the destination folder. Test with sample files first and keep a backup of important data. Review the scan preview before selecting **Organize Files**.

## Table of contents

- [Features](#features)
- [How it works](#how-it-works)
- [Technology stack](#technology-stack)
- [System requirements](#system-requirements)
- [Run from source](#run-from-source)
- [How to use the application](#how-to-use-the-application)
- [File categories](#file-categories)
- [Configuration and local data](#configuration-and-local-data)
- [Technical architecture](#technical-architecture)
- [HTTP API reference](#http-api-reference)
- [Run tests](#run-tests)
- [Build a Windows executable](#build-a-windows-executable)
- [Build the Windows installer](#build-the-windows-installer)
- [Troubleshooting](#troubleshooting)
- [Limitations and safety notes](#limitations-and-safety-notes)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Scan and preview:** Inspect files before moving them. The preview includes filename, extension, category, and size.
- **Extension-based classification:** Group files into configured categories.
- **Duplicate-name protection:** Existing destination filenames are preserved; a numeric suffix such as `report (1).pdf` is generated for a collision.
- **Undo last batch:** Uses a local SQLite history database to track file moves and attempt to restore the most recent batch.
- **Cancel an operation:** Request cancellation while a batch is running.
- **Background work:** Scanning and organizing use worker threads so the interface can remain responsive.
- **Local-first desktop workflow:** The Flask interface is hosted locally and displayed in a native PyWebView window.
- **Configurable scanning:** Settings support recursive scanning and excluded directory names.
- **Logs:** Application events and errors are recorded for troubleshooting.

## How it works

1. Select a **Source Folder** containing files to organize.
2. Select an existing **Destination Folder** for the organized output.
3. Click **Scan Files** and review the preview and category counts.
4. Click **Organize Files** to move the scanned files into category subfolders under the destination.
5. If needed, click **Cancel** during an active operation to request cancellation.
6. Use **Undo Last** to attempt to reverse the most recent recorded batch.

The application creates destination subfolders as needed. It does not intentionally overwrite an existing file with the same destination name.

## Technology stack

| Component | Purpose |
| --- | --- |
| Python | File scanning, classification, organization, history, and application orchestration |
| Flask | Local web routes and JSON API |
| PyWebView | Displays the interface in a native desktop window and provides folder selection |
| HTML, CSS, JavaScript | User interface, file preview, progress display, and API polling |
| SQLite | Persistent operation history used by Undo |
| PyInstaller | Packages the application into a Windows executable |
| Inno Setup (optional) | Builds a Windows installer from the executable |

## System requirements

- **Operating system:** Windows 10 or Windows 11 is the intended environment.
- **Python:** Python 3.9 or later is recommended when running from source.
- **Dependencies:** Flask and PyWebView are required to launch the desktop application. PyInstaller is required only for packaging.
- **Build tools:** Inno Setup is optional and is needed only to build the installer.

The application uses Windows-specific behavior in some UI actions, including opening a destination folder with `os.startfile`. Other operating systems are not currently documented as supported.

## Run from source

### 1. Download the repository

Open a terminal or Command Prompt and run:

```bash
git clone https://github.com/senguptajeet/CleartheClutter1.0.git
cd CleartheClutter1.0
```

Alternatively, use GitHub's **Code → Download ZIP** option and extract the archive.

### 2. Create and activate a virtual environment

**Windows Command Prompt:**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

**PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt or follow your organization's Python environment policy rather than changing system execution policy without understanding the implications.

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install Flask pywebview
```

For executable packaging, also install PyInstaller:

```bash
python -m pip install pyinstaller
```

There is currently no `requirements.txt` in the repository, so these commands install the runtime and packaging dependencies explicitly.

### 4. Launch the desktop application

Run the current application entry point from the repository root:

```bash
python web_main.py
```

A native **Clear The Clutter** window should open. The repository's current entry point is `web_main.py`; there is no `main.py` in the current project tree.

## How to use the application

### Select folders

- **Source Folder:** The location to scan for files.
- **Destination Folder:** The location where categorized folders and moved files will be created.
- Use each **Browse** button to open the folder picker.
- Choose separate source and destination folders. Do not use a critical operating-system or application folder as a test target.

### Scan and review

1. Click **Scan Files**.
2. Wait for the scan to finish.
3. Review the file preview table and the dashboard counters.
4. Confirm that the source and destination paths are correct before proceeding.

The default setting is a **non-recursive scan**: only files directly inside the selected source folder are included. Files inside nested folders are scanned only when recursive scanning is enabled in the settings file.

### Organize

Click **Organize Files** after reviewing the scan. The app creates category subfolders inside the destination and moves each planned file into its category. A progress indicator reports the current file and overall progress.

### Cancel

Click **Cancel** to request cancellation. The organizer checks the cancellation flag between file moves, so the file currently being moved may finish before cancellation takes effect.

### Undo the last batch

Click **Undo Last** and confirm. The app uses the operation history to restore files from the most recently recorded batch to their original paths when possible. Undo may report errors if a moved file no longer exists, the original path is occupied, or permissions prevent restoration.

**Do not treat Undo as a substitute for a backup.** Verify the result after using it.

## File categories

The default mapping is stored in `src/settings_manager.py` and is copied to `config/settings.json` when settings are first initialized.

| Destination category | Example extensions |
| --- | --- |
| `pdf` | `.pdf` |
| `docs` | `.doc`, `.docx`, `.odt`, `.rtf`, `.txt`, `.md`, `.tex` |
| `excel` | `.xls`, `.xlsx`, `.csv`, `.tsv`, `.ods` |
| `ppt` | `.ppt`, `.pptx`, `.ppsx`, `.odp` |
| `Images` | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg` |
| `Videos` | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm` |
| `Compressed` | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.iso` |
| `Programs` | `.exe`, `.msi`, `.bat`, `.cmd`, `.ps1`, `.apk`, `.dmg` |
| `Others` | Any extension not matched by the configured categories, including extensionless files |

Classification is based on the file's final suffix and is case-insensitive. For example, `.JPG` is recognized as an image. Although the classifier contains a comment about multi-part extensions, the current implementation checks the final suffix; `.tar.gz` is therefore classified by `.gz`.

## Configuration and local data

When running from source, the app normally stores its generated data relative to the repository root. When running as a PyInstaller bundle, the application routes writable data to the user's Windows roaming AppData location under `ClearTheClutter`.

| Path | Purpose |
| --- | --- |
| `config/settings.json` | Runtime settings, category mappings, excluded directory names, and recursive-scan option |
| `data/history.db` | SQLite operation history used by Undo |
| `logs/` | Application log files |
| `src/` | Python backend modules |
| `templates/index.html` | Main interface markup |
| `static/style.css` | Interface styling |
| `static/script.js` | Browser-side interactions and API polling |
| `assets/` | Application icon and splash image |
| `ClearTheClutter.spec` | PyInstaller build configuration |
| `installer_script.iss` | Inno Setup installer configuration |

### Settings

The default settings include:

- `recursive_scan`: `false` by default.
- `handle_duplicates`: present in the defaults; the current organizer independently generates a safe destination filename when a collision occurs.
- `categories`: extension-to-category mappings.
- `excluded_dirs`: directory names skipped during recursive traversal, including common protected Windows directory names and `.git`.

Edit `config/settings.json` only when the application is closed, and keep a backup before changing it. The current excluded-directory behavior applies to directories encountered during traversal; it is not a comprehensive safety boundary for every possible source path.

## Technical architecture

```text
web_main.py
  ├── Flask routes and PyWebView desktop window
  ├── SettingsManager       (src/settings_manager.py)
  ├── FileScanner           (src/file_scanner.py)
  ├── FileClassifier        (src/file_classifier.py)
  ├── FileOrganizer         (src/file_organizer.py)
  ├── HistoryManager        (src/operation_history.py)
  └── Logger                (src/logger.py)

templates/index.html
  └── static/script.js
        └── Flask JSON endpoints in web_main.py
```

- **`SettingsManager`** loads defaults or reads the JSON settings file.
- **`FileScanner`** walks the source directory according to the recursive setting and skips the destination directory itself.
- **`FileClassifier`** maps file suffixes to configured categories.
- **`FileOrganizer`** moves files, avoids filename collisions, reports progress, and checks cancellation between moves.
- **`HistoryManager`** writes move records to SQLite and marks restored records as undone.
- **`logger`** writes diagnostic messages to log files.
- **Frontend** polls the status endpoint for scan rows, progress updates, and completion messages.

## HTTP API reference

These endpoints are implemented by the local Flask app and are intended for the desktop UI.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Render the main interface |
| `GET` | `/api/browse` | Open the native folder picker and return the selected path |
| `POST` | `/api/scan` | Validate paths and start a background scan |
| `POST` | `/api/organize` | Start organizing the current scan plan |
| `POST` | `/api/cancel` | Request cancellation of the current organization operation |
| `POST` | `/api/undo` | Attempt to reverse the latest recorded batch |
| `GET` | `/api/status` | Drain and return queued status/progress messages |

### Example request bodies

Scan:

```json
{
  "source": "C:/Users/Example/Downloads",
  "dest": "C:/Users/Example/Organized"
}
```

Organize:

```json
{
  "source": "C:/Users/Example/Downloads",
  "dest": "C:/Users/Example/Organized"
}
```

The browse endpoint depends on an active PyWebView window. These routes are designed for local application use and should not be exposed to an untrusted network without adding authentication, request validation, and appropriate security controls.

## Run tests

The repository includes a core test module at `src/test_core.py`. From the repository root, run:

```bash
python -m unittest src.test_core
```

The tests create temporary directories and sample files. They do not intentionally operate on a user's chosen documents. Note that the current test expectations and default category names should be kept aligned: the default classifier uses categories such as `pdf` and `docs`, while parts of the test module still expect `Documents`. If a test fails for this reason, update the test expectation or category configuration as part of a separate code change.

## Build a Windows executable

Run these commands from the repository root in an activated virtual environment:

```bash
python -m pip install Flask pywebview pyinstaller
pyinstaller --clean ClearTheClutter.spec
```

The spec file uses `web_main.py` as the entry point and includes the `templates`, `static`, and `assets` directories. If the build fails, check the PyInstaller output for missing hidden imports or platform-specific PyWebView dependencies.

After a successful build, look for the executable under `dist/`. Test the executable on a clean Windows environment before distributing it.

## Build the Windows installer

1. Build and verify `dist/ClearTheClutter.exe` first.
2. Install [Inno Setup](https://jrsoftware.org/isinfo.php) on the Windows build machine.
3. Open `installer_script.iss` in Inno Setup Compiler, or run `ISCC installer_script.iss` if the compiler is available on your PATH.
4. The script is configured to write the installer to the `Output` directory as `ClearTheClutter_Setup_v1.0.exe`.
5. Install and test the generated installer on a separate Windows test account or machine.

The installer script requests administrator privileges to install under Program Files. Review the installer settings before distributing a build.

## Troubleshooting

- **The app does not start:** Confirm that the virtual environment is active and that Flask and PyWebView are installed. Run `python web_main.py` from the repository root to see startup errors.
- **Folder picker does not open:** Launch the app through `web_main.py`; the browse endpoint relies on an initialized PyWebView window.
- **No files appear in the scan:** Check that the source folder exists, is accessible, and contains files at its top level. Recursive scanning is disabled by default.
- **A file is categorized as `Others`:** Check its extension against `categories` in `config/settings.json`.
- **A file could not be moved:** Check file permissions, whether the file is open in another program, available disk space, and the log output.
- **Undo reports errors:** Confirm that the destination copy still exists and the original path is available.
- **Executable packaging fails:** Confirm that PyInstaller is installed in the same environment as Flask and PyWebView, then review the build output.

## Limitations and safety notes

- The application **moves** files; it does not create a separate backup before moving them.
- Undo depends on the local SQLite history and the continued existence of the moved files.
- The current scanner skips the destination directory itself, but users should still select sensible, separate source and destination locations.
- Recursive scanning is disabled by default.
- The current duplicate setting is represented in configuration, while collision handling is performed by the organizer's safe-name routine.
- The application is designed for local desktop use. Do not run the Flask app as a public web service without a security review.
- Review the file preview carefully, especially when executable or script files are included.

## Contributing

Contributions and bug reports are welcome.

1. Create a fork of the repository.
2. Create a feature branch for your change.
3. Test changes with temporary folders and sample files.
4. Submit a pull request with a clear description of the change and test results.

Please avoid testing file-moving changes against important personal, system, or production folders.

## License

No license file is currently present in this repository. Unless a license is added, reuse and redistribution permissions are not explicitly granted. Add a license file if you intend to permit open-source reuse.

---

**Repository:** https://github.com/senguptajeet/CleartheClutter1.0
