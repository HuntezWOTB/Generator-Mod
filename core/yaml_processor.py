import re
import yaml
from collections import OrderedDict

CLASS_ORDER = {'lightTank': 0, 'mediumTank': 1, 'heavyTank': 2, 'AT-SPG': 3}

def parse_tree_yaml(text):
    commented = set()
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith('#'):
            content = stripped[1:].strip()
            match = re.match(r'^([\w\-\.]+)\s*:', content)
            if match:
                commented.add(match.group(1))
    try:
        data = yaml.safe_load(text)
    except:
        data = {}
    premium_rows = data.get('premium_rows', 1)
    tanks_dict = data.get('tanks', {})
    existing = set(tanks_dict.keys()) if tanks_dict else set()
    return premium_rows, existing, commented

def classify_tank(tank_name, tank_info):
    if tank_info['not_in_shop_orig'] and not tank_info['price_gold'] and 'deprecated' in tank_info['tags_orig']:
        return 'ordinary'
    if tank_info['price_gold']:
        if 'collectible' in tank_info['tags_orig']:
            return 'collectible'
        else:
            return 'premium'
    return 'premium'

def generate_tree_yaml(original_text, xml_tanks_data, nation_code=None):
    premium_rows, existing, commented = parse_tree_yaml(original_text)

    try:
        orig_data = yaml.safe_load(original_text)
        orig_tanks = orig_data.get('tanks', {})
    except:
        orig_tanks = {}

    # ТОЛЬКО ДЛЯ HN: корректируем уровни видимых танков согласно реальным уровням из XML
    if nation_code == 'HN':
        corrected_tanks = {}
        for name, params in orig_tanks.items():
            if isinstance(params, dict) and 'position' in params and name in xml_tanks_data:
                pos = params['position']
                if len(pos) >= 2:
                    real_level = xml_tanks_data[name]['level']
                    params['position'] = [real_level, pos[1]]
            corrected_tanks[name] = params
        orig_tanks = corrected_tanks

    visible_by_level = {}
    max_row_global = 0
    for name, params in orig_tanks.items():
        if isinstance(params, dict) and 'position' in params:
            pos = params['position']
            if len(pos) >= 2:
                lvl = pos[0]
                row = pos[1]
                if lvl not in visible_by_level:
                    visible_by_level[lvl] = []
                visible_by_level[lvl].append((row, name))
                if row > max_row_global:
                    max_row_global = row

    all_hidden = set()
    all_hidden.update(commented)
    for name in xml_tanks_data:
        if name not in existing:
            all_hidden.add(name)

    level_data = {}
    for name in all_hidden:
        if name not in xml_tanks_data:
            continue
        info = xml_tanks_data[name]
        lvl = info['level']   # реальный уровень (не меняется ни для какой нации)
        cat = classify_tank(name, info)
        cls = info['class_type']
        if lvl not in level_data:
            level_data[lvl] = {'ordinary': [], 'collectible': [], 'premium': []}
        level_data[lvl][cat].append((name, cls))

    for lvl in level_data:
        for cat in level_data[lvl]:
            level_data[lvl][cat].sort(key=lambda x: (CLASS_ORDER.get(x[1], 99), x[0]))

    for lvl in visible_by_level:
        visible_by_level[lvl].sort(key=lambda x: x[0])

    output = []
    output.append("# HiddenTanks-Generator")
    output.append("# v 1.0.0")
    output.append("# Generated code")
    output.append(f"premium_rows: {premium_rows}")
    output.append("")
    output.append("tanks:")

    all_levels = sorted(set(list(visible_by_level.keys()) + list(level_data.keys())))

    for lvl in all_levels:
        if lvl in visible_by_level:
            output.append(f"# Visible - {lvl} level - HiddenTanks-Generator")
            for row, name in visible_by_level[lvl]:
                output.append(f"    {name}:")
                output.append(f"        position: [{lvl}, {row}]")

        if lvl in level_data:
            # Единый стиль: все скрытые начинаются с глобального максимума + 1
            current_row = max_row_global + 1
            cats = ['ordinary', 'collectible', 'premium']
            for cat in cats:
                if not level_data[lvl][cat]:
                    continue
                output.append(f"# Hidden - {lvl} level - HiddenTanks-Generator")
                for name, _ in level_data[lvl][cat]:
                    output.append(f"    {name}:")
                    output.append(f"        position: [{lvl}, {current_row}]")
                    current_row += 1

    return "\n".join(output)