import os
import zipfile
import shutil
import json
import struct
import time
import sys
import ctypes
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import tkinter.ttk as ttk
import pyzipper
import py7zr

# ===== ЛОКАЛИЗАЦИЯ =====
LANG = {
    "ru": {
        "title": "alanator",
        "file": "Файл",
        "new_archive": "Новый архив",
        "open": "Открыть",
        "exit": "Выход",
        "edit": "Изменить",
        "copy": "Копировать",
        "cut": "Вырезать",
        "paste": "Вставить",
        "delete": "Удалить",
        "rename": "Переименовать",
        "select_all": "Выбрать все",
        "view": "Вид",
        "refresh": "Обновить",
        "list": "Список",
        "by_name": "По имени",
        "by_size": "По размеру",
        "by_type": "По типу",
        "by_date": "По дате",
        "tools": "Инструменты",
        "settings": "Настройки",
        "test": "Тест системы",
        "secure_delete": "Надёжное удаление",
        "view_archive": "Просмотреть архив",
        "options": "Параметры",
        "run_as_admin": "Запустить от имени администратора",
        "run_as_other": "Запустить от имени другого пользователя",
        "associate": "Сделать архиватором по умолчанию",
        "associations": "Ассоциации файлов",
        "context_menu": "Интеграция в контекстное меню",
        "zip_encoding": "Кодировка для имён файлов ZIP",
        "language": "Язык",
        "help": "Помощь",
        "website": "Веб-сайт проекта",
        "online_help": "Онлайн-помощь",
        "faq": "FAQ",
        "changelog": "Журнал изменений",
        "about": "О программе",
        "folder": "папка",
        "file_size": "размер",
        "modified": "изменён",
        "error": "ошибка",
        "ok": "OK",
        "cancel": "Отмена",
        "clear": "Очистить",
        "target": "Целевой",
        "type": "Тип",
        "level": "Уровень",
        "password": "Ввести пароль/выбрать ключевой файл",
        "delete_source": "Удалить файлы после архивации",
        "browse": "Обзор",
        "processing": "обработка",
        "ready": "готово",
        "archive_created": "архив создан",
        "archive_extracted": "архив извлечён",
        "choose_folder": "выберите папку для извлечения",
        "choose_archive": "выберите архив",
        "select_real_folder": "выберите реальную папку (не 'Мой компьютер')",
        "no_files": "нет файлов для архивации",
        "folder_not_found": "папка не найдена",
        "properties": "свойства",
        "new_folder": "Новая папка",
        "convert_archive": "Преобразовать архив",
        "extract": "Извлечь",
    },
    "en": {
        "title": "alanator",
        "file": "File",
        "new_archive": "New archive",
        "open": "Open",
        "exit": "Exit",
        "edit": "Edit",
        "copy": "Copy",
        "cut": "Cut",
        "paste": "Paste",
        "delete": "Delete",
        "rename": "Rename",
        "select_all": "Select all",
        "view": "View",
        "refresh": "Refresh",
        "list": "List",
        "by_name": "By name",
        "by_size": "By size",
        "by_type": "By type",
        "by_date": "By date",
        "tools": "Tools",
        "settings": "Settings",
        "test": "System test",
        "secure_delete": "Secure delete",
        "view_archive": "View archive",
        "options": "Options",
        "run_as_admin": "Run as administrator",
        "run_as_other": "Run as another user",
        "associate": "Make default archiver",
        "associations": "File associations",
        "context_menu": "Context menu integration",
        "zip_encoding": "ZIP file name encoding",
        "language": "Language",
        "help": "Help",
        "website": "Project website",
        "online_help": "Online help",
        "faq": "FAQ",
        "changelog": "Changelog",
        "about": "About",
        "folder": "folder",
        "file_size": "size",
        "modified": "modified",
        "error": "error",
        "ok": "OK",
        "cancel": "Cancel",
        "clear": "Clear",
        "target": "Target",
        "type": "Type",
        "level": "Level",
        "password": "Enter password/select key file",
        "delete_source": "Delete files after archiving",
        "browse": "Browse",
        "processing": "processing",
        "ready": "ready",
        "archive_created": "archive created",
        "archive_extracted": "archive extracted",
        "choose_folder": "choose folder for extraction",
        "choose_archive": "choose archive",
        "select_real_folder": "select a real folder (not 'My Computer')",
        "no_files": "no files to archive",
        "folder_not_found": "folder not found",
        "properties": "properties",
        "new_folder": "New folder",
        "convert_archive": "Convert archive",
        "extract": "Extract",
    }
}

