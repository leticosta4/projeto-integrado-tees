from pathlib import Path

class FileLister:
    def list(self) -> list[Path]:
        path = Path('data')
        files = list(path.glob('*.xml'))
        return files
