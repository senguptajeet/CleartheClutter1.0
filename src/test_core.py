import unittest
from pathlib import Path
import tempfile
import shutil
from src.settings_manager import SettingsManager
from src.file_classifier import FileClassifier
from src.file_organizer import FileOrganizer
import queue

class TestCoreLogic(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.src_dir = Path(self.test_dir) / "source"
        self.dest_dir = Path(self.test_dir) / "dest"
        self.src_dir.mkdir()
        self.dest_dir.mkdir()
        
        # Create dummy files
        (self.src_dir / "report.pdf").touch()
        (self.src_dir / "holiday.JPG").touch()
        (self.src_dir / "setup.exe").touch()
        (self.src_dir / "unknown.xyz").touch()
        
        self.settings = SettingsManager()
        self.classifier = FileClassifier(self.settings)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_classification(self):
        self.assertEqual(self.classifier.classify(self.src_dir / "report.pdf"), "Documents")
        # Test case-insensitivity
        self.assertEqual(self.classifier.classify(self.src_dir / "holiday.JPG"), "Images")
        self.assertEqual(self.classifier.classify(self.src_dir / "setup.exe"), "Programs")
        self.assertEqual(self.classifier.classify(self.src_dir / "unknown.xyz"), "Others")

    def test_duplicate_handling(self):
        q = queue.Queue()
        organizer = FileOrganizer(self.classifier, q)
        
        # Fake existing destination file
        target_dir = self.dest_dir / "Documents"
        target_dir.mkdir()
        target_file = target_dir / "report.pdf"
        target_file.touch()
        
        safe_path = organizer.get_safe_destination(target_file)
        self.assertEqual(safe_path.name, "report (1).pdf")

if __name__ == "__main__":
    unittest.main()