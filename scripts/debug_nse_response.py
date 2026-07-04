import requests
import pprint

symbol = "RELIANCE"
url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json, text/plain, */*",
}

s = requests.Session()
try:
    # Initial request to set cookies/headers
    s.get("https://www.nseindia.com", headers=headers, timeout=10)
except Exception as e:
    print("Initial homepage request failed:", e)

try:
    r = s.get(url, headers=headers, timeout=10)
    print("Status:", r.status_code)
    try:
        data = r.json()
        print("Top-level keys:", list(data.keys()))
        print('\nSample securityInfo:')
        pprint.pprint(data.get('securityInfo'), depth=2)
        print('\nSample tradeInfo / summary:')
        pprint.pprint({k: data.get(k) for k in ['priceInfo','dayHighLow','totalTradedVolume']}, depth=2)
    except Exception as e:
        print('JSON decode failed:', e)
        print('Text snippet:', r.text[:2000])
except Exception as e:
    print('API request failed:', e)
