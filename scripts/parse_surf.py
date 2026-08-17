import re
import json
import html
import sys
import math


def get_row_cells(raw, row_name, next_row_name):
    """Return list of <td> inner-HTML strings for a given data-row, in column order."""
    start_marker = f'data-row="{row_name}"'
    idx = raw.find(start_marker)
    if idx == -1:
        return []
    end_marker = f'data-row="{next_row_name}"' if next_row_name else None
    end = raw.find(end_marker, idx) if end_marker else len(raw)
    if end == -1:
        end = len(raw)
    section = raw[idx:end]
    return re.findall(r'<td class="forecast-table__cell">(.*?)</td>\s*(?=<td|</tr)', section, re.S)


def parse_wind(cell):
    if not cell:
        return None
    m = re.search(r'data-speed="([\d.]+)"', cell)
    d = re.search(r'wind-icon__letters">([A-Z]+)<', cell)
    if not m:
        return None
    return {"speed_kmh": float(m.group(1)), "direction": d.group(1) if d else None}


def parse_tide(cell):
    if not cell:
        return None
    m = re.search(r'tide-time__time[^"]*">\s*([\d:APM]+)</span><span class="tide-time__height">([-\d.]+)', cell)
    if not m:
        return None
    return {"time": m.group(1).strip(), "height_m": float(m.group(2))}


def parse_temp(cell):
    if not cell:
        return None
    m = re.search(r'data-value="([-\d.]+)"', cell)
    return float(m.group(1)) if m else None


def parse_rain(cell):
    if not cell:
        return None
    m = re.search(r'data-value="([\d.]+)"', cell)
    return float(m.group(1)) if m else 0.0


def parse_weather(cell):
    if not cell:
        return None
    m = re.search(r'alt="([^"]+)"', cell)
    return m.group(1).strip() if m else None


def parse_suntime(cell):
    if not cell:
        return None
    m = re.search(r'<span>([^<]+)</span>', cell)
    if not m:
        return None
    v = m.group(1).strip()
    return None if v == '\u2014' else v


def parse_sea_temperature_today(raw):
    m = re.search(r"sea temperature is.*?data-value=\"([\d.]+)\"", raw, re.S)
    return float(m.group(1)) if m else None


def load_current_data(path):
    """Load Open-Meteo current data and return dict keyed by ISO datetime."""
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Warning: current data file not found at {path}", file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(f"Warning: could not parse JSON from {path}: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Warning: error loading current data from {path}: {e}", file=sys.stderr)
        return {}
    
    current_by_time = {}
    times = data.get("hourly", {}).get("time", [])
    u_vals = data.get("hourly", {}).get("ocean_current_u", [])
    v_vals = data.get("hourly", {}).get("ocean_current_v", [])
    
    for i, timestamp in enumerate(times):
        if i < len(u_vals) and i < len(v_vals):
            u = u_vals[i]
            v = v_vals[i]
            # Store both components and derived values
            speed_ms = math.sqrt(u**2 + v**2) if u is not None and v is not None else None
            speed_kmh = speed_ms * 3.6 if speed_ms is not None else None
            # Direction in degrees: 0=N, 90=E, 180=S, 270=W
            # v is north-south (positive=N), u is east-west (positive=E)
            if u is not None and v is not None:
                direction_rad = math.atan2(u, v)  # atan2(E, N)
                direction_deg = (math.degrees(direction_rad) + 360) % 360
            else:
                direction_deg = None
            
            current_by_time[timestamp] = {
                "current_u_ms": u,  # east-west component (m/s)
                "current_v_ms": v,  # north-south component (m/s), positive = northward
                "current_speed_ms": speed_ms,
                "current_speed_kmh": speed_kmh,
                "current_direction_deg": direction_deg,  # 0=N, 90=E, 180=S, 270=W
            }
    
    return current_by_time


