"""
Gelişmiş Rastgele Şifre Üretici  v2.0
------------------------------------
• Uzunluk seç, karakter tiplerini belirle
• Güç göstergesi (zayıf - mükemmel)
• Panoya kopyala
• Log: txt  +  csv  (+ xlsx — isteğe bağlı)
• Koyu/açık tema arasında geçiş
@author  :  Batuhan
"""

import random, string, csv, os, datetime, sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyperclip                       # pip install pyperclip
try:
    import openpyxl                   # pip install openpyxl  (isteğe bağlı)
except ImportError:
    openpyxl = None

# ─────────────────────────────  Ayarlar  ───────────────────────────── #
DEFAULT_LEN = 12
LOG_FILE_TXT = "sifre_log.txt"
LOG_FILE_CSV = "sifre_log.csv"
LOG_FILE_XLSX = "sifre_log.xlsx"

# ─────────────────────────────  Tema  ──────────────────────────────── #
def koyu_tema(root):
    style.theme_use("clam")
    style.configure(".", background="#222", foreground="#EEE",
                    fieldbackground="#333", insertcolor="#fff")
    style.configure("TButton", background="#444")
    root["bg"] = "#222"

def acik_tema(root):
    style.theme_use("default")
    style.configure(".", background="#f0f0f0", foreground="#000")
    root["bg"] = "#f0f0f0"

# ─────────────────────────────  Güç hesabı  ────────────────────────── #
def sifre_gucu(pwd: str) -> tuple[int, str]:
    puan = 0
    uz = len(pwd)
    if uz >= 8:  puan += 1
    if uz >= 12: puan += 1
    if any(c.islower() for c in pwd): puan += 1
    if any(c.isupper() for c in pwd): puan += 1
    if any(c.isdigit() for c in pwd): puan += 1
    if any(c in string.punctuation for c in pwd): puan += 1
    etiket = ("Çok Zayıf", "Zayıf", "Orta", "İyi", "Güçlü", "Mükemmel")[puan]
    return puan, etiket

# ─────────────────────────────  Şifre üret  ────────────────────────── #
def uret():
    try:
        uzunluk = int(entry_len.get())
        if uzunluk < 6: raise ValueError
    except ValueError:
        messagebox.showerror("Hata", "Lütfen 6 veya daha uzun bir sayı gir.")
        return

    havuz = ""
    if var_l.get(): havuz += string.ascii_letters
    if var_d.get(): havuz += string.digits
    if var_s.get(): havuz += string.punctuation
    if not havuz:
        messagebox.showerror("Hata", "En az bir karakter tipi seçmelisin.")
        return

    pwd = ''.join(random.choice(havuz) for _ in range(uzunluk))
    entry_pwd_var.set(pwd)
    pyperclip.copy(pwd)

    # güç güncelle
    puan, etiket = sifre_gucu(pwd)
    bar["value"] = puan
    lbl_guc["text"] = f"Güç: {etiket}"

    # log kaydet
    if var_log.get():
        klasor = entry_dir.get() or os.getcwd()
        os.makedirs(klasor, exist_ok=True)
        tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # txt
        with open(os.path.join(klasor, LOG_FILE_TXT), "a", encoding="utf-8") as f:
            f.write(f"[{tarih}] {pwd} ({etiket})\n")
        # csv
        yenicsv = not os.path.exists(os.path.join(klasor, LOG_FILE_CSV))
        with open(os.path.join(klasor, LOG_FILE_CSV), "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if yenicsv: w.writerow(["tarih", "sifre", "guc"])
            w.writerow([tarih, pwd, etiket])
        # xlsx (isteğe bağlı)
        if openpyxl:
            path_x = os.path.join(klasor, LOG_FILE_XLSX)
            if os.path.exists(path_x):
                wb = openpyxl.load_workbook(path_x)
                ws = wb.active
            else:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.append(["tarih", "sifre", "guc"])
            ws.append([tarih, pwd, etiket])
            wb.save(path_x)

# ─────────────────────────────  Dosya seç  ────────────────────────── #
def klasor_sec():
    yol = filedialog.askdirectory()
    if yol:
        entry_dir.delete(0, tk.END); entry_dir.insert(0, yol)

# ─────────────────────────────  GUI  ──────────────────────────────── #
root = tk.Tk()
root.title("Gelişmiş Şifre Üretici")
if os.path.exists("app.ico"): root.iconbitmap("app.ico")

style = ttk.Style(root)
koyu_tema(root)          # varsayılan koyu tema

# Uzunluk
frame_len = ttk.Frame(root); frame_len.pack(pady=10)
ttk.Label(frame_len, text="Uzunluk:").pack(side=tk.LEFT, padx=5)
entry_len = ttk.Entry(frame_len, width=6); entry_len.pack(side=tk.LEFT)
entry_len.insert(0, str(DEFAULT_LEN))

# Karakter tipleri
frame_chk = ttk.Frame(root); frame_chk.pack(pady=5)
var_l = tk.BooleanVar(value=True)
var_d = tk.BooleanVar(value=True)
var_s = tk.BooleanVar(value=True)
ttk.Checkbutton(frame_chk, text="Harf",   variable=var_l).grid(row=0,column=0,padx=8)
ttk.Checkbutton(frame_chk, text="Rakam",  variable=var_d).grid(row=0,column=1,padx=8)
ttk.Checkbutton(frame_chk, text="Sembol", variable=var_s).grid(row=0,column=2,padx=8)

# Şifre kutusu
entry_pwd_var = tk.StringVar()
ttk.Entry(root, textvariable=entry_pwd_var, width=40,
          font=("Consolas", 12)).pack(pady=5)

# Güç göstergesi
bar = ttk.Progressbar(root, length=250, maximum=6); bar.pack(pady=(0,2))
lbl_guc = ttk.Label(root, text="Güç: -"); lbl_guc.pack()

# Log seçenekleri
frame_log = ttk.Frame(root); frame_log.pack(pady=5)
var_log = tk.BooleanVar(value=False)
ttk.Checkbutton(frame_log, text="Log dosyasına kaydet", variable=var_log).grid(row=0,column=0)
entry_dir = ttk.Entry(frame_log, width=30); entry_dir.grid(row=0,column=1,padx=5)
ttk.Button(frame_log, text="Klasör Seç…", command=klasor_sec).grid(row=0,column=2)

# Tema düğmesi
def tema_degistir():
    if btn_tema["text"] == "Açık Tema":
        koyu_tema(root); btn_tema["text"]="Açık Tema"
    else:
        acik_tema(root); btn_tema["text"]="Koyu Tema"
btn_tema = ttk.Button(root, text="Açık Tema", command=tema_degistir)
btn_tema.pack(pady=(2,8))

# ÜRET butonu
ttk.Button(root, text="Şifre Oluştur", command=uret).pack(ipadx=40, pady=5)

root.mainloop()
