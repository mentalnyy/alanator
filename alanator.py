import os
import zipfile
import shutil
import json
import struct
import time
import sys
import ctypes
import threading
import tempfile
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import tkinter.ttk as ttk

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
        "associate": "Сделать архиватором по умолчанию",
        "associations": "Ассоциации файлов",
        "context_menu": "Интеграция в контекстное меню",
        "zip_encoding": "Кодировка для имён файлов ZIP",
        "language": "Язык",
        "help": "Помощь",
        "website": "Веб-сайт проекта",
        "about": "О программе",
        "folder": "папка",
        "file_size": "размер",
        "error": "ошибка",
        "ok": "OK",
        "cancel": "Отмена",
        "clear": "Очистить",
        "target": "Целевой",
        "type": "Тип",
        "level": "Уровень",
        "password": "Пароль",
        "delete_source": "Удалить файлы после архивации",
        "browse": "Обзор",
        "processing": "обработка",
        "ready": "готово",
        "archive_created": "архив создан",
        "archive_extracted": "архив извлечён",
        "choose_folder": "выберите папку",
        "no_files": "нет файлов для архивации",
        "folder_not_found": "папка не найдена",
        "properties": "свойства",
        "new_folder": "Новая папка",
        "add_to_archive": "Добавить в архив",
        "remove_from_archive": "Удалить из архива",
        "extract_selected": "Извлечь выбранные",
        "archive_manager": "Управление архивом",
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
        "associate": "Make default archiver",
        "associations": "File associations",
        "context_menu": "Context menu integration",
        "zip_encoding": "ZIP file name encoding",
        "language": "Language",
        "help": "Help",
        "website": "Project website",
        "about": "About",
        "folder": "folder",
        "file_size": "size",
        "error": "error",
        "ok": "OK",
        "cancel": "Cancel",
        "clear": "Clear",
        "target": "Target",
        "type": "Type",
        "level": "Level",
        "password": "Password",
        "delete_source": "Delete files after archiving",
        "browse": "Browse",
        "processing": "processing",
        "ready": "ready",
        "archive_created": "archive created",
        "archive_extracted": "archive extracted",
        "choose_folder": "choose folder",
        "no_files": "no files to archive",
        "folder_not_found": "folder not found",
        "properties": "properties",
        "new_folder": "New folder",
        "add_to_archive": "Add to archive",
        "remove_from_archive": "Remove from archive",
        "extract_selected": "Extract selected",
        "archive_manager": "Archive manager",
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

