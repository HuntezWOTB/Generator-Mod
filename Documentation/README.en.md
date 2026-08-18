# 🚀 Generator-Mod

**Automation to display all vehicles in the research tree of WOT BLITZ.**  
Works with all file formats (original `xml`/`yaml` and packed `dvpl`).

The program allows you to **fully reveal** all tanks in the garage, including hidden, collectible, premium, and reward vehicles, by modifying the game configuration files. All changes are reversible thanks to automatic backup creation.

---

## 📌 What is it?

Generator-Mod is a desktop application written in Python/Tkinter that:

- Reads the technology tree files (`tree_*.yaml`) and vehicle list files (`list.xml`) of World of Tanks Blitz.
- Extracts all tanks from `list.xml`, removes unnecessary tags (`deprecated`, `secret`, `testTank`, etc.), and sets `notInShop` to `false`.
- Based on the original `tree.yaml`, builds a new tree that **adds all previously hidden tanks** (both commented out and missing from the tree) with correct categorisation (ordinary, collectible, premium).
- Writes back the modified files, preserving their format (DVPL/text) and encoding.
- Supports modification of both the main game files and files from **DLC packs** (the `packs` folder).
- Provides a user-friendly graphical interface with language, theme, mode settings, and buttons for generation, restore, statistics, and export.

---

## ⚙️ How it works (technical overview)

### 1. File detection
For each nation (CN, EU, FR, DE, JP, HN, UK, US, SU), the program determines the paths to `tree_*.yaml` and `list.xml` in the game's `Data` folder. If the **"Modify DLC files"** option is enabled, it also looks for these files in `%USERPROFILE%/AppData/Local/wotblitz/packs` (with `.dvpl` suffix). DLC files take priority if they exist.

### 2. Reading and decompression
Files can be:
- Plain text (`xml`, `yaml`)
- Packed in **DVPL** format (signature `DVPL` at the end, LZ4 compression)

The program automatically detects the type, decompresses the content, and remembers compression parameters for later writing.

### 3. XML processing (`list.xml`)
All `<vehicle>` tags are extracted. For each tank, the following are stored:
- `id`, `level`, `price` (gold presence), `notInShop`, `tags`.
- Tags from the list `deprecated`, `secret`, `testTank`, `lightTankArtefacts_User`, `grousers_user`, `event_battles` are removed.
- The `notInShop` flag is forcibly set to `false` (making the tank available).

### 4. YAML processing (`tree_*.yaml`)
- The original tree is read, visible tanks and their positions `[level, row]` are memorised.
- Commented lines are identified (they are considered hidden).
- All tanks from XML that are not visible and not commented are marked as **hidden**.

### 5. New tree generation
For each `level`, groups are created:
- **Visible tanks** – stay in their original places.
- **Hidden tanks** – appended at the end of the level with new row numbers, grouped by category:
  - `ordinary` – no gold price, tagged `deprecated`, not in shop.
  - `collectible` – gold price and `collectible` tag.
  - `premium` – gold price but no `collectible` tag.

Categories are sorted by tank class (`lightTank`, `mediumTank`, `heavyTank`, `AT-SPG`) and then by name.

### 6. Writing files
Modified files are written back preserving:
- Original format (DVPL or text).
- Original encoding (usually UTF-8 with or without BOM).
- Compression type (if it was DVPL).

If the file belongs to DLC, it is set to **read-only** as in the original.

### 7. Backup and restore
Before making changes, the program creates a full copy of the modified files in the `HiddenTanks_Backup` folder inside the game folder, preserving the `Game/` and `DLC/` subfolder structure. Restoring copies these files back.

---

## 🎯 Features

- **Three operation modes**:
  - `NON-DVPL` – always reads/writes files as plain text (no compression).
  - `DVPL` – always uses LZ4 compression (type 2).
  - `UNIVERSAL` – automatically detects the format of each file and saves it in the same form.

- **DLC support** – modifies files in the `packs` folder if present.

- **Export mod** – creates a folder `result/HiddenTanks_Generated_<game_version>/` with two subfolders:
  - `Mod/` – ready‑to‑use modified files for distribution.
  - `Backup/` – original files for restoration.

- **Statistics** – shows the number of visible and hidden tanks per nation, and compares DLC vs game lists (how many new tanks are in DLC).

- **Full localization** – interface and all log messages are translated into **6 languages**: English, Russian, Polish, Ukrainian, Turkish, German. Easily add new languages via JSON files.

- **Settings saved** – game path, language, theme, mode, and DLC option are saved in `config.json`.

- **Convenient log** – all actions and errors are displayed in a separate window with copy (`Ctrl+C`), select all (`Ctrl+A`), and clear capabilities.

---

## 🖥️ Interface

The main window contains:
- A field to select the game folder.
- Dropdown lists for language, theme, and mode.
- A checkbox "Modify DLC files".
- Buttons: **"Generate Mod"**, **"Restore Original"**, **"Statistics"**, **"Export Mod"**.
- A log area with additional "Copy" and "Clear" buttons.

---

## ⚠️ Important: Micro‑updates and DLC

When the game receives **micro‑updates** (new vehicles, small patches), the game files may change. If you are using **DLC packs** (the "Modify DLC files" option is enabled), it is **recommended to keep this option enabled** when regenerating the mod after an update.

This ensures that new tanks added to DLC will also be correctly displayed in the research tree. If DLC files are not modified, new DLC vehicles may remain hidden.

**Recommendation:**  
- After every game update, first **restore originals** (the "Restore Original" button), then regenerate the mod with the same settings (including DLC, if you used it).

---

## 📥 Installation and launch

### Requirements
- **Python 3.8+** (recommended 3.10)

