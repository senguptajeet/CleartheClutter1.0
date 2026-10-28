import shutil
import uuid
from pathlib import Path
from threading import Event
from .logger import logger
from .operation_history import HistoryManager

class FileOrganizer:
    def __init__(self, classifier, queue):
        self.classifier = classifier
        self.queue = queue
        self.history = HistoryManager()
        self.cancel_event = Event()

    def get_safe_destination(self, dest_path: Path) -> Path:
        if not dest_path.exists():
            return dest_path
        
        counter = 1
        while True:
            new_name = f"{dest_path.stem} ({counter}){dest_path.suffix}"
            new_path = dest_path.parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def organize(self, files_plan: list, source_dir: Path, dest_dir: Path):
        self.cancel_event.clear()
        batch_id = str(uuid.uuid4())
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for idx, (file_path, category) in enumerate(files_plan):
            if self.cancel_event.is_set():
                self.queue.put({"type": "status", "msg": "Operation cancelled by user."})
                break
                
            try:
                target_folder = dest_dir / category
                target_folder.mkdir(parents=True, exist_ok=True)
                
                target_path = self.get_safe_destination(target_folder / file_path.name)
                
                # Move file
                shutil.move(str(file_path), str(target_path))
                self.history.record_move(batch_id, str(file_path), str(target_path))
                success_count += 1
                
                self.queue.put({"type": "progress", "current": idx + 1, "total": len(files_plan), "file": file_path.name})
            except Exception as e:
                logger.error(f"Failed to move {file_path}: {e}")
                error_count += 1
                
        self.queue.put({"type": "done", "success": success_count, "errors": error_count})

    def undo_latest_batch(self):
        batch_id = self.history.get_latest_batch_id()
        if not batch_id:
            return "No operations to undo."
            
        ops = self.history.get_operations_by_batch(batch_id)
        restored = 0
        errors = 0
        
        for op_id, orig_path_str, new_path_str in ops:
            orig_path = Path(orig_path_str)
            new_path = Path(new_path_str)
            
            if new_path.exists() and not orig_path.exists():
                try:
                    orig_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(new_path), str(orig_path))
                    self.history.mark_undone(op_id)
                    restored += 1
                except Exception as e:
                    logger.error(f"Undo failed for {new_path}: {e}")
                    errors += 1
            else:
                errors += 1
                
        return f"Undo complete. Restored: {restored}, Errors: {errors}"