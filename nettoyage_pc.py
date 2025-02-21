import os
import shutil
import locale
from pathlib import Path

def detect_language():
    lang = locale.getdefaultlocale()[0]
    if lang and lang.startswith("fr"):
        return "fr"
    return "en"

LANG = detect_language()

MESSAGES = {
    "fr": {
        "cleaning": "Nettoyage en cours...\n",
        "files_deleted": "✅ {name} : {count} fichiers supprimés ({size})",
        "no_files": "⚠️ {name} : Aucun fichier à supprimer.",
        "folder_missing": "⚠️ {name} : Dossier introuvable.",
        "windows_update_deleted": "✅ Cache Windows Update supprimé.",
        "windows_update_failed": "⚠️ Cache Windows Update : Aucun fichier à supprimer ou accès refusé.",
        "empty_recycle": "Voulez-vous vider la corbeille ? (y/n): ",
        "recycle_emptied": "✅ Corbeille vidée.",
        "recycle_error": "⚠️ Erreur lors du vidage de la corbeille : {error}",
        "recycle_not_emptied": "❌ Corbeille non vidée.",
        "finished": "\n◦ Nettoyage terminé ! {count} fichiers supprimés, {size} libérés.",
        "press_enter": "Appuyez sur Entrée pour fermer..."
    },
    "en": {
        "cleaning": "Cleaning in progress...\n",
        "files_deleted": "✅ {name}: {count} files deleted ({size})",
        "no_files": "⚠️ {name}: No files to delete.",
        "folder_missing": "⚠️ {name}: Folder not found.",
        "windows_update_deleted": "✅ Windows Update cache deleted.",
        "windows_update_failed": "⚠️ Windows Update cache: No files to delete or access denied.",
        "empty_recycle": "Do you want to empty the recycle bin? (y/n): ",
        "recycle_emptied": "✅ Recycle bin emptied.",
        "recycle_error": "⚠️ Error emptying the recycle bin: {error}",
        "recycle_not_emptied": "❌ Recycle bin not emptied.",
        "finished": "\n◦ Cleaning completed! {count} files deleted, {size} freed.",
        "press_enter": "Press Enter to close..."
    }
}

def nettoyer_dossier(dossier):
    total_taille = 0
    total_fichiers = 0
    
    if os.path.exists(dossier):
        for root, dirs, files in os.walk(dossier):
            for fichier in files:
                chemin_complet = os.path.join(root, fichier)
                try:
                    total_taille += os.path.getsize(chemin_complet)
                    total_fichiers += 1
                    os.remove(chemin_complet)
                except Exception:
                    pass
    return total_fichiers, total_taille

def nettoyer_cache_windows_update():
    dossier = r"C:\\Windows\\SoftwareDistribution\\Download"
    if os.path.exists(dossier):
        try:
            shutil.rmtree(dossier)
            return True
        except Exception:
            return False
    return False

def taille_formattee(taille):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if taille < 1024.0:
            return f"{taille:.2f} {unit}"
        taille /= 1024.0

dossiers = {
    "Temp": r"C:\\Windows\\Temp",
    "AppData Temp": Path.home() / "AppData" / "Local" / "Temp",
    "Prefetch": r"C:\\Windows\\Prefetch",
    "Windows Logs": r"C:\\Windows\\System32\\LogFiles",
    "Cache Windows Update": r"C:\\Windows\\SoftwareDistribution\\Download",
    "Miniatures": Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer",
}

print(MESSAGES[LANG]["cleaning"])
total_fichiers = 0
total_taille = 0

for nom, chemin in dossiers.items():
    if os.path.exists(chemin):
        fichiers_supprimes, taille_supprimee = nettoyer_dossier(chemin)
        total_fichiers += fichiers_supprimes
        total_taille += taille_supprimee
        if fichiers_supprimes > 0:
            print(MESSAGES[LANG]["files_deleted"].format(name=nom, count=fichiers_supprimes, size=taille_formattee(taille_supprimee)))
        else:
            print(MESSAGES[LANG]["no_files"].format(name=nom))
    else:
        print(MESSAGES[LANG]["folder_missing"].format(name=nom))

if nettoyer_cache_windows_update():
    print(MESSAGES[LANG]["windows_update_deleted"])
else:
    print(MESSAGES[LANG]["windows_update_failed"])

reponse = input(MESSAGES[LANG]["empty_recycle"])
if reponse.lower() == "y":
    try:
        os.system('powershell -command "Clear-RecycleBin -Force -Confirm:$false"')
        print(MESSAGES[LANG]["recycle_emptied"])
    except Exception as e:
        print(MESSAGES[LANG]["recycle_error"].format(error=e))
else:
    print(MESSAGES[LANG]["recycle_not_emptied"])

print(MESSAGES[LANG]["finished"].format(count=total_fichiers, size=taille_formattee(total_taille)))
input(MESSAGES[LANG]["press_enter"])