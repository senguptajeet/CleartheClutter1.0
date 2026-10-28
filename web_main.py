import os
import sys
import queue
import threading
from pathlib import Path

# --- PyInstaller Path Routing ---
if getattr(sys, 'frozen', False):
    # Running as a bundled .exe
    bundle_dir = sys._MEIPASS 
    # CRITICAL FIX: Save writable files to the Windows AppData folder, not Program Files
    app_data_dir = Path(os.getenv('APPDATA')) / "ClearTheClutter"
else:
    # Running as a normal Python script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    app_data_dir = Path(bundle_dir)

# CRITICAL FIX: Tell Python exactly where to find the 'src' folder
sys.path.insert(0, bundle_dir)

# Export the data directory so the src/ modules know where to save files permanently
os.environ["CTC_DATA_DIR"] = str(app_data_dir)

# --- Initialize Flask with absolute paths ---
from flask import Flask, render_template, request, jsonify
import webview

app = Flask(__name__, 
            template_folder=os.path.join(bundle_dir, 'templates'),
            static_folder=os.path.join(bundle_dir, 'static'))

# Import your EXACT EXISTING business logic
from src.settings_manager import SettingsManager
from src.file_classifier import FileClassifier
from src.file_scanner import FileScanner
from src.file_organizer import FileOrganizer
from src.logger import logger

# Global state
settings_manager = SettingsManager()
classifier = FileClassifier(settings_manager)
scanner = FileScanner(settings_manager)
msg_queue = queue.Queue()
organizer = FileOrganizer(classifier, msg_queue)

current_files_plan = []
scan_stats = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/browse')
def browse():
    if webview.windows:
        window = webview.windows[0]
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        folder = result[0] if result else ""
        return jsonify({"path": folder})
    return jsonify({"error": "Window not initialized"}), 500

@app.route('/api/scan', methods=['POST'])
def start_scan():
    global current_files_plan, scan_stats
    data = request.json
    src = Path(data.get('source', ''))
    dst = Path(data.get('dest', ''))
    
    if not src.exists() or not dst.exists():
        return jsonify({"error": "Invalid paths"}), 400

    current_files_plan.clear()
    scan_stats = {"Documents": 0, "Images": 0, "Videos": 0, "Compressed": 0, "Programs": 0, "Others": 0, "pdf": 0, "docs": 0, "excel": 0, "ppt": 0}
    
    while not msg_queue.empty(): msg_queue.get()

    def scan_thread():
        try:
            files = list(scanner.scan(src, dst))
            for f in files:
                cat = classifier.classify(f)
                scan_stats[cat] = scan_stats.get(cat, 0) + 1
                size_kb = f.stat().st_size / 1024
                current_files_plan.append((f, cat))
                msg_queue.put({
                    "type": "tree_insert", 
                    "name": f.name, "ext": f.suffix, "cat": cat, "size": f"{size_kb:.1f} KB"
                })
            msg_queue.put({"type": "scan_done", "stats": scan_stats, "total": len(files)})
        except Exception as e:
            msg_queue.put({"type": "status", "msg": f"Error: {str(e)}"})
            msg_queue.put({"type": "scan_done", "stats": {}, "total": 0})

    threading.Thread(target=scan_thread, daemon=True).start()
    return jsonify({"status": "Scanning started"})

@app.route('/api/organize', methods=['POST'])
def start_organize():
    data = request.json
    src = Path(data.get('source'))
    dst = Path(data.get('dest'))
    
    if not current_files_plan:
        return jsonify({"error": "No files to organize"}), 400
        
    threading.Thread(target=organizer.organize, args=(current_files_plan, src, dst), daemon=True).start()
    return jsonify({"status": "Organization started"})

@app.route('/api/undo', methods=['POST'])
def undo():
    res = organizer.undo_latest_batch()
    current_files_plan.clear()
    return jsonify({"message": res})

@app.route('/api/cancel', methods=['POST'])
def cancel():
    organizer.cancel_event.set()
    return jsonify({"status": "Cancellation requested"})

@app.route('/api/status')
def get_status():
    messages = []
    while not msg_queue.empty():
        messages.append(msg_queue.get_nowait())
    return jsonify({"messages": messages})


if __name__ == '__main__':
    # Ensure directories exist in the safe AppData folder
    app_run_dir = Path(app_data_dir)
    (app_run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (app_run_dir / "config").mkdir(parents=True, exist_ok=True)
    (app_run_dir / "data").mkdir(parents=True, exist_ok=True)

    # --- CLOSE SPLASH SCREEN EARLY ---
    try:
        import pyi_splash
        pyi_splash.close()
    except ImportError:
        pass  # Running from standard Python script, ignore

    # Create the PyWebView standalone desktop window
    window = webview.create_window(
        title='Clear The Clutter', 
        url=app,                  
        width=1050, 
        height=750,
        min_size=(800, 600),
        background_color='#0f172a'
    )
    
    # Start the native window loop
    webview.start(debug=False)
