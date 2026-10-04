"""Small, local record file. Broken or missing saves never stop the game."""
import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent / 'saves' / 'records.json'

def load(path=DEFAULT_PATH):
    try:
        data = json.loads(Path(path).read_text())
        return {key: max(0, min(10**9, int(data.get(key, 0)))) for key in ('score', 'shift', 'served')}
    except (OSError, ValueError, TypeError, AttributeError):
        return {'score': 0, 'shift': 0, 'served': 0}

def save(game, path=DEFAULT_PATH):
    path = Path(path)
    old = load(path)
    data = {'score': max(old['score'], game.score), 'shift': max(old['shift'], game.shift), 'served': max(old['served'], game.served)}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(data, indent=2)); temporary.replace(path)
        return True
    except OSError:
        return False
