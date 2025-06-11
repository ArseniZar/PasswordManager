import csv
from io import StringIO
from flask import Response

def export_passwords_to_csv(passwords: list[dict]) -> Response:
    """
    Экспортирует список словарей в CSV с колонками:
    url, username (вместо login), password.
    """
    si = StringIO()
    writer = csv.writer(si)

    # Заголовки
    writer.writerow(['url', 'username', 'password'])

    for p in passwords:
        writer.writerow([
            p.get('url', ''),
            p.get('login', ''),      # login будет в username
            p.get('password', '')
        ])

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=passwords.csv"}
    )
