import cloudscraper
import pprint

symbol = "RELIANCE"
url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"

scraper = cloudscraper.create_scraper(browser={"browser":"chrome","platform":"windows","mobile":False})
headers = {"User-Agent":"Mozilla/5.0","Accept":"application/json","Referer":"https://www.nseindia.com/"}

try:
    # initial request to set cookies / bypass protections
    scraper.get('https://www.nseindia.com', headers=headers, timeout=10)
    r = scraper.get(url, headers=headers, timeout=10)
    print('Status:', r.status_code)
    data = r.json()
    print('Top-level keys:', list(data.keys()))
    print('\nsecurityInfo sample:')
    pprint.pprint(data.get('securityInfo'))
    print('\nmarketDeptOrderBook sample:')
    pprint.pprint(data.get('marketDeptOrderBook'))
    print('\npriceInfo sample:')
    pprint.pprint(data.get('priceInfo'))
except Exception as e:
    print('Error:', e)
