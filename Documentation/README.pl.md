# 🚀 HiddenTanks-Generator-Mod

**Automatyzacja wyświetlania wszystkich pojazdów w drzewie badań WOT BLITZ.**  
Działa ze wszystkimi formatami plików (oryginalne `xml`/`yaml` i spakowane `dvpl`).

Program pozwala **w pełni odsłonić** wszystkie czołgi w hangarze, w tym ukryte, kolekcjonerskie, premium i nagrodowe, poprzez modyfikację plików konfiguracyjnych gry. Wszystkie zmiany są odwracalne dzięki automatycznemu tworzeniu kopii zapasowych.

---

## 📌 Co to jest?

HiddenTanks-Generator-Mod to aplikacja komputerowa napisana w Pythonie/Tkinter, która:

- Czyta pliki drzewa technologii (`tree_*.yaml`) i listy pojazdów (`list.xml`) gry World of Tanks Blitz.
- Wyodrębnia wszystkie czołgi z `list.xml`, usuwa zbędne tagi (`deprecated`, `secret`, `testTank` itp.) i ustawia flagę `notInShop` na `false`.
- Na podstawie oryginalnego `tree.yaml` buduje nowe drzewo, które **dodaje wszystkie wcześniej ukryte czołgi** (zarówno zakomentowane, jak i brakujące w drzewie) z odpowiednią kategoryzacją (zwykłe, kolekcjonerskie, premium).
- Zapisuje zmodyfikowane pliki z powrotem, zachowując ich format (DVPL/tekst) i kodowanie.
- Obsługuje modyfikację zarówno głównych plików gry, jak i plików z **pakietów DLC** (folder `packs`).
- Zapewnia przyjazny interfejs graficzny z ustawieniami języka, motywu, trybu pracy oraz przyciskami do generowania, przywracania, statystyk i eksportu moda.

---

## ⚙️ Jak to działa (technicznie)

### 1. Wykrywanie plików
Dla każdej nacji (CN, EU, FR, DE, JP, HN, UK, US, SU) program określa ścieżki do plików `tree_*.yaml` i `list.xml` w folderze `Data` gry. Jeśli włączona jest opcja **„Modyfikuj pliki DLC”**, program szuka tych plików również w folderze `%USERPROFILE%/AppData/Local/wotblitz/packs` (z rozszerzeniem `.dvpl`). Pliki DLC mają priorytet, jeśli istnieją.

### 2. Odczyt i dekompresja
Pliki mogą być:
- Zwykłym tekstem (`xml`, `yaml`).
- Spakowane w formacie **DVPL** (sygnatura `DVPL` na końcu, kompresja LZ4).

Program automatycznie wykrywa typ, dekompresuje zawartość i zapamiętuje parametry kompresji do późniejszego zapisu.

### 3. Przetwarzanie XML (`list.xml`)
Wyodrębniane są wszystkie tagi `<vehicle>`. Dla każdego czołgu zapisywane są:
- `id`, `level`, `price` (obecność złota), `notInShop`, `tags`.
- Usuwane są tagi z listy `deprecated`, `secret`, `testTank`, `lightTankArtefacts_User`, `grousers_user`, `event_battles`.
- Flaga `notInShop` jest wymuszana na `false` (czołg staje się dostępny).

### 4. Przetwarzanie YAML (`tree_*.yaml`)
- Oryginalne drzewo jest odczytywane, zapamiętywane są widoczne czołgi i ich pozycje `[level, row]`.
- Identyfikowane są zakomentowane linie (są one uznawane za ukryte).
- Wszystkie czołgi z XML, które nie są widoczne ani zakomentowane, są oznaczane jako **ukryte**.

### 5. Generowanie nowego drzewa
Dla każdego poziomu (`level`) tworzone są grupy:
- **Widoczne czołgi** – pozostają na swoich miejscach.
- **Ukryte** – dodawane na końcu poziomu z nowymi numerami wierszy, pogrupowane według kategorii:
  - `ordinary` – zwykłe (bez ceny w złocie, oznaczone `deprecated`, nie w sklepie)
  - `collectible` – kolekcjonerskie (cena w złocie i tag `collectible`)
  - `premium` – premium (cena w złocie, ale bez tagu `collectible`)

