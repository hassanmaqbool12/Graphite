import requests

# 1. Primary method (fast, no key, unofficial Google endpoint)
def _google_free(text, source="en", target="ur"):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": source,
        "tl": target,
        "dt": "t",
        "q": text
    }

    r = requests.get(url, params=params, timeout=5)
    r.raise_for_status()
    return r.json()[0][0][0]


# 2. Fallback method (MyMemory API - more stable, limited)
def _mymemory(text, source="en", target="ur"):
    url = "https://api.mymemory.translated.net/get"
    params = {
        "q": text,
        "langpair": f"{source}|{target}"
    }

    r = requests.get(url, params=params, timeout=5)
    r.raise_for_status()
    data = r.json()
    return data["responseData"]["translatedText"]


# 3. Main function with fallback logic
def translate(text, source  , target):
    try:
        return _google_free(text, source, target)
    except Exception:
        try:
            return _mymemory(text, source, target)
        except Exception:
            return "Translation failed"