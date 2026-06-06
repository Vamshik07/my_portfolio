import json
from pathlib import Path

def profile(request):
    p = Path(__file__).resolve().parents[1] / 'data' / 'profile.json'
    data = {}
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}
    return {'profile_data': data}
