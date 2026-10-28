from pathlib import Path
from typing import List, Iterator
from .logger import logger

class FileScanner:
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.excluded_dirs = set(d.lower() for d in self.settings.get("excluded_dirs", []))

    def scan(self, source_dir: Path, dest_dir: Path) -> Iterator[Path]:
        source_dir = source_dir.resolve()
        dest_dir = dest_dir.resolve()
        recursive = self.settings.get("recursive_scan", False)
        
        logger.info(f"Scanning directory: {source_dir}")
        try:
            yield from self._scan_directory(source_dir, dest_dir, recursive)
        except Exception as e:
            logger.error(f"Error scanning {source_dir}: {e}")

    def _scan_directory(self, current_dir: Path, dest_dir: Path, recursive: bool) -> Iterator[Path]:
        try:
            for item in current_dir.iterdir():
                # Skip destination directory to prevent recursion trap
                if item.resolve() == dest_dir:
                    continue
                    
                if item.is_dir():
                    if item.name.lower() in self.excluded_dirs:
                        continue
                    if recursive:
                        yield from self._scan_directory(item, dest_dir, recursive)
                elif item.is_file():
                    yield item
        except PermissionError:
            logger.warning(f"Permission denied accessing: {current_dir}")
        except Exception as e:
            logger.error(f"Error reading {current_dir}: {e}")