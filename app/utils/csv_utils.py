import csv
from io import StringIO
from typing import List, Dict, Union
from flask import Response
import pandas as pd

COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "url": ["site", "website", "url", "site_url", "website_url"],
    "login": ["username", "login", "name", "user", "user_name", "email"],
    "password": ["password", "pass", "passwd", "pwd"],
    "description": ["comments", "notes", "description", "comment"],
    "site": ["title"],
}

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map: Dict[str, str] = {}
    for std_col, synonyms in COLUMN_SYNONYMS.items():
        for syn in synonyms:
            for col in df.columns:
                if col.lower() == syn.lower():
                    col_map[col] = std_col
                    break
    df = df.rename(columns=col_map)
    return df

def parse_csv(file: Union[str, StringIO]) -> List[Dict[str, str]]:
    try:
        df: pd.DataFrame = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    df = normalize_columns(df)
    expected_cols: set[str] = set(COLUMN_SYNONYMS.keys())
    df = df[[col for col in df.columns if col in expected_cols]]
    df = df.fillna("")
    records: List[Dict[str, str]] = df.to_dict(orient="records")
    return records

def merge_passwords(
    existing_passwords: List[Dict[str, str]],
    imported_passwords: List[Dict[str, str]],
    replace_existing: bool = False,
) -> List[Dict[str, str]]:
    def key_func(p: Dict[str, str]) -> tuple[str, str]:
        url: str = p.get("url", "").strip().lower()
        login: str = p.get("login", "").strip().lower()
        return (url, login)

    existing_map: Dict[tuple[str, str], Dict[str, str]] = {key_func(p): p for p in existing_passwords}
    imported_map: Dict[tuple[str, str], Dict[str, str]] = {key_func(imp): imp for imp in imported_passwords}

    merged: List[Dict[str, str]] = []
    for p in existing_passwords:
        key: tuple[str, str] = key_func(p)
        if key in imported_map and replace_existing:
            merged.append({**p, **imported_map[key]})
        else:
            merged.append(p)

    for imp in imported_passwords:
        if key_func(imp) not in existing_map:
            merged.append(imp)

    for record in merged:
        if not record.get("site") and record.get("url"):
            record["site"] = record["url"]

    return merged


def export_passwords_to_csv(passwords: List[Dict[str, str]]) -> Response:
    fieldnames = ["url", "login", "password", "notes", "title"]

    with StringIO(newline="") as si:
        writer = csv.DictWriter(si, fieldnames=fieldnames)
        writer.writeheader()

        if isinstance(passwords, list):
            for p in passwords:
                if not isinstance(p, dict):
                    continue
                writer.writerow(
                    {
                        "url": p.get("url", ""),
                        "login": p.get("login", ""),
                        "password": p.get("password", ""),
                        "notes": p.get("description", ""),
                        "title": p.get("site", ""),
                    }
                )

        output = si.getvalue()

    return Response(
        output.encode("utf-8"),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=passwords.csv"},
    )


# def main():   
#     csv_file1 = "/home/ars/Documents/passwords.csv"
#     csv_file2 = "/home/ars/Documents/passwords(6).csv"

#     existing_passwords = parse_csv(csv_file1)


#     imported_passwords = parse_csv(csv_file2)

#     # Объединение
#     merged = merge_passwords(
#         existing_passwords, imported_passwords, replace_existing=True
#     )

#     for i, p in enumerate(merged, 1):
#         url = p.get("url", "")
#         login = p.get("login", "")
#         password = p.get("password", "")
#         description = p.get("description", "")
#         site = p.get("site", "")
#         print(
#             f"{i:03d}. Site: {site} | URL: {url} | Login: {login} | Password: {password} | Notes: {description}"
#         )


# if __name__ == "__main__":
#     main()
