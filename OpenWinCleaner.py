import os
import shutil
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import subprocess
from pathlib import Path
import threading
import psutil

class SystemCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nettoyeur Système")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        self.space_saved = 0
        self.files_deleted = 0
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="white")
        self.style.configure("TCheckbutton", font=("Helvetica", 10))
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Nettoyeur Système Avancé", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        desc_label = ttk.Label(main_frame, text="Sélectionnez les options de nettoyage ci-dessous:", style="Header.TLabel")
        desc_label.pack(pady=5, anchor="w")
        
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        left_options = ttk.Frame(options_frame)
        left_options.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.temp_files_var = tk.BooleanVar(value=True)
        temp_cb = ttk.Checkbutton(left_options, text="Fichiers temporaires Windows", variable=self.temp_files_var)
        temp_cb.pack(anchor="w", pady=3)
        
        self.prefetch_var = tk.BooleanVar(value=True)
        prefetch_cb = ttk.Checkbutton(left_options, text="Fichiers Prefetch", variable=self.prefetch_var)
        prefetch_cb.pack(anchor="w", pady=3)
        
        self.recycle_bin_var = tk.BooleanVar(value=False)
        recycle_cb = ttk.Checkbutton(left_options, text="Corbeille", variable=self.recycle_bin_var)
        recycle_cb.pack(anchor="w", pady=3)
        
        self.browser_cache_var = tk.BooleanVar(value=False)
        browser_cb = ttk.Checkbutton(left_options, text="Cache des navigateurs", variable=self.browser_cache_var)
        browser_cb.pack(anchor="w", pady=3)
        
        right_options = ttk.Frame(options_frame)
        right_options.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        self.windows_logs_var = tk.BooleanVar(value=False)
        logs_cb = ttk.Checkbutton(right_options, text="Logs Windows", variable=self.windows_logs_var)
        logs_cb.pack(anchor="w", pady=3)
        
        self.update_cache_var = tk.BooleanVar(value=False)
        update_cb = ttk.Checkbutton(right_options, text="Cache Windows Update", variable=self.update_cache_var)
        update_cb.pack(anchor="w", pady=3)
        
        self.thumbnails_var = tk.BooleanVar(value=False)
        thumb_cb = ttk.Checkbutton(right_options, text="Cache des miniatures", variable=self.thumbnails_var)
        thumb_cb.pack(anchor="w", pady=3)
        
        self.recent_docs_var = tk.BooleanVar(value=False)
        recent_cb = ttk.Checkbutton(right_options, text="Documents récents", variable=self.recent_docs_var)
        recent_cb.pack(anchor="w", pady=3)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.analyze_button = ttk.Button(button_frame, text="Analyser", command=self.analyze)
        self.analyze_button.pack(side=tk.LEFT, padx=5)
        
        self.clean_button = ttk.Button(button_frame, text="Nettoyer", command=self.clean, state=tk.DISABLED)
        self.clean_button.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=10)
        
        results_frame = ttk.LabelFrame(main_frame, text="Résultats")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_text = tk.Text(results_frame, height=8, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_text.config(state=tk.DISABLED)
        
        self.status_var = tk.StringVar(value="Prêt")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_results(self, message):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def analyze(self):
        self.space_saved = 0
        self.files_deleted = 0
        self.progress_var.set(0)
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
        self.analyze_button.config(state=tk.DISABLED)
        self.status_var.set("Analyse en cours...")
        
        threading.Thread(target=self._analyze_thread, daemon=True).start()
    
    def _analyze_thread(self):
        paths_to_check = []
        size_info = {}
        
        if self.temp_files_var.get():
            temp_path = tempfile.gettempdir()
            paths_to_check.append(("Fichiers temporaires", temp_path))
            
        if self.prefetch_var.get():
            prefetch_path = r"C:\Windows\Prefetch"
            paths_to_check.append(("Prefetch", prefetch_path))
        
        if self.recycle_bin_var.get():
            recyclebin_path = os.path.join(os.environ.get('SystemDrive', 'C:'), '$Recycle.Bin')
            paths_to_check.append(("Corbeille", recyclebin_path))
        
        if self.browser_cache_var.get():
            chrome_cache = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Cache")
            firefox_cache = os.path.expanduser(r"~\AppData\Local\Mozilla\Firefox\Profiles")
            edge_cache = os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\Cache")
            
            paths_to_check.extend([
                ("Chrome Cache", chrome_cache),
                ("Firefox Cache", firefox_cache),
                ("Edge Cache", edge_cache)
            ])
        
        if self.windows_logs_var.get():
            logs_path = r"C:\Windows\Logs"
            paths_to_check.append(("Windows Logs", logs_path))
        
        if self.update_cache_var.get():
            update_cache = r"C:\Windows\SoftwareDistribution\Download"
            paths_to_check.append(("Windows Update Cache", update_cache))
        
        if self.thumbnails_var.get():
            thumbs_path = os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Explorer")
            paths_to_check.append(("Cache miniatures", thumbs_path))
        
        if self.recent_docs_var.get():
            recent_path = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Recent")
            paths_to_check.append(("Documents récents", recent_path))
        
        total_paths = len(paths_to_check)
        for idx, (name, path) in enumerate(paths_to_check):
            try:
                self.status_var.set(f"Analyse de {name}...")
                self.update_results(f"Analyse de {name} ({path})...")
                
                size = self.get_directory_size(path)
                size_info[name] = size
                
                readable_size = self.format_size(size)
                self.update_results(f"→ {name}: {readable_size}")
                
                progress = ((idx + 1) / total_paths) * 100
                self.progress_var.set(progress)
                
            except Exception as e:
                self.update_results(f"Erreur lors de l'analyse de {name}: {str(e)}")
        
        total_size = sum(size_info.values())
        self.update_results(f"\nEspace total pouvant être libéré: {self.format_size(total_size)}")
        
        self.clean_button.config(state=tk.NORMAL)
        self.analyze_button.config(state=tk.NORMAL)
        self.status_var.set("Analyse terminée")
    
    def clean(self):
        result = messagebox.askyesno("Confirmation", 
                                   "Êtes-vous sûr de vouloir nettoyer ces fichiers? Cette action est irréversible.")
        if not result:
            return
        
        self.analyze_button.config(state=tk.DISABLED)
        self.clean_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("Nettoyage en cours...")
        
        threading.Thread(target=self._clean_thread, daemon=True).start()
    
    def _clean_thread(self):
        paths_to_clean = []
        
        if self.temp_files_var.get():
            paths_to_clean.append(("Fichiers temporaires", tempfile.gettempdir()))
            
        if self.prefetch_var.get():
            paths_to_clean.append(("Fichiers Prefetch", r"C:\Windows\Prefetch"))
        
        if self.recycle_bin_var.get():
            self.update_results("Vidage de la Corbeille...")
            try:
                subprocess.run(["PowerShell", "-Command", "Clear-RecycleBin", "-Force", "-ErrorAction", "SilentlyContinue"], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.update_results("→ Corbeille vidée avec succès")
            except Exception as e:
                self.update_results(f"→ Erreur lors du vidage de la Corbeille: {str(e)}")
        
        if self.browser_cache_var.get():
            paths_to_clean.extend([
                ("Chrome Cache", os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\Cache")),
                ("Firefox Cache", os.path.expanduser(r"~\AppData\Local\Mozilla\Firefox\Profiles")),
                ("Edge Cache", os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\Cache"))
            ])
        
        if self.windows_logs_var.get():
            paths_to_clean.append(("Windows Logs", r"C:\Windows\Logs"))
        
        if self.update_cache_var.get():
            paths_to_clean.append(("Windows Update Cache", r"C:\Windows\SoftwareDistribution\Download"))
        
        if self.thumbnails_var.get():
            thumbs_db = os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Explorer\thumbcache_*.db")
            paths_to_clean.append(("Cache miniatures", thumbs_db))
        
        if self.recent_docs_var.get():
            paths_to_clean.append(("Documents récents", os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Recent")))
        
        total_paths = len(paths_to_clean)
        for idx, (name, path) in enumerate(paths_to_clean):
            try:
                if name == "Cache miniatures" and "*" in path:
                    import glob
                    files = glob.glob(path)
                    self.update_results(f"Nettoyage de {name}...")
                    for f in files:
                        try:
                            os.remove(f)
                            self.files_deleted += 1
                        except:
                            pass
                else:
                    self.status_var.set(f"Nettoyage de {name}...")
                    self.update_results(f"Nettoyage de {name}...")
                    deleted, saved = self.clean_directory(path)
                    self.files_deleted += deleted
                    self.space_saved += saved
                    self.update_results(f"→ {deleted} fichiers supprimés, {self.format_size(saved)} libérés")
                
                progress = ((idx + 1) / total_paths) * 100
                self.progress_var.set(progress)
                
            except Exception as e:
                self.update_results(f"Erreur lors du nettoyage de {name}: {str(e)}")
        
        self.update_results(f"\nNettoyage terminé :")
        self.update_results(f"→ {self.files_deleted} fichiers supprimés au total")
        self.update_results(f"→ {self.format_size(self.space_saved)} d'espace disque libéré")
        
        self.analyze_button.config(state=tk.NORMAL)
        self.clean_button.config(state=tk.DISABLED)
        self.status_var.set("Nettoyage terminé")
    
    def get_directory_size(self, path):
        """Calcule la taille d'un répertoire récursivement."""
        total_size = 0
        
        if "*" in path:
            import glob
            files = glob.glob(path)
            for f in files:
                if os.path.isfile(f):
                    try:
                        total_size += os.path.getsize(f)
                    except (OSError, FileNotFoundError):
                        continue
            return total_size
        
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        if os.path.islink(file_path):
                            continue
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        continue
        except (PermissionError, FileNotFoundError):
            pass
            
        return total_size
    
    def clean_directory(self, path):
        """Nettoie un répertoire récursivement."""
        files_deleted = 0
        space_saved = 0
        
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                os.remove(path)
                return 1, size
            
            for root, dirs, files in os.walk(path, topdown=False):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        if os.path.islink(file_path):
                            continue
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        files_deleted += 1
                        space_saved += size
                    except (OSError, PermissionError, FileNotFoundError):
                        continue
                        
                for dir in dirs:
                    try:
                        dir_path = os.path.join(root, dir)
                        if os.path.islink(dir_path):
                            continue
                        try:
                            os.rmdir(dir_path)
                        except OSError:
                            pass
                    except (OSError, PermissionError):
                        continue
        except (PermissionError, FileNotFoundError):
            pass
            
        return files_deleted, space_saved
    
    def format_size(self, size_bytes):
        """Convertit une taille en octets en format lisible."""
        if size_bytes == 0:
            return "0 B"
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        return f"{size_bytes:.2f} {size_names[i]}"


def get_system_info():
    """Récupère des informations sur le système."""
    info = {}
    
    info["cpu"] = psutil.cpu_percent(interval=1)
    
    mem = psutil.virtual_memory()
    info["memory_percent"] = mem.percent
    info["memory_used"] = mem.used
    info["memory_total"] = mem.total
    
    disk = psutil.disk_usage('/')
    info["disk_percent"] = disk.percent
    info["disk_used"] = disk.used
    info["disk_total"] = disk.total
    
    return info


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemCleanerApp(root)
    root.mainloop()
