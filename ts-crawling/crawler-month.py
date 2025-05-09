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
    base_url = f"https://www.tagesschau.de/archiv?datum={datum_str}"
    print(f"📥 Lade: {base_url}")

    artikel = []
    page_index = 1

    while True:
        # URL für die aktuelle Seite
        url = f"{base_url}&pageIndex={page_index}"
        print(f"📥 Lade Seite {page_index}: {url}")

        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"⚠️ Fehler {res.status_code} für {url}")
            break

        soup = BeautifulSoup(res.content, "html.parser")

        # Selektor für die Artikel anpassen
        teasers = soup.select("div.teaser-right")
        if not teasers:
            print(f"🚫 Keine weiteren Artikel auf Seite {page_index}")
            break

        for teaser in teasers:
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

        # Zur nächsten Seite wechseln
        page_index += 1

    return artikel

# Funktion zum Crawlen eines Zeitbereichs
def crawl_timeframe(start_date, end_date):
    alle = []
    current_date = start_date
    while current_date <= end_date:
        # Crawle den ersten Tag des Monats
        artikel = crawl_archiv_tag(current_date)
        alle.extend(artikel)
        
        # Erhöhe den Monat um 1
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    return alle

# Hauptlauf
# Zeitbereich angeben (z. B. vom 1. Januar 2020 bis 1. Dezember 2020)
start_date = datetime(2020, 1, 1)
end_date = datetime(2024, 6, 1)

artikel = crawl_timeframe(start_date, end_date)
df = pd.DataFrame(artikel)
df.to_csv("tagesschau_headlines_test_20200101-20240601.csv", index=False, encoding="utf-8")
print(f"✅ {len(df)} Artikel gespeichert in CSV-Datei.")