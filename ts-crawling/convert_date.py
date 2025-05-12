import csv
from datetime import datetime
import pytz

# Eingabedatei (CSV-Datei mit den ursprünglichen Daten)
input_file = 'tagesschau_headlines_2006-2025.csv'

# Ausgabedatei (CSV-Datei mit aktualisierten Datumsformaten)
output_file = 'output.csv'

# Zeitzone für Berlin
berlin_tz = pytz.timezone('Europe/Berlin')

# Funktion zur Konvertierung des Datumsformats mit Zeitzone
def convert_to_iso_format_with_timezone(date_str):
    try:
        # Ursprüngliches Datumsformat
        original_format = "%Y-%m-%d %H:%M:%S"
        # Datumsumwandlung
        naive_date = datetime.strptime(date_str, original_format)
        # Lokalisieren in der Berlin-Zeitzone (automatische Berücksichtigung von Sommer-/Winterzeit)
        localized_date = berlin_tz.localize(naive_date)
        # ISO 8601-Format mit Zeitzone
        return localized_date.isoformat()
    except ValueError:
        # Falls das Datum nicht im erwarteten Format ist, wird es unverändert zurückgegeben
        return date_str

# CSV-Datei lesen und Datum konvertieren
with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    
    # Kopfzeile schreiben
    writer.writeheader()
    
    for row in reader:
        # Datum konvertieren
        row['datum'] = convert_to_iso_format_with_timezone(row['datum'])
        # Zeile in die Ausgabedatei schreiben
        writer.writerow(row)

print(f"Die Datumsangaben wurden erfolgreich in das ISO-Format mit Zeitzone konvertiert und in '{output_file}' gespeichert.")