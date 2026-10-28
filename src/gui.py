import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import time
from pathlib import Path
import os

from .settings_manager import SettingsManager
from .file_classifier import FileClassifier
from .file_scanner import FileScanner
from .file_organizer import FileOrganizer
from .logger import logger

class ClearTheClutterApp:
    def __init__(self, root):
        self.root = root
        self.settings_manager = SettingsManager()
        self.classifier = FileClassifier(self.settings_manager)
        self.scanner = FileScanner(self.settings_manager)
        self.msg_queue = queue.Queue()
        self.organizer = FileOrganizer(self.classifier, self.msg_queue)
        
        self.files_plan = []
        self.is_processing = False
        
        self.setup_ui()
        self.root.after(100, self.process_queue)

    def setup_ui(self):
        # Top Frame for Paths
        path_frame = ttk.LabelFrame(self.root, text="Folder Selection", padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=5)

        self.source_var = tk.StringVar()
        ttk.Label(path_frame, text="Source Folder:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(path_frame, textvariable=self.source_var, width=60).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(path_frame, text="Browse", command=self.browse_source).grid(row=0, column=2)

        self.dest_var = tk.StringVar()
        ttk.Label(path_frame, text="Destination Folder:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(path_frame, textvariable=self.dest_var, width=60).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(path_frame, text="Browse", command=self.browse_dest).grid(row=1, column=2)

        # Dashboard / Stats Frame
        stats_frame = ttk.LabelFrame(self.root, text="Dashboard", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        self.lbl_stats = ttk.Label(stats_frame, text="Ready to scan. Select source and destination folders.")
        self.lbl_stats.pack(fill=tk.X)

        # Buttons Frame
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill=tk.X)
        
        self.btn_scan = ttk.Button(btn_frame, text="Scan Files", command=self.start_scan)
        self.btn_scan.pack(side=tk.LEFT, padx=5)
        
        self.btn_org = ttk.Button(btn_frame, text="Organize Files", command=self.start_organize, state=tk.DISABLED)
        self.btn_org.pack(side=tk.LEFT, padx=5)
        
        self.btn_cancel = ttk.Button(btn_frame, text="Cancel", command=self.cancel_operation, state=tk.DISABLED)
        self.btn_cancel.pack(side=tk.LEFT, padx=5)

        self.btn_undo = ttk.Button(btn_frame, text="Undo Last", command=self.undo_last)
        self.btn_undo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Open Destination", command=self.open_dest).pack(side=tk.RIGHT, padx=5)

        # Treeview (Preview)
        tree_frame = ttk.Frame(self.root, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        cols = ("Name", "Ext", "Category", "Size")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        self.tree.column("Name", width=300)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Progress Frame
        prog_frame = ttk.Frame(self.root, padding=10)
        prog_frame.pack(fill=tk.X)
        
        self.prog_var = tk.DoubleVar()
        self.prog_bar = ttk.Progressbar(prog_frame, variable=self.prog_var, maximum=100)
        self.prog_bar.pack(fill=tk.X)
        
        self.lbl_status = ttk.Label(prog_frame, text="Idle")
        self.lbl_status.pack(fill=tk.X, pady=5)

    def browse_source(self):
        d = filedialog.askdirectory()
        if d: self.source_var.set(d)

    def browse_dest(self):
        d = filedialog.askdirectory()
        if d: self.dest_var.set(d)

    def set_gui_state(self, processing: bool):
        self.is_processing = processing
        st = tk.DISABLED if processing else tk.NORMAL
        self.btn_scan.config(state=st)
        self.btn_org.config(state=tk.DISABLED if processing or not self.files_plan else tk.NORMAL)
        self.btn_cancel.config(state=tk.NORMAL if processing else tk.DISABLED)
        self.btn_undo.config(state=st)

    def start_scan(self):
        src = self.source_var.get()
        dst = self.dest_var.get()
        if not src or not dst:
            messagebox.showwarning("Missing Folders", "Please select source and destination folders.")
            return
            
        self.files_plan.clear()
        self.tree.delete(*self.tree.get_children())
        self.set_gui_state(True)
        self.lbl_status.config(text="Scanning...")
        self.prog_var.set(0)
        
        threading.Thread(target=self._scan_thread, args=(Path(src), Path(dst)), daemon=True).start()

    def _scan_thread(self, src: Path, dst: Path):
        try:
            files = list(self.scanner.scan(src, dst))
            stats = {"Documents": 0, "Images": 0, "Videos": 0, "Compressed": 0, "Programs": 0, "Others": 0}
            
            for f in files:
                cat = self.classifier.classify(f)
                stats[cat] = stats.get(cat, 0) + 1
                size_kb = f.stat().st_size / 1024
                self.files_plan.append((f, cat))
                self.msg_queue.put({"type": "tree_insert", "values": (f.name, f.suffix, cat, f"{size_kb:.1f} KB")})
                
            self.msg_queue.put({"type": "scan_done", "stats": stats, "total": len(files)})
        except Exception as e:
            logger.error(f"Scan thread error: {e}")
            self.msg_queue.put({"type": "status", "msg": "Error during scan. See logs."})
            self.msg_queue.put({"type": "scan_done", "stats": {}, "total": 0})

    def start_organize(self):
        if not self.files_plan:
            return
        
        # Warning for executable files
        has_programs = any(cat == "Programs" for _, cat in self.files_plan)
        if has_programs:
            if not messagebox.askyesno("Executable Warning", "Program files (.exe, .msi, etc.) were found. Move them safely?"):
                return

        src = Path(self.source_var.get())
        dst = Path(self.dest_var.get())
        
        self.set_gui_state(True)
        self.lbl_status.config(text="Organizing files...")
        
        threading.Thread(target=self.organizer.organize, args=(self.files_plan, src, dst), daemon=True).start()

    def cancel_operation(self):
        if self.is_processing:
            self.organizer.cancel_event.set()
            self.lbl_status.config(text="Cancelling... Please wait.")

    def undo_last(self):
        if messagebox.askyesno("Confirm Undo", "Reverse the last organization batch?"):
            res = self.organizer.undo_latest_batch()
            messagebox.showinfo("Undo Result", res)
            self.files_plan.clear()
            self.tree.delete(*self.tree.get_children())
            self.lbl_stats.config(text="Undo completed. Rescan required.")

    def open_dest(self):
        dst = self.dest_var.get()
        if dst and Path(dst).exists():
            os.startfile(dst)

    def process_queue(self):
        while not self.msg_queue.empty():
            try:
                msg = self.msg_queue.get_nowait()
                mtype = msg.get("type")
                
                if mtype == "tree_insert":
                    self.tree.insert("", tk.END, values=msg["values"])
                elif mtype == "status":
                    self.lbl_status.config(text=msg["msg"])
                elif mtype == "progress":
                    c, t = msg["current"], msg["total"]
                    self.prog_var.set((c / t) * 100)
                    self.lbl_status.config(text=f"Moving: {msg['file']} ({c}/{t})")
                elif mtype == "scan_done":
                    self.set_gui_state(False)
                    stats = msg["stats"]
                    stat_txt = f"Total: {msg['total']} | Docs: {stats.get('Documents',0)} | Img: {stats.get('Images',0)} | Vid: {stats.get('Videos',0)} | Prog: {stats.get('Programs',0)}"
                    self.lbl_stats.config(text=stat_txt)
                    self.lbl_status.config(text="Scan complete. Review preview below.")
                elif mtype == "done":
                    self.set_gui_state(False)
                    self.lbl_status.config(text=f"Done! Moved: {msg['success']}, Errors: {msg['errors']}")
                    messagebox.showinfo("Complete", f"Successfully organized {msg['success']} files.")
                    self.files_plan.clear()
            except queue.Empty:
                break
        self.root.after(100, self.process_queue)

    def on_close(self):
        if self.is_processing:
            if messagebox.askokcancel("Quit", "Operation in progress. Are you sure you want to quit?"):
                self.organizer.cancel_event.set()
                self.root.destroy()
        else:
            self.root.destroy()