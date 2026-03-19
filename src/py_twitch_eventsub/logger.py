import logging
from rich.logging import RichHandler

from pathlib import Path
from datetime import datetime

class FileCompatibleFormatter(logging.Formatter):
    fmt = "[%(asctime)s] [%(levelname)-8s] [%(filename)s:%(lineno)d] -> %(message)s"

    def format(self, record):
        formatter = logging.Formatter(self.fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logging(name: str, level = logging.INFO, console: bool = True) -> logging.Logger:
    initial: logging.Logger = logging.getLogger(name=name)
    initial.setLevel(level)
    
    initial.addHandler(RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_path=True
    ))
    
    path: Path = Path("logs/")
    if not path.exists():
        path.mkdir(parents=True)    
    
    if not initial.hasHandlers():    
        date: str = datetime.now().date().strftime("%Y-%m-%d.log")
        filename: Path = path.joinpath(f"{date.replace("-", ".")}")
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(FileCompatibleFormatter())
        file_handler.setLevel(level)
        
        if console:
            stream_handler: logging.StreamHandler = logging.StreamHandler()
            stream_handler.setLevel(level)
            initial.addHandler(stream_handler)
        initial.addHandler(file_handler)
    
    return initial