def tr(text):
    if hasattr(tr, 'lang'):
        lang = tr.lang
    else:
        lang = "ru"
    return LANG.get(lang, LANG["ru"]).get(text, text)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AlanatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if file_path.endswith(('.aln', '.zip', '.7z')):
                self.view_archive_file(file_path)
                return
        
        self.title("alanator")
        self.geometry("1200x700")
        self.current_path = "Computer"
        self.cut_path = None
        self.copy_path = None
        self.selected_files = []
        self.selected_folder = None
        
        self.settings_file = "alanator_settings.json"
        self.settings = self.load_settings()
        
        self.current_lang = self.settings.get("language", "ru")
        tr.lang = self.current_lang
        
        theme = self.settings.get("theme", "Тёмная")
        if theme == "Тёмная":
            ctk.set_appearance_mode("dark")
        elif theme == "Светлая":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_real_menu()
        self.create_toolbar()
        self.create_main_area()
        self.refresh_tree()
        self.refresh_files()
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except:
            pass
    
    def update_language(self):
        self.title(tr("title"))
        self.create_real_menu()
        self.create_toolbar()
    
    def create_real_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)
        
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("file"), menu=file_menu)
        file_menu.add_command(label=tr("new_archive"), command=self.open_add_menu)
        file_menu.add_command(label=tr("open"), command=lambda: os.startfile(self.current_path) if self.current_path != "Computer" else None)
        file_menu.add_separator()
        file_menu.add_command(label=tr("exit"), command=self.quit)
        
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("edit"), menu=edit_menu)
        edit_menu.add_command(label=tr("copy"), command=self.copy_file)
        edit_menu.add_command(label=tr("cut"), command=self.cut_file)
        edit_menu.add_command(label=tr("paste"), command=self.paste_file)
        edit_menu.add_separator()
        edit_menu.add_command(label=tr("delete"), command=self.delete_file)
        edit_menu.add_command(label=tr("rename"), command=self.rename_file)
        edit_menu.add_command(label=tr("select_all"), command=self.select_all_files)
        
        view_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("view"), menu=view_menu)
        view_menu.add_command(label=tr("refresh"), command=self.refresh_files)
        
        list_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("list"), menu=list_menu)
        list_menu.add_command(label=tr("by_name"), command=lambda: self.sort_files("name"))
        list_menu.add_command(label=tr("by_size"), command=lambda: self.sort_files("size"))
        list_menu.add_command(label=tr("by_type"), command=lambda: self.sort_files("type"))
        list_menu.add_command(label=tr("by_date"), command=lambda: self.sort_files("date"))
        
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("tools"), menu=tools_menu)
        tools_menu.add_command(label=tr("settings"), command=self.open_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label=tr("test"), command=self.run_test)
        tools_menu.add_command(label=tr("secure_delete"), command=self.secure_delete)
        tools_menu.add_command(label=tr("view_archive"), command=self.view_archive)
        tools_menu.add_command(label=tr("convert_archive"), command=self.convert_archive)
        
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("options"), menu=settings_menu)
        settings_menu.add_command(label=tr("settings"), command=self.open_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label=tr("run_as_admin"), command=self.run_as_admin)
        settings_menu.add_command(label=tr("run_as_other"), command=self.run_as_other)
        settings_menu.add_separator()
        settings_menu.add_command(label=tr("associate"), command=self.associate_files)
        settings_menu.add_separator()
        settings_menu.add_command(label=tr("associations"), command=self.file_associations)
        settings_menu.add_command(label=tr("context_menu"), command=self.context_menu_integration)
        settings_menu.add_separator()
        settings_menu.add_command(label=tr("zip_encoding"), command=self.zip_encoding)
        settings_menu.add_command(label=tr("language"), command=self.open_settings)
        
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("help"), menu=help_menu)
        help_menu.add_command(label=tr("website"), command=lambda: os.system("start https://github.com/mentalnyy/alanator"))
        help_menu.add_command(label=tr("about"), command=self.about_program)
    
    def open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title("Настройки alanator")
        win.geometry("900x650")
        win.attributes("-topmost", True)
        
        tabview = ctk.CTkTabview(win, width=850, height=550)
        tabview.pack(fill="both", expand=True, padx=20, pady=15)
        
        tabview.add("Основные")
        self.create_settings_general(tabview.tab("Основные"))
        tabview.add("Дополнительные")
        self.create_settings_advanced(tabview.tab("Дополнительные"))
        tabview.add("Архивы")
        self.create_settings_archives(tabview.tab("Архивы"))
        tabview.add("Тема")
        self.create_settings_theme(tabview.tab("Тема"))
        
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(btn_frame, text="OK", width=100, command=lambda: self.apply_settings(win)).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Отмена", width=100, command=win.destroy).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="Очистить", width=100, command=lambda: self.clear_settings()).pack(side="right", padx=5)
    
    def apply_settings(self, win):
        self.settings["theme"] = self.theme_var.get()
        self.settings["language"] = self.lang_var.get()
        self.settings["assoc_aln"] = self.assoc_aln.get()
        self.settings["assoc_zip"] = self.assoc_zip.get()
        self.settings["assoc_7z"] = self.assoc_7z.get()
        self.settings["context_menu"] = self.context_menu_var.get()
        self.settings["performance"] = self.perf_var.get()
        self.settings["opt_view"] = self.opt_view.get()
        self.settings["show_tips"] = self.show_tips.get()
        self.settings["encoding"] = self.enc_var.get()
        self.settings["only_utf8"] = self.only_utf8.get()
        self.settings["show_utf8"] = self.show_utf8.get()
        self.settings["start_path"] = self.start_path_var.get()
        self.settings["auto_update"] = self.auto_update.get()
        self.settings["open_corrupted"] = self.open_corrupted.get()
        self.settings["exclude_empty"] = self.exclude_empty.get()
        self.settings["default_format"] = self.default_format.get()
        self.settings["default_level"] = self.default_level.get()
        self.settings["delete_after"] = self.delete_after.get()
        self.settings["archive_to_source"] = self.archive_to_source.get()
        self.settings["extract_new_folder"] = self.extract_new_folder.get()
        self.settings["skip_existing"] = self.skip_existing.get()
        self.settings["auto_extract_tar"] = self.auto_extract_tar.get()
        self.settings["app_color"] = self.app_color.get()
        self.settings["link_color"] = self.link_color.get()
        self.settings["contrast"] = self.contrast_var.get()
        self.settings["spacing"] = self.spacing_var.get()
        
        theme = self.settings["theme"]
        if theme == "Тёмная":
            ctk.set_appearance_mode("dark")
        elif theme == "Светлая":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        self.save_settings()
        
        new_lang = self.settings.get("language", "ru")
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            tr.lang = new_lang
            self.update_language()
        
        messagebox.showinfo("настройки", "настройки сохранены")
        win.destroy()
    
    def clear_settings(self):
        self.settings = {}
        self.save_settings()
        ctk.set_appearance_mode("dark")
        messagebox.showinfo("очистка", "настройки сброшены")
    
    def create_settings_general(self, parent):
        ctk.CTkLabel(parent, text=tr("language"), font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        lang_frame = ctk.CTkFrame(parent)
        lang_frame.pack(fill="x", padx=20, pady=5)
        self.lang_var = ctk.StringVar(value=self.settings.get("language", "ru"))
        ctk.CTkOptionMenu(lang_frame, values=["ru", "en"], variable=self.lang_var, width=100).pack(side="left", padx=5)
        
        ctk.CTkLabel(parent, text=tr("associations"), font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        assoc_frame = ctk.CTkFrame(parent)
        assoc_frame.pack(fill="x", padx=20, pady=5)
        self.assoc_aln = ctk.BooleanVar(value=self.settings.get("assoc_aln", True))
        self.assoc_zip = ctk.BooleanVar(value=self.settings.get("assoc_zip", False))
        self.assoc_7z = ctk.BooleanVar(value=self.settings.get("assoc_7z", False))
        ctk.CTkCheckBox(assoc_frame, text="Связать .aln с alanator", variable=self.assoc_aln).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(assoc_frame, text="Связать .zip с alanator", variable=self.assoc_zip).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(assoc_frame, text="Связать .7z с alanator", variable=self.assoc_7z).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(parent, text=tr("context_menu"), font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        self.context_menu_var = ctk.BooleanVar(value=self.settings.get("context_menu", True))
        ctk.CTkCheckBox(parent, text="Добавить alanator в контекстное меню проводника", variable=self.context_menu_var).pack(anchor="w", padx=20)
        
        ctk.CTkLabel(parent, text="Производительность", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        perf_frame = ctk.CTkFrame(parent)
        perf_frame.pack(fill="x", padx=20, pady=5)
        self.perf_var = ctk.StringVar(value=self.settings.get("performance", "Нормально"))
        ctk.CTkOptionMenu(perf_frame, values=["Нормально", "Максимально"], variable=self.perf_var, width=150).pack(side="left", padx=5)
        self.opt_view = ctk.BooleanVar(value=self.settings.get("opt_view", True))
        ctk.CTkCheckBox(perf_frame, text="Оптимизация просмотра", variable=self.opt_view).pack(side="left", padx=10)
        self.show_tips = ctk.BooleanVar(value=self.settings.get("show_tips", True))
        ctk.CTkCheckBox(parent, text="Показывать подсказки", variable=self.show_tips).pack(anchor="w", padx=20)
    
    def create_settings_advanced(self, parent):
        ctk.CTkLabel(parent, text="Кодировка", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        enc_frame = ctk.CTkFrame(parent)
        enc_frame.pack(fill="x", padx=20, pady=5)
        self.enc_var = ctk.StringVar(value=self.settings.get("encoding", "UTF-8"))
        ctk.CTkOptionMenu(enc_frame, values=["UTF-8", "Windows-1251", "CP866"], variable=self.enc_var, width=150).pack(side="left", padx=5)
        self.only_utf8 = ctk.BooleanVar(value=self.settings.get("only_utf8", False))
        ctk.CTkCheckBox(enc_frame, text="Только UTF-8", variable=self.only_utf8).pack(side="left", padx=10)
        self.show_utf8 = ctk.BooleanVar(value=self.settings.get("show_utf8", True))
        ctk.CTkCheckBox(parent, text="Показывать содержимое архива в UTF-8", variable=self.show_utf8).pack(anchor="w", padx=20)
        
        ctk.CTkLabel(parent, text="Пути", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        path_frame = ctk.CTkFrame(parent)
        path_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(path_frame, text="Открывать при старте:").pack(side="left", padx=5)
        self.start_path_var = ctk.StringVar(value=self.settings.get("start_path", "Мой компьютер"))
        ctk.CTkOptionMenu(path_frame, values=["Мой компьютер", "Рабочий стол", "Документы"], variable=self.start_path_var, width=150).pack(side="left", padx=10)
        
        ctk.CTkLabel(parent, text="Поведение", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        self.auto_update = ctk.BooleanVar(value=self.settings.get("auto_update", True))
        ctk.CTkCheckBox(parent, text="Автообновление изменённых файлов", variable=self.auto_update).pack(anchor="w", padx=20)
        self.open_corrupted = ctk.BooleanVar(value=self.settings.get("open_corrupted", False))
        ctk.CTkCheckBox(parent, text="Попробовать открыть содержащий ошибки архив", variable=self.open_corrupted).pack(anchor="w", padx=20)
        self.exclude_empty = ctk.BooleanVar(value=self.settings.get("exclude_empty", False))
        ctk.CTkCheckBox(parent, text="Исключить пустые папки из архивации", variable=self.exclude_empty).pack(anchor="w", padx=20)
    
    def create_settings_archives(self, parent):
        ctk.CTkLabel(parent, text="Параметры архивации", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        arch_frame = ctk.CTkFrame(parent)
        arch_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(arch_frame, text="Формат по умолчанию:").pack(side="left", padx=5)
        self.default_format = ctk.StringVar(value=self.settings.get("default_format", "ZIP"))
        ctk.CTkOptionMenu(arch_frame, values=["ZIP", "7Z", "TAR", "ALN"], variable=self.default_format, width=120).pack(side="left", padx=10)
        ctk.CTkLabel(arch_frame, text="Уровень:").pack(side="left", padx=10)
        self.default_level = ctk.StringVar(value=self.settings.get("default_level", "Очень быстро"))
        ctk.CTkOptionMenu(arch_frame, values=["Очень быстро", "Быстро", "Нормально", "Максимально"], variable=self.default_level, width=120).pack(side="left", padx=10)
        self.delete_after = ctk.BooleanVar(value=self.settings.get("delete_after", False))
        ctk.CTkCheckBox(parent, text="Удалять исходники после архивации по умолчанию", variable=self.delete_after).pack(anchor="w", padx=20)
        self.archive_to_source = ctk.BooleanVar(value=self.settings.get("archive_to_source", False))
        ctk.CTkCheckBox(parent, text="Архивировать в исходную директорию", variable=self.archive_to_source).pack(anchor="w", padx=20)
        
        ctk.CTkLabel(parent, text="Параметры извлечения", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        self.extract_new_folder = ctk.BooleanVar(value=self.settings.get("extract_new_folder", True))
        ctk.CTkCheckBox(parent, text="Извлекать в новую папку по умолчанию", variable=self.extract_new_folder).pack(anchor="w", padx=20)
        self.skip_existing = ctk.BooleanVar(value=self.settings.get("skip_existing", False))
        ctk.CTkCheckBox(parent, text="Пропускать существующие файлы", variable=self.skip_existing).pack(anchor="w", padx=20)
        self.auto_extract_tar = ctk.BooleanVar(value=self.settings.get("auto_extract_tar", False))
        ctk.CTkCheckBox(parent, text="Автоматически извлекать TAR из сжатых TAR.*", variable=self.auto_extract_tar).pack(anchor="w", padx=20)
    
    def create_settings_theme(self, parent):
        ctk.CTkLabel(parent, text="Тема", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        theme_frame = ctk.CTkFrame(parent)
        theme_frame.pack(fill="x", padx=20, pady=5)
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "Тёмная"))
        ctk.CTkOptionMenu(theme_frame, values=["Тёмная", "Светлая", "Системная"], variable=self.theme_var, width=150).pack(side="left", padx=5)
        ctk.CTkButton(theme_frame, text="Загрузить темы", width=150).pack(side="left", padx=10)
        
        ctk.CTkLabel(parent, text="Цвета", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        color_frame = ctk.CTkFrame(parent)
        color_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(color_frame, text="Цвет приложения:").grid(row=0, column=0, padx=5, pady=5)
        self.app_color = ctk.StringVar(value=self.settings.get("app_color", "Синий"))
        ctk.CTkOptionMenu(color_frame, values=["Синий", "Зелёный", "Красный", "Фиолетовый"], variable=self.app_color, width=120).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(color_frame, text="Цвет ссылок:").grid(row=1, column=0, padx=5, pady=5)
        self.link_color = ctk.StringVar(value=self.settings.get("link_color", "Голубой"))
        ctk.CTkOptionMenu(color_frame, values=["Голубой", "Белый", "Жёлтый"], variable=self.link_color, width=120).grid(row=1, column=1, padx=5)
        
        ctk.CTkLabel(parent, text="Контраст", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        self.contrast_var = ctk.StringVar(value=self.settings.get("contrast", "Нормальный"))
        ctk.CTkOptionMenu(parent, values=["Нормальный", "Высокий", "Низкий"], variable=self.contrast_var, width=150).pack(anchor="w", padx=20)
        
        ctk.CTkLabel(parent, text="Межстрочный интервал", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        self.spacing_var = ctk.StringVar(value=self.settings.get("spacing", "Нормальный"))
        ctk.CTkOptionMenu(parent, values=["Маленький", "Нормальный", "Большой"], variable=self.spacing_var, width=150).pack(anchor="w", padx=20)
    
    def run_as_admin(self):
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showinfo("информация", "alanator уже запущен от имени администратора")
                return
            script = os.path.abspath(sys.argv[0])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
            self.quit()
        except Exception as e:
            messagebox.showerror("ошибка", f"не удалось запустить от имени администратора: {e}")
    
    def run_as_other(self):
        messagebox.showinfo("другой пользователь", "функция будет в следующей версии")
    
    def load_profile(self):
        messagebox.showinfo("профиль", "загрузка профиля будет в следующей версии")
    
    def save_profile(self):
        messagebox.showinfo("профиль", "сохранение профиля будет в следующей версии")
    
    def file_associations(self):
        messagebox.showinfo("ассоциации файлов", "связать .aln, .zip, .7z с alanator")
    
    def context_menu_integration(self):
        messagebox.showinfo("контекстное меню", "добавить alanator в пкм проводника")
    
    def zip_encoding(self):
        messagebox.showinfo("кодировка", "выбор кодировки для zip (utf-8, cp866, etc)")
    
    def language_settings(self):
        messagebox.showinfo("язык", "русский, английский и другие")
    
    def show_changelog(self):
        changelog = "alanator 1.0\n- первый релиз\n- поддержка zip, 7z, tar, aln\n- шифрование архивов\n- пкм меню\n- просмотр bat файлов\n- прогресс-бар"
        messagebox.showinfo("журнал изменений", changelog)
    
    def about_program(self):
        about = "alanator\nархиватор от алана\nверсия 1.0\n\nсделано с любовью и промтами"
        messagebox.showinfo("о программе", about)
    
    def associate_files(self):
        try:
            import winreg
            exe_path = os.path.abspath(sys.argv[0])
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".aln") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "alanator.aln")
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "alanator.aln") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "alanator архив")
                with winreg.CreateKey(key, "shell\\open\\command") as cmd:
                    winreg.SetValue(cmd, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".zip") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "alanator.zip")
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "alanator.zip") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "alanator zip архив")
                with winreg.CreateKey(key, "shell\\open\\command") as cmd:
                    winreg.SetValue(cmd, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            
            messagebox.showinfo("готово", "ассоциация .aln и .zip добавлена. перезапустите проводник для применения.")
        except Exception as e:
            messagebox.showerror("ошибка", f"не удалось добавить ассоциацию. запустите программу от имени администратора.\n{str(e)}")
    
    def view_archive(self):
        file_path = filedialog.askopenfilename(filetypes=[("Архивы", "*.zip *.7z *.aln")])
        if not file_path:
            return
        self.view_archive_file(file_path)
    
    def view_archive_file(self, file_path):
        try:
            if file_path.endswith('.aln'):
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                    if header != b'ALN\x00':
                        messagebox.showerror("ошибка", "неверный формат .aln")
                        return
                    data = f.read()
                    zip_start = data.find(b'PK')
                    if zip_start == -1:
                        messagebox.showerror("ошибка", "архив .aln повреждён")
                        return
                    temp_zip = file_path.replace('.aln', '_temp.zip')
                    with open(temp_zip, 'wb') as zf:
                        zf.write(data[zip_start:])
                    with zipfile.ZipFile(temp_zip, 'r') as zf:
                        files = zf.namelist()
                    os.remove(temp_zip)
            elif file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zf:
                    files = zf.namelist()
            else:
                messagebox.showerror("ошибка", "формат не поддерживается")
                return
            
            win = ctk.CTkToplevel(self)
            win.title(f"содержимое {os.path.basename(file_path)}")
            win.geometry("500x400")
            
            textbox = ctk.CTkTextbox(win, font=("Courier New", 12))
            textbox.pack(fill="both", expand=True, padx=10, pady=10)
            textbox.insert("1.0", "\n".join(files))
            textbox.configure(state="disabled")
            
            ctk.CTkButton(win, text="извлечь все", command=lambda: self.extract_all_from_view(file_path, win)).pack(pady=5)
        except Exception as e:
            messagebox.showerror("ошибка", str(e))
    
    def extract_all_from_view(self, file_path, win):
        dest = filedialog.askdirectory()
        if not dest:
            return
        try:
            if file_path.endswith('.aln'):
                with open(file_path, 'rb') as f:
                    data = f.read()
                    zip_start = data.find(b'PK')
                    temp_zip = file_path.replace('.aln', '_temp.zip')
                    with open(temp_zip, 'wb') as zf:
                        zf.write(data[zip_start:])
                    with zipfile.ZipFile(temp_zip, 'r') as zf:
                        zf.extractall(dest)
                    os.remove(temp_zip)
            else:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    zf.extractall(dest)
            messagebox.showinfo("готово", f"архив извлечён в {dest}")
            win.destroy()
        except Exception as e:
            messagebox.showerror("ошибка", str(e))
    
    def convert_archive(self):
        file_path = filedialog.askopenfilename(filetypes=[("Архивы", "*.zip *.7z")])
        if not file_path:
            return
        if file_path.endswith(".zip"):
            out_path = file_path.replace(".zip", ".7z")
        else:
            out_path = file_path.replace(".7z", ".zip")
        if os.path.exists(out_path):
            if not messagebox.askyesno("подтверждение", f"файл {out_path} уже существует. перезаписать?"):
                return
        try:
            temp_dir = os.path.join(os.path.dirname(file_path), "_temp_convert")
            os.makedirs(temp_dir, exist_ok=True)
            if file_path.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zf:
                    zf.extractall(temp_dir)
            else:
                shutil.unpack_archive(file_path, temp_dir)
            if out_path.endswith(".zip"):
                with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(temp_dir):
                        for f in files:
                            full = os.path.join(root, f)
                            arcname = os.path.relpath(full, temp_dir)
                            zf.write(full, arcname)
            else:
                shutil.make_archive(out_path.replace(".7z", ""), 'zip', temp_dir)
                os.rename(out_path.replace(".7z", ".zip"), out_path)
            shutil.rmtree(temp_dir)
            messagebox.showinfo("готово", f"конвертация завершена\n{os.path.basename(out_path)}")
            self.refresh_files()
        except Exception as e:
            messagebox.showerror("ошибка", str(e))
    
    def open_add_menu(self):
        win = ctk.CTkToplevel(self)
        win.title(tr("new_archive"))
        win.geometry("850x800")
        win.attributes("-topmost", True)
        win.configure(fg_color="#2b2b2b")
        
        main_frame = ctk.CTkScrollableFrame(win, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text=tr("target"), font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(0,5))
        target_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        target_frame.pack(fill="x", pady=(0,15))
        target_entry = ctk.CTkEntry(target_frame, width=500, height=30)
        target_entry.pack(side="left", padx=(0,10))
        target_entry.insert(0, os.path.join(os.path.expanduser("~"), "Desktop"))
        ctk.CTkButton(target_frame, text=tr("browse"), width=80, height=30, command=lambda: self.browse_target(target_entry)).pack(side="left")
        
        ctk.CTkLabel(main_frame, text=tr("type"), font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(0,5))
        type_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=(0,15))
        type_var = ctk.StringVar(value="zip")
        for t in ["ZIP", "7Z", "TAR", "ALN"]:
            rb = ctk.CTkRadioButton(type_frame, text=t, variable=type_var, value=t.lower())
            rb.pack(side="left", padx=15)
        
        ctk.CTkLabel(main_frame, text=tr("level"), font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(0,5))
        level_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        level_frame.pack(fill="x", pady=(0,15))
        level_var = ctk.StringVar(value="Очень быстро")
        for l in ["Очень быстро", "Быстро", "Нормально", "Максимально"]:
            rb = ctk.CTkRadioButton(level_frame, text=l, variable=level_var, value=l)
            rb.pack(side="left", padx=15)
        
        ctk.CTkLabel(main_frame, text="Функция", font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(0,5))
        func_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        func_frame.pack(fill="x", pady=(0,15))
        func_var = ctk.StringVar(value="Новый архив")
        ctk.CTkOptionMenu(func_frame, values=["Новый архив", "Преобразовать существующие архивы", "Изменить пароль", "Добавить (если архив существует)"], variable=func_var, width=250).pack(side="left")
        
        ctk.CTkLabel(main_frame, text="Разделить", font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(0,5))
        split_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        split_frame.pack(fill="x", pady=(0,15))
        split_var = ctk.StringVar(value="Одиночный том")
        ctk.CTkOptionMenu(split_frame, values=["Одиночный том", "4486 MB (DVD)", "700 MB (CD)", "100 MB"], variable=split_var, width=200).pack(side="left")
        
        drop_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8, height=100)
        drop_frame.pack(fill="both", pady=15)
        drop_frame.pack_propagate(False)
        drop_label = ctk.CTkLabel(drop_frame, text="Правая кнопка мыши позволяет добавлять и перетаскивать файлы в архив,\nа также просматривать другие доступные функции", font=("Arial", 12), text_color="#888888", anchor="center", justify="center")
        drop_label.pack(expand=True, fill="both")
        
        drop_frame.bind("<Button-3>", lambda e: self.show_drop_menu(e, target_entry))
        
        checks_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        checks_frame.pack(fill="x", pady=10)
        del_var = ctk.BooleanVar()
        ctk.CTkCheckBox(checks_frame, text=tr("delete_source"), variable=del_var).pack(anchor="w", pady=3)
        separate_var = ctk.BooleanVar()
        ctk.CTkCheckBox(checks_frame, text="Упаковка каждый объект в отдельный архив", variable=separate_var).pack(anchor="w", pady=3)
        tar_var = ctk.BooleanVar()
        ctk.CTkCheckBox(checks_frame, text="Сначала в TAR", variable=tar_var).pack(anchor="w", pady=3)
        
        pass_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        pass_frame.pack(fill="x", pady=10)
        pass_var = ctk.BooleanVar()
        ctk.CTkCheckBox(pass_frame, text=tr("password"), variable=pass_var).pack(anchor="w")
        pass_entry = ctk.CTkEntry(pass_frame, width=300, show="*", placeholder_text="пароль")
        pass_entry.pack(anchor="w", padx=25, pady=5)
        
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        ctk.CTkButton(btn_frame, text=tr("ok"), width=100, fg_color="green", text_color="black", command=lambda: self.do_archive_full(
            target_entry.get(), type_var.get(), level_var.get(), func_var.get(),
            split_var.get(), del_var.get(), separate_var.get(), tar_var.get(),
            pass_entry.get() if pass_var.get() else "", win
        )).pack(side="right", padx=10)
        ctk.CTkButton(btn_frame, text=tr("cancel"), width=100, command=win.destroy).pack(side="right")
    
    def show_drop_menu(self, event, target_entry):
        menu = Menu(self, tearoff=0)
        menu.add_command(label="Добавить файлы", command=lambda: self.add_files_to_archive(target_entry))
        menu.add_separator()
        menu.add_command(label="Добавить папку", command=lambda: self.add_folder_to_archive(target_entry))
        menu.post(event.x_root, event.y_root)
    
    def add_files_to_archive(self, target_entry):
        files = filedialog.askopenfilenames(title="выберите файлы для добавления")
        if files:
            self.selected_files = list(files)
            messagebox.showinfo("выбрано", f"выбрано {len(files)} файлов")
            self.add_selected_to_archive(target_entry)
    
    def add_folder_to_archive(self, target_entry):
        folder = filedialog.askdirectory(title="выберите папку для добавления")
        if folder:
            self.selected_folder = folder
            messagebox.showinfo("выбрано", f"выбрана папка: {os.path.basename(folder)}")
            self.add_selected_to_archive(target_entry)
    
    def add_selected_to_archive(self, target_entry):
        if not self.selected_files and not self.selected_folder:
            messagebox.showwarning("внимание", "сначала выберите файлы или папку")
            return
        
        target = target_entry.get()
        if not os.path.exists(target):
            messagebox.showerror("ошибка", "папка не найдена")
            return
        
        files_to_add = []
        if self.selected_files:
            files_to_add.extend(self.selected_files)
        if self.selected_folder:
            for root, dirs, files in os.walk(self.selected_folder):
                for f in files:
                    files_to_add.append(os.path.join(root, f))
        
        if not files_to_add:
            messagebox.showwarning("внимание", "нет файлов для добавления")
            return
        
        arch_path = os.path.join(target, "alanator_backup.zip")
        try:
            if os.path.exists(arch_path):
                with zipfile.ZipFile(arch_path, 'a', zipfile.ZIP_DEFLATED) as zf:
                    for f in files_to_add:
                        zf.write(f, os.path.basename(f))
            else:
                with zipfile.ZipFile(arch_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for f in files_to_add:
                        zf.write(f, os.path.basename(f))
            messagebox.showinfo("готово", f"добавлено {len(files_to_add)} файлов в архив")
            self.refresh_files()
            self.selected_files = []
            self.selected_folder = None
        except Exception as e:
            messagebox.showerror("ошибка", str(e))
    
    def sort_files(self, sort_by):
        if self.current_path == "Computer" or not os.path.exists(self.current_path):
            return
        
        items = os.listdir(self.current_path)
        if not items:
            return
        
        file_data = []
        for item in items:
            full_path = os.path.join(self.current_path, item)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else 0
            mtime = os.path.getmtime(full_path)
            ext = os.path.splitext(item)[1].lower() if not is_dir else ""
            
            file_data.append({
                'name': item,
                'is_dir': is_dir,
                'size': size,
                'mtime': mtime,
                'ext': ext,
                'path': full_path
            })
        
        if sort_by == "name":
            file_data.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        elif sort_by == "size":
            file_data.sort(key=lambda x: (not x['is_dir'], x['size']))
        elif sort_by == "type":
            file_data.sort(key=lambda x: (not x['is_dir'], x['ext'], x['name'].lower()))
        elif sort_by == "date":
            file_data.sort(key=lambda x: (not x['is_dir'], x['mtime']), reverse=True)
        
        for item in self.tree_files.get_children():
            self.tree_files.delete(item)
        
        for data in file_data:
            if data['is_dir']:
                self.tree_files.insert("", "end", values=(f"📁 {data['name']}", ""))
            else:
                self.tree_files.insert("", "end", values=(data['name'], self.get_file_size(data['path'])))
    
    def do_archive_full(self, target, arch_type, level, func, split, delete_source, separate, tar_first, password, win):
        print(f"текущий путь: {self.current_path}")
        print(f"целевая папка: {target}")
        print(f"пароль: {'установлен' if password else 'не установлен'}")
        
        if not os.path.exists(target):
            messagebox.showerror("ошибка", f"папка не найдена: {target}")
            return
        
        if self.current_path == "Computer" or not os.path.exists(self.current_path):
            messagebox.showerror("ошибка", f"выберите реальную папку. текущий путь: {self.current_path}")
            return
        
        files = [os.path.join(self.current_path, f) for f in os.listdir(self.current_path) if os.path.isfile(os.path.join(self.current_path, f))]
        
        print(f"найдено файлов: {len(files)}")
        
        if not files:
            messagebox.showerror("ошибка", f"нет файлов для архивации в {self.current_path}")
            return
        
        ext = f".{arch_type}"
        arch_path = os.path.join(target, f"alanator_backup{ext}")
        print(f"путь к архиву: {arch_path}")
        
        try:
            if arch_type == "zip":
                compress = zipfile.ZIP_DEFLATED
                if level == "Очень быстро":
                    compress = zipfile.ZIP_STORED
                
                if password:
                    with pyzipper.AESZipFile(arch_path, 'w', compression=compress, encryption=pyzipper.WZ_AES) as zf:
                        zf.setpassword(password.encode('utf-8'))
                        for f in files:
                            zf.write(f, os.path.basename(f))
                    print("зашифрованный zip создан")
                else:
                    with zipfile.ZipFile(arch_path, 'w', compress, allowZip64=True) as zf:
                        for f in files:
                            zf.write(f, os.path.basename(f))
                    print("zip создан успешно")
            
            elif arch_type == "7z":
                if password:
                    with py7zr.SevenZipFile(arch_path, 'w', password=password) as archive:
                        for f in files:
                            archive.write(f, os.path.basename(f))
                    print("зашифрованный 7z создан")
                else:
                    with py7zr.SevenZipFile(arch_path, 'w') as archive:
                        for f in files:
                            archive.write(f, os.path.basename(f))
                    print("7z создан успешно")
            
            elif arch_type == "tar":
                import tarfile
                if password:
                    temp_tar = arch_path.replace('.tar', '_temp.tar')
                    with tarfile.open(temp_tar, 'w') as tar:
                        for f in files:
                            tar.add(f, arcname=os.path.basename(f))
                    with pyzipper.AESZipFile(arch_path, 'w', encryption=pyzipper.WZ_AES) as zf:
                        zf.setpassword(password.encode('utf-8'))
                        zf.write(temp_tar, os.path.basename(temp_tar))
                    os.remove(temp_tar)
                    print("зашифрованный tar (в zip) создан")
                else:
                    with tarfile.open(arch_path, 'w') as tar:
                        for f in files:
                            tar.add(f, arcname=os.path.basename(f))
                    print("tar создан успешно")
            
            elif arch_type == "aln":
                if password:
                    temp_zip = arch_path.replace('.aln', '_temp.zip')
                    with pyzipper.AESZipFile(temp_zip, 'w', encryption=pyzipper.WZ_AES) as zf:
                        zf.setpassword(password.encode('utf-8'))
                        for f in files:
                            zf.write(f, os.path.basename(f))
                    arch_path = self.create_aln_archive_from_zip(target, temp_zip, password)
                    os.remove(temp_zip)
                    print("зашифрованный aln создан")
                else:
                    arch_path = self.create_aln_archive(target, files, password, None)
                    print("aln создан успешно")
            
            if delete_source:
                for f in files:
                    try:
                        os.remove(f)
                    except:
                        pass
            
            messagebox.showinfo(tr("archive_created"), f"{tr('archive_created')}: {arch_path}")
            win.destroy()
            self.refresh_files()
        
        except Exception as e:
            print(f"ошибка: {e}")
            messagebox.showerror(tr("error"), str(e))
    
    def create_aln_archive_from_zip(self, target, temp_zip, password):
        arch_path = os.path.join(target, "alanator_backup.aln")
        with open(arch_path, 'wb') as f_out:
            f_out.write(b'ALN\x00')
            f_out.write(struct.pack('<H', 1))
            timestamp = int(time.time())
            f_out.write(struct.pack('<Q', timestamp))
            f_out.write(struct.pack('<I', 1))
            if password:
                f_out.write(b'PASS')
                f_out.write(password.encode('utf-8'))
                f_out.write(b'\x00')
            else:
                f_out.write(b'NOPASS\x00')
            with open(temp_zip, 'rb') as zf:
                f_out.write(zf.read())
        return arch_path
    
    def create_aln_archive(self, target, files, password, progress_callback=None):
        arch_path = os.path.join(target, "alanator_backup.aln")
        temp_zip = arch_path.replace('.aln', '_temp.zip')
        total_files = len(files)
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, f in enumerate(files):
                zf.write(f, os.path.basename(f))
                if progress_callback:
                    progress_callback(i + 1, total_files)
        with open(arch_path, 'wb') as f_out:
            f_out.write(b'ALN\x00')
            f_out.write(struct.pack('<H', 1))
            timestamp = int(time.time())
            f_out.write(struct.pack('<Q', timestamp))
            f_out.write(struct.pack('<I', len(files)))
            if password:
                f_out.write(b'PASS')
                f_out.write(password.encode('utf-8'))
                f_out.write(b'\x00')
            else:
                f_out.write(b'NOPASS\x00')
            with open(temp_zip, 'rb') as zf:
                f_out.write(zf.read())
        os.remove(temp_zip)
        return arch_path
    
    def extract_archive(self):
        file_path = filedialog.askopenfilename(filetypes=[("Архивы", "*.zip *.7z *.aln *.tar")])
        if not file_path:
            return
        
        password = None
        pwd = ctk.CTkInputDialog(text="введите пароль (если есть):", title="пароль").get_input()
        if pwd:
            password = pwd
        
        dest = filedialog.askdirectory()
        if not dest:
            return
        
        try:
            if file_path.endswith(".zip"):
                if password:
                    with pyzipper.AESZipFile(file_path, 'r') as zf:
                        zf.setpassword(password.encode('utf-8'))
                        zf.extractall(dest)
                else:
                    with zipfile.ZipFile(file_path, 'r') as zf:
                        zf.extractall(dest)
            
            elif file_path.endswith(".7z"):
                if password:
                    with py7zr.SevenZipFile(file_path, 'r', password=password) as archive:
                        archive.extractall(dest)
                else:
                    with py7zr.SevenZipFile(file_path, 'r') as archive:
                        archive.extractall(dest)
            
            elif file_path.endswith(".tar"):
                import tarfile
                if password:
                    with pyzipper.AESZipFile(file_path, 'r') as zf:
                        zf.setpassword(password.encode('utf-8'))
                        temp_dir = os.path.join(os.path.dirname(file_path), "_temp_tar")
                        os.makedirs(temp_dir, exist_ok=True)
                        zf.extractall(temp_dir)
                        tar_file = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                        with tarfile.open(tar_file, 'r') as tar:
                            tar.extractall(dest)
                        shutil.rmtree(temp_dir)
                else:
                    with tarfile.open(file_path, 'r') as tar:
                        tar.extractall(dest)
            
            elif file_path.endswith(".aln"):
                with open(file_path, 'rb') as f:
                    data = f.read()
                    zip_start = data.find(b'PK')
                    if zip_start == -1:
                        messagebox.showerror("ошибка", "архив .aln повреждён")
                        return
                    temp_zip = file_path.replace('.aln', '_temp.zip')
                    with open(temp_zip, 'wb') as zf:
                        zf.write(data[zip_start:])
                if password:
                    with pyzipper.AESZipFile(temp_zip, 'r') as zf:
                        zf.setpassword(password.encode('utf-8'))
                        zf.extractall(dest)
                else:
                    with zipfile.ZipFile(temp_zip, 'r') as zf:
                        zf.extractall(dest)
                os.remove(temp_zip)
            
            else:
                shutil.unpack_archive(file_path, dest)
            messagebox.showinfo("готово", f"архив извлечён в {dest}")
        except Exception as e:
            messagebox.showerror("ошибка", f"не удалось извлечь архив: {e}")
    
    def browse_target(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, "end")
            entry.insert(0, folder)
    
    def test_archive(self):
        file_path = filedialog.askopenfilename(filetypes=[("Архивы", "*.zip *.7z *.aln")])
        if not file_path:
            return
        try:
            if file_path.endswith(".aln"):
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                    if header == b'ALN\x00':
                        messagebox.showinfo("готово", "архив .aln цел")
                    else:
                        messagebox.showerror("ошибка", "неверный формат .aln")
                return
            if file_path.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zf:
                    bad = zf.testzip()
                    if bad:
                        messagebox.showerror("ошибка", f"архив повреждён, первый битый файл: {bad}")
                    else:
                        messagebox.showinfo("готово", "архив цел, ошибок не найдено")
            else:
                test_dir = os.path.dirname(file_path) + "/_test_"
                shutil.unpack_archive(file_path, test_dir)
                shutil.rmtree(test_dir)
                messagebox.showinfo("готово", "архив цел, ошибок не найдено")
        except Exception as e:
            messagebox.showerror("ошибка", f"архив повреждён: {e}")
    
    def secure_delete(self):
        files = filedialog.askopenfilenames(title="выберите файлы для безвозвратного удаления")
        if not files:
            return
        if not messagebox.askyesno("внимание", f"удалить {len(files)} файлов без возможности восстановления?"):
            return
        for file_path in files:
            try:
                size = os.path.getsize(file_path)
                with open(file_path, "wb") as f:
                    for _ in range(3):
                        f.seek(0)
                        f.write(os.urandom(size))
                        f.flush()
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("ошибка", f"не удалось удалить {file_path}: {e}")
        messagebox.showinfo("готово", "выбранные файлы удалены")
        self.refresh_files()
    
    def copy_file(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            self.copy_path = os.path.join(self.current_path, name)
            messagebox.showinfo("скопировано", f"{name} скопирован")
    
    def paste_file(self):
        if hasattr(self, 'copy_path') and self.copy_path and os.path.exists(self.copy_path):
            dest = self.current_path
            name = os.path.basename(self.copy_path)
            new_path = os.path.join(dest, name)
            if os.path.exists(new_path):
                if not messagebox.askyesno("подтверждение", f"{name} уже существует. заменить?"):
                    return
            try:
                if os.path.isdir(self.copy_path):
                    shutil.copytree(self.copy_path, new_path)
                else:
                    shutil.copy2(self.copy_path, new_path)
                self.refresh_files()
            except Exception as e:
                messagebox.showerror("ошибка", str(e))
        else:
            messagebox.showwarning("вставка", "нечего вставлять")
    
    def delete_file(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            if messagebox.askyesno("удаление", f"удалить {name}?"):
                try:
                    full_path = os.path.join(self.current_path, name)
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                    self.refresh_files()
                except Exception as e:
                    messagebox.showerror("ошибка", str(e))
    
    def rename_file(self):
        selection = self.tree_files.selection()
        if selection:
            old_name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            old_path = os.path.join(self.current_path, old_name)
            new_name = ctk.CTkInputDialog(text="новое имя:", title="Переименовать").get_input()
            if new_name:
                try:
                    os.rename(old_path, os.path.join(self.current_path, new_name))
                    self.refresh_files()
                except Exception as e:
                    messagebox.showerror("ошибка", str(e))
    
    def new_folder(self):
        name = ctk.CTkInputDialog(text="имя новой папки:", title="Новая папка").get_input()
        if name:
            try:
                os.mkdir(os.path.join(self.current_path, name))
                self.refresh_files()
            except Exception as e:
                messagebox.showerror("ошибка", str(e))
    
    def cut_file(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            self.cut_path = os.path.join(self.current_path, name)
            messagebox.showinfo("вырезано", f"{name} вырезан")
    
    def view_bat_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            win = ctk.CTkToplevel(self)
            win.title(f"просмотр {os.path.basename(path)}")
            win.geometry("800x600")
            textbox = ctk.CTkTextbox(win, font=("Courier New", 12))
            textbox.pack(fill="both", expand=True, padx=10, pady=10)
            textbox.insert("1.0", content)
            textbox.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("ошибка", f"не удалось прочитать файл: {e}")
    
    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, height=50, corner_radius=0)
        toolbar.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        btn_add = ctk.CTkButton(toolbar, text=tr("new_archive"), width=80, height=35, fg_color="gray30", hover_color="gray40", command=self.open_add_menu).pack(side="left", padx=4, pady=5)
        btn_convert = ctk.CTkButton(toolbar, text=tr("convert_archive"), width=100, height=35, fg_color="gray30", hover_color="gray40", command=self.convert_archive).pack(side="left", padx=4, pady=5)
        btn_extract = ctk.CTkButton(toolbar, text=tr("extract"), width=80, height=35, fg_color="gray30", hover_color="gray40", command=self.extract_archive).pack(side="left", padx=4, pady=5)
        btn_test = ctk.CTkButton(toolbar, text=tr("test"), width=80, height=35, fg_color="gray30", hover_color="gray40", command=self.test_archive).pack(side="left", padx=4, pady=5)
        btn_delete = ctk.CTkButton(toolbar, text=tr("secure_delete"), width=130, height=35, fg_color="gray30", hover_color="gray40", command=self.secure_delete).pack(side="left", padx=4, pady=5)
    
    def create_main_area(self):
        main_panel = ctk.CTkFrame(self)
        main_panel.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        main_panel.grid_columnconfigure(0, weight=1)
        main_panel.grid_columnconfigure(1, weight=3)
        main_panel.grid_rowconfigure(0, weight=1)
        
        left_frame = ctk.CTkFrame(main_panel, width=280)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        left_frame.grid_propagate(False)
        
        ctk.CTkLabel(left_frame, text="Закладки", font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=5, pady=5)
        bookmarks = ["Computer's root", os.path.expanduser("~"), "Desktop", "Документы", "Downloads", "OneDrive"]
        for b in bookmarks:
            lbl = ctk.CTkLabel(left_frame, text=b, anchor="w", cursor="hand2")
            lbl.pack(fill="x", padx=15, pady=2)
            lbl.bind("<Button-1>", lambda e, path=b: self.quick_open(self.get_bookmark_path(path)))
        
        ctk.CTkLabel(left_frame, text="Файловая система", font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=5, pady=(15,5))
        self.tree = ttk.Treeview(left_frame, show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.on_tree_click)
        
        right_frame = ctk.CTkFrame(main_panel)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        right_frame.grid_rowconfigure(0, weight=0)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        addr_frame = ctk.CTkFrame(right_frame)
        addr_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        addr_frame.grid_columnconfigure(0, weight=1)
        self.path_label = ctk.CTkLabel(addr_frame, text="", anchor="w")
        self.path_label.grid(row=0, column=0, sticky="ew", padx=5)
        btn_back = ctk.CTkButton(addr_frame, text="Назад", width=60, command=self.go_back).grid(row=0, column=1, padx=2)
        btn_up = ctk.CTkButton(addr_frame, text="Вверх", width=60, command=self.go_up).grid(row=0, column=2, padx=2)
        
        self.tree_files = ttk.Treeview(right_frame, columns=("name", "size"), show="headings")
        self.tree_files.heading("name", text=tr("file"))
        self.tree_files.heading("size", text=tr("file_size"))
        self.tree_files.column("name", width=500)
        self.tree_files.column("size", width=100)
        self.tree_files.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.tree_files.bind("<Double-1>", self.on_file_click)
        self.tree_files.bind("<Button-3>", self.on_right_click)
        self.tree_files.bind("<Button-3>", self.on_right_click_empty, add=True)
        
        scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree_files.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.tree_files.configure(yscrollcommand=scroll.set)
    
    def on_right_click(self, event):
        item = self.tree_files.identify_row(event.y)
        if not item:
            return
        self.tree_files.selection_set(item)
        name = self.tree_files.item(item, "values")[0]
        clean_name = name.replace("📁 ", "").replace("📄 ", "")
        full_path = os.path.join(self.current_path, clean_name)
        
        menu = Menu(self, tearoff=0)
        menu.add_command(label=tr("open"), command=lambda: os.startfile(full_path) if os.path.exists(full_path) else None)
        menu.add_separator()
        
        if full_path.endswith('.bat') and os.path.isfile(full_path):
            menu.add_command(label="Просмотреть текст .bat", command=lambda: self.view_bat_file(full_path))
            menu.add_separator()
        
        menu.add_command(label=tr("copy"), command=self.copy_file)
        menu.add_command(label=tr("cut"), command=self.cut_file)
        menu.add_command(label=tr("paste"), command=self.paste_file)
        menu.add_separator()
        menu.add_command(label=tr("rename"), command=self.rename_file)
        menu.add_command(label=tr("delete"), command=self.delete_file)
        menu.add_separator()
        
        nav_menu = Menu(menu, tearoff=0)
        nav_menu.add_command(label="Обзор пути", command=lambda: self.quick_open(os.path.dirname(full_path) if os.path.isfile(full_path) else full_path))
        nav_menu.add_command(label="Открыть командную строку", command=lambda: os.system(f"start cmd /k cd \"{self.current_path}\""))
        nav_menu.add_command(label="Открыть PowerShell", command=lambda: os.system(f"start powershell -NoExit -Command \"cd '{self.current_path}'\""))
        menu.add_cascade(label="Навигация", menu=nav_menu)
        
        sort_menu = Menu(menu, tearoff=0)
        sort_menu.add_command(label=tr("by_name"), command=self.refresh_files)
        sort_menu.add_command(label=tr("by_size"), command=lambda: messagebox.showinfo("сортировка", "будет в следующей версии"))
        menu.add_cascade(label="Сортировать по", menu=sort_menu)
        
        menu.add_command(label=tr("select_all"), command=self.select_all_files)
        menu.add_command(label=tr("refresh"), command=self.refresh_files)
        menu.add_separator()
        
        menu.add_command(label="Открыть с помощью...", command=lambda: os.startfile(full_path) if os.path.exists(full_path) else None)
        menu.add_separator()
        
        file_menu = Menu(menu, tearoff=0)
        file_menu.add_command(label=tr("copy"), command=self.copy_file)
        file_menu.add_command(label=tr("rename"), command=self.rename_file)
        file_menu.add_command(label=tr("delete"), command=self.delete_file)
        menu.add_cascade(label="Менеджер файлов", menu=file_menu)
        
        tools_menu = Menu(menu, tearoff=0)
        tools_menu.add_command(label=tr("test"), command=self.test_archive)
        tools_menu.add_command(label=tr("secure_delete"), command=self.secure_delete_selected)
        menu.add_cascade(label="Файловые инструменты", menu=tools_menu)
        
        func_menu = Menu(menu, tearoff=0)
        func_menu.add_command(label="Поиск в интернете", command=lambda: os.system(f"start https://www.google.com/search?q={clean_name}"))
        func_menu.add_command(label="Обзор пути", command=lambda: self.quick_open(self.current_path))
        func_menu.add_command(label=tr("properties"), command=self.show_properties)
        menu.add_cascade(label="Функции", menu=func_menu)
        
        menu.add_separator()
        menu.add_command(label=tr("properties"), command=self.show_properties)
        
        menu.post(event.x_root, event.y_root)
    
    def on_right_click_empty(self, event):
        item = self.tree_files.identify_row(event.y)
        if item:
            return
        menu = Menu(self, tearoff=0)
        menu.add_command(label=tr("new_folder"), command=self.new_folder)
        menu.add_separator()
        menu.add_command(label=tr("paste"), command=self.paste_file)
        menu.add_separator()
        menu.add_command(label=tr("refresh"), command=self.refresh_files)
        menu.add_command(label=tr("properties"), command=self.show_folder_properties)
        menu.post(event.x_root, event.y_root)
    
    def show_folder_properties(self):
        if os.path.exists(self.current_path):
            info = f"папка: {self.current_path}\n"
            try:
                items = os.listdir(self.current_path)
                files = [f for f in items if os.path.isfile(os.path.join(self.current_path, f))]
                folders = [f for f in items if os.path.isdir(os.path.join(self.current_path, f))]
                info += f"файлов: {len(files)}\n"
                info += f"папок: {len(folders)}"
            except:
                info += "не удалось получить информацию"
            messagebox.showinfo(tr("properties"), info)
    
    def secure_delete_selected(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            full_path = os.path.join(self.current_path, name)
            if messagebox.askyesno("внимание", f"безвозвратно удалить {name}?"):
                try:
                    if os.path.isfile(full_path):
                        size = os.path.getsize(full_path)
                        with open(full_path, "wb") as f:
                            for _ in range(3):
                                f.seek(0)
                                f.write(os.urandom(size))
                                f.flush()
                    os.remove(full_path)
                    messagebox.showinfo("готово", f"{name} удалён без возможности восстановления")
                    self.refresh_files()
                except Exception as e:
                    messagebox.showerror("ошибка", str(e))
    
    def show_properties(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            full_path = os.path.join(self.current_path, name)
            if os.path.exists(full_path):
                info = f"имя: {name}\n"
                info += f"путь: {full_path}\n"
                if os.path.isfile(full_path):
                    info += f"размер: {self.get_file_size(full_path)}\n"
                try:
                    creation_time = os.path.getctime(full_path)
                    info += f"создан: {time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(creation_time))}\n"
                except:
                    info += "создан: неизвестно\n"
                try:
                    mod_time = os.path.getmtime(full_path)
                    info += f"изменён: {time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(mod_time))}\n"
                except:
                    info += "изменён: неизвестно\n"
                try:
                    access_time = os.path.getatime(full_path)
                    info += f"открыт: {time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(access_time))}"
                except:
                    info += "открыт: неизвестно"
                messagebox.showinfo(tr("properties"), info)
    
    def get_bookmark_path(self, name):
        if name == "Computer's root":
            return "Computer"
        elif name == "Desktop":
            return os.path.join(os.path.expanduser("~"), "Desktop")
        elif name == "Документы":
            return os.path.join(os.path.expanduser("~"), "Documents")
        elif name == "Downloads":
            return os.path.join(os.path.expanduser("~"), "Downloads")
        elif name == "OneDrive":
            return os.path.join(os.path.expanduser("~"), "OneDrive")
        else:
            return name
    
    def quick_open(self, path):
        if path == "Computer" or os.path.exists(path):
            self.current_path = path
            self.refresh_files()
    
    def get_drives_info(self):
        drives = []
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    usage = shutil.disk_usage(drive)
                    total_gb = usage.total / (1024**3)
                    free_gb = usage.free / (1024**3)
                    used_percent = (1 - usage.free / usage.total) * 100
                    drives.append({
                        "name": drive,
                        "size": f"{total_gb:.1f} GB",
                        "free": f"{free_gb:.1f} GB ({used_percent:.0f}% занято)",
                        "fs": "NTFS"
                    })
                except:
                    drives.append({"name": drive, "size": "?", "free": "?", "fs": "?"})
        return drives
    
    def get_file_size(self, path):
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                if size < 1024:
                    return f"{size} B"
                elif size < 1024**2:
                    return f"{size/1024:.1f} KB"
                elif size < 1024**3:
                    return f"{size/1024**2:.1f} MB"
                else:
                    return f"{size/1024**3:.1f} GB"
        except:
            return "ошибка"
        return ""
    
    def refresh_files(self):
        for item in self.tree_files.get_children():
            self.tree_files.delete(item)
        self.path_label.configure(text=f"путь: {self.current_path}")
        try:
            if self.current_path == "Computer":
                for drive in self.get_drives_info():
                    name = f"💾 {drive['name']}"
                    info = f"{drive['free']} свободно из {drive['size']}"
                    self.tree_files.insert("", "end", values=(name, info))
                return
            
            if os.path.exists(self.current_path):
                items = os.listdir(self.current_path)
                for item in sorted(items):
                    full_path = os.path.join(self.current_path, item)
                    if os.path.isdir(full_path):
                        self.tree_files.insert("", "end", values=(f"📁 {item}", ""))
                    else:
                        self.tree_files.insert("", "end", values=(item, self.get_file_size(full_path)))
        except Exception as e:
            self.tree_files.insert("", "end", values=(f"ошибка: {e}", ""))
    
    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        comp = self.tree.insert("", "end", text="Мой компьютер", open=True)
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if os.path.exists(f"{letter}:\\"):
                self.tree.insert(comp, "end", text=f"{letter}:\\")
        user = self.tree.insert(comp, "end", text="Пользователь")
        home = os.path.expanduser("~")
        for name in ["Desktop", "Documents", "Downloads", "Music", "Videos", "Pictures"]:
            p = os.path.join(home, name)
            if os.path.exists(p):
                self.tree.insert(user, "end", text=name)
    
    def on_tree_click(self, event):
        item = self.tree.focus()
        if not item:
            return
        text = self.tree.item(item, "text")
        if ":" in text:
            self.current_path = text
            self.refresh_files()
        elif text == "Мой компьютер":
            self.current_path = "Computer"
            self.refresh_files()
        else:
            parts = []
            i = item
            while i:
                txt = self.tree.item(i, "text")
                if txt == "Мой компьютер":
                    break
                parts.insert(0, txt)
                i = self.tree.parent(i)
            if parts:
                if ":" in parts[0]:
                    self.current_path = "".join(parts)
                else:
                    self.current_path = "C:/" + "/".join(parts)
                self.refresh_files()
    
    def on_file_click(self, event):
        selection = self.tree_files.selection()
        if not selection:
            return
        name = self.tree_files.item(selection[0], "values")[0]
        if name.startswith("📁"):
            folder = name.replace("📁 ", "")
            new_path = os.path.join(self.current_path, folder)
            if os.path.isdir(new_path):
                self.current_path = new_path
                self.refresh_files()
        elif name.startswith("💾") or (len(name) == 3 and name[1] == ":"):
            disk = name.replace("💾 ", "") if name.startswith("💾") else name
            self.current_path = disk
            self.refresh_files()
        elif self.current_path != "Computer":
            full_path = os.path.join(self.current_path, name)
            if os.path.isfile(full_path):
                os.startfile(full_path)
    
    def go_back(self):
        if self.current_path == "Computer":
            return
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self.refresh_files()
        else:
            self.current_path = "Computer"
            self.refresh_files()
    
    def go_up(self):
        self.go_back()
    
    def run_test(self):
        messagebox.showinfo(tr("test"), "OK")
    
    def select_all_files(self):
        for item in self.tree_files.get_children():
            self.tree_files.selection_add(item)

if __name__ == "__main__":
    app = AlanatorApp()
    app.mainloop()
