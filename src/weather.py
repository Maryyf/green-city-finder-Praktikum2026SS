import requests
from datetime import date, timedelta

RAIN_CODES = {61, 63, 65, 80, 81, 82, 95, 96, 99}

def will_not_rain(lat, lon, days=3, precip_thresh=0.2, start_date=None, end_date=None):
    if start_date and end_date:
        from datetime import datetime
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
    else:
        start = date.today() + timedelta(days=1)
        end = start + timedelta(days=days-1)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,weathercode",
        "timezone": "auto",
        "start_date": start.isoformat(),
        "end_date": end.isoformat()
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    daily = j.get("daily", {})
    times = daily.get("time", [])
    precs = daily.get("precipitation_sum", [])
    codes = daily.get("weathercode", [])
    result = []
    for d, p, c in zip(times, precs, codes):
        no_rain = (p is not None and p <= precip_thresh) and (c not in RAIN_CODES)
        result.append({"date": d, "precip_mm": p, "weathercode": c, "no_rain": no_rain})
    return result

if __name__ == "__main__":
    # 测试示例
    print(will_not_rain(48.8566, 2.3522, days=3))

"""
weathercode：0: Clear sky
    1: Mainly clear
2: Partly cloudy
3: Overcast
45,48: Fog / depositing rime fog
51,53,55: Drizzle
61,63,65: Rain
66,67: Freezing rain
71,73,75: Snow fall
77: Snow grains
80,81,82: Rain showers
85,86: Snow showers
95: Thunderstorm
96,99: Thunderstorm with hail
"""