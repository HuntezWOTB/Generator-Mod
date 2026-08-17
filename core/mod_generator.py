import os
import shutil
import stat
import xml.etree.ElementTree as ET
from core.dvpl_utils import is_dvpl_file, decompress_dvpl_to_text, compress_text_to_dvpl, read_dvpl, write_dvpl
from core.xml_processor import process_xml
from core.yaml_processor import generate_tree_yaml

NATIONS = {
    'CN': ('china', 'Configs/TechTree/china_tree.yaml', 'XML/item_defs/vehicles/china/list.xml'),
    'EU': ('european', 'Configs/TechTree/european_tree.yaml', 'XML/item_defs/vehicles/european/list.xml'),
    'FR': ('france', 'Configs/TechTree/france_tree.yaml', 'XML/item_defs/vehicles/france/list.xml'),
    'DE': ('germany', 'Configs/TechTree/germany_tree.yaml', 'XML/item_defs/vehicles/germany/list.xml'),
    'JP': ('japan', 'Configs/TechTree/japan_tree.yaml', 'XML/item_defs/vehicles/japan/list.xml'),
    'HN': ('other', 'Configs/TechTree/other_tree.yaml', 'XML/item_defs/vehicles/other/list.xml'),
    'UK': ('uk', 'Configs/TechTree/uk_tree.yaml', 'XML/item_defs/vehicles/uk/list.xml'),
    'US': ('usa', 'Configs/TechTree/usa_tree.yaml', 'XML/item_defs/vehicles/usa/list.xml'),
    'SU': ('ussr', 'Configs/TechTree/ussr_tree.yaml', 'XML/item_defs/vehicles/ussr/list.xml'),
}

BACKUP_DIR_NAME = "HiddenTanks_Backup"
DLC_ROOT = os.path.expanduser("~") + "/AppData/Local/wotblitz/packs"

def decode_text(data):
    encodings = ['utf-8-sig', 'utf-8', 'cp1251', 'latin-1', 'cp866']
    for enc in encodings:
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', errors='replace'), 'utf-8'

def read_file_content(filepath, log_func=print, tr_func=None):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'rb') as f:
        raw_data = f.read()
    data, compression_type = read_dvpl(filepath)
    if compression_type is not None:
        text, encoding = decode_text(data)
        if tr_func:
            log_func(tr_func('log_detected_dvpl', compression_type=compression_type))
        else:
            log_func(f"  Detected as DVPL file (compression_type={compression_type})")
        if encoding == 'utf-8-sig':
            encoding = 'utf-8'
        return text, encoding, True, compression_type
    try:
        text, encoding = decode_text(raw_data)
        if text.strip().startswith(('<', '#')):
            if tr_func:
                log_func(tr_func('log_detected_plain'))
            else:
                log_func(f"  Detected as plain text file")
            if encoding == 'utf-8-sig':
                encoding = 'utf-8'
            return text, encoding, False, None
    except:
        pass
    if tr_func:
        log_func(tr_func('log_detected_binary'))
    else:
        log_func(f"  Detected as binary file, trying to decode...")
    text, encoding = decode_text(raw_data)
    if encoding == 'utf-8-sig':
        encoding = 'utf-8'
    return text, encoding, False, None

def write_file_content(filepath, text, encoding, is_dvpl, compression_type=None, log_func=print, tr_func=None):
    if is_dvpl:
        if compression_type is None:
            compression_type = 2
        if tr_func:
            log_func(tr_func('log_writing_dvpl', compression_type=compression_type))
        else:
            log_func(f"  Writing as DVPL file (compression_type={compression_type})")
        compress_text_to_dvpl(filepath, text, encoding, compression_type)
    else:
        if tr_func:
            log_func(tr_func('log_writing_plain'))
        else:
            log_func(f"  Writing as plain text")
        with open(filepath, 'wb') as f:
            f.write(text.encode(encoding))