Kategorie są sortowane według klasy czołgu (`lightTank`, `mediumTank`, `heavyTank`, `AT-SPG`), a następnie według nazwy.

### 6. Zapis plików
Zmodyfikowane pliki są zapisywane z zachowaniem:
- Oryginalnego formatu (DVPL lub tekst).
- Oryginalnego kodowania (zazwyczaj UTF-8 z BOM lub bez).
- Typu kompresji (jeśli był DVPL).

Jeśli plik należy do DLC, ustawiany jest atrybut **„tylko do odczytu”**, jak w oryginale.

### 7. Kopia zapasowa i przywracanie
Przed zmianami program tworzy pełną kopię modyfikowanych plików w folderze `HiddenTanks_Backup` wewnątrz folderu gry, zachowując strukturę podfolderów `Game/` i `DLC/`. Przywracanie polega na skopiowaniu tych plików z powrotem.

---

## 🎯 Funkcje

- **Trzy tryby pracy**:
  - `NON-DVPL` – zawsze odczytuje i zapisuje pliki jako zwykły tekst (bez kompresji).
  - `DVPL` – zawsze używa kompresji LZ4 (typ 2).
  - `UNIVERSAL` – automatycznie wykrywa format każdego pliku i zapisuje go w tej samej formie.

- **Obsługa DLC** – modyfikuje pliki w folderze `packs`, jeśli istnieją.

- **Eksport moda** – tworzy katalog `result/HiddenTanks_Generated_<wersja_gry>/` z dwoma podfolderami:
  - `Mod/` – gotowe zmodyfikowane pliki do dystrybucji.
  - `Backup/` – oryginalne pliki do przywracania.

- **Statystyki** – wyświetla liczbę widocznych i ukrytych czołgów według nacji, a także porównanie list DLC i gry (ile nowych czołgów dodano w DLC).

- **Pełna lokalizacja** – interfejs i wszystkie komunikaty dziennika są przetłumaczone na **6 języków**: angielski, rosyjski, polski, ukraiński, turecki, niemiecki. Łatwo dodawać nowe języki poprzez pliki JSON.

- **Zapis ustawień** – ścieżka do gry, język, motyw, tryb i opcja DLC są zapisywane w `config.json`.

- **Wygodny dziennik** – wszystkie działania i błędy są wyświetlane w osobnym oknie z możliwością kopiowania (`Ctrl+C`), zaznaczenia wszystkiego (`Ctrl+A`) i czyszczenia.

---

## 🖥️ Interfejs

Główne okno zawiera:
- Pole wyboru folderu z grą.
- Listy rozwijane dla języka, motywu i trybu.
- Pole wyboru „Modyfikuj pliki DLC”.
- Przyciski: **„Generuj mod”**, **„Przywróć oryginał”**, **„Statystyki”**, **„Eksportuj mod”**.
- Obszar dziennika z dodatkowymi przyciskami „Kopiuj” i „Wyczyść”.

---

## ⚠️ Ważne: mikroaktualizacje i DLC

Gdy gra otrzymuje **mikroaktualizacje** (nowe pojazdy, małe łatki), pliki gry mogą ulec zmianie. Jeśli używasz **pakietów DLC** (opcja „Modyfikuj pliki DLC” jest włączona), **zaleca się pozostawienie tej opcji włączonej** podczas ponownego generowania moda po aktualizacji.

Gwarantuje to, że nowe czołgi dodane w DLC będą również poprawnie wyświetlane w drzewie badań. Jeśli pliki DLC nie zostaną zmodyfikowane, nowe pojazdy z DLC mogą pozostać ukryte.

**Zalecenie:**  
- Po każdej aktualizacji gry najpierw **przywróć oryginały** (przycisk „Przywróć oryginał”), a następnie wygeneruj mod ponownie z tymi samymi ustawieniami (w tym DLC, jeśli go używałeś).

---

## 📥 Instalacja i uruchomienie

### Wymagania
- **Python 3.8+** (zalecany 3.10)