class ArchiveManager:
    """класс для управления архивами (добавление/удаление файлов)"""
    
    @staticmethod
    def get_archive_files(file_path):
        """получает список файлов в архиве"""
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zf:
                return zf.namelist()
        elif file_path.endswith('.aln'):
            with open(file_path, 'rb') as f:
                data = f.read()
                zip_start = data.find(b'PK')
                if zip_start == -1:
                    return []
                temp_zip = file_path.replace('.aln', '_temp.zip')
                with open(temp_zip, 'wb') as zf:
                    zf.write(data[zip_start:])
                with zipfile.ZipFile(temp_zip, 'r') as zf:
                    files = zf.namelist()
                os.remove(temp_zip)
                return files
        return []
    
    @staticmethod
    def add_files_to_archive(file_path, files_to_add, progress_callback=None):
        """добавляет файлы в существующий архив"""
        if not file_path.endswith(('.zip', '.aln')):
            return False, "формат не поддерживается"
        
        # создаём временную папку
        temp_dir = tempfile.mkdtemp()
        
        try:
            # извлекаем существующий архив во временную папку
            if file_path.endswith('.aln'):
                with open(file_path, 'rb') as f:
                    data = f.read()
                    zip_start = data.find(b'PK')
                    if zip_start == -1:
                        shutil.rmtree(temp_dir)
                        return False, "архив повреждён"
                    temp_zip = file_path.replace('.aln', '_temp.zip')
                    with open(temp_zip, 'wb') as zf:
                        zf.write(data[zip_start:])
                    with zipfile.ZipFile(temp_zip, 'r') as zf:
                        zf.extractall(temp_dir)
                    os.remove(temp_zip)
            else:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    zf.extractall(temp_dir)
            
            # копируем новые файлы во временную папку
            for f in files_to_add:
                dest = os.path.join(temp_dir, os.path.basename(f))
                shutil.copy2(f, dest)
                if progress_callback:
                    progress_callback()
            
            # создаём новый архив
            new_zip = file_path + '.new'
            with zipfile.ZipFile(new_zip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
                for root, dirs, files in os.walk(temp_dir):
                    for f in files:
                        full_path = os.path.join(root, f)
                        arcname = os.path.relpath(full_path, temp_dir)
                        zf.write(full_path, arcname)
            
            # заменяем старый архив
            shutil.rmtree(temp_dir)
            os.remove(file_path)
            os.rename(new_zip, file_path)
            return True, "файлы добавлены"
        except Exception as e:
            shutil.rmtree(temp_dir)
            return False, str(e)
    
    @staticmethod
    def remove_files_from_archive(file_path, files_to_remove, progress_callback=None):
        """удаляет файлы из архива"""
        if not file_path.endswith(('.zip', '.aln')):
            return False, "формат не поддерживается"
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # извлекаем архив во временную папку
            if file_path.endswith('.aln'):
                with open(file_path, 'rb') as f:
                    data = f.read()
                    zip_start = data.find(b'PK')
                    if zip_start == -1:
                        shutil.rmtree(temp_dir)
                        return False, "архив повреждён"
                    temp_zip = file_path.replace('.aln', '_temp.zip')
                    with open(temp_zip, 'wb') as zf:
                        zf.write(data[zip_start:])
                    with zipfile.ZipFile(temp_zip, 'r') as zf:
                        zf.extractall(temp_dir)
                    os.remove(temp_zip)
            else:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    zf.extractall(temp_dir)
            
            # удаляем указанные файлы
            for f in files_to_remove:
                f_path = os.path.join(temp_dir, f)
                if os.path.exists(f_path):
                    if os.path.isdir(f_path):
                        shutil.rmtree(f_path)
                    else:
                        os.remove(f_path)
                if progress_callback:
                    progress_callback()
            
            # создаём новый архив
            new_zip = file_path + '.new'
            with zipfile.ZipFile(new_zip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
                for root, dirs, files in os.walk(temp_dir):
                    for f in files:
                        full_path = os.path.join(root, f)
                        arcname = os.path.relpath(full_path, temp_dir)
                        zf.write(full_path, arcname)
            
            shutil.rmtree(temp_dir)
            os.remove(file_path)
            os.rename(new_zip, file_path)
            return True, "файлы удалены"
        except Exception as e:
            shutil.rmtree(temp_dir)
            return False, str(e)

class AlanatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if file_path.endswith(('.aln', '.zip', '.7z', '.tar')):
                self.view_archive_file(file_path)
                return
        
        self.settings_file = "alanator_settings.json"
        self.settings = self.load_settings()
        self.current_lang = self.settings.get("language", "ru")
        tr.lang = self.current_lang
        
        self.title(tr("title"))
        self.geometry("1200x700")
        self.current_path = "Computer"
        self.cut_path = None
        self.copy_path = None
        self.current_archive = None  # для управления архивом
        
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
        
        self.bind("<Control-c>", lambda event: self.copy_file())
        self.bind("<Control-v>", lambda event: self.paste_file())
        self.bind("<F5>", lambda event: self.refresh_files())
    
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
        list_menu.add_command(label=tr("by_name"), command=self.refresh_files)
        list_menu.add_command(label=tr("by_size"), command=lambda: messagebox.showinfo("info", tr("by_size")))
        
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("tools"), menu=tools_menu)
        tools_menu.add_command(label=tr("settings"), command=self.open_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label=tr("test"), command=self.run_test)
        tools_menu.add_command(label=tr("secure_delete"), command=self.secure_delete)
        tools_menu.add_command(label=tr("view_archive"), command=self.view_archive)
        tools_menu.add_command(label=tr("archive_manager"), command=self.open_archive_manager)
        
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("options"), menu=settings_menu)
        settings_menu.add_command(label=tr("settings"), command=self.open_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label=tr("run_as_admin"), command=self.run_as_admin)
        settings_menu.add_command(label=tr("associate"), command=self.associate_files)
        settings_menu.add_separator()
        settings_menu.add_command(label=tr("language"), command=self.open_settings)
        
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=tr("help"), menu=help_menu)
        help_menu.add_command(label=tr("website"), command=lambda: os.system("start https://github.com/mentalnyy/alanator"))
        help_menu.add_command(label=tr("about"), command=self.about_program)
    
    def open_settings(self):
        win = ctk.CTkToplevel(self)
        win.title(tr("settings"))
        win.geometry("900x650")
        win.attributes("-topmost", True)
        
        tabview = ctk.CTkTabview(win, width=850, height=550)
        tabview.pack(fill="both", expand=True, padx=20, pady=15)
        
        tabview.add(tr("settings"))
        self.create_settings_general(tabview.tab(tr("settings")))
        
        tabview.add(tr("options"))
        self.create_settings_advanced(tabview.tab(tr("options")))
        
        tabview.add(tr("view"))
        self.create_settings_theme(tabview.tab(tr("view")))
        
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(btn_frame, text=tr("ok"), width=100, command=lambda: self.apply_settings(win)).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text=tr("cancel"), width=100, command=win.destroy).pack(side="right", padx=5)
    
    def create_settings_general(self, parent):
        ctk.CTkLabel(parent, text=tr("language"), font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        lang_frame = ctk.CTkFrame(parent)
        lang_frame.pack(fill="x", padx=20, pady=5)
        self.lang_var = ctk.StringVar(value=self.settings.get("language", "ru"))
        ctk.CTkOptionMenu(lang_frame, values=["ru", "en"], variable=self.lang_var, width=100).pack(side="left", padx=5)
    
    def create_settings_advanced(self, parent):
        ctk.CTkLabel(parent, text=tr("associations"), font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        assoc_frame = ctk.CTkFrame(parent)
        assoc_frame.pack(fill="x", padx=20, pady=5)
        self.assoc_aln = ctk.BooleanVar(value=self.settings.get("assoc_aln", True))
        ctk.CTkCheckBox(assoc_frame, text=".aln", variable=self.assoc_aln).pack(anchor="w", pady=2)
        self.assoc_zip = ctk.BooleanVar(value=self.settings.get("assoc_zip", False))
        ctk.CTkCheckBox(assoc_frame, text=".zip", variable=self.assoc_zip).pack(anchor="w", pady=2)
    
    def create_settings_theme(self, parent):
        ctk.CTkLabel(parent, text=tr("view"), font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        theme_frame = ctk.CTkFrame(parent)
        theme_frame.pack(fill="x", padx=20, pady=5)
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "Тёмная"))
        ctk.CTkOptionMenu(theme_frame, values=["Тёмная", "Светлая", "Системная"], variable=self.theme_var, width=150).pack(side="left", padx=5)
    
    def apply_settings(self, win):
        self.settings["theme"] = self.theme_var.get()
        self.settings["language"] = self.lang_var.get()
        self.settings["assoc_aln"] = self.assoc_aln.get()
        self.settings["assoc_zip"] = self.assoc_zip.get()
        
        theme = self.settings["theme"]
        if theme == "Тёмная":
            ctk.set_appearance_mode("dark")
        elif theme == "Светлая":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        
        new_lang = self.settings["language"]
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            tr.lang = new_lang
            self.update_language()
        
        self.save_settings()
        messagebox.showinfo(tr("settings"), tr("settings") + " " + tr("ok"))
        win.destroy()
    
    def run_as_admin(self):
        try:
            if ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showinfo(tr("settings"), "already admin")
                return
            script = os.path.abspath(sys.argv[0])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
            self.quit()
        except Exception as e:
            messagebox.showerror(tr("error"), str(e))
    
    def associate_files(self):
        try:
            import winreg
            exe_path = os.path.abspath(sys.argv[0])
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".aln") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "alanator.aln")
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "alanator.aln") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "alanator archive")
                with winreg.CreateKey(key, "shell\\open\\command") as cmd:
                    winreg.SetValue(cmd, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".zip") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "alanator.zip")
            
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, "alanator.zip") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "alanator zip archive")
                with winreg.CreateKey(key, "shell\\open\\command") as cmd:
                    winreg.SetValue(cmd, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
            
            messagebox.showinfo(tr("settings"), "associations added")
        except Exception as e:
            messagebox.showerror(tr("error"), str(e))
    
    def about_program(self):
        about = "alanator 1.0\narchiver by alan\n\nzip, 7z, tar, aln support\narchive manager included"
        messagebox.showinfo(tr("about"), about)
    
    def view_archive(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.7z *.aln *.tar")])
        if not file_path:
            return
        self.view_archive_file(file_path)
    
    def view_archive_file(self, file_path):
        try:
            files = ArchiveManager.get_archive_files(file_path) if file_path.endswith(('.zip', '.aln')) else []
            if not files:
                if file_path.endswith('.7z'):
                    import py7zr
                    with py7zr.SevenZipFile(file_path, 'r') as zf:
                        files = zf.getnames()
                elif file_path.endswith('.tar'):
                    import tarfile
                    with tarfile.open(file_path, 'r') as tar:
                        files = tar.getnames()
                else:
                    messagebox.showerror(tr("error"), "format not supported")
                    return
            
            self.current_archive = file_path
            
            win = ctk.CTkToplevel(self)
            win.title(f"📦 {os.path.basename(file_path)} ({len(files)} files)")
            win.geometry("600x500")
            win.attributes("-topmost", True)
            
            # список файлов
            listbox = ctk.CTkScrollableFrame(win)
            listbox.pack(fill="both", expand=True, padx=10, pady=10)
            
            check_vars = {}
            for f in files:
                var = ctk.BooleanVar()
                cb = ctk.CTkCheckBox(listbox, text=f, variable=var)
                cb.pack(anchor="w", pady=1)
                check_vars[f] = var
            
            # кнопки управления
            btn_frame = ctk.CTkFrame(win)
            btn_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkButton(btn_frame, text=tr("add_to_archive"), command=lambda: self.add_files_to_archive_ui(file_path, win)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text=tr("remove_from_archive"), command=lambda: self.remove_files_from_archive_ui(file_path, check_vars, win)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text=tr("extract_selected"), command=lambda: self.extract_selected_from_archive(file_path, check_vars, win)).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text=tr("refresh"), command=lambda: self.refresh_archive_view(file_path, win)).pack(side="left", padx=5)
        except Exception as e:
            messagebox.showerror(tr("error"), str(e))
    
    def refresh_archive_view(self, file_path, win):
        win.destroy()
        self.view_archive_file(file_path)
    
    def add_files_to_archive_ui(self, file_path, win):
        files = filedialog.askopenfilenames(title="выберите файлы для добавления")
        if not files:
            return
        
        def progress_callback():
            win.update()
        
        success, msg = ArchiveManager.add_files_to_archive(file_path, files, progress_callback)
        messagebox.showinfo(tr("info"), msg)
        if success:
            self.refresh_archive_view(file_path, win)
            self.refresh_files()
    
    def remove_files_from_archive_ui(self, file_path, check_vars, win):
        selected = [f for f, var in check_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning(tr("warning"), "выберите файлы для удаления")
            return
        
        if not messagebox.askyesno(tr("confirm"), f"удалить {len(selected)} файлов из архива?"):
            return
        
        def progress_callback():
            win.update()
        
        success, msg = ArchiveManager.remove_files_from_archive(file_path, selected, progress_callback)
        messagebox.showinfo(tr("info"), msg)
        if success:
            self.refresh_archive_view(file_path, win)
            self.refresh_files()
    
    def extract_selected_from_archive(self, file_path, check_vars, win):
        selected = [f for f, var in check_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning(tr("warning"), "выберите файлы для извлечения")
            return
        
        dest = filedialog.askdirectory(title=tr("choose_folder"))
        if not dest:
            return
        
        try:
            if file_path.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zf:
                    for f in selected:
                        zf.extract(f, dest)
            elif file_path.endswith('.aln'):
                with open(file_path, 'rb') as f:
                    data = f.read()
                    zip_start = data.find(b'PK')
                    if zip_start != -1:
                        temp_zip = file_path.replace('.aln', '_temp.zip')
                        with open(temp_zip, 'wb') as zf:
                            zf.write(data[zip_start:])
                        with zipfile.ZipFile(temp_zip, 'r') as zf:
                            for f in selected:
                                zf.extract(f, dest)
                        os.remove(temp_zip)
            messagebox.showinfo(tr("info"), f"извлечено {len(selected)} файлов")
        except Exception as e:
            messagebox.showerror(tr("error"), str(e))
    
    def open_archive_manager(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.aln")])
        if not file_path:
            return
        self.view_archive_file(file_path)
    
    def create_toolbar(self):
        if hasattr(self, 'toolbar'):
            self.toolbar.destroy()
        self.toolbar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.toolbar.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        ctk.CTkButton(self.toolbar, text=tr("new_archive"), width=80, height=35, fg_color="gray30", hover_color="gray40", command=self.open_add_menu).pack(side="left", padx=4, pady=5)
        ctk.CTkButton(self.toolbar, text=tr("secure_delete"), width=130, height=35, fg_color="gray30", hover_color="gray40", command=self.secure_delete).pack(side="left", padx=4, pady=5)
        ctk.CTkButton(self.toolbar, text=tr("archive_manager"), width=130, height=35, fg_color="gray30", hover_color="gray40", command=self.open_archive_manager).pack(side="left", padx=4, pady=5)
    
    def open_add_menu(self):
        win = ctk.CTkToplevel(self)
        win.title(tr("new_archive"))
        win.geometry("800x750")
        win.attributes("-topmost", True)
        
        ctk.CTkLabel(win, text=tr("target"), font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15,5))
        target_frame = ctk.CTkFrame(win)
        target_frame.pack(fill="x", padx=20, pady=5)
        target_entry = ctk.CTkEntry(target_frame, width=500)
        target_entry.pack(side="left", padx=5)
        target_entry.insert(0, os.path.join(os.path.expanduser("~"), "Desktop"))
        ctk.CTkButton(target_frame, text=tr("browse"), width=80, command=lambda: self.browse_target(target_entry)).pack(side="left", padx=5)
        
        ctk.CTkLabel(win, text=tr("type"), font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,5))
        type_frame = ctk.CTkFrame(win)
        type_frame.pack(fill="x", padx=20, pady=5)
        type_var = ctk.StringVar(value="zip")
        for t in ["ZIP", "7Z", "TAR", "ALN"]:
            rb = ctk.CTkRadioButton(type_frame, text=t, variable=type_var, value=t.lower())
            rb.pack(side="left", padx=15)
        
        ctk.CTkLabel(win, text=tr("level"), font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,5))
        level_frame = ctk.CTkFrame(win)
        level_frame.pack(fill="x", padx=20, pady=5)
        level_var = ctk.StringVar(value="Очень быстро")
        for l in ["Очень быстро", "Быстро", "Нормально", "Максимально"]:
            rb = ctk.CTkRadioButton(level_frame, text=l, variable=level_var, value=l)
            rb.pack(side="left", padx=10)
        
        ctk.CTkLabel(win, text=tr("password"), font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,5))
        pass_frame = ctk.CTkFrame(win)
        pass_frame.pack(fill="x", padx=20, pady=5)
        pass_entry = ctk.CTkEntry(pass_frame, width=300, show="*", placeholder_text="password")
        pass_entry.pack(side="left", padx=5)
        
        checks_frame = ctk.CTkFrame(win)
        checks_frame.pack(fill="x", padx=20, pady=10)
        del_var = ctk.BooleanVar()
        ctk.CTkCheckBox(checks_frame, text=tr("delete_source"), variable=del_var).pack(anchor="w", pady=2)
        
        progress_label = ctk.CTkLabel(win, text="")
        progress_label.pack(pady=5)
        progress_bar = ctk.CTkProgressBar(win, width=400)
        progress_bar.pack(pady=5)
        progress_bar.set(0)
        
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(btn_frame, text=tr("ok"), width=100, command=lambda: self.do_archive_with_progress(
            target_entry.get(), type_var.get(), level_var.get(), pass_entry.get(), 
            del_var.get(), win, progress_bar, progress_label
        )).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text=tr("cancel"), width=100, command=win.destroy).pack(side="right", padx=5)
    
    def do_archive_with_progress(self, target, arch_type, level, password, delete_source, win, progress_bar, progress_label):
        if self.current_path != "Computer" and os.path.exists(self.current_path):
            target = self.current_path
        
        if self.current_path == "Computer":
            messagebox.showerror(tr("error"), tr("folder_not_found"))
            return
        
        if not os.path.exists(target):
            messagebox.showerror(tr("error"), tr("folder_not_found"))
            return
        
        files = [os.path.join(target, f) for f in os.listdir(target) if os.path.isfile(os.path.join(target, f))]
        if not files:
            messagebox.showerror(tr("error"), tr("no_files"))
            return
        
        def update_progress(current, total):
            progress_bar.set(current / total)
            progress_label.configure(text=f"{tr('processing')}: {current}/{total}")
            win.update()
        
        def archive_task():
            try:
                if arch_type == "aln":
                    arch_path = self.create_aln_archive(target, files, password, update_progress)
                else:
                    ext = f".{arch_type}"
                    arch_path = os.path.join(target, f"alanator_backup{ext}")
                    if arch_type == "zip":
                        compress = zipfile.ZIP_DEFLATED
                        if level == "Очень быстро":
                            compress = zipfile.ZIP_STORED
                        with zipfile.ZipFile(arch_path, 'w', compress, allowZip64=True) as zf:
                            for i, f in enumerate(files):
                                zf.write(f, os.path.basename(f))
                                update_progress(i + 1, len(files))
                    elif arch_type == "7z":
                        temp_path = arch_path.replace('.7z', '.zip')
                        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
                            for i, f in enumerate(files):
                                zf.write(f, os.path.basename(f))
                                update_progress(i + 1, len(files))
                        if os.path.exists(temp_path):
                            os.rename(temp_path, arch_path)
                    elif arch_type == "tar":
                        import tarfile
                        with tarfile.open(arch_path, 'w') as tar:
                            for i, f in enumerate(files):
                                tar.add(f, arcname=os.path.basename(f))
                                update_progress(i + 1, len(files))
                        progress_bar.set(1)
                        progress_label.configure(text=tr("ready"))
                if delete_source:
                    for f in files:
                        try:
                            os.remove(f)
                        except:
                            pass
                win.after(0, lambda: messagebox.showinfo(tr("settings"), f"{tr('archive_created')}: {arch_path}"))
                win.after(0, win.destroy)
                win.after(0, self.refresh_files)
            except Exception as e:
                win.after(0, lambda: messagebox.showerror(tr("error"), str(e)))
        
        threading.Thread(target=archive_task, daemon=True).start()
    
    def browse_target(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, "end")
            entry.insert(0, folder)
    
    def extract_archive(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.7z *.aln *.tar")])
        if not file_path:
            return
        dest = filedialog.askdirectory(title=tr("choose_folder"))
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
            elif file_path.endswith('.7z'):
                import py7zr
                with py7zr.SevenZipFile(file_path, 'r') as zf:
                    zf.extractall(dest)
            elif file_path.endswith('.tar'):
                import tarfile
                with tarfile.open(file_path, 'r') as tar:
                    tar.extractall(dest)
            else:
                with zipfile.ZipFile(file_path, 'r') as zf:
                    zf.extractall(dest)
            messagebox.showinfo(tr("settings"), f"{tr('archive_extracted')}: {dest}")
        except Exception as e:
            messagebox.showerror(tr("error"), str(e))
    
    def secure_delete(self):
        files = filedialog.askopenfilenames(title="choose files to delete")
        if not files:
            return
        if not messagebox.askyesno(tr("secure_delete"), f"delete {len(files)} files?"):
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
                messagebox.showerror(tr("error"), str(e))
        self.refresh_files()
    
    def run_test(self):
        messagebox.showinfo(tr("test"), "OK")
    
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
    
    def create_main_area(self):
        main_panel = ctk.CTkFrame(self)
        main_panel.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        main_panel.grid_columnconfigure(0, weight=1)
        main_panel.grid_columnconfigure(1, weight=3)
        main_panel.grid_rowconfigure(0, weight=1)
        
        left_frame = ctk.CTkFrame(main_panel, width=280)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        left_frame.grid_propagate(False)
        
        ctk.CTkLabel(left_frame, text="Bookmarks", font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=5, pady=5)
        bookmarks = ["Computer's root", os.path.expanduser("~"), "Desktop", "Documents", "Downloads", "OneDrive"]
        for b in bookmarks:
            lbl = ctk.CTkLabel(left_frame, text=b, anchor="w", cursor="hand2")
            lbl.pack(fill="x", padx=15, pady=2)
            lbl.bind("<Button-1>", lambda e, path=b: self.quick_open(self.get_bookmark_path(path)))
        
        ctk.CTkLabel(left_frame, text="File system", font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=5, pady=(15,5))
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
        btn_back = ctk.CTkButton(addr_frame, text=tr("refresh"), width=60, command=self.go_back).grid(row=0, column=1, padx=2)
        btn_up = ctk.CTkButton(addr_frame, text="↑", width=60, command=self.go_up).grid(row=0, column=2, padx=2)
        
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
        
        if full_path.endswith(('.zip', '.aln')):
            menu.add_command(label=tr("view_archive"), command=lambda: self.view_archive_file(full_path))
            menu.add_command(label=tr("archive_manager"), command=lambda: self.view_archive_file(full_path))
            menu.add_separator()
        
        menu.add_command(label=tr("copy"), command=self.copy_file)
        menu.add_command(label=tr("cut"), command=self.cut_file)
        menu.add_command(label=tr("paste"), command=self.paste_file)
        menu.add_separator()
        menu.add_command(label=tr("rename"), command=self.rename_file)
        menu.add_command(label=tr("delete"), command=self.delete_file)
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
            info = f"folder: {self.current_path}\n"
            try:
                items = os.listdir(self.current_path)
                files = [f for f in items if os.path.isfile(os.path.join(self.current_path, f))]
                folders = [f for f in items if os.path.isdir(os.path.join(self.current_path, f))]
                info += f"files: {len(files)}\n"
                info += f"folders: {len(folders)}"
            except:
                info += "cannot get info"
            messagebox.showinfo(tr("properties"), info)
    
    def show_properties(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            full_path = os.path.join(self.current_path, name)
            if os.path.exists(full_path):
                info = f"name: {name}\n"
                info += f"path: {full_path}\n"
                if os.path.isfile(full_path):
                    info += f"size: {self.get_file_size(full_path)}"
                messagebox.showinfo(tr("properties"), info)
    
    def get_bookmark_path(self, name):
        if name == "Computer's root":
            return "Computer"
        elif name == "Desktop":
            return os.path.join(os.path.expanduser("~"), "Desktop")
        elif name == "Documents":
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
                    drives.append({"name": drive, "size": f"{total_gb:.1f} GB", "free": f"{free_gb:.1f} GB ({used_percent:.0f}% full)", "fs": "NTFS"})
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
            return "error"
        return ""
    
    def refresh_files(self):
        for item in self.tree_files.get_children():
            self.tree_files.delete(item)
        self.path_label.configure(text=f"path: {self.current_path}")
        try:
            if self.current_path == "Computer":
                for drive in self.get_drives_info():
                    self.tree_files.insert("", "end", values=(drive['name'], drive['size']))
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
            self.tree_files.insert("", "end", values=(f"{tr('error')}: {e}", ""))
    
    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        comp = self.tree.insert("", "end", text="My Computer", open=True)
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if os.path.exists(f"{letter}:\\"):
                self.tree.insert(comp, "end", text=f"{letter}:\\")
        user = self.tree.insert(comp, "end", text="User")
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
        elif text == "My Computer":
            self.current_path = "Computer"
            self.refresh_files()
        else:
            parts = []
            i = item
            while i:
                txt = self.tree.item(i, "text")
                if txt == "My Computer":
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
        elif name.endswith(('.zip', '.7z', '.aln', '.tar')):
            full_path = os.path.join(self.current_path, name)
            self.view_archive_file(full_path)
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
    
    def select_all_files(self):
        for item in self.tree_files.get_children():
            self.tree_files.selection_add(item)
    
    def copy_file(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            self.copy_path = os.path.join(self.current_path, name)
            messagebox.showinfo(tr("copy"), f"copied: {name}")
    
    def paste_file(self):
        if hasattr(self, 'copy_path') and self.copy_path and os.path.exists(self.copy_path):
            dest = self.current_path
            name = os.path.basename(self.copy_path)
            new_path = os.path.join(dest, name)
            if os.path.exists(new_path):
                if not messagebox.askyesno(tr("paste"), f"replace {name}?"):
                    return
            try:
                if os.path.isdir(self.copy_path):
                    shutil.copytree(self.copy_path, new_path)
                else:
                    shutil.copy2(self.copy_path, new_path)
                self.refresh_files()
            except Exception as e:
                messagebox.showerror(tr("error"), str(e))
    
    def delete_file(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            if messagebox.askyesno(tr("delete"), f"delete {name}?"):
                try:
                    full_path = os.path.join(self.current_path, name)
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                    self.refresh_files()
                except Exception as e:
                    messagebox.showerror(tr("error"), str(e))
    
    def rename_file(self):
        selection = self.tree_files.selection()
        if selection:
            old_name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            old_path = os.path.join(self.current_path, old_name)
            new_name = ctk.CTkInputDialog(text="new name:", title=tr("rename")).get_input()
            if new_name:
                try:
                    os.rename(old_path, os.path.join(self.current_path, new_name))
                    self.refresh_files()
                except Exception as e:
                    messagebox.showerror(tr("error"), str(e))
    
    def new_folder(self):
        name = ctk.CTkInputDialog(text=tr("new_folder") + ":", title=tr("new_folder")).get_input()
        if name:
            try:
                os.mkdir(os.path.join(self.current_path, name))
                self.refresh_files()
            except Exception as e:
                messagebox.showerror(tr("error"), str(e))
    
    def cut_file(self):
        selection = self.tree_files.selection()
        if selection:
            name = self.tree_files.item(selection[0], "values")[0].replace("📁 ", "").replace("📄 ", "")
            self.cut_path = os.path.join(self.current_path, name)
            messagebox.showinfo(tr("cut"), f"cut: {name}")

if __name__ == "__main__":
    app = AlanatorApp()
    app.mainloop()