def get_row_cells(raw, row_name, next_row_name):
    """Return list of <td> inner-HTML strings for a given data-row, in column order."""
    start_marker = f'data-row="{row_name}"'
    idx = raw.find(start_marker)
    if idx == -1:
        return []
    end_marker = f'data-row="{next_row_name}"' if next_row_name else None
    end = raw.find(end_marker, idx) if end_marker else len(raw)
    if end == -1:
        end = len(raw)
    section = raw[idx:end]
    return re.findall(r'<td class="forecast-table__cell">(.*?)</td>\s*(?=<td|</tr)', section, re.S)


def parse_wind(cell):
    if not cell:
        return None
    m = re.search(r'data-speed="([\d.]+)"', cell)
    d = re.search(r'wind-icon__letters">([A-Z]+)<', cell)
    if not m:
        return None
    return {"speed_kmh": float(m.group(1)), "direction": d.group(1) if d else None}


def parse_tide(cell):
    if not cell:
        return None
    m = re.search(r'tide-time__time[^"]*">\s*([\d:APM]+)</span><span class="tide-time__height">([-\d.]+)', cell)
    if not m:
        return None
    return {"time": m.group(1).strip(), "height_m": float(m.group(2))}


def parse_temp(cell):
    if not cell:
        return None
    m = re.search(r'data-value="([-\d.]+)"', cell)
    return float(m.group(1)) if m else None


def parse_rain(cell):
    if not cell:
        return None
    m = re.search(r'data-value="([\d.]+)"', cell)
    return float(m.group(1)) if m else 0.0


def parse_weather(cell):
    if not cell:
        return None
    m = re.search(r'alt="([^"]+)"', cell)
    return m.group(1).strip() if m else None


def parse_suntime(cell):
    if not cell:
        return None
    m = re.search(r'<span>([^<]+)</span>', cell)
    if not m:
        return None
    v = m.group(1).strip()
    return None if v == '\u2014' else v


def parse_sea_temperature_today(raw):
    m = re.search(r"sea temperature is.*?data-value=\"([\d.]+)\"", raw, re.S)
    return float(m.group(1)) if m else None


def parse_page(path):
    with open(path) as f:
        raw = f.read()

    tooltips_raw = re.findall(r'data-swell-tooltip="([^"]+)"', raw)

    wind_cells = get_row_cells(raw, "wind", "wind-state")
    tide_high_cells = get_row_cells(raw, "tide-high", "tide-low")
    tide_low_cells = get_row_cells(raw, "tide-low", "tabs")
    temp_cells = get_row_cells(raw, "temperature-max", "temperature-max_feel")
    rain_cells = get_row_cells(raw, "rain", "temperature-max")
    weather_cells = get_row_cells(raw, "weather", "sunrise")
    sunrise_cells = get_row_cells(raw, "sunrise", "sunset")
    sunset_cells = get_row_cells(raw, "sunset", "rain")

    def safe(lst, i):
        return lst[i] if i < len(lst) else None

    out = []
    for i, t in enumerate(tooltips_raw):
        try:
            data = json.loads(html.unescape(t))
        except Exception:
            continue
        swells = [s for s in data.get("swells", []) if s]

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
            "wind": parse_wind(safe(wind_cells, i)),
            "tide_high": parse_tide(safe(tide_high_cells, i)),
            "tide_low": parse_tide(safe(tide_low_cells, i)),
            "air_temp_c": parse_temp(safe(temp_cells, i)),
            "rain_mm": parse_rain(safe(rain_cells, i)),
            "weather_code": parse_weather(safe(weather_cells, i)),
            "sunrise": parse_suntime(safe(sunrise_cells, i)),
            "sunset": parse_suntime(safe(sunset_cells, i)),
        })

    return out, parse_sea_temperature_today(raw)


if __name__ == "__main__":
    hourly_path, sixday_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    hourly, sea_temp_h = parse_page(hourly_path)
    sixday, sea_temp_s = parse_page(sixday_path)

    result = {
        "sea_temperature_today_c": sea_temp_h or sea_temp_s,
        "hourly": hourly,
        "sixteen_day": sixday,
    }

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {len(hourly)} hourly slots + {len(sixday)} 16-day slots to {out_path}")
