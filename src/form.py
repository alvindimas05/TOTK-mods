from configuration.settings import *
from configuration.settings_config import Setting
from modules.TOTK_Optimizer_Modules import * # imports all needed files.
from modules.GameManager.GameManager import *
from modules.GameManager.FileManager import *
import threading
import webbrowser
import ttkbootstrap as ttk

class Manager:

    patches = []
    patchInfo = None
    _window = ttk.Window
    constyle = Style

    def __init__(self, window):
        
        Game_Manager.LoadPatches()
        FileManager.Initialize(window, self)
        self.patches = Game_Manager.GetPatches()

        # This should be set Dynamically
        self.patchInfo = self.patches[1]
        log.info(f"{self.patchInfo.Folder}")

        self._window = window
        self.constyle = Style(theme=theme.lower())
        self.constyle.configure("TButton", font=btnfont)

        # ULTRACAM 2.0 PATCHES ARE SAVED HERE.
        self.BEYOND_Patches = {}

        # Set initialize different Classes.
        self.on_canvas = Canvas_Create()
        self.setting = Setting()

        # Append all canvas in Manager class.
        self.all_canvas = []

        # Load the Config.
        self.config = localconfig

        # Read the Current Emulator Mode.
        self.mode = config.get("Mode", "managermode", fallback="Legacy")
        self.all_pages = ["main", "extra", "randomizer"]

        # Force to Ryujinx default
        if platform.system() == "Darwin":
            self.mode = "Ryujinx"

        # Set neccesary variables.
        self.Curr_Benchmark = None
        self.is_Ani_running = False
        self.is_Ani_Paused = False
        self.tooltip_active = False
        self.warn_again = "yes"
        self.title_id = title_id
        self.config_title_id = config_title_id
        self.old_cheats = {}
        self.cheat_version = ttk.StringVar(value="Version - 1.2.1")

        # Initialize Json Files.
        self.description = load_json("Description.json", descurl)
        self.presets = load_json("beyond_presets.json", presetsurl)
        self.version_options = load_json("Version.json", versionurl)
        self.cheat_options = load_json("Cheats.json", cheatsurl)
        self.ultracam_beyond = load_json("UltraCam_Template.json", ultracambeyond)
        self.Legacy_settings = load_json("Legacy_presets.json", Legacy_presets_url)

        self.benchmarks = {}

        if os.path.exists(os.path.join("TOTKOptimizer/UltraCam_Template.json")):
            with open("TOTKOptimizer/UltraCam_Template.json", "r", encoding="utf-8") as file:
                self.ultracam_beyond = json.load(file)

        # Local text variable
        self.switch_text = ttk.StringVar(value="Switch to Ryujinx")

        # Load Canvas
        Load_ImagePath(self)
        self.load_canvas()
        self.switchmode("false")

        #Window protocols
        self._window.protocol("WM_DELETE_WINDOW", lambda: self.on_canvas.on_closing(self._window))

    def warning(self, e):
        messagebox.showwarning(f"{e}")

    def create_canvas(self):
        # Create Canvas
        self.maincanvas = ttk.Canvas(self._window, width=scale(1200), height=scale(600))
        canvas = self.maincanvas
        self.maincanvas.pack()
        self.all_canvas.append(self.maincanvas)

        self.selected_options = {}

        # Load UI Elements
        load_UI_elements(self, self.maincanvas)
        create_tab_buttons(self, self.maincanvas)

        # Create Text Position
        row = 40
        cul_tex = 60
        cul_sel = 220

        # Used for 2nd column.
        row_2 = 160
        cul_tex_2 = 400
        cul_sel_2 = 550

        def increase_row(row, cul_sel, cul_tex):
            row += 40
            if row >= 480:
                row = 160
                cul_tex += 180
                cul_sel += 180
            return row, cul_sel, cul_tex

        # Run Scripts for checking OS and finding location
        FileManager.checkpath(self.mode)
        FileManager.DetectOS(self.mode)

        # FOR DEBUGGING PURPOSES
        def onCanvasClick(event):
            print(f"CRODS = X={event.x} + Y={event.y} + {event.widget}")

        self.maincanvas.bind("<Button-3>", onCanvasClick)
        # Start of CANVAS options.

        # Create preset menu.
        presets = {"Saved": {}} | load_json("beyond_presets.json", presetsurl)
        values = list(presets.keys())
        self.selected_preset = self.on_canvas.create_combobox(
                                                            master=self._window, canvas=canvas,
                                                            text="OPTIMIZER PRESETS:",
                                                            variable=values[0], values=values,
                                                            row=row, cul=cul_tex - 20,
                                                            tags=["text"], tag="Optimizer",
                                                            description_name="Presets",
                                                            command=lambda event: apply_selected_preset(self)
                                                        )

        # Setting Preset - returns variable.

        value = ["No Change"]
        for item in self.Legacy_settings:
            value.append(item)
        self.selected_settings = self.on_canvas.create_combobox(
                                                            master=self._window, canvas=canvas,
                                                            text="Legacy SETTINGS:",
                                                            variable=value[0], values=value,
                                                            row=row, cul=340, drop_cul=480,
                                                            tags=["text"], tag="Legacy",
                                                            description_name="Settings"
                                                        )

        row += 40
        # Create a label for Legacy.exe selection
        backupbutton = cul_sel
        command = lambda event: self.select_Legacy_exe()
        def browse():
            self.select_Legacy_exe()

        text = "SELECT EXECUTABLE"
        self.on_canvas.create_button(
                                    master=self._window, canvas=canvas,
                                    btn_text="Browse",
                                    row=row, cul=cul_sel, width=6,
                                    tags=["Button"],
                                    description_name="Browse",
                                    command=lambda: browse()
                                    )

        # Reset to Appdata
        def Legacy_appdata():
            FileManager.checkpath(self.mode)
            log.info("Successfully Defaulted to Appdata!")
            save_user_choices(self, self.config, "appdata", None)

        self.on_canvas.create_button(
                                    master=self._window, canvas=canvas,
                                    btn_text="Use Appdata",
                                    row=row, cul=cul_sel + 68, width=9,
                                    tags=["Button"],
                                    description_name="Reset",
                                    command=Legacy_appdata
                                    )
        backupbutton = cul_sel + 165


        self.on_canvas.create_label(
                                    master=self._window, canvas=canvas,
                                    text=text,
                                    description_name="Browse",
                                    row=row, cul=cul_tex - 20,
                                    tags=["text"], tag=["Select-EXE"], outline_tag="outline",
                                    command=command
                                    )

        # Create a Backup button
        self.on_canvas.create_button(
                                    master=self._window, canvas=canvas,
                                    btn_text="Backup",
                                    row=row, cul=backupbutton, width=7,
                                    tags=["Button"],
                                    description_name="Backup",
                                    command=lambda: backup(self)
        )

        self.on_canvas.create_button(
                                    master=self._window, canvas=canvas,
                                    btn_text="Clear Shaders",
                                    row=row, cul=backupbutton+78, width=9,
                                    tags=["Button", "Legacy"],
                                    description_name="Shaders",
                                    command=lambda: clean_shaders(self)
        )
        row += 40

        self.graphics_element = self.on_canvas.Photo_Image(
            image_path="graphics.png",
            width=int(70*1.6), height=int(48*1.6),
        )

        self.graphics_element_active = self.on_canvas.Photo_Image(
            image_path="graphics_active.png",
            width=int(70*1.6), height=int(48*1.6),
        )

        self.extra_element = self.on_canvas.Photo_Image(
            image_path="extra.png",
            width=int(70*1.6), height=int(48*1.6),
        )

        self.extra_element_active = self.on_canvas.Photo_Image(
            image_path="extra_active.png",
            width=int(70*1.6), height=int(48*1.6),
        )

        # Graphics & Extra & More - the -20 is extra
        self.on_canvas.image_Button(
            canvas=canvas,
            row=row - 35, cul=cul_tex - 10 - 20,
            img_1=self.graphics_element, img_2=self.graphics_element_active,
            command=lambda event: self.toggle_page(event, "main")
        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=row - 35, cul=cul_tex + 190 - 10,
            img_1=self.extra_element, img_2=self.extra_element_active,
            command=lambda event: self.toggle_page(event, "extra")
        )

        # BIG TEXT.
        self.on_canvas.create_label(
                                    master=self._window, canvas=canvas,
                                    text="Tears Of The Kingdom", font=bigfont, color=BigTextcolor,
                                    description_name="Mod Improvements", anchor="c",
                                    row=row, cul=575,
                                    tags=["Big-Text"]
                                    )

        row += 40

        ##              AUTO PATCH INFO STARTS HERE ALL CONTROLLED IN JSON FILE.
        ##              THIS IS FOR ULTRACAM BEYOND GRAPHICS AND PERFORMANCE (2.0)
        ##              REMOVED DFPS, SINCE ULTRACAM BEYOND DOES IT ALL AND SO MUCH BETTER.
        ##

        pos_dict = {
            "main": [row,  cul_tex, cul_sel, row_2, cul_tex_2, cul_sel_2],
            "extra": [row, cul_tex, cul_sel,  row_2, cul_tex_2, cul_sel_2]
        }

        keys = self.ultracam_beyond.get("Keys", [""])

        for name in keys:
            dicts = keys[name]

            patch_var = None
            patch_list = dicts.get("Name_Values", [""])
            patch_values = dicts.get("Values")
            patch_name = dicts.get("Name")
            patch_auto = dicts.get("Auto")
            section_auto = dicts.get("Section")
            patch_description = dicts.get("Description")
            patch_default_index = dicts.get("Default")
            pos = pos_dict[section_auto]
            if patch_auto is True:
                self.BEYOND_Patches[name] = ttk.StringVar(master=self._window, value="auto")
                continue

            if dicts["Class"].lower() == "dropdown":
                patch_var = self.on_canvas.create_combobox(
                            master=self._window, canvas=canvas,
                            text=patch_name,
                            values=patch_list, variable=patch_list[patch_default_index],
                            row=pos[0], cul=pos[1], drop_cul=pos[2], width=100,
                            tags=["dropdown"], tag=section_auto,
                            text_description=patch_description
                            )
                new_pos = increase_row(pos[0], pos[1], pos[2])
                pos[0] = new_pos[0]
                pos[1] = new_pos[1]
                pos[2] = new_pos[2]

            if dicts["Class"].lower() == "scale":
                patch_type = dicts.get("Type")
                patch_increments = dicts.get("Increments")
                patch_var = self.on_canvas.create_scale(
                    master=self._window, canvas=canvas,
                    text=patch_name,
                    scale_from=patch_values[0], scale_to=patch_values[1], type=patch_type,
                    row=pos[0], cul=pos[1], drop_cul=pos[2], width=100, increments=float(patch_increments),
                    tags=["scale"], tag=section_auto,
                    text_description=patch_description
                )
                if patch_type == "f32":
                    print(f"{patch_name} - {patch_default_index}")
                    patch_var.set(float(patch_default_index))
                else:
                    patch_var.set(patch_default_index)

                canvas.itemconfig(patch_name, text=f"{float(patch_default_index)}")
                new_pos = increase_row(pos[0], pos[1], pos[2])
                pos[0] = new_pos[0]
                pos[1] = new_pos[1]
                pos[2] = new_pos[2]

            if dicts["Class"].lower() == "bool":
                patch_var = self.on_canvas.create_checkbutton(
                    master=self._window, canvas=canvas,
                    text=patch_name,
                    variable="Off",
                    row=pos[3], cul=pos[4], drop_cul=pos[5],
                    tags=["bool"], tag=section_auto,
                    text_description=patch_description
                )
                if patch_default_index:
                    patch_var.set("On")
                new_pos = increase_row(pos[3], pos[4], pos[5])
                pos[3] = new_pos[0]
                pos[4] = new_pos[1]
                pos[5] = new_pos[2]

            if patch_var is None:
                continue
            self.BEYOND_Patches[name] = patch_var

        row = pos_dict["main"][0]
        row_2 = pos_dict["main"][3]

        self.apply_element = self.on_canvas.Photo_Image(
                        image_path="apply.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )

        self.apply_element_active = self.on_canvas.Photo_Image(
                        image_path="apply_active.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )

        self.launch_element = self.on_canvas.Photo_Image(
                        image_path="launch.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )
        self.launch_element_active = self.on_canvas.Photo_Image(
                        image_path="launch_active.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )

        self.extract_element = self.on_canvas.Photo_Image(
                        image_path="extract.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )
        self.extract_element_active = self.on_canvas.Photo_Image(
                        image_path="extract_active.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )

        self.LOGO_element = self.on_canvas.Photo_Image(
                        image_path="optimizer_logo.png",
                        width=int(3316/10), height=int(823/10),
                        )

        self.LOGO_element_active = self.on_canvas.Photo_Image(
                        image_path="optimizer_logo_active.png",
                        width=int(3316/10), height=int(823/10),
                        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=510, cul=25,
            img_1=self.apply_element, img_2=self.apply_element_active,
            command=lambda event: FileManager.submit()
        )

        # reverse scale.
        self.on_canvas.image_Button(
            canvas=canvas,
            row=510, cul=25 + int(self.apply_element.width() / sf),
            img_1=self.launch_element, img_2=self.launch_element_active,
            command=lambda event: FileManager.launch_GAME()
        )

        # extract
        self.on_canvas.image_Button(
            canvas=canvas,
            row=510, cul=25 + int(7 + int(self.apply_element.width() / sf) * 2),
            img_1=self.extract_element, img_2=self.extract_element_active,
            command=lambda event: self.extract_patches()
        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=520, cul=850,
            img_1=self.LOGO_element, img_2=self.LOGO_element_active,
            command=lambda event: self.open_browser("Kofi")
        )

        # Load Saved User Options.
        self.toggle_page(0, "main")
        load_user_choices(self, self.config)
        return self.maincanvas

    def update_scaling_variable(self, something=None):
        self.fps_var.set(self.fps_var_new.get())

    def create_cheat_canvas(self):
        # Create Cheat Canvas
        self.cheatcanvas = ttk.Canvas(self._window, width=scale(1200), height=scale(600))
        self.cheatcanvas.pack(expand=1, fill=BOTH)
        canvas = self.cheatcanvas
        self.all_canvas.append(self.cheatcanvas)

        # Create UI elements.
        self.Cheat_UI_elements(self.cheatcanvas)
        create_tab_buttons(self, self.cheatcanvas)

        # Push every version in combobox
        versionvalues = []
        for each in self.cheat_options:
            for key, value in each.items():
                if key == "Aversion":
                    versionvalues.append("Version - " + value)

        self.cheat_version = self.on_canvas.create_combobox(
                                                            master=self._window, canvas=canvas,
                                                            text="",
                                                            values=versionvalues, variable=versionvalues[1],
                                                            row=520, cul=130+2, drop_cul=130+2,
                                                            tags=["text"], tag=None,
                                                            description_name="CheatVersion",
                                                            command=lambda event: loadCheats()
                                                            )
        load_user_choices(self, self.config)


        def loadCheats():
            row = 40
            cul_tex = 40
            cul_sel = 200

            corrent_cheats = self.cheat_options[versionvalues.index(self.cheat_version.get())].items()
            corrent_cheats_dict = dict(corrent_cheats)
            sorted_cheats = dict(sorted(corrent_cheats_dict.items(), key=lambda item: item[0]))
            try:
                for key_var, value in self.selected_cheats.items():
                    value = value.get()
                    self.old_cheats[key_var] = value
            except AttributeError as e:
                self.old_cheats = {}

            self.selected_cheats = {}

            self.cheatcanvas.delete("cheats")

            for version_option_name, version_option_value in sorted_cheats.items():
                # Exclude specific keys from being displayed
                if version_option_name in ["Source", "nsobid", "offset", "version"]:
                    continue

                # Create label
                if version_option_name not in ["Source", "Version", "Aversion", "Cheat Example"]:

                    version_option_var = self.on_canvas.create_checkbutton(
                        master=self._window, canvas=canvas,
                        text=version_option_name,
                        variable="Off",
                        row=row, cul=cul_tex, drop_cul=cul_sel,
                        tags=["text"], tag="cheats",
                        description_name=version_option_name
                    )

                    # Create enable/disable dropdown menu
                    try:
                        if self.old_cheats.get(version_option_name) == "On":
                            version_option_var.set("On")
                    except AttributeError as e:
                        self.old_cheats = {}
                    self.selected_cheats[version_option_name] = version_option_var
                else:
                    continue

                row += 40

                if row > 480:
                    row = 40
                    cul_tex += 200
                    cul_sel += 200


        def ResetCheats():
            try:
                for key, value in self.selected_cheats.items():
                    value.set("Off")
            except AttributeError as e:
                log.error(f"Error found from ResetCheats, the script will continue. {e}")


        # Create a submit button
        self.on_canvas.create_button(
                                    master=self._window, canvas=canvas,
                                    btn_text="Apply Cheats",
                                    row=520, cul=39, width=9, padding=5,
                                    tags=["Button"],
                                    style="success",
                                    description_name="Apply Cheats",
                                    command=lambda: FileManager.submit()
        )

        # Create a submit button
        self.on_canvas.create_button(
                                    master=self._window, canvas=canvas,
                                    btn_text="Reset Cheats",
                                    row=520, cul=277+6+2, width=8, padding=5,
                                    tags=["Button"],
                                    style="default",
                                    description_name="Reset Cheats",
                                    command=ResetCheats
        )
        # Read Cheats
        self.on_canvas.create_button(
                                    master=self._window, canvas=canvas,
                                    btn_text="Read Saved Cheats",
                                    row=520, cul=366+2, width=11, padding=5,
                                    tags=["Button"],
                                    style="default",
                                    description_name="Read Cheats",
                                    command=lambda: load_user_choices(self, self.config, "Cheats")
        )

        #Backup
        self.on_canvas.create_button(
                                    master=self._window, canvas=canvas,
                                    btn_text="Backup",
                                    row=520, cul=479+2, width=7, padding=5,
                                    tags=["Button"],
                                    style="default",
                                    description_name="Backup",
                                    command=lambda: backup(self)
        )
        loadCheats()
        load_user_choices(self, self.config)

    def select_Legacy_exe(self):
        if self.os_platform == "Windows":
            Legacy_path = filedialog.askopenfilename(
                title=f"Please select {self.mode}.exe",
                filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")]
            )
            executable_name = Legacy_path
            if executable_name.endswith("Ryujinx.exe") or executable_name.endswith("Ryujinx.Ava.exe"):
                if self.mode == "Legacy":
                    self.switchmode("true")
            else:
                if self.mode == "Ryujinx":
                    self.switchmode("true")

            if Legacy_path:
                # Save the selected Legacy.exe path to a configuration file
                save_user_choices(self, self.config, Legacy_path)
                home_directory = os.path.dirname(Legacy_path)
                fullpath = os.path.dirname(Legacy_path)
                if any(item in os.listdir(fullpath) for item in ["user", "portable"]):
                    log.info(
                        f"Successfully selected {self.mode}.exe! And a portable folder was found at {home_directory}!")
                    FileManager.checkpath(self.mode)
                    return Legacy_path
                else:
                    log.info(f"Portable folder for {self.mode} not found defaulting to appdata directory!")
                    FileManager.checkpath(self.mode)
                    return Legacy_path

                # Update the Legacy.exe path in the current session
                self.Legacy_path = Legacy_path
            else:
                FileManager.checkpath(self.mode)
                return None
            # Save the selected Legacy.exe path to a configuration file
            save_user_choices(self, self.config, Legacy_path)
        if self.os_platform == "Linux":
            Legacy_path = filedialog.askopenfilename(
                title=f"Please select {self.mode}.AppImage",
                filetypes=[("Select AppImages or Executable: ", "*.*"), ("All Files", "*.*")]
            )

            executable_name = Legacy_path

            if executable_name.startswith("Ryujinx") or executable_name.startswith("Ryujinx.ava"):
                if self.mode == "Legacy":
                    self.switchmode("true")
            else:
                if self.mode == "Ryujinx":
                    self.switchmode("true")

            save_user_choices(self, self.config, Legacy_path)
        return Legacy_path

    def show_main_canvas(self):
        self.on_canvas.is_Ani_Paused = True
        self.cheatcanvas.pack_forget()
        self.maincanvas.pack()

    def toggle_page(self, event, show):
        self.maincanvas.itemconfig(show, state="normal")
        log.info(show)
        for state in self.all_pages:
            if state is not show:
                self.maincanvas.itemconfig(state, state="hidden")

    def show_cheat_canvas(self):
        self.on_canvas.is_Ani_Paused = False
        self.cheatcanvas.pack()
        self.maincanvas.pack_forget()

        self.ani = threading.Thread(name="cheatbackground",
                                    target=lambda: self.on_canvas.canvas_animation(self._window, self.cheatcanvas))
        if not self.is_Ani_running == True:
            self.is_Ani_running = True
            self.ani.start()

    def open_browser(self, web, event=None):
        url = "https://ko-fi.com/maxlastbreath#"
        if web == "Kofi":
            url = "https://ko-fi.com/maxlastbreath#"
        elif web == "Github":
            url = "https://github.com/MaxLastBreath/TOTK-mods"
        elif web == "Discord":
            url = "https://discord.gg/7MMv4yGfhM"
        webbrowser.open(url)
        return

    def load_canvas(self):
        # Main
        self.create_canvas()
        self.create_cheat_canvas()
        self.cheatcanvas.pack_forget()
        load_benchmark(self)

    def Cheat_UI_elements(self, canvas):
        self.cheatbg = canvas.create_image(0, -scale(300), anchor="nw", image=self.blurbackground, tags="background")
        canvas.create_image(0, 0, anchor="nw", image=self.background_LegacyBG, tags="overlay-1")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI_Cheats, tags="overlay")

    def switchmode(self, command="true"):
        if command == "true":
            if self.mode == "Legacy":
                self.mode = "Ryujinx"
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_RyuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="hidden")
                if self.os_platform == "Darwin":
                    self.switch_text.set("Only Ryujinx supported")
                else:
                    self.switch_text.set("Switch to Legacy")
                return
            elif self.mode == "Ryujinx" and self.os_platform != "Darwin":
                self.mode = "Legacy"
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_LegacyBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="normal")
                # change text
                self.switch_text.set("Switch to Ryujinx")
                return
        elif command == "false":
            if self.mode == "Ryujinx":
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_RyuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="hidden")
                if self.os_platform == "Darwin":
                    self.switch_text.set("Only Ryujinx supported")
                else:
                    self.switch_text.set("Switch to Legacy")
                return
        elif command == "Mode":
            return self.mode

    def fetch_var(self, var, dict, option):
        if not dict.get(option, "") == "":
            var.set(dict.get(option, ""))
        return

    def extract_patches(self):
        FileManager.is_extracting = True
        FileManager.checkpath(self.mode)
        FileManager.submit()