def get_file_paths(game_path, nation_code, use_dlc=False, log_func=print, tr_func=None):
    _, tree_rel, list_rel = NATIONS[nation_code]
    game_tree = os.path.join(game_path, "Data", tree_rel)
    game_list = os.path.join(game_path, "Data", list_rel)
    game_tree_dvpl = game_tree + ".dvpl"
    game_list_dvpl = game_list + ".dvpl"
    dlc_tree = os.path.join(DLC_ROOT, tree_rel) + ".dvpl"
    dlc_list = os.path.join(DLC_ROOT, list_rel) + ".dvpl"

    final_tree = game_tree_dvpl if os.path.exists(game_tree_dvpl) else game_tree
    final_list = game_list_dvpl if os.path.exists(game_list_dvpl) else game_list
    is_dlc = False

    if use_dlc:
        if tr_func:
            log_func(tr_func('log_dlc_checking_tree', file=dlc_tree))
        else:
            log_func(f"  [DLC] Checking tree: {dlc_tree}")
        dlc_tree_exists = os.path.exists(dlc_tree)
        if tr_func:
            log_func(tr_func('log_dlc_tree_exists', exists=dlc_tree_exists))
        else:
            log_func(f"  [DLC] Tree exists? {dlc_tree_exists}")

        if tr_func:
            log_func(tr_func('log_dlc_checking_list', file=dlc_list))
        else:
            log_func(f"  [DLC] Checking list: {dlc_list}")
        dlc_list_exists = os.path.exists(dlc_list)
        if tr_func:
            log_func(tr_func('log_dlc_list_exists', exists=dlc_list_exists))
        else:
            log_func(f"  [DLC] List exists? {dlc_list_exists}")

        if dlc_tree_exists:
            final_tree = dlc_tree
            is_dlc = True
            if tr_func:
                log_func(tr_func('log_dlc_using_dlc_tree'))
            else:
                log_func(f"  [DLC] Using DLC tree")
        else:
            if tr_func:
                log_func(tr_func('log_dlc_using_game_tree'))
            else:
                log_func(f"  [DLC] Using Game tree (DLC not found)")

        if dlc_list_exists:
            final_list = dlc_list
            is_dlc = True
            if tr_func:
                log_func(tr_func('log_dlc_using_dlc_list'))
            else:
                log_func(f"  [DLC] Using DLC list")
        else:
            if tr_func:
                log_func(tr_func('log_dlc_using_game_list'))
            else:
                log_func(f"  [DLC] Using Game list (DLC not found)")

        if not is_dlc:
            if tr_func:
                log_func(tr_func('log_dlc_no_files'))
            else:
                log_func(f"  [DLC] No DLC files found, falling back to Game")
    else:
        if tr_func:
            log_func(tr_func('log_using_game'))
        else:
            log_func(f"  Using Game files (DLC disabled)")

    return final_tree, final_list, is_dlc, tree_rel, list_rel

def load_and_process_files(game_path, nation_code, use_dlc=False, log_func=print, tr_func=None):
    tree_file, list_file, is_dlc, tree_rel, list_rel = get_file_paths(game_path, nation_code, use_dlc, log_func, tr_func)
    if not os.path.exists(tree_file) or not os.path.exists(list_file):
        if tr_func:
            log_func(tr_func('log_files_not_found'))
        else:
            log_func(f"  ✗ Files not found, skipping")
        return None

    if tr_func:
        log_func(tr_func('log_reading_tree', file=tree_file))
    else:
        log_func(f"  Reading tree: {tree_file}")
    tree_text, tree_encoding, tree_is_dvpl, tree_compression_type = read_file_content(tree_file, log_func, tr_func)

    if tr_func:
        log_func(tr_func('log_reading_list', file=list_file))
    else:
        log_func(f"  Reading list: {list_file}")
    list_text, list_encoding, list_is_dvpl, list_compression_type = read_file_content(list_file, log_func, tr_func)

    if not list_text.strip() or not tree_text.strip():
        if tr_func:
            log_func(tr_func('log_empty_file'))
        else:
            log_func(f"  ✗ Empty file, skipping")
        return None

    original_tree_text = tree_text
    original_list_text = list_text

    if tr_func:
        log_func(tr_func('log_processing_xml'))
    else:
        log_func("  Processing XML...")
    new_list_text, tank_data = process_xml(list_text)

    if tr_func:
        log_func(tr_func('log_processing_yaml'))
    else:
        log_func("  Processing YAML...")
    new_tree_text = generate_tree_yaml(tree_text, tank_data, nation_code=nation_code)

    stat = get_nation_stat(tank_data, tree_text)

    return {
        'tree_file': tree_file,
        'list_file': list_file,
        'is_dlc': is_dlc,
        'tree_rel': tree_rel,
        'list_rel': list_rel,
        'tree_encoding': tree_encoding,
        'list_encoding': list_encoding,
        'tree_is_dvpl': tree_is_dvpl,
        'list_is_dvpl': list_is_dvpl,
        'tree_compression_type': tree_compression_type,
        'list_compression_type': list_compression_type,
        'original_tree_text': original_tree_text,
        'original_list_text': original_list_text,
        'new_tree_text': new_tree_text,
        'new_list_text': new_list_text,
        'tank_data': tank_data,
        'stat': stat
    }

