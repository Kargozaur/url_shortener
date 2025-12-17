import re


def extract_domain(url):
    pattern = r"^(?:https?:\/\/)?(?:[^@\n]+@)?([^:\/\n?]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None
