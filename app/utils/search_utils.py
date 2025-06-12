from typing import List, Dict

def search_passwords(passwords: List[Dict[str, str]], query: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    q = query.lower()
    for p in passwords:
        if (
            q in p.get("url", "").lower()
            or q in p.get("login", "").lower()
            or q in p.get("site", "").lower()
            or q in p.get("description", "").lower()
        ):
            results.append(p)
    return results