import json
from pathlib import Path


class Config():
    def __init__(self):
        self.file = Path('config.json')
        if not self.file.exists():
            with open(self.file, 'w') as f:
                f.write(json.dumps({'status': 'online', 'activity_type': 'watching', 'activity_name': 'beim schlafen zu'}, indent=4))