# 🚀 HiddenTanks-Generator-Mod

**Automatisierung zur Anzeige aller Fahrzeuge im Forschungbaum von WOT BLITZ.**  
Arbeitet mit allen Dateiformaten (original `xml`/`yaml` und gepackte `dvpl`).

Das Programm ermöglicht es, **alle Panzer im Hangar vollständig sichtbar zu machen**, einschließlich verborgener, Sammel-, Premium- und Belohnungsfahrzeuge, durch die Modifikation der Konfigurationsdateien des Spiels. Alle Änderungen sind dank automatischer Sicherungskopien rückgängig machbar.

---

## 📌 Was ist das?

HiddenTanks-Generator-Mod ist eine Desktop-Anwendung, geschrieben in Python/Tkinter, die:

- Die Technologiebaum-Dateien (`tree_*.yaml`) und Fahrzeuglisten-Dateien (`list.xml`) des Spiels World of Tanks Blitz liest.
- Alle Panzer aus `list.xml` extrahiert, unnötige Tags entfernt (`deprecated`, `secret`, `testTank` usw.) und das Flag `notInShop` auf `false` setzt.
- Basierend auf dem ursprünglichen `tree.yaml` einen neuen Baum erstellt, der **alle zuvor versteckten Panzer** (sowohl auskommentierte als auch im Baum fehlende) mit korrekter Kategorisierung (gewöhnlich, Sammel, Premium) hinzufügt.
- Die geänderten Dateien unter Beibehaltung ihres Formats (DVPL/Text) und ihrer Kodierung zurückschreibt.
- Die Modifikation sowohl der Hauptspieldateien als auch der Dateien aus **DLC-Paketen** (Ordner `packs`) unterstützt.
- Eine benutzerfreundliche grafische Oberfläche mit Einstellungen für Sprache, Thema, Arbeitsmodus sowie Schaltflächen zum Generieren, Wiederherstellen, Statistik und Export bereitstellt.

---

## ⚙️ Wie es funktioniert (technische Übersicht)

### 1. Dateierkennung
Für jede Nation (CN, EU, FR, DE, JP, HN, UK, US, SU) ermittelt das Programm die Pfade zu den Dateien `tree_*.yaml` und `list.xml` im `Data`-Ordner des Spiels. Wenn die Option **"DLC-Dateien ändern"** aktiviert ist, sucht es auch in `%USERPROFILE%/AppData/Local/wotblitz/packs` (mit `.dvpl`-Suffix). DLC-Dateien haben Priorität, falls vorhanden.

### 2. Lesen und Dekomprimierung
Dateien können sein:
- Klartext (`xml`, `yaml`)
- Im **DVPL**-Format gepackt (Signatur `DVPL` am Ende, LZ4-Komprimierung)

Das Programm erkennt den Typ automatisch, dekomprimiert den Inhalt und merkt sich die Komprimierungsparameter für das spätere Schreiben.

### 3. XML-Verarbeitung (`list.xml`)
Alle `<vehicle>`-Tags werden extrahiert. Für jeden Panzer werden gespeichert:
- `id`, `level`, `price` (Gold vorhanden), `notInShop`, `tags`.
- Tags aus der Liste `deprecated`, `secret`, `testTank`, `lightTankArtefacts_User`, `grousers_user`, `event_battles` werden entfernt.
- Das Flag `notInShop` wird erzwungen auf `false` gesetzt (Panzer wird verfügbar).

### 4. YAML-Verarbeitung (`tree_*.yaml`)
- Der ursprüngliche Baum wird gelesen, sichtbare Panzer und ihre Positionen `[level, row]` werden gemerkt.
- Auskommentierte Zeilen werden identifiziert (sie gelten als versteckt).
- Alle Panzer aus XML, die weder sichtbar noch auskommentiert sind, werden als **versteckt** markiert.

### 5. Generierung des neuen Baums
Für jede `level` werden Gruppen erstellt:
- **Sichtbare Panzer** – bleiben an ihren ursprünglichen Plätzen.
- **Versteckte** – werden am Ende der Ebene mit neuen Zeilennummern angehängt, gruppiert nach Kategorie:
  - `ordinary` – gewöhnlich (kein Goldpreis, mit `deprecated`-Tag, nicht im Shop)
  - `collectible` – Sammel (Goldpreis und `collectible`-Tag)
  - `premium` – Premium (Goldpreis, aber kein `collectible`-Tag)

