import re
import json
import html
import sys

def parse_16day(path):
    with open(path) as f:
        raw = f.read()

    tooltips = re.findall(r'data-swell-tooltip="([^"]+)"', raw)
    out = []
    for t in tooltips:
        try:
            data = json.loads(html.unescape(t))
        except Exception:
            continue
        swells = [s for s in data.get('swells', []) if s]
        out.append({
            "date": data.get("date"),
            "swells": [
                {
                    "height_m": s["height"],
                    "direction": s["letters"],
                    "period_s": s["period"],
                    "energy_kj": s["energy"],
                }
                for s in swells
            ],
            "combined_energy_kj": data.get("sumEnergy"),
            "wind_state": (data.get("windState") or {}).get("text"),
            "rating": data.get("rating"),
        })
    return out

if __name__ == "__main__":
    result = parse_16day(sys.argv[1])
    with open(sys.argv[2], "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {len(result)} time slots to {sys.argv[2]}")
