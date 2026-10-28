import os
import json
from pathlib import Path
from typing import Dict, Any

class SettingsManager:
    def __init__(self):
        # Using the PyInstaller-safe path we created earlier
        base_dir = Path(os.environ.get("CTC_DATA_DIR", Path(__file__).parent.parent))
        self.config_file = base_dir / "config" / "settings.json"
        
        self.default_settings = {
            "recursive_scan": False,
            "handle_duplicates": True,
            "categories": {
                "pdf": [".pdf"],
                "docs": [".doc", ".docx", ".odt", ".rtf", ".txt", ".md", ".tex"],
                "excel": [".xls", ".xlsx", ".csv", ".tsv", ".ods"],
                "ppt": [".ppt", ".pptx", ".ppsx", ".odp"],
                "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
                "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
                "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
                "Programs": [".exe", ".msi", ".bat", ".cmd", ".ps1", ".apk", ".dmg"]
            },
            "excluded_dirs": ["Windows", "Program Files", "ProgramData", "$Recycle.Bin", ".git"]
        }
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            self.save_settings(self.default_settings)
            return self.default_settings
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self.default_settings

    def save_settings(self, settings_dict: Dict[str, Any]):
        # Ensure the directory exists before saving
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(settings_dict, f, indent=4)
        self.settings = settings_dict

    def get(self, key: str, default=None):
        return self.settings.get(key, default)