Die Kategorien werden nach Panzerklasse (`lightTank`, `mediumTank`, `heavyTank`, `AT-SPG`) und dann nach Namen sortiert.

### 6. Schreiben der Dateien
Die geänderten Dateien werden unter Beibehaltung von:
- Originalformat (DVPL oder Text).
- Originalkodierung (normalerweise UTF-8 mit oder ohne BOM).
- Komprimierungstyp (falls DVPL) zurückgeschrieben.

Wenn die Datei zu DLC gehört, wird sie auf **schreibgeschützt** gesetzt, wie im Original.

### 7. Sicherung und Wiederherstellung
Vor Änderungen erstellt das Programm eine vollständige Kopie der modifizierten Dateien im Ordner `HiddenTanks_Backup` innerhalb des Spielordners, wobei die Unterordnerstruktur `Game/` und `DLC/` beibehalten wird. Die Wiederherstellung kopiert diese Dateien zurück.

---

## 🎯 Funktionen

- **Drei Betriebsmodi**:
  - `NON-DVPL` – liest und schreibt Dateien immer als Klartext (keine Komprimierung).
  - `DVPL` – verwendet immer LZ4-Komprimierung (Typ 2).
  - `UNIVERSAL` – erkennt automatisch das Format jeder Datei und speichert es in derselben Form.

- **DLC-Unterstützung** – modifiziert Dateien im `packs`-Ordner, falls vorhanden.

- **Mod-Export** – erstellt ein Verzeichnis `result/HiddenTanks_Generated_<Spielversion>/` mit zwei Unterordnern:
  - `Mod/` – gebrauchsfertige modifizierte Dateien zur Verteilung.
  - `Backup/` – Originaldateien zur Wiederherstellung.

- **Statistiken** – zeigt die Anzahl der sichtbaren und versteckten Panzer pro Nation und vergleicht DLC- und Spiel-Listen (wie viele neue Panzer im DLC enthalten sind).

- **Vollständige Lokalisierung** – Oberfläche und alle Logmeldungen sind in **6 Sprachen** übersetzt: Englisch, Russisch, Polnisch, Ukrainisch, Türkisch, Deutsch. Neue Sprachen können einfach über JSON-Dateien hinzugefügt werden.

- **Einstellungen werden gespeichert** – Spielpfad, Sprache, Thema, Modus und DLC-Option werden in `config.json` gespeichert.

- **Praktisches Log** – alle Aktionen und Fehler werden in einem separaten Fenster mit Kopierfunktion (`Ctrl+C`), Alles auswählen (`Ctrl+A`) und Löschen angezeigt.

---

## 🖥️ Oberfläche

Das Hauptfenster enthält:
- Ein Feld zur Auswahl des Spielordners.
- Dropdown-Listen für Sprache, Thema und Modus.
- Ein Kontrollkästchen "DLC-Dateien ändern".
- Schaltflächen: **"Mod generieren"**, **"Original wiederherstellen"**, **"Statistiken"**, **"Mod exportieren"**.
- Einen Log-Bereich mit zusätzlichen Schaltflächen "Kopieren" und "Löschen".

---

## ⚠️ Wichtig: Mikro-Updates und DLC

Wenn das Spiel **Mikro-Updates** (neue Fahrzeuge, kleine Patches) erhält, können sich die Spieldateien ändern. Wenn Sie **DLC-Pakete** verwenden (Option "DLC-Dateien ändern" ist aktiviert), wird **empfohlen, diese Option beim erneuten Generieren des Mods nach einem Update aktiviert zu lassen**.

Dies stellt sicher, dass neue Panzer, die zum DLC hinzugefügt wurden, auch korrekt im Forschungsbaum angezeigt werden. Wenn DLC-Dateien nicht modifiziert werden, können neue Fahrzeuge aus dem DLC verborgen bleiben.

**Empfehlung:**  
- Stellen Sie nach jedem Spielupdate zunächst die **Originale wieder her** (Schaltfläche "Original wiederherstellen") und generieren Sie dann den Mod mit denselben Einstellungen (einschließlich DLC, falls verwendet) neu.

---

## 📥 Installation und Start

### Voraussetzungen
- **Python 3.8+** (empfohlen 3.10)

