import configparser
import os
import re

def list_all_folders(directory_path):
    folders = []
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            folders.append(item)
    return folders

def find_folder_index_by_name(directory_path, folder_name):
    all_folders = list_all_folders(directory_path)
    try:
        index = all_folders.index(folder_name)
        return index
    except ValueError:
        return None

def find_title_id_index(config, title_id):
    section = f"DisabledAddOns"
    if not config.has_section(section):
        config.add_section(section)
    else:
        for key, value in config.items(section):
            if value == title_id:
                TitleIndexnum = key.split("\\")[0]
                return TitleIndexnum
    return 

def find_highest_title_id_index(config):
    section = "DisabledAddOns"
    if not config.has_section(section):
        config.add_section(section)
    else:
        highest_index = -1
        for key, value in config.items(section):
            match = re.match(r'^(\d+)\\title_id$', key)
            if match:
                index = int(match.group(1))
                highest_index = max(highest_index, index)
        return highest_index
    return None

def find_highest_disabled_index(config, title_id):
    section = "DisabledAddOns"
    if not config.has_section(section):
        config.add_section(section)
    else:
        highest_index = -1
        for key, value in config.items(section):
            match = re.match(r'^(\d+)\\disabled\\(\d+)\\d$', key)
            if match:
                title_index = int(match.group(1))
                if title_index == int(title_id):
                    disabled_index = int(match.group(2))
                    highest_index = max(highest_index, disabled_index)
        if highest_index >= 0:
            return highest_index
    # Return -1 if no disabled entry is found for the title_id
    return -1

def remove_entries_for_each(config, title_id):
    section = "DisabledAddOns"
    properindex = find_title_id_index(config, title_id)
    keys_to_remove = []
    # Find all properindexes present in the configuration
    for key in config[section]:
        match = re.match(f'^{properindex}\\\\disabled\\\\(\\d+)\\\\d', key)
        if match:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        config.remove_option(section, key)

def remove_duplicates(arr):
    return list(set(arr))

def get_d_values(config, properindex):
    section = "DisabledAddOns"
    d_values = []
    for key, value in config.items(section):
        if key.startswith(f"{properindex}\\disabled\\") and key.endswith("\\d"):
            d_values.append(value)
    return d_values

def find_and_remove_entry(configdir, directory, config, title_id, entry_to_remove):
    properindex = find_title_id_index(config, title_id)
    section = "DisabledAddOns"
    d_values = sorted(get_d_values(config, properindex))
    if not config.has_section(section):
        config.add_section(section)

    TitleIndexnum = find_title_id_index(config, title_id)
    disabledindex = find_highest_disabled_index(config, TitleIndexnum)
    testforfolder = find_folder_index_by_name(directory, entry_to_remove)
    if testforfolder is None:
        return

    found = False
    for key, value in config.items(section):
        if value == entry_to_remove:
            print(f"Entry to remove found: {entry_to_remove}")
            found = True
            break
    if not found:
        print(f"Entry '{entry_to_remove}' doesn't exist in section with title_id: {title_id}")
        return

    d_values.remove(f"{entry_to_remove}")
    d_values = remove_duplicates(d_values)
    d_values.sort()

    for i, d_value in enumerate(d_values):
        key = f"{properindex}\\disabled\\{i + 1}\\d"
        default_key = f"{properindex}\\disabled\\{i + 1}\\d\\default"
        config.set(section, key, d_value)
        config.set(section, default_key, "false")

    config.set(section, f"{TitleIndexnum}\\disabled\\size", str(disabledindex))
    write_config_file(configdir, config)

def add_entry(configdir, directory, config, title_id, entry_to_add):
    properindex = find_title_id_index(config, title_id)
    section = f"DisabledAddOns"
    if not config.has_section(section):
        config.add_section(section)

    TitleIndexnum = find_title_id_index(config, title_id)
    disabledindex = find_highest_disabled_index(config, TitleIndexnum)
    testforfolder = find_folder_index_by_name(directory, entry_to_add)
    if testforfolder is None:
        return
    # Check if the entry already exists
    d_values = sorted(get_d_values(config, properindex))
    if entry_to_add in d_values:
        print(f"Already exists{entry_to_add}")
        return

    d_values.append(f"{entry_to_add}")
    d_values = remove_duplicates(d_values)
    d_values.sort()

    for i, d_value in enumerate(d_values):
        key = f"{properindex}\\disabled\\{i + 1}\\d"
        default_key = f"{properindex}\\disabled\\{i + 1}\\d\\default"
        config.set(section, key, d_value)
        config.set(section, default_key, "false")

    config.set(section, f"{TitleIndexnum}\\disabled\\size", str(disabledindex))
    write_config_file(configdir, config)

def modify_disabled_key(configdir, directory, config, title_id, entry, action='add'):
    if action == "add":
        print("Adding key:", entry)
        add_entry(configdir, directory, config, title_id, entry)
    if action == "remove":
        print("Adding key:", entry)
        find_and_remove_entry(configdir, directory, config, title_id, entry)

def write_config_file(configdir, config):
    with open(configdir, 'w') as config_file:
        config.write(config_file, space_around_delimiters=False)