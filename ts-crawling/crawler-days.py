import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# HTTP-Header für die Anfrage
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.tagesschau.de/archiv",
    "Upgrade-Insecure-Requests": "1"
}

# Funktion zum Crawlen der Headlines eines bestimmten Tages
def crawl_archiv_tag(datum):
    datum_str = datum.strftime("%Y-%m-%d")
    url = f"https://www.tagesschau.de/archiv?datum={datum_str}"
    print(f"📥 Lade: {url}")

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"⚠️ Fehler {res.status_code} für {datum_str}")
        return []

    soup = BeautifulSoup(res.content, "html.parser")
    artikel = []

    # Selektor für die Artikel anpassen
    for teaser in soup.select("div.teaser-right"):
        titel_tag = teaser.select_one("span.teaser-right__headline")
        titel = titel_tag.get_text(strip=True) if titel_tag else "Kein Titel"

        labeltop_tag = teaser.select_one("span.teaser-right__labeltopline")
        labeltop = labeltop_tag.get_text(strip=True) if labeltop_tag else "Kein Label"

        shortext_tag = teaser.select_one("p.teaser-right__shorttext")
        shortext = shortext_tag.get_text(strip=True) if shortext_tag else "Kein Shorttext"

        autor_tag = shortext_tag.select_one("em") if shortext_tag else None
        autor = autor_tag.get_text(strip=True) if autor_tag else "Kein Autor"

        link_tag = teaser.select_one("a.teaser-right__link")
        link = link_tag["href"] if link_tag else "Kein Link"
        if not link.startswith("http"):
            link = "https://www.tagesschau.de" + link

        # Datum aus dem HTML extrahieren und in ISO-Format umwandeln
        datum_tag = teaser.select_one("div.teaser-right__date")
        raw_datum = datum_tag.get_text(strip=True) if datum_tag else "Kein Datum"
        try:
            # Konvertiere das Datum in ISO-Format
            datum_iso = datetime.strptime(raw_datum, "%d.%m.%Y • %H:%M Uhr").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            datum_iso = "Unbekannt"

        # Ressort aus der URL extrahieren
        ressort = link.split("/")[3] if link != "Kein Link" else "Unbekannt"

        artikel.append({
            "datum": datum_iso,
            "titel": titel,
            "ressort": ressort,
            "labeltop": labeltop,
            "shorttext": shortext,
            "autor": autor,
            "link": link
        })

    return artikel

# Funktion zum Crawlen eines Zeitbereichs
def crawl_timeframe(start_date, end_date):
    alle = []
    current_date = start_date
    while current_date <= end_date:
        artikel = crawl_archiv_tag(current_date)
        alle.extend(artikel)
        current_date += timedelta(days=1)
    return alle

# Hauptlauf
# Zeitbereich angeben (z. B. vom 1. Juni 2025 bis 8. Mai 2025)
start_date = datetime(2024, 6, 1)
end_date = datetime(2025, 5, 1)

artikel = crawl_timeframe(start_date, end_date)
df = pd.DataFrame(artikel)
df.to_csv("tagesschau_headlines_20240601-20250501.csv", index=False, encoding="utf-8")
print(f"✅ {len(df)} Artikel gespeichert in der CSV-Datei.")