### Schnellstart
1. Installieren Sie Python, falls nicht vorhanden – laden Sie es von [python.org](https://python.org) herunter.
2. Entpacken Sie das Archiv mit dem Programm in einen beliebigen Ordner.
3. Führen Sie die Datei **`autoinstall_modules.bat`** aus – sie installiert automatisch die erforderlichen Bibliotheken (`lz4`, `pyyaml`) über `pip`.
4. Nach der Installation starten Sie **`start_program.bat`** – die grafische Oberfläche öffnet sich.

> 💡 **Hinweis:** Falls Sie aus irgendeinem Grund diese `.bat`-Dateien nicht haben, können Sie die Installation manuell durchführen:
> ```bash
> pip install -r requirements.txt
> python gui.py
> ```

### Erster Start
- Eine `config.json`-Datei mit Standardeinstellungen wird automatisch erstellt.
- Der Ordner `locales/` enthält Übersetzungsdateien – Sie können sie bearbeiten, um Texte zu ändern.

---

## 🎮 Bedienungsanleitung

1. **Geben Sie den Spielpfad an** – klicken Sie auf "Durchsuchen..." und wählen Sie den Stammordner von WoT Blitz (z.B. `C:/Games/World_of_Tanks_Blitz`).

2. **Passen Sie die Einstellungen an**:
   - Wählen Sie die Oberflächensprache.
   - Wählen Sie das Thema (hell/dunkel).
   - Wählen Sie den Modus (empfohlen: `UNIVERSAL`).
   - Aktivieren Sie "DLC-Dateien ändern", wenn Sie DLC-Pakete modifizieren möchten.

3. **Führen Sie eine Aktion aus**:
   - **"Mod generieren"** – wendet Änderungen an und erstellt ein Backup im Spielordner.
   - **"Original wiederherstellen"** – stellt Dateien aus dem Backup wieder her (Backup bleibt erhalten, Sie können es manuell löschen).
   - **"Statistiken"** – zeigt Informationen an, ohne Änderungen vorzunehmen.
   - **"Mod exportieren"** – erstellt einen gebrauchsfertigen Mod im Ordner `result/` zur Verteilung.

4. **Starten Sie das Spiel** – alle Panzer sollten nun im Forschungsbaum sichtbar sein.

---

## 📂 Projektstruktur
Generator-Mod/
├── Documentation/ # Vollständige Dokumentation in mehreren Sprachen
├── core/
│ ├── config.py # Einstellungen laden/speichern
│ ├── localization.py # Lokalisierungsfunktionen
│ ├── dvpl_utils.py # DVPL lesen/schreiben (LZ4, Signatur)
│ ├── xml_processor.py # list.xml parsen und modifizieren
│ ├── yaml_processor.py # tree.yaml aus Daten generieren
│ └── mod_generator.py # Hauptlogik: Suche, Lesen, Verarbeitung, Schreiben, Backup, Export
├── locales/ # Lokalisierungsdateien (en.json, ru.json, pl.json, uk.json, tr.json, de.json, template.json)
├── gui.py # Grafische Oberfläche (Tkinter)
├── autoinstall_modules.bat # Abhängigkeiten installieren
├── start_program.bat # Programm starten
├── config.json # Gespeicherte Einstellungen (automatisch erstellt)
├── requirements.txt # Abhängigkeiten
└── README.md # Diese Datei

---

## 🔧 Technische Details

### Dateiformate
- **DVPL** – proprietäres WoT-Blitz-Format: komprimierter Datenblock (LZ4) + 20‑Byte-Footer mit:
  - `original_size` (4 Bytes)
  - `compressed_size` (4 Bytes)
  - `crc32` (4 Bytes)
  - `compression_type` (4 Bytes: 0 – keine Komprimierung, 1 – LZ4, 2 – LZ4 HC)
  - Signatur `DVPL` (4 Bytes)

- **tree_*.yaml** – YAML-Datei mit dem Schlüssel `tanks`, wobei jeder Panzer eine Position `[level, row]` hat.

- **list.xml** – XML-Dokument mit Wurzelelement `<root>`, darin `<vehicle>`-Elemente mit Attributen und Kind-Tags (`id`, `price`, `notInShop`, `tags`, `level`).

### Modifikationsalgorithmus (Schritt für Schritt)
1. Für jede Nation werden die Pfade zu den `tree`- und `list`-Dateien ermittelt (im Spiel oder DLC).
2. Die Dateien werden gelesen (ggf. DVPL dekomprimiert), Kodierung und Komprimierungstyp werden bestimmt.
3. Aus `list.xml` werden alle Panzer extrahiert, unnötige Tags entfernt, `notInShop` auf `false` gesetzt.
4. Aus `tree.yaml` werden sichtbare Panzer und ihre Positionen extrahiert. Auch auskommentierte Zeilen werden identifiziert.
5. Ein neues YAML wird erstellt:
   - Zuerst sichtbare Panzer (wie im Original).
   - Dann werden für jede Ebene versteckte Panzer mit neuen Zeilennummern, gruppiert nach Kategorie, angehängt.
6. Die Dateien werden unter Beibehaltung des ursprünglichen Formats und der Komprimierung zurückgeschrieben.
7. Wenn die Dateien aus dem DLC stammen, wird das Attribut `S_IREAD` (schreibgeschützt) gesetzt.

### Besonderheiten der Verarbeitung
- Für die Nation **HN** (Other) werden die Ebenen der sichtbaren Panzer gemäß den tatsächlichen Werten aus XML korrigiert (die `level`-Position in YAML wird ignoriert).
- Kategorisierung versteckter Panzer:
  - `ordinary` – wenn `notInShop` `true` war, Preis kein Gold enthält und das Tag `deprecated` vorhanden ist.
  - `collectible` – wenn Preis Gold enthält und das Tag `collectible` vorhanden ist.
  - `premium` – wenn Preis Gold enthält, aber kein `collectible`-Tag vorhanden ist.
- Beim Anhängen versteckter Panzer werden sie nach Klasse und Name sortiert, um eine vorhersagbare Reihenfolge zu gewährleisten.

---

## 🌍 Lokalisierung

Alle Oberflächen- und Log-Texte werden in JSON-Dateien im Ordner `locales/` gespeichert.  
Die Dateien sind nach dem Sprachcode benannt (z.B. `ru.json`) und enthalten ein Feld `"lang_code"` für die Anzeige in der Dropdown-Liste.

**So fügen Sie eine neue Sprache hinzu:**
1. Kopieren Sie `template.json` in eine neue Datei mit dem neuen Code (z.B. `fr.json`).
2. Ändern Sie `"lang_code"` auf `"FR"`.
3. Übersetzen Sie alle Zeichenfolgen.
4. Starten Sie das Programm neu – die Sprache erscheint in der Liste.

---

## ❓ Häufig gestellte Fragen

**F: Ist das sicher für meinen Account?**  
A: Das Programm ändert nur lokale Konfigurationsdateien. Es beeinflusst nicht das Gameplay, das Gleichgewicht oder verschafft Vorteile. Oberflächenmodifikationen sind gemäß den WoT-Blitz-Regeln erlaubt. Verwenden Sie es jedoch auf eigenes Risiko.

**F: Was tun, wenn das Spiel nach dem Mod nicht startet?**  
A: Klicken Sie auf **"Original wiederherstellen"**, um die Dateien zurückzusetzen. Wenn das Problem weiterhin besteht, überprüfen Sie die Spieldateien über den Launcher.

**F: Bleiben die Änderungen nach einem Spielupdate erhalten?**  
A: Nein, Updates überschreiben die Dateien. Sie müssen den Mod nach jedem Update neu generieren. Es wird empfohlen, vor dem Update die Originale wiederherzustellen.

**F: Wo werden die Backups gespeichert?**  
A: Im Ordner `HiddenTanks_Backup` innerhalb des Spielordners. Löschen Sie ihn erst, wenn Sie sicher sind, dass der Mod stabil läuft.

**F: Kann ich dies zusammen mit anderen Mods verwenden?**  
A: Wenn andere Mods dieselben Dateien (`tree_*.yaml` und `list.xml`) ändern, kann es zu Konflikten kommen. Es wird empfohlen, es auf einer sauberen Spielinstallation anzuwenden.

**F: Was tun, wenn `autoinstall_modules.bat` nicht funktioniert?**  
A: Stellen Sie sicher, dass Python in der Systemvariablen `PATH` enthalten ist. Wenn nicht, installieren Sie die Abhängigkeiten manuell mit `pip install -r requirements.txt`.

---

## 📄 Lizenz

Dieses Projekt wird als **Freeware** vertrieben – kostenlos für den persönlichen, nicht-kommerziellen Gebrauch.  
Der Quellcode ist offen; Sie können ihn für Ihre eigenen Zwecke anpassen.

---

## ✉️ Feedback

Bei Fragen, Vorschlägen oder Fehlermeldungen erstellen Sie bitte ein **Issue** im Repository oder kontaktieren Sie den Entwickler per E-Mail.

---

**Viel Spaß beim Spielen!** 🎮