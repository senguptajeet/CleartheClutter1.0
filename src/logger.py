import logging
from pathlib import Path
from datetime import datetime

def setup_logger():
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"clutter_{datetime.now().strftime('%Y%m%d')}.log"

    logger = logging.getLogger("ClearTheClutter")
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger

logger = setup_logger()