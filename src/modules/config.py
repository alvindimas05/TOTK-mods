from modules.checkpath import checkpath
from configuration.settings import *
import os, json, uuid

def save_user_choices(self, config_file, yuzu_path=None, mode=None):
    log.info(f"Saving user choices in {localconfig}")
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)

    if mode == "Cheats":
        config["Cheats"] = {}
        for option_name, option_var in self.selected_cheats.items():
            config['Cheats'][option_name] = option_var.get()
        with open(config_file, 'w', encoding="utf-8") as file:
            config["Manager"] = {}
            config["Manager"]["Cheat_Version"] = self.cheat_version.get()
            config.write(file)
        return

    # This is only required for the UI and FP mods.
    if not config.has_section("Options"):
        config["Options"] = {}
    config['Options']['UI'] = self.ui_var.get()
    config['Options']['First Person'] = self.fp_var.get()

    # Save the enable/disable choices
    for option_name, option_var in self.selected_options.items():
        config['Options'][option_name] = option_var.get()

    # Save the yuzu.exe path if provided
    if not config.has_section("Paths"):
        config["Paths"] = {}
    if self.mode == "Yuzu":
        if yuzu_path:
            config['Paths']['YuzuPath'] = yuzu_path
    if self.mode == "Ryujinx":
        if yuzu_path:
            config['Paths']['RyujinxPath'] = yuzu_path

    # Save the manager selected mode I.E Ryujinx/Yuzu
    config["Mode"] = {"ManagerMode": self.mode}

    if not config.has_section("Beyond"):
        config["Beyond"] = {}

    # UltraCam Beyond new patches.
    patch_info = self.ultracam_beyond.get("Keys", [""])
    for patch in self.BEYOND_Patches:
        patch_dict = patch_info[patch]
        patch_class = patch_dict["Class"]
        if patch_class.lower() == "dropdown":
            patch_Names = patch_dict["Name_Values"]
            index = patch_Names.index(self.BEYOND_Patches[patch].get())
            config["Beyond"][patch] = str(index)
            continue
        config["Beyond"][patch] = self.BEYOND_Patches[patch].get()

    log.info("User choices saved in Memory,"
             "Attempting to write into file.")
    # Write the updated configuration back to the file
    with open(config_file, 'w', encoding="utf-8") as file:
        config.write(file)
    log.info("Successfully written into log file")


def load_user_choices(self, config_file, mode=None):
    config = configparser.ConfigParser()
    config.read(config_file, encoding="utf-8")
    if mode == "Cheats":
        self.cheat_version.set(config.get("Manager", "Cheat_Version", fallback="Version - 1.2.0"))
        try:
            for option_name, option_var in self.selected_cheats.items():
                option_value = config.get('Cheats', option_name, fallback="Off")
                option_var.set(option_value)
        except AttributeError as e:
            # continue, not important.
            handle = e
        return

    # Load Ui and FP
    self.ui_var.set(config.get('Options', 'UI', fallback="None"))
    self.fp_var.set(config.get('Options', 'First Person', fallback="Off"))

    # Load UltraCam Beyond new patches.
    patch_info = self.ultracam_beyond.get("Keys", [""])
    for patch in self.BEYOND_Patches:
        patch_dict = patch_info[patch]
        patch_class = patch_dict["Class"]
        if patch_class.lower() == "dropdown":
            patch_Names = patch_dict["Name_Values"]
            try:
                self.BEYOND_Patches[patch].set(patch_Names[int(config["Beyond"][patch])])
            except KeyError:
                pass
            continue
        try:
            self.BEYOND_Patches[patch].set(config["Beyond"][patch])
        except KeyError:
            pass

    # Load the enable/disable choices
    for option_name, option_var in self.selected_options.items():
        option_value = config.get('Options', option_name, fallback="Off")
        option_var.set(option_value)

    # Load the enable/disabled cheats
    try:
        for option_name, option_var in self.selected_cheats.items():
            option_value = config.get('Cheats', option_name, fallback="Off")
            option_var.set(option_value)
    except AttributeError as e:
        # continue, not important.
        handle = e

def write_yuzu_config(configfile, section, setting, selection):
    yuzuconfig = configparser.ConfigParser()
    yuzuconfig.read(configfile, encoding="utf-8")
    if not yuzuconfig.has_section(section):
        yuzuconfig[f"{section}"] = {}
    yuzuconfig[f"{section}"][f"{setting}\\use_global"] = "false"
    yuzuconfig[f"{section}"][f"{setting}\\default"] = "false"
    yuzuconfig[f"{section}"][f"{setting}"] = selection
    with open(configfile, "w", encoding="utf-8") as configfile:
        yuzuconfig.write(configfile, space_around_delimiters=False)


def write_ryujinx_config(configfile, setting, selection):
    with open(configfile, "r", encoding="utf-8") as file:
        data = json.load(file)
        data[setting] = selection

    os.remove(configfile)
    with open(configfile, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2)