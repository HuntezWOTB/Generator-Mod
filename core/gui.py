import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.config import load_config, save_config
from core.localization import load_locales, get_localized_string, get_lang_display
from core.mod_generator import backup_files, apply_mod, restore_original, export_mod, get_mod_stats, compare_lists

if sys.platform == 'win32':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


class LogWidget(tk.Frame):
    """Виджет лога с поддержкой выделения, копирования и очистки.
    Работает как обычный текстовый редактор, но без возможности редактирования.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Текстовое поле с запретом редактирования, но разрешённым выделением
        self.text = tk.Text(
            self,
            height=10,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            font=('Consolas', 9),
            state='disabled'          # блокируем ввод, но выделение работает
        )
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Горячие клавиши
        self.text.bind('<Control-a>', self.select_all)
        self.text.bind('<Control-A>', self.select_all)
        # Ctrl+C работает по умолчанию в состоянии DISABLED – ничего не делаем

        # Контекстное меню
        self.context_menu = tk.Menu(self.text, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selection)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all)
        self.context_menu.add_command(label="Clear", command=self.clear)
        self.text.bind('<Button-3>', self._show_context_menu)

        # При клике на лог – фокус на нём (для удобства выделения)
        self.text.bind('<Button-1>', lambda e: self.text.focus_set())

    def _show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def log(self, message):
        """Добавляет строку в лог."""
        self.text.config(state='normal')
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)
        self.text.config(state='disabled')
        self.update_idletasks()

    def copy_selection(self, event=None):
        """Копирует выделенный текст в буфер обмена."""
        try:
            # В состоянии DISABLED selection_get() работает
            selected = self.text.selection_get()
            if selected:
                self.clipboard_clear()
                self.clipboard_append(selected)
                self.update()
        except tk.TclError:
            pass  # нет выделения
        return "break"

    def select_all(self, event=None):
        """Выделяет весь текст."""
        self.text.focus_set()
        self.text.tag_add('sel', '1.0', 'end')
        return "break"

    def clear(self):
        """Очищает лог."""
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.config(state='disabled')

    def set_menu_labels(self, copy_label, select_all_label, clear_label):
        """Обновляет подписи в контекстном меню (для локализации)."""
        self.context_menu.entryconfig(0, label=copy_label)
        self.context_menu.entryconfig(2, label=select_all_label)
        self.context_menu.entryconfig(3, label=clear_label)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("HiddenTanks Generator Mod")
        self.root.geometry("850x650")
        self.root.minsize(750, 500)

        self.config = load_config()
        self.locales = load_locales()
        self.lang_display = get_lang_display(self.locales)

        self.available_langs = sorted(self.lang_display.keys(), key=lambda k: self.lang_display[k])
        self.display_to_lang = {v: k for k, v in self.lang_display.items()}

        lang = self.config.get('language', 'en')
        self.current_lang = lang if lang in self.locales else 'en'

        theme = self.config.get('theme', 'system')
        if theme == 'system':
            from core.config import get_system_theme
            theme = get_system_theme()
        self.current_theme = theme

        self.game_path_var = tk.StringVar(value=self.config.get('game_path', ''))
        self.mode_var = tk.StringVar(value=self.config.get('mode', 'DVPL'))
        self.dlc_var = tk.BooleanVar(value=self.config.get('use_dlc', False))

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.create_widgets()
        self.update_theme()
        self.update_texts()

        # Глобальные обработчики НЕ нужны – всё внутри LogWidget

    def create_widgets(self):
        self.path_frame = ttk.LabelFrame(self.main_frame, padding="5")
        self.path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        self.main_frame.columnconfigure(0, weight=1)

        self.path_label = ttk.Label(self.path_frame)
        self.path_label.grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.game_path_var, width=50)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.path_frame.columnconfigure(1, weight=1)
        self.btn_browse = ttk.Button(self.path_frame, command=self.browse_folder)
        self.btn_browse.grid(row=0, column=2, padx=(0, 0))

        self.settings_frame = ttk.LabelFrame(self.main_frame, padding="5")
        self.settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.lang_label = ttk.Label(self.settings_frame)
        self.lang_label.grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.lang_combo = ttk.Combobox(self.settings_frame, state='readonly', width=10)
        self.lang_combo.grid(row=0, column=1, padx=(0, 15), sticky=tk.W)
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_lang_change)

        self.theme_label = ttk.Label(self.settings_frame)
        self.theme_label.grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.theme_combo = ttk.Combobox(self.settings_frame, state='readonly', width=10)
        self.theme_combo.grid(row=0, column=3, padx=(0, 15), sticky=tk.W)
        self.theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)

        self.mode_label = ttk.Label(self.settings_frame)
        self.mode_label.grid(row=0, column=4, padx=(0, 5), sticky=tk.W)
        self.mode_combo = ttk.Combobox(self.settings_frame, state='readonly', width=12)
        self.mode_combo.grid(row=0, column=5, padx=(0, 15), sticky=tk.W)
        self.mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)

        self.dlc_var = tk.BooleanVar(value=self.config.get('use_dlc', False))
        self.dlc_check = tk.Checkbutton(
            self.settings_frame,
            variable=self.dlc_var,
            command=self.on_dlc_change,
            relief='flat',
            highlightthickness=0
        )
        self.dlc_check.grid(row=0, column=6, padx=(0, 0), sticky=tk.W)

        actions_frame = ttk.Frame(self.main_frame)
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.btn_generate = ttk.Button(actions_frame, command=self.generate_mod)
        self.btn_generate.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_restore = ttk.Button(actions_frame, command=self.restore_original)
        self.btn_restore.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_info = ttk.Button(actions_frame, command=self.show_info)
        self.btn_info.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_export = ttk.Button(actions_frame, command=self.export_mod)
        self.btn_export.pack(side=tk.LEFT)

        self.log_frame = ttk.LabelFrame(self.main_frame, padding="5")
        self.log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        self.main_frame.rowconfigure(3, weight=1)

        log_controls = ttk.Frame(self.log_frame)
        log_controls.pack(fill=tk.X, pady=(0, 5))

        self.btn_copy_log = ttk.Button(log_controls, command=self.copy_log_selection)
        self.btn_copy_log.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_clear_log = ttk.Button(log_controls, command=self.clear_log)
        self.btn_clear_log.pack(side=tk.LEFT)

        self.log_hint_label = ttk.Label(log_controls)
        self.log_hint_label.pack(side=tk.RIGHT)

        self.log_widget = LogWidget(self.log_frame)
        self.log_widget.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_widget.log(message)

    def copy_log_selection(self):
        self.log_widget.copy_selection()
        self.btn_copy_log.config(text="✅ Copied!")
        self.root.after(1500, lambda: self.btn_copy_log.config(text=self.loc('btn_copy_log')))

    def clear_log(self):
        self.log_widget.clear()

    def loc(self, key, **kwargs):
        return get_localized_string(self.locales, self.current_lang, key, **kwargs)

    def get_theme_display_list(self):
        return [self.loc('theme_light'), self.loc('theme_dark')]

    def theme_display_to_internal(self, display):
        if display == self.loc('theme_light'):
            return 'light'
        elif display == self.loc('theme_dark'):
            return 'dark'
        return 'light'

    def get_mode_display_list(self):
        return [self.loc('mode_non_dvpl'), self.loc('mode_dvpl'), self.loc('mode_universal')]

    def mode_display_to_internal(self, display):
        if display == self.loc('mode_non_dvpl'):
            return 'NON-DVPL'
        elif display == self.loc('mode_dvpl'):
            return 'DVPL'
        elif display == self.loc('mode_universal'):
            return 'UNIVERSAL'
        return 'DVPL'

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.game_path_var.set(folder)
            self.config['game_path'] = folder
            save_config(self.config)

    def on_lang_change(self, event):
        selected_display = self.lang_combo.get()
        self.current_lang = self.display_to_lang.get(selected_display, 'en')
        self.config['language'] = self.current_lang
        save_config(self.config)
        self.update_texts()
        self.root.focus()
        self.lang_combo.selection_clear()

    def on_theme_change(self, event):
        selected_display = self.theme_combo.get()
        self.current_theme = self.theme_display_to_internal(selected_display)
        self.config['theme'] = self.current_theme
        save_config(self.config)
        self.update_theme()
        self.root.focus()
        self.theme_combo.selection_clear()

    def on_mode_change(self, event):
        selected_display = self.mode_combo.get()
        internal = self.mode_display_to_internal(selected_display)
        self.mode_var.set(internal)
        self.config['mode'] = internal
        save_config(self.config)
        self.root.focus()
        self.mode_combo.selection_clear()

    def on_dlc_change(self):
        self.config['use_dlc'] = self.dlc_var.get()
        save_config(self.config)
        self.root.focus()

    def update_texts(self):
        self.root.title(self.loc('app_title'))
        self.btn_generate.config(text=self.loc('btn_generate'))
        self.btn_restore.config(text=self.loc('btn_restore'))
        self.btn_info.config(text=self.loc('btn_info'))
        self.btn_export.config(text=self.loc('btn_export'))
        self.btn_browse.config(text=self.loc('btn_browse'))
        self.btn_copy_log.config(text=self.loc('btn_copy_log'))
        self.btn_clear_log.config(text=self.loc('btn_clear_log'))
        self.dlc_check.config(text=self.loc('dlc_check'))
        self.path_label.config(text=self.loc('label_game_path'))
        self.lang_label.config(text=self.loc('label_language'))
        self.theme_label.config(text=self.loc('label_theme'))
        self.mode_label.config(text=self.loc('label_mode'))
        self.path_frame.config(text=self.loc('frame_game_path'))
        self.settings_frame.config(text=self.loc('frame_settings'))
        self.log_frame.config(text=self.loc('frame_log'))
        self.log_hint_label.config(text=self.loc('hint_copy'))

        if hasattr(self, 'log_widget'):
            self.log_widget.set_menu_labels(
                self.loc('btn_copy_log'),
                self.loc('menu_select_all'),
                self.loc('btn_clear_log')   # для пункта Clear в меню
            )

        display_values = [self.lang_display[k] for k in self.available_langs]
        self.lang_combo['values'] = display_values
        self.lang_combo.set(self.lang_display.get(self.current_lang, self.current_lang.upper()))

        theme_displays = self.get_theme_display_list()
        self.theme_combo['values'] = theme_displays
        self.theme_combo.set(self.loc('theme_light') if self.current_theme == 'light' else self.loc('theme_dark'))

        mode_displays = self.get_mode_display_list()
        self.mode_combo['values'] = mode_displays
        current_mode_internal = self.mode_var.get()
        if current_mode_internal == 'NON-DVPL':
            self.mode_combo.set(self.loc('mode_non_dvpl'))
        elif current_mode_internal == 'DVPL':
            self.mode_combo.set(self.loc('mode_dvpl'))
        else:
            self.mode_combo.set(self.loc('mode_universal'))

        self.root.update_idletasks()

    def generate_mod(self):
        game_path = self.game_path_var.get().strip()
        if not game_path or not os.path.exists(game_path):
            messagebox.showerror("Error", self.loc('error_invalid_path'))
            return
        mode = self.mode_var.get()
        use_dlc = self.dlc_var.get()
        self.config['mode'] = mode
        self.config['game_path'] = game_path
        self.config['use_dlc'] = use_dlc
        save_config(self.config)

        self.log("="*50)
        self.log(self.loc('log_starting_mod', mode=mode))
        self.log("="*50)
        try:
            backup_files(game_path, mode, use_dlc, log_func=self.log)
            stats = apply_mod(game_path, mode, use_dlc, log_func=self.log)
            self.log("="*50)
            self.log(self.loc('log_mod_completed'))
            self.log("="*50)
            self.last_stats = stats
        except Exception as e:
            self.log("="*50)
            self.log(self.loc('log_error', error=str(e)))
            import traceback
            self.log(traceback.format_exc())
            self.log("="*50)

    def restore_original(self):
        game_path = self.game_path_var.get().strip()
        if not game_path or not os.path.exists(game_path):
            messagebox.showerror("Error", self.loc('error_invalid_path'))
            return
        self.log("="*50)
        self.log(self.loc('log_restore_start'))
        try:
            restore_original(game_path, log_func=self.log)
            self.log(self.loc('log_restore_completed'))
            self.log("="*50)
        except Exception as e:
            self.log(self.loc('log_error', error=str(e)))
            self.log("="*50)

    def export_mod(self):
        game_path = self.game_path_var.get().strip()
        if not game_path or not os.path.exists(game_path):
            messagebox.showerror("Error", self.loc('error_invalid_path'))
            return
        mode = self.mode_var.get()
        use_dlc = self.dlc_var.get()
        self.log("="*50)
        self.log(self.loc('log_export_start'))
        try:
            export_mod(game_path, mode, use_dlc, log_func=self.log)
            self.log(self.loc('log_export_completed'))
        except Exception as e:
            self.log(self.loc('log_error', error=str(e)))
            import traceback
            self.log(traceback.format_exc())
        self.log("="*50)

    def show_info(self):
        game_path = self.game_path_var.get().strip()
        if not game_path or not os.path.exists(game_path):
            messagebox.showerror("Error", self.loc('error_invalid_path'))
            return
        mode = self.mode_var.get()
        use_dlc = self.dlc_var.get()
        self.log("="*50)
        self.log("Calculating statistics...")
        try:
            stats = get_mod_stats(game_path, mode, use_dlc, log_func=self.log)
            self.log("="*50)
            self.display_stats(stats)

            if use_dlc:
                self.log("\n--- " + self.loc('dlc_comparison_title') + " ---")
                for code in stats.keys():
                    comp = compare_lists(game_path, code, use_dlc, log_func=self.log)
                    if comp is not None:
                        msg = self.loc('dlc_new_tanks',
                                       code=code,
                                       count=comp['only_in_dlc'],
                                       total_dlc=comp['total_dlc'],
                                       total_game=comp['total_game'])
                        self.log(f"  {msg}")
            self.log("="*50)
        except Exception as e:
            self.log(f"Error: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.log("="*50)

    def display_stats(self, stats):
        if not stats:
            self.log("No statistics available.")
            return
        info = f"\n{self.loc('statistics_title')}:\n" + "="*30 + "\n"
        nation_names = {
            'CN': 'China', 'EU': 'Europe', 'FR': 'France', 'DE': 'Germany',
            'JP': 'Japan', 'HN': 'Other', 'UK': 'UK', 'US': 'USA', 'SU': 'USSR'
        }
        total_visible = 0
        total_hidden = 0
        for code, stat in stats.items():
            name = nation_names.get(code, code)
            info += f"\n{name}:\n"
            info += f"  {self.loc('stat_visible')}: {stat['visible']}\n"
            info += f"  {self.loc('stat_hidden_ordinary')}: {stat['hidden_ordinary']}\n"
            info += f"  {self.loc('stat_hidden_collectible')}: {stat['hidden_collectible']}\n"
            info += f"  {self.loc('stat_hidden_premium')}: {stat['hidden_premium']}\n"
            total_visible += stat['visible']
            total_hidden += stat['hidden_ordinary'] + stat['hidden_collectible'] + stat['hidden_premium']
        info += f"\n{'='*30}\n"
        info += f"{self.loc('stat_total_visible')}: {total_visible}\n"
        info += f"{self.loc('stat_total_hidden')}: {total_hidden}\n"
        info += f"{self.loc('stat_grand_total')}: {total_visible + total_hidden}\n"
        self.log(info)

    def update_theme(self):
        if self.current_theme == 'dark':
            bg = '#1e1e1e'
            fg = '#ffffff'
            entry_bg = '#2d2d2d'
            select_bg = '#3a5f7a'
            trough = '#2d2d2d'
            scroll = '#4a4a4a'
            active = '#5a5a5a'
            light = '#3a3a3a'
            dark = '#1a1a1a'
            frame_bg = '#2d2d2d'
            label_bg = '#1e1e1e'
            button_bg = '#2d2d2d'
            combobox_bg = '#2d2d2d'
            arrow_color = '#ffffff'
            check_bg = '#2d2d2d'
        else:
            bg = '#f0f0f0'
            fg = '#000000'
            entry_bg = '#ffffff'
            select_bg = '#cce8ff'
            trough = '#e0e0e0'
            scroll = '#d0d0d0'
            active = '#b0b0b0'
            light = '#e8e8e8'
            dark = '#c0c0c0'
            frame_bg = '#f0f0f0'
            label_bg = '#f0f0f0'
            button_bg = '#e0e0e0'
            combobox_bg = '#ffffff'
            arrow_color = '#000000'
            check_bg = '#f0f0f0'

        self.root.configure(bg=bg)
        self.main_frame.configure(style='TFrame')

        self.style.configure('.', background=bg, foreground=fg, fieldbackground=entry_bg)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabelframe', background=frame_bg, foreground=fg,
                           bordercolor=light, lightcolor=light, darkcolor=dark)
        self.style.configure('TLabelframe.Label', background=frame_bg, foreground=fg)
        self.style.configure('TLabel', background=label_bg, foreground=fg)
        self.style.configure('TButton', background=button_bg, foreground=fg,
                           bordercolor=light, lightcolor=light, darkcolor=dark,
                           padding=6, focuscolor='none')
        self.style.map('TButton',
                      background=[('active', active), ('pressed', active), ('disabled', button_bg)],
                      foreground=[('disabled', '#888888')])
        self.style.configure('TEntry', fieldbackground=entry_bg, foreground=fg,
                           bordercolor=light, lightcolor=light, darkcolor=dark)
        self.style.map('TEntry',
                      fieldbackground=[('readonly', entry_bg)],
                      background=[('readonly', entry_bg)])
        self.style.configure('TCombobox', fieldbackground=entry_bg, background=combobox_bg,
                           foreground=fg, arrowcolor=arrow_color,
                           bordercolor=light, lightcolor=light, darkcolor=dark)
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', entry_bg)],
                      background=[('readonly', combobox_bg)],
                      foreground=[('readonly', fg)],
                      arrowcolor=[('readonly', arrow_color)])
        self.style.configure('Vertical.TScrollbar', background=scroll, troughcolor=trough,
                           arrowcolor=arrow_color, bordercolor=bg,
                           lightcolor=light, darkcolor=dark)
        self.style.map('Vertical.TScrollbar',
                      background=[('active', active), ('pressed', active)])

        if hasattr(self, 'dlc_check'):
            self.dlc_check.config(
                bg=frame_bg,
                fg=fg,
                selectcolor=entry_bg,
                activebackground=active,
                activeforeground=fg
            )

        if hasattr(self, 'log_widget'):
            self.log_widget.text.configure(
                bg=entry_bg,
                fg=fg,
                insertbackground=fg,
                selectbackground=select_bg,
                selectforeground=fg,
                relief='flat'
            )


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()