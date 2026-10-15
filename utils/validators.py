import re

def validate_url(url: str) -> bool:
    regex = re.compile(
        r'^(https?://)?'
        r'(([A-Z0-9][A-Z0-9-]*[A-Z0-9]\.)+[A-Z]{2,6}|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?(?:/[-A-Z0-9+&@#/%=~_|?$਼]*)?$',
        re.IGNORECASE
    )
    return bool(regex.match(url))