### Quick start
1. Install Python if you don't have it – download from [python.org](https://python.org).
2. Unzip the archive with the program to any folder.
3. Run **`autoinstall_modules.bat`** – it will automatically install the required libraries (`lz4`, `pyyaml`) via `pip`.
4. After installation, run **`start_program.bat`** – the graphical interface will open.

> 💡 **Note:** If you don't have these `.bat` files, you can install manually:
> ```bash
> pip install -r requirements.txt
> python gui.py
> ```

### First run
- A `config.json` file with default settings is automatically created.
- The `locales/` folder contains translation files – you can edit them to change texts.

---

## 🎮 Usage guide

1. **Specify the game path** – click "Browse..." and select the root folder of WoT Blitz (e.g., `C:/Games/World_of_Tanks_Blitz`).

2. **Adjust settings**:
   - Choose the interface language.
   - Choose theme (light/dark).
   - Choose mode (recommended: `UNIVERSAL`).
   - Enable "Modify DLC files" if you want to modify DLC packs.

3. **Perform an action**:
   - **"Generate Mod"** – applies changes, creating a backup in the game folder.
   - **"Restore Original"** – restores files from backup (backup remains, you can delete it manually).
   - **"Statistics"** – shows information without making changes.
   - **"Export Mod"** – creates a ready‑to‑use mod in the `result/` folder for distribution.

4. **Launch the game** – all tanks should now be visible in the research tree.

---

## 📂 Project structure
Generator-Mod/
├── Documentation/ # Full documentation in multiple languages
├── core/
│ ├── config.py # Load/save settings
│ ├── localization.py # Localisation functions
│ ├── dvpl_utils.py # DVPL read/write (LZ4, signature)
│ ├── xml_processor.py # Parse and modify list.xml
│ ├── yaml_processor.py # Generate tree.yaml from data
│ └── mod_generator.py # Main logic: search, read, process, write, backup, export
├── locales/ # Localisation files (en.json, ru.json, pl.json, uk.json, tr.json, de.json, template.json)
├── gui.py # Graphical interface (Tkinter)
├── autoinstall_modules.bat # Install dependencies
├── start_program.bat # Launch the program
├── config.json # Saved settings (created automatically)
├── requirements.txt # Dependencies
└── README.md # This file

---

## 🔧 Technical details

### File formats
- **DVPL** – proprietary WoT Blitz format: compressed data block (LZ4) + 20‑byte footer containing:
  - `original_size` (4 bytes)
  - `compressed_size` (4 bytes)
  - `crc32` (4 bytes)
  - `compression_type` (4 bytes: 0 – no compression, 1 – LZ4, 2 – LZ4 HC)
  - signature `DVPL` (4 bytes)

- **tree_*.yaml** – YAML file with key `tanks`, where each tank has a position `[level, row]`.

- **list.xml** – XML document with root `<root>`, inside `<vehicle>` elements with attributes and child tags (`id`, `price`, `notInShop`, `tags`, `level`).

### Modification algorithm (step-by-step)
1. For each nation, determine paths to `tree` and `list` files (in game or DLC).
2. Read files (decompressing DVPL if needed), determine encoding and compression type.
3. From `list.xml`, extract all tanks, remove unnecessary tags, set `notInShop` to `false`.
4. From `tree.yaml`, extract visible tanks and their positions. Also identify commented lines.
5. Build a new YAML:
   - Visible tanks first (as in original).
   - Then, for each level, hidden tanks are appended with new row numbers, grouped by category.
6. Write files back preserving original format and compression.
7. If files are from DLC, set `S_IREAD` attribute (read‑only).

### Processing peculiarities
- For nation **HN** (Other), visible tank levels are corrected according to the real values from XML (ignoring the `level` position in YAML).
- Hidden tank categorisation:
  - `ordinary` – if `notInShop` was `true`, price has no gold, and tag `deprecated` present.
  - `collectible` – if price has gold and tag `collectible`.
  - `premium` – if price has gold but no `collectible` tag.
- When appending hidden tanks, they are sorted by class and name for predictable order.

---

## 🌍 Localisation

All interface and log texts are stored in JSON files in the `locales/` folder.  
Files are named after the language code (e.g., `ru.json`) and contain a `"lang_code"` field for display in the dropdown list.

**How to add a new language:**
1. Copy `template.json` to a new file with the new code (e.g., `fr.json`).
2. Change `"lang_code"` to `"FR"`.
3. Translate all strings.
4. Restart the program – the language will appear in the list.

---

## ❓ Frequently Asked Questions

**Q: Is this safe for my account?**  
A: The program only modifies local configuration files. It does not affect gameplay, balance, or give any advantage. Interface modifications are allowed by WoT Blitz rules. However, use at your own risk.

**Q: What if the game doesn't start after applying the mod?**  
A: Click **"Restore Original"** to revert files. If the problem persists, verify game files through the launcher.

**Q: Will the changes survive a game update?**  
A: No, updates overwrite files. You need to re‑generate the mod after each update. It is recommended to restore originals before updating.

**Q: Where are backups stored?**  
A: In the `HiddenTanks_Backup` folder inside the game folder. Do not delete it until you are sure the mod works properly.

**Q: Can I use this alongside other mods?**  
A: If other mods modify the same files (`tree_*.yaml` and `list.xml`), conflicts may occur. It is recommended to apply on a clean game installation.

**Q: What if `autoinstall_modules.bat` doesn't work?**  
A: Make sure Python is in your system `PATH`. If not, install dependencies manually with `pip install -r requirements.txt`.

---

## 📄 License

This project is distributed as **Freeware** – free for personal, non‑commercial use.  
The source code is open; you can modify it for your own needs.

---

## ✉️ Feedback

For questions, suggestions, or bug reports, please create an **Issue** in the repository or contact the developer by email.

---

**Enjoy the game!** 🎮
