def search_passwords(passwords, query):
    results = []
    q = query.lower()
    for p in passwords:
        if (
            q in (p["url"] or "").lower()
            or q in (p["login"] or "").lower()
            or q in (p["site"] or "").lower()
            or q in (p["description"] or "").lower()
        ):
            results.append(p)
    return results