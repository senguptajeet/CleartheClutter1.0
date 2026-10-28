from pathlib import Path
from typing import Dict

class FileClassifier:
    def __init__(self, settings_manager):
        self.categories = settings_manager.get("categories", {})
        self._build_extension_map()

    def _build_extension_map(self):
        self.ext_map = {}
        for category, extensions in self.categories.items():
            for ext in extensions:
                self.ext_map[ext.lower()] = category

    def classify(self, file_path: Path) -> str:
        # Handle multi-part extensions like .tar.gz, falling back to final suffix
        ext = file_path.suffix.lower()
        if ext in self.ext_map:
            return self.ext_map[ext]
        return "Others"