### Szybki start
1. Zainstaluj Pythona, jeśli go nie masz – pobierz z [python.org](https://python.org).
2. Rozpakuj archiwum z programem do dowolnego folderu.
3. Uruchom plik **`autoinstall_modules.bat`** – automatycznie zainstaluje wymagane biblioteki (`lz4`, `pyyaml`) przez `pip`.
4. Po zakończeniu instalacji uruchom **`start_program.bat`** – otworzy się interfejs graficzny.

> 💡 **Uwaga:** Jeśli nie masz tych plików `.bat`, możesz zainstalować ręcznie:
> ```bash
> pip install -r requirements.txt
> python gui.py
> ```

### Pierwsze uruchomienie
- Automatycznie tworzony jest plik `config.json` z domyślnymi ustawieniami.
- Folder `locales/` zawiera pliki tłumaczeń – możesz je edytować, aby zmienić teksty.

---

## 🎮 Instrukcja użytkowania

1. **Wskaż ścieżkę do gry** – kliknij „Przeglądaj...” i wybierz główny folder WoT Blitz (np. `C:/Games/World_of_Tanks_Blitz`).

2. **Dostosuj ustawienia**:
   - Wybierz język interfejsu.
   - Wybierz motyw (jasny/ciemny).
   - Wybierz tryb (zalecany: `UNIVERSAL`).
   - Włącz „Modyfikuj pliki DLC”, jeśli chcesz modyfikować pakiety DLC.

3. **Wykonaj akcję**:
   - **„Generuj mod”** – zastosuje zmiany, tworząc kopię zapasową w folderze gry.
   - **„Przywróć oryginał”** – przywróci pliki z kopii zapasowej (kopia pozostaje, możesz ją usunąć ręcznie).
   - **„Statystyki”** – pokaże informacje bez wprowadzania zmian.
   - **„Eksportuj mod”** – utworzy gotowy mod w folderze `result/` do dystrybucji.

4. **Uruchom grę** – wszystkie czołgi powinny być widoczne w drzewie badań.

---

## 📂 Struktura projektu
Generator-Mod/
├── Documentation/ # Pełna dokumentacja w wielu językach
├── core/
│ ├── config.py # Wczytywanie/zapisywanie ustawień
│ ├── localization.py # Funkcje lokalizacji
│ ├── dvpl_utils.py # Odczyt/zapis DVPL (LZ4, sygnatura)
│ ├── xml_processor.py # Parsowanie i modyfikacja list.xml
│ ├── yaml_processor.py # Generowanie tree.yaml na podstawie danych
│ └── mod_generator.py # Główna logika: wyszukiwanie, odczyt, przetwarzanie, zapis, kopia, eksport
├── locales/ # Pliki lokalizacji (en.json, ru.json, pl.json, uk.json, tr.json, de.json, template.json)
├── gui.py # Interfejs graficzny (Tkinter)
├── autoinstall_modules.bat # Instalacja zależności
├── start_program.bat # Uruchomienie programu
├── config.json # Zapisane ustawienia (tworzone automatycznie)
├── requirements.txt # Zależności
└── README.md # Ten plik

---

## 🔧 Szczegóły techniczne

### Formaty plików
- **DVPL** – zastrzeżony format WoT Blitz: blok skompresowanych danych (LZ4) + 20‑bajtowy nagłówek zawierający:
  - `original_size` (4 bajty)
  - `compressed_size` (4 bajty)
  - `crc32` (4 bajty)
  - `compression_type` (4 bajty: 0 – bez kompresji, 1 – LZ4, 2 – LZ4 HC)
  - sygnatura `DVPL` (4 bajty)

- **tree_*.yaml** – plik YAML z kluczem `tanks`, gdzie każdy czołg ma pozycję `[level, row]`.

- **list.xml** – dokument XML z elementem głównym `<root>`, wewnątrz elementy `<vehicle>` z atrybutami i tagami potomnymi (`id`, `price`, `notInShop`, `tags`, `level`).

### Algorytm modyfikacji (krok po kroku)
1. Dla każdej nacji określane są ścieżki do plików `tree` i `list` (w grze lub DLC).
2. Pliki są odczytywane (dekompresja DVPL w razie potrzeby), określane jest kodowanie i typ kompresji.
3. Z `list.xml` wyodrębniane są wszystkie czołgi, usuwane zbędne tagi, ustawiane `notInShop` na `false`.
4. Z `tree.yaml` wyodrębniane są widoczne czołgi i ich pozycje. Identyfikowane są również zakomentowane linie.
5. Budowany jest nowy YAML:
   - Najpierw widoczne czołgi (jak w oryginale).
   - Następnie, dla każdego poziomu, ukryte czołgi są dodawane z nowymi numerami wierszy, pogrupowane według kategorii.
6. Pliki są zapisywane z powrotem z zachowaniem oryginalnego formatu i kompresji.
7. Jeśli pliki pochodzą z DLC, ustawiany jest atrybut `S_IREAD` (tylko do odczytu).

### Osobliwości przetwarzania
- Dla nacji **HN** (Other) poziomy widocznych czołgów są korygowane zgodnie z rzeczywistymi wartościami z XML (ignorowana jest pozycja `level` w YAML).
- Kategoryzacja ukrytych czołgów:
  - `ordinary` – jeśli `notInShop` był `true`, cena nie zawiera złota i występuje tag `deprecated`.
  - `collectible` – jeśli cena zawiera złoto i tag `collectible`.
  - `premium` – jeśli cena zawiera złoto, ale nie ma tagu `collectible`.
- Podczas dodawania ukrytych czołgów są one sortowane według klasy i nazwy dla przewidywalnego porządku.

---

## 🌍 Lokalizacja

Wszystkie teksty interfejsu i logów są przechowywane w plikach JSON w folderze `locales/`.  
Pliki są nazwane zgodnie z kodem języka (np. `ru.json`) i zawierają pole `"lang_code"` do wyświetlania na liście rozwijanej.

**Jak dodać nowy język:**
1. Skopiuj `template.json` do pliku z nowym kodem (np. `fr.json`).
2. Zmień `"lang_code"` na `"FR"`.
3. Przetłumacz wszystkie napisy.
4. Uruchom ponownie program – język pojawi się na liście.

---

## ❓ Często zadawane pytania

**P: Czy to bezpieczne dla konta?**  
O: Program modyfikuje tylko lokalne pliki konfiguracyjne. Nie wpływa na rozgrywkę, balans ani nie daje przewagi. Modyfikacje interfejsu są dozwolone zgodnie z zasadami WoT Blitz. Jednak używasz na własne ryzyko.

**P: Co zrobić, jeśli gra nie uruchamia się po zastosowaniu moda?**  
O: Kliknij **„Przywróć oryginał”**, aby przywrócić pliki. Jeśli problem nadal występuje, zweryfikuj pliki gry przez launcher.

**P: Czy zmiany przetrwają aktualizację gry?**  
O: Nie, aktualizacje nadpisują pliki. Musisz ponownie wygenerować mod po każdej aktualizacji. Zaleca się przywrócenie oryginałów przed aktualizacją.

**P: Gdzie przechowywane są kopie zapasowe?**  
O: W folderze `HiddenTanks_Backup` wewnątrz folderu gry. Nie usuwaj go, dopóki nie upewnisz się, że mod działa poprawnie.

**P: Czy można używać razem z innymi modami?**  
O: Jeśli inne mody modyfikują te same pliki (`tree_*.yaml` i `list.xml`), mogą wystąpić konflikty. Zaleca się stosowanie na czystej instalacji gry.

**P: Co zrobić, jeśli `autoinstall_modules.bat` nie działa?**  
O: Upewnij się, że Python jest w zmiennej systemowej `PATH`. Jeśli nie, zainstaluj zależności ręcznie poleceniem `pip install -r requirements.txt`.

---

## 📄 Licencja

Projekt jest rozpowszechniany jako **Freeware** – bezpłatny do osobistego, niekomercyjnego użytku.  
Kod źródłowy jest otwarty, możesz go modyfikować na własne potrzeby.

---

## ✉️ Kontakt

W przypadku pytań, sugestii lub zgłaszania błędów utwórz **Issue** w repozytorium lub skontaktuj się z deweloperem przez e-mail.

---

**Miłej gry!** 🎮