def apply_mod(game_path, mode, use_dlc=False, log_func=print, tr_func=None):
    stats = {}
    for code, (name, tree_rel, list_rel) in NATIONS.items():
        if tr_func:
            log_func(tr_func('log_processing_nation', code=code, name=name))
        else:
            log_func(f"\n{'='*50}")
            log_func(f"Processing {code} ({name})...")
        result = load_and_process_files(game_path, code, use_dlc, log_func, tr_func)
        if result is None:
            continue
        if tr_func:
            log_func(tr_func('log_writing_files'))
        else:
            log_func("  Writing files...")
        write_file_content(result['tree_file'], result['new_tree_text'], result['tree_encoding'],
                           result['tree_is_dvpl'], result['tree_compression_type'], log_func, tr_func)
        write_file_content(result['list_file'], result['new_list_text'], result['list_encoding'],
                           result['list_is_dvpl'], result['list_compression_type'], log_func, tr_func)
        if result['is_dlc']:
            os.chmod(result['tree_file'], stat.S_IREAD)
            os.chmod(result['list_file'], stat.S_IREAD)
            if tr_func:
                log_func(tr_func('log_set_readonly'))
            else:
                log_func("  Set read-only attribute on DLC files")
        stats[code] = result['stat']
        if tr_func:
            log_func(tr_func('log_stats_line',
                             visible=result['stat']['visible'],
                             ordinary=result['stat']['hidden_ordinary'],
                             collectible=result['stat']['hidden_collectible'],
                             premium=result['stat']['hidden_premium']))
        else:
            log_func(f"  Stats: {result['stat']['visible']} visible, {result['stat']['hidden_ordinary']} ordinary, "
                    f"{result['stat']['hidden_collectible']} collectible, {result['stat']['hidden_premium']} premium")
        if tr_func:
            log_func(tr_func('log_completed', code=code))
        else:
            log_func(f"  ✓ {code} completed")
    return stats

def get_mod_stats(game_path, mode, use_dlc=False, log_func=print, tr_func=None):
    stats = {}
    for code, (name, tree_rel, list_rel) in NATIONS.items():
        if tr_func:
            log_func(tr_func('log_processing_nation', code=code, name=name))
        else:
            log_func(f"\n{'='*50}")
            log_func(f"Processing {code} ({name})...")
        tree_file, list_file, is_dlc, tree_rel, list_rel = get_file_paths(game_path, code, use_dlc, log_func, tr_func)
        if tr_func:
            log_func(tr_func('log_using_game' if not is_dlc else 'log_dlc_using_dlc_tree')) # упростим
        else:
            log_func(f"  Using {'DLC' if is_dlc else 'Game'} files")
        result = load_and_process_files(game_path, code, use_dlc, log_func, tr_func)
        if result is None:
            continue
        stats[code] = result['stat']
        if tr_func:
            log_func(tr_func('log_stats_line',
                             visible=result['stat']['visible'],
                             ordinary=result['stat']['hidden_ordinary'],
                             collectible=result['stat']['hidden_collectible'],
                             premium=result['stat']['hidden_premium']))
        else:
            log_func(f"  Stats: {result['stat']['visible']} visible, {result['stat']['hidden_ordinary']} ordinary, "
                    f"{result['stat']['hidden_collectible']} collectible, {result['stat']['hidden_premium']} premium")
    return stats

def backup_files(game_path, mode, use_dlc=False, log_func=print, tr_func=None):
    backup_root = os.path.join(game_path, BACKUP_DIR_NAME)
    if not os.path.exists(backup_root):
        os.makedirs(backup_root)
    for code, (name, tree_rel, list_rel) in NATIONS.items():
        tree_file, list_file, is_dlc, tree_rel, list_rel = get_file_paths(game_path, code, use_dlc, log_func, tr_func)
        if is_dlc:
            base = DLC_ROOT
        else:
            base = game_path
        rel_tree = os.path.relpath(tree_file, base)
        rel_list = os.path.relpath(list_file, base)
        prefix = "DLC" if is_dlc else "Game"
        backup_tree = os.path.join(backup_root, prefix, rel_tree)
        backup_list = os.path.join(backup_root, prefix, rel_list)
        os.makedirs(os.path.dirname(backup_tree), exist_ok=True)
        os.makedirs(os.path.dirname(backup_list), exist_ok=True)
        shutil.copy2(tree_file, backup_tree)
        shutil.copy2(list_file, backup_list)
        if tr_func:
            log_func(tr_func('log_backup_file', file=backup_tree))
            log_func(tr_func('log_backup_file', file=backup_list))
        else:
            log_func(f"Backup: {backup_tree}")
            log_func(f"Backup: {backup_list}")
    return backup_root

def restore_original(game_path, log_func=print, tr_func=None):
    backup_root = os.path.join(game_path, BACKUP_DIR_NAME)
    if not os.path.exists(backup_root):
        if tr_func:
            log_func(tr_func('log_no_backup'))
        else:
            log_func("No backup found.")
        return
    if tr_func:
        log_func(tr_func('log_restore_start'))
    else:
        log_func("Restoring original files...")
    restored = 0
    for prefix in ["Game", "DLC"]:
        src_root = os.path.join(backup_root, prefix)
        if not os.path.exists(src_root):
            continue
        base = game_path if prefix == "Game" else DLC_ROOT
        for dirpath, _, filenames in os.walk(src_root):
            for f in filenames:
                src = os.path.join(dirpath, f)
                rel = os.path.relpath(src, src_root)
                dst = os.path.join(base, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if os.path.exists(dst):
                    try:
                        os.chmod(dst, stat.S_IWRITE)
                    except:
                        pass
                shutil.copy2(src, dst)
                if tr_func:
                    log_func(tr_func('log_restored_file', file=dst))
                else:
                    log_func(f"Restored: {dst}")
                restored += 1
    if tr_func:
        log_func(tr_func('log_restored_count', count=restored))
    else:
        log_func(f"Restored {restored} files. Backup folder kept.")

def get_game_version(game_path):
    version_file = os.path.join(game_path, "Data", "version.txt")
    version_dvpl = version_file + ".dvpl"
    try:
        if os.path.exists(version_dvpl):
            text, enc, is_dvpl, comp = read_file_content(version_dvpl, log_func=lambda x: None)
        elif os.path.exists(version_file):
            text, enc, is_dvpl, comp = read_file_content(version_file, log_func=lambda x: None)
        else:
            return "unknown"
        first_line = text.splitlines()[0] if text else ""
        version = first_line.split()[0] if first_line else "unknown"
        return version
    except:
        return "unknown"

def export_mod(game_path, mode, use_dlc=False, log_func=print, tr_func=None):
    try:
        version = get_game_version(game_path)
        if version == "unknown":
            version = "unknown_version"
        result_root = os.path.join(os.getcwd(), "result", f"HiddenTanks_Generated_{version}")
        mod_root = os.path.join(result_root, "Mod")
        backup_root_out = os.path.join(result_root, "Backup")
        os.makedirs(mod_root, exist_ok=True)
        os.makedirs(backup_root_out, exist_ok=True)

        for code, (name, tree_rel, list_rel) in NATIONS.items():
            if tr_func:
                log_func(tr_func('log_processing_nation', code=code, name=name))
            else:
                log_func(f"\nProcessing {code}...")
            result = load_and_process_files(game_path, code, use_dlc, log_func, tr_func)
            if result is None:
                continue

            tree_file = result['tree_file']
            list_file = result['list_file']
            user_home = os.path.expanduser("~")
            if tree_file.startswith(DLC_ROOT):
                rel_tree = os.path.relpath(tree_file, user_home)
            else:
                rel_tree = os.path.relpath(tree_file, game_path)

            if list_file.startswith(DLC_ROOT):
                rel_list = os.path.relpath(list_file, user_home)
            else:
                rel_list = os.path.relpath(list_file, game_path)

            dest_tree = os.path.join(mod_root, rel_tree)
            dest_list = os.path.join(mod_root, rel_list)
            os.makedirs(os.path.dirname(dest_tree), exist_ok=True)
            os.makedirs(os.path.dirname(dest_list), exist_ok=True)
            write_file_content(dest_tree, result['new_tree_text'], result['tree_encoding'],
                               result['tree_is_dvpl'], result['tree_compression_type'], log_func, tr_func)
            write_file_content(dest_list, result['new_list_text'], result['list_encoding'],
                               result['list_is_dvpl'], result['list_compression_type'], log_func, tr_func)

            dest_backup_tree = os.path.join(backup_root_out, rel_tree)
            dest_backup_list = os.path.join(backup_root_out, rel_list)
            os.makedirs(os.path.dirname(dest_backup_tree), exist_ok=True)
            os.makedirs(os.path.dirname(dest_backup_list), exist_ok=True)
            write_file_content(dest_backup_tree, result['original_tree_text'], result['tree_encoding'],
                               result['tree_is_dvpl'], result['tree_compression_type'], log_func, tr_func)
            write_file_content(dest_backup_list, result['original_list_text'], result['list_encoding'],
                               result['list_is_dvpl'], result['list_compression_type'], log_func, tr_func)

            if tr_func:
                log_func(tr_func('log_completed', code=code))
            else:
                log_func(f"  ✓ {code} exported")

        if tr_func:
            log_func(tr_func('log_export_completed_to', path=result_root))
        else:
            log_func(f"Export completed to {result_root}")
    except Exception as e:
        if tr_func:
            log_func(tr_func('log_export_error', error=str(e)))
        else:
            log_func(f"Export error: {e}")
        import traceback
        log_func(traceback.format_exc())

def get_list_tanks(filepath, log_func=print, tr_func=None):
    try:
        text, encoding, is_dvpl, comp_type = read_file_content(filepath, log_func, tr_func)
        if not text or not text.strip():
            return set()
        root = ET.fromstring(text)
        tanks = set()
        for vehicle in root:
            tanks.add(vehicle.tag)
        return tanks
    except Exception as e:
        if tr_func:
            log_func(tr_func('log_error_reading_list', file=filepath, error=str(e)))
        else:
            log_func(f"  Error reading list file {filepath}: {e}")
        return set()

def compare_lists(game_path, nation_code, use_dlc, log_func=print, tr_func=None):
    if not use_dlc:
        return None
    _, tree_rel, list_rel = NATIONS[nation_code]
    game_list = os.path.join(game_path, "Data", list_rel)
    game_list_dvpl = game_list + ".dvpl"
    dlc_list = os.path.join(DLC_ROOT, list_rel) + ".dvpl"

    if os.path.exists(game_list_dvpl):
        game_path_to_read = game_list_dvpl
    elif os.path.exists(game_list):
        game_path_to_read = game_list
    else:
        if tr_func:
            log_func(tr_func('log_game_list_not_found', code=nation_code))
        else:
            log_func(f"  Game list not found for {nation_code}")
        return None

    if not os.path.exists(dlc_list):
        if tr_func:
            log_func(tr_func('log_dlc_list_not_found', code=nation_code))
        else:
            log_func(f"  DLC list not found for {nation_code}")
        return None

    if tr_func:
        log_func(tr_func('log_comparing_dlc_game', code=nation_code))
    else:
        log_func(f"  Comparing game list and DLC list for {nation_code}...")

    game_tanks = get_list_tanks(game_path_to_read, log_func, tr_func)
    dlc_tanks = get_list_tanks(dlc_list, log_func, tr_func)

    if not game_tanks and not dlc_tanks:
        return None

    only_in_dlc = dlc_tanks - game_tanks
    only_in_game = game_tanks - dlc_tanks
    common = game_tanks & dlc_tanks

    return {
        'only_in_dlc': len(only_in_dlc),
        'only_in_game': len(only_in_game),
        'common': len(common),
        'total_dlc': len(dlc_tanks),
        'total_game': len(game_tanks),
        'new_tanks': sorted(only_in_dlc)
    }

def get_nation_stat(tank_data, tree_yaml_text):
    import yaml
    visible = set()
    try:
        data = yaml.safe_load(tree_yaml_text)
        if data and 'tanks' in data:
            visible = set(data['tanks'].keys())
    except:
        pass
    visible_count = len(visible)
    hidden = {'ordinary': 0, 'collectible': 0, 'premium': 0}
    for name, info in tank_data.items():
        if name not in visible:
            cat = classify_tank_static(info)
            hidden[cat] = hidden.get(cat, 0) + 1
    return {
        'visible': visible_count,
        'hidden_ordinary': hidden.get('ordinary', 0),
        'hidden_collectible': hidden.get('collectible', 0),
        'hidden_premium': hidden.get('premium', 0),
    }

def classify_tank_static(info):
    from core.yaml_processor import classify_tank
    return classify_tank(None, info)