# Clear The Clutter
*Organize Your Files. Simplify Your Digital Life.*

Clear The Clutter is a safe, locally run Python desktop application built to automatically organize files into categorized folders based on their extensions. It utilizes `Tkinter` for a seamless desktop experience without needing external software installs or dependencies.

## Features
- **Smart Classification:** Sorts files into Documents, Images, Videos, Compressed, Programs, and Others.
- **Safety First:** Prevents silent overwriting with automatic duplicate handling `(1)`.
- **Protected Environment Checks:** Excludes critical Windows folders automatically.
- **Undo Architecture:** Powered by a local SQLite transaction log allowing you to reverse recent moves.
- **Responsive GUI:** Asynchronous background worker threads ensure the UI never freezes during large operations.

## System Requirements
- OS: Windows 10 or Windows 11
- Python: 3.8+ (if running from source)

## How to Run (Development)
1. Ensure Python 3 is installed.
2. Clone or download this repository.
3. Open a terminal/command prompt in the `Clear-The-Clutter` directory.
4. Run: `python main.py`

## Testing Instructions
To verify the core file management logic safely:
1. Open terminal in the project root.
2. Run: `python -m unittest tests/test_core.py`
*(Tests use synthetic temp directories and will never harm your real files).*

## Packaging as a Standalone Windows Executable
You can build a single `.exe` file that users can run without installing Python using PyInstaller.

1. Create a virtual environment (optional but recommended):
   ```cmd
   python -m venv venv
   call venv\Scripts\activate