"""
PetDex Desktop  🐾
Pet virtual yang hidup di desktop Windows kamu.

Gerakan otomatis: idle, jalan, lari, loncat, tidur, berpikir,
                  makan 🍎, main bola ⚽, main musik 🎵, bersiul ♪.
Interaksi      : drag (geser), dobel-klik (ngobrol), klik kanan (menu lengkap).
LLM            : bisa dihubungkan ke endpoint OpenAI-compatible (Hermes, dll) di Pengaturan.

Jalankan : klik dua kali "Jalankan_Pet.bat"  atau  `pythonw desktop_pet.py`
Tutup    : klik kanan pet -> Keluar semua
Butuh    : Python (Tkinter/json/urllib bawaan) - tanpa pip install.
"""
import ctypes
import json
import math
import os
import random
import threading
import time
import tkinter as tk
import urllib.parse
from ctypes import wintypes
from urllib import error as urlerror
from urllib import request as urlrequest

import pet_art

# --------------------------- konstanta -----------------------------------
TICK_MS = 70
TRANSPARENT = "#ff00ff"
GRID = pet_art.GRID

GRAVITY = 2.2
JUMP_V = 23.0

# ---- kata-kata (teks saja; ikon benda dimunculkan terpisah sebagai sprite) ----
PHRASES = {
    "idle": [
        "Hmm...", "Lagi ngapain nih?", "Jangan lupa commit", "Lanjut ngoding yuk",
        "Aku jagain ya", "Semangat!", "Istirahat bentar gpp", "Kerja bagus hari ini",
        "Mau minum dulu?", "Fokus... fokus...", "Kamu pasti bisa", "Sini main bareng",
        "Bug-nya kabur kok", "Tarik napas dulu~", "Dikit lagi selesai!",
    ],
    "happy": ["Yay!", "Hehe~", "Asyik!", "Hore!", "Senangnya~", "Kamu baik deh", "Wheee!"],
    "sleep": ["Zzz...", "Zzz", "...zzz", "*ngorok kecil*", "lima menit lagi..."],
    "eat": ["Nyam nyam~", "Laparrr...", "Enak banget!", "Makan dulu ya", "Kriuk kriuk", "Mau sesuap?"],
    "ball": ["Lempar sini!", "Wheee!", "Tangkap!", "Main bola yuk", "Gooal!", "Pantul pantul~"],
    "music": ["La la la~", "Lagu favoritku", "Dengerin ini~", "Asyik!", "Nge-jam dulu~"],
    "whistle": ["Fiuuh~", "*bersiul*", "Siul siul~", "Hari yang cerah"],
    "donut": ["Donat!", "Manis banget~", "Hap!", "Satu lagi boleh?", "Yumm"],
    "skate": ["Wuuush!", "Lihat aku meluncur~", "Kickflip!", "Ngebut nih!", "Asyiknya~"],
    "flower": ["Bunga buat kamu", "Cantiknya~", "Petik satu ah", "Wangi!", "Buat kamu deh"],
    "kite": ["Layang-layang!", "Tinggi sekali~", "Angin bagus nih", "Whee, terbang!", "Lihat ke atas!"],
    "umbrella": ["Hujan? Siap!", "Aman di bawah payung~", "Cuaca apa pun oke", "Teduh~"],
    "roll": ["Gulung gulung~", "Wheee berputar!", "Pusing tapi seru", "Roll roll roll!"],
    "butterfly": ["Tunggu, kupu-kupu!", "Kejar!", "Hampir dapat~", "Cantiknya terbang", "Sini sini~"],
}
THINK_FRAMES = ["Hmm", "Hmm .", "Hmm . .", "Hmm . . ."]

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, "pet_config.json")

SCALE_PRESETS = {"Kecil": 3, "Sedang": 5, "Besar": 7, "Jumbo": 9}

# jeda (idle) antar aktivitas, dalam "tick" (1 tick = TICK_MS ms)
GAP_RANGES = {
    "singkat": (6, 20),
    "medium": (32, 75),
    "lama": (90, 180),
}

DEFAULT_CONFIG = {
    "scale": 5,
    "activity_gap": "medium",
    "llm": {
        "base_url": "http://localhost:1234/v1",
        "model": "hermes",
        "api_key": "",
        "system_prompt": ("Kamu adalah Hermes, sebuah pet desktop yang ramah dan ringkas. "
                          "Jawab singkat (1-3 kalimat), santai, sesekali pakai emoji."),
        "temperature": 0.7,
        "max_tokens": 300,
    },
    "telegram": {
        "enabled": False,
        "bot_token": "",
    },
}

# --------------------------- prop sprites (item kecil) -------------------
# karakter -> warna; spasi = transparan
_PROPS = {
    "ball": ([
        "  ####  ",
        " ###### ",
        "##oo####",
        "##oo####",
        "########",
        "########",
        " ###### ",
        "  ####  ",
    ], {"#": "#e8554d", "o": "#ffffff"}),
    "apple": ([
        "   gg   ",
        "  hg    ",
        " rrrrr  ",
        "rrrrrrr ",
        "rrrhrrr ",
        "rrrrrrr ",
        " rrrrr  ",
        "  rrr   ",
    ], {"r": "#e8554d", "g": "#6fcf6f", "h": "#ff9b8a"}),
    "note": ([
        "    ##",
        "    ##",
        "    # ",
        "    # ",
        "    # ",
        "  ### ",
        " #### ",
        "  ##  ",
    ], {"#": "ACCENT"}),
    "donut": ([
        "  ####  ",
        " #oooo# ",
        "#oo  oo#",
        "#o    o#",
        "#oo  oo#",
        " #oooo# ",
        "  ####  ",
    ], {"#": "#ff8fc7", "o": "#c8884a"}),
    "board": ([
        "            ",
        " ########## ",
        " ########## ",
        "  O      O  ",
    ], {"#": "ACCENT", "O": "#2a2a2a"}),
    "flower": ([
        " w w  ",
        "wwyww ",
        " www  ",
        "  g   ",
        " Gg   ",
        "  g   ",
        "  g   ",
    ], {"w": "ACCENT", "y": "#ffd166", "g": "#4c9a5b", "G": "#6fcf6f"}),
    "kite": ([
        "   #   ",
        "  ###  ",
        " ##### ",
        "#######",
        " ##### ",
        "  ###  ",
        "   #   ",
        "   t   ",
        "  t    ",
        "   t   ",
    ], {"#": "ACCENT", "t": "#cfcfcf"}),
    "umbrella": ([
        "    #    ",
        "  #####  ",
        " ####### ",
        "#########",
        "    |    ",
        "    |    ",
        "    |    ",
        "   _|    ",
    ], {"#": "ACCENT", "|": "#8a5a2b", "_": "#8a5a2b"}),
    "butterfly": ([
        " ww ww ",
        "wwwwwww",
        "  wbw  ",
        "wwwwwww",
        " ww ww ",
    ], {"w": "ACCENT", "b": "#2a2a2a"}),
    # ---- makanan ----
    "icecream": ([
        " sss ",
        "sssss",
        "sssss",
        " sss ",
        " ccc ",
        "  c  ",
        "  c  ",
    ], {"s": "ACCENT", "c": "#d99a4e"}),
    "cake": ([
        "   r   ",
        " fffff ",
        "sssssss",
        "fffffff",
        "sssssss",
        "fffffff",
        "sssssss",
    ], {"r": "#e8554d", "f": "#ffe6a0", "s": "#c8884a"}),
    "cookie": ([
        " ##### ",
        "##c##c#",
        "#######",
        "#c###c#",
        "####c##",
        "##c####",
        " ##### ",
    ], {"#": "#d2a35a", "c": "#5a3a1a"}),
    "candy": ([
        "t  ###  t",
        "tt#####tt",
        "t  ###  t",
    ], {"t": "#ffd166", "#": "ACCENT"}),
    "banana": ([
        "      by",
        "    yyy ",
        "   yyy  ",
        " yyy    ",
        "yyy     ",
        " byy    ",
    ], {"y": "#ffd24a", "b": "#6a4a1a"}),
    "cherry": ([
        "    gg ",
        "   g g ",
        "  g  g ",
        "rr  rr ",
        "rrr rrr",
        " r   r ",
    ], {"r": "#e8554d", "g": "#4c9a5b"}),
    "watermelon": ([
        "  rrr  ",
        " rrrrr ",
        "rrkrrkr",
        "rrrrrrr",
        "wwwwwww",
        "ggggggg",
    ], {"r": "#f0566a", "k": "#2a2a2a", "w": "#ffd6d6", "g": "#4c9a5b"}),
    "strawberry": ([
        " g g ",
        "rrrrr",
        "rkrkr",
        "rrkrr",
        " rkr ",
        "  r  ",
    ], {"r": "#e8554d", "k": "#ffe066", "g": "#4c9a5b"}),
    "grapes": ([
        "  gg ",
        " ppp ",
        "ppppp",
        " ppp ",
        " pp  ",
        " p   ",
    ], {"p": "#8a6cf0", "g": "#4c9a5b"}),
    "egg": ([
        " wwww ",
        "wwwwww",
        "wwyyww",
        "wwyyww",
        "wwwwww",
        " wwww ",
    ], {"w": "#fbf6ee", "y": "#ffcf4d"}),
    # ---- minuman ----
    "coffee": ([
        "mmmmm ",
        "mcccmH",
        "mcccmH",
        "mcccm ",
        "mmmmm ",
        " mmm  ",
    ], {"m": "#e8edf5", "c": "#5a3a1e", "H": "#e8edf5"}),
    "boba": ([
        "  pp  ",
        " tttt ",
        " mccm ",
        " mccm ",
        " moom ",
        " moom ",
        " tttt ",
    ], {"p": "ACCENT", "t": "#c8884a", "m": "#cfe6f0", "c": "#c89a5a", "o": "#2a2a2a"}),
    "milk": ([
        "mmmmm",
        "mwwwm",
        "mwwwm",
        "mwwwm",
        "mwwwm",
        "mmmmm",
    ], {"m": "#cfe0ef", "w": "#ffffff"}),
    "soda": ([
        "  s  ",
        " ttt ",
        " ccc ",
        " ccc ",
        " ccc ",
        " ttt ",
    ], {"s": "#cfcfcf", "t": "#e8554d", "c": "#c84e6e"}),
    # ---- benda & hobi ----
    "book": ([
        "AAAAAAA",
        "AwwwwwA",
        "Aw###wA",
        "AwwwwwA",
        "Aw###wA",
        "AwwwwwA",
        "AAAAAAA",
    ], {"A": "ACCENT", "w": "#f5efdc", "#": "#caa066"}),
    "gift": ([
        " r    r ",
        " rr  rr ",
        "AArrrrAA",
        "AAArrAAA",
        "AAArrAAA",
        "AAArrAAA",
        "AAArrAAA",
    ], {"A": "ACCENT", "r": "#e8554d"}),
    "balloon": ([
        " AAAA ",
        "AAAAAA",
        "AAAAAA",
        "AAAAAA",
        " AAAA ",
        "  AA  ",
        "   t  ",
        "  t   ",
    ], {"A": "ACCENT", "t": "#9aa0ad"}),
    "star": ([
        "   #   ",
        "   #   ",
        "#######",
        " ##### ",
        " ##### ",
        " ## ## ",
        " #   # ",
    ], {"#": "#ffd54a"}),
    "heart": ([
        " ## ## ",
        "#######",
        "#######",
        " ##### ",
        "  ###  ",
        "   #   ",
    ], {"#": "#e8554d"}),
    "lightbulb": ([
        " #### ",
        "######",
        "######",
        "######",
        " #### ",
        " #bb# ",
        "  bb  ",
    ], {"#": "#ffe066", "b": "#8a8f99"}),
    "trophy": ([
        "ttttttt",
        "htttttth",
        "htttttth",
        " ttttt ",
        "  ttt  ",
        "   t   ",
        " bbbbb ",
    ], {"t": "ACCENT", "h": "ACCENT", "b": "#8a6a2a"}),
    "laptop": ([
        " sssssss ",
        " sCCCCCs ",
        " sCCCCCs ",
        " sssssss ",
        "bbbbbbbbb",
        " bbbbbbb ",
    ], {"s": "#454b59", "C": "ACCENT", "b": "#9aa0ad"}),
    # ---- olahraga ----
    "basketball": ([
        "  ####  ",
        " ###k## ",
        "####k###",
        "kkkkkkkk",
        "####k###",
        " ###k## ",
        "  ####  ",
    ], {"#": "#e8843a", "k": "#3a2410"}),
    # ---- alam & hewan ----
    "mushroom": ([
        " ##### ",
        "##d#d##",
        "#######",
        "#d###d#",
        " sssss ",
        "  sss  ",
        "  sss  ",
    ], {"#": "#e8554d", "d": "#ffffff", "s": "#f0e6cf"}),
    "leaf": ([
        "    ## ",
        "   ### ",
        "  ##v# ",
        " ##v## ",
        "##v### ",
        "#v###  ",
        " #     ",
    ], {"#": "#4c9a5b", "v": "#2e6b3a"}),
    "cloud": ([
        "   ###   ",
        " ####### ",
        "#########",
        "#########",
        " ####### ",
    ], {"#": "#eef3fb"}),
    "sun": ([
        "r  r  r",
        " ##### ",
        "r#####r",
        "r#####r",
        "r#####r",
        " ##### ",
        "r  r  r",
    ], {"#": "#ffd24a", "r": "#ffb454"}),
    "moon": ([
        " ####  ",
        "###    ",
        "##     ",
        "##     ",
        "##     ",
        "###    ",
        " ####  ",
    ], {"#": "#ffe27a"}),
    "snowflake": ([
        "   #   ",
        "# # # #",
        " ##### ",
        "###k###",
        " ##### ",
        "# # # #",
        "   #   ",
    ], {"#": "#bfe6ff", "k": "#8fd0f0"}),
    "bee": ([
        "w     w",
        "wyKyKyw",
        " yKyKy ",
        " yKyKy ",
        "  yyy  ",
    ], {"w": "#dfe8f5", "y": "#ffd24a", "K": "#2a2a2a"}),
    "bird": ([
        "  ###  ",
        " ##### ",
        "####o b",
        "###### ",
        " ####  ",
        "  ##   ",
    ], {"#": "ACCENT", "o": "#ffffff", "b": "#ff9f43"}),
    "fish": ([
        " ####  t",
        "###### t",
        "##o###tt",
        "###### t",
        " ####  t",
    ], {"#": "ACCENT", "o": "#ffffff", "t": "#ff9f6e"}),
    "parachute": ([
        "   #####   ",
        "  #######  ",
        " ######### ",
        "###########",
        "###########",
        "s    s    s",
        " s   s   s ",
        "  s  s  s  ",
        "   s s s   ",
        "    sss    ",
    ], {"#": "ACCENT", "s": "#cfcfcf"}),
}

# Tabel aktivitas (data-driven supaya gampang ditambah):
#   prop   = nama item overlay (atau None)
#   place  = cara menaruh item: front_feet/bounce/float_up/under/above/high/flit
#   motion = gerak pet: still/sway/glide/roll/chase
#   pose   = frame tubuh: idle/walk/tuck
ACT = {
    "eat":       {"prop": "apple",     "place": "front_feet", "motion": "still", "pose": "idle", "dur": (28, 50)},
    "donut":     {"prop": "donut",     "place": "front_feet", "motion": "still", "pose": "idle", "dur": (28, 50)},
    "ball":      {"prop": "ball",      "place": "bounce",     "motion": "still", "pose": "idle", "dur": (35, 60)},
    "music":     {"prop": "note",      "place": "float_up",   "motion": "sway",  "pose": "idle", "dur": (30, 55)},
    "whistle":   {"prop": "note",      "place": "float_up",   "motion": "still", "pose": "idle", "dur": (24, 45)},
    "skate":     {"prop": "board",     "place": "under",      "motion": "glide", "pose": "tuck", "dur": (45, 80)},
    "flower":    {"prop": "flower",    "place": "front_feet", "motion": "still", "pose": "idle", "dur": (28, 50)},
    "kite":      {"prop": "kite",      "place": "high",       "motion": "still", "pose": "idle", "dur": (40, 70)},
    "umbrella":  {"prop": "umbrella",  "place": "above",      "motion": "still", "pose": "idle", "dur": (30, 55)},
    "roll":      {"prop": None,        "place": None,         "motion": "roll",  "pose": "tuck", "dur": (18, 36)},
    "butterfly": {"prop": "butterfly", "place": "flit",       "motion": "chase", "pose": "walk", "dur": (40, 70)},
}

# ------------------------------------------------------------------------
# Aktivitas tambahan. Format: (nama, prop|None, place, motion, pose, frasa)
#   prop  : nama sprite di _PROPS (atau None = gerak murni tanpa item)
#   place : front_feet / above / high / float_up / flit / bounce
#   motion: still / sway / hop / spin / dance / pace / shiver / glide /
#           moonwalk / wander / zoomies / chase
# Kalimat = TEKS SAJA; ikon benda muncul sebagai sprite terpisah di luar teks.
# ------------------------------------------------------------------------
_SPECS = [
    # --- makanan ---
    ("makan_eskrim",   "icecream",   "front_feet", "still", "idle", "Es krim enak~"),
    ("makan_kue",      "cake",       "front_feet", "still", "idle", "Kue manis!"),
    ("makan_kukis",    "cookie",     "front_feet", "still", "idle", "Kukis kriuk~"),
    ("makan_permen",   "candy",      "front_feet", "hop",   "idle", "Permen!"),
    ("makan_pisang",   "banana",     "front_feet", "still", "idle", "Pisang sehat"),
    ("makan_ceri",     "cherry",     "front_feet", "still", "idle", "Ceri segar~"),
    ("makan_semangka", "watermelon", "front_feet", "still", "idle", "Semangka!"),
    ("makan_stroberi", "strawberry", "front_feet", "still", "idle", "Stroberi~"),
    ("makan_anggur",   "grapes",     "front_feet", "still", "idle", "Anggur!"),
    ("makan_telur",    "egg",        "front_feet", "still", "idle", "Telur ceplok~"),
    # --- minuman ---
    ("minum_kopi",     "coffee",     "front_feet", "still", "idle", "Ngopi dulu~"),
    ("minum_boba",     "boba",       "front_feet", "still", "idle", "Boba time!"),
    ("minum_susu",     "milk",       "front_feet", "still", "idle", "Susu biar kuat"),
    ("minum_soda",     "soda",       "front_feet", "still", "idle", "Soda dingin~"),
    # --- benda & hobi ---
    ("baca_buku",      "book",       "front_feet", "still", "idle", "Baca buku dulu"),
    ("buka_kado",      "gift",       "front_feet", "hop",   "idle", "Ada kado!"),
    ("main_balon",     "balloon",    "high",       "sway",  "idle", "Balon terbang~"),
    ("ngoding",        "laptop",     "front_feet", "still", "idle", "Ngoding terus~"),
    ("main_game",      "laptop",     "front_feet", "still", "idle", "Main game seru!"),
    ("dapat_ide",      "lightbulb",  "above",      "hop",   "idle", "Dapat ide!"),
    # --- olahraga & penghargaan ---
    ("basket",         "basketball", "bounce",     "still", "idle", "Slam dunk!"),
    ("juara",          "trophy",     "above",      "hop",   "idle", "Juara!"),
    # --- alam & hewan ---
    ("lihat_bintang",  "star",       "float_up",   "still", "idle", "Bintang berkilau~"),
    ("petik_jamur",    "mushroom",   "front_feet", "still", "idle", "Jamur mungil"),
    ("main_daun",      "leaf",       "float_up",   "still", "idle", "Daun gugur~"),
    ("lihat_awan",     "cloud",      "high",       "sway",  "idle", "Adem~"),
    ("berjemur",       "sun",        "high",       "still", "idle", "Cerah sekali!"),
    ("lihat_bulan",    "moon",       "high",       "still", "idle", "Malam tenang~"),
    ("main_salju",     "snowflake",  "float_up",   "still", "idle", "Turun salju~"),
    ("kejar_lebah",    "bee",        "flit",       "chase", "walk", "Awas lebah!"),
    ("kejar_burung",   "bird",       "flit",       "chase", "walk", "Kejar burung~"),
    ("kejar_ikan",     "fish",       "flit",       "chase", "walk", "Lihat ikan!"),
    # --- emosi ---
    ("jatuh_cinta",    "heart",      "float_up",   "sway",  "idle", "Sayang kamu~"),
    ("suka_banget",    "heart",      "above",      "hop",   "idle", "Suka ini!"),
    # --- gerak murni (tanpa item) ---
    ("berputar",       None, None, "spin",     "idle", "Muter muter~"),
    ("lompat_lompat",  None, None, "hop",      "tuck", "Hop hop hop!"),
    ("mondar_mandir",  None, None, "pace",     "walk", "Mikir sambil jalan~"),
    ("gemetar",        None, None, "shiver",   "idle", "Brrr dingin"),
    ("menari",         None, None, "dance",    "idle", "Nari yuk!"),
    ("moonwalk",       None, None, "moonwalk", "walk", "Moonwalk~"),
    ("jalan_santai",   None, None, "wander",   "walk", "Jalan-jalan dulu"),
    ("zoomies",        None, None, "zoomies",  "tuck", "Zoom zoom!"),
    ("lari_keliling",  None, None, "zoomies",  "tuck", "Lari keliling!"),
    ("peregangan",     None, None, "still",    "idle", "Stretching dulu~"),
    ("jingkrak",       None, None, "dance",    "tuck", "Yeay yeay!"),
    ("melambai",       None, None, "sway",     "idle", "Hai hai!"),
    ("pesta",          None, None, "dance",    "idle", "Pesta!"),
    ("tepuk_tangan",   None, None, "dance",    "idle", "Tepuk tangan!"),
]

for _name, _prop, _place, _motion, _pose, _phrase in _SPECS:
    ACT[_name] = {"prop": _prop, "place": _place, "motion": _motion,
                  "pose": _pose, "dur": (22, 48)}
    PHRASES[_name] = [_phrase]


def normalize_url(url):
    url = (url or "").strip()
    if url and not url.startswith(("http://", "https://")):
        url = "http://" + url
    return url


# --------------------------- config --------------------------------------
def load_config():
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg["scale"] = data.get("scale", cfg["scale"])
        cfg["activity_gap"] = data.get("activity_gap", cfg["activity_gap"])
        cfg["llm"].update(data.get("llm", {}))
        cfg["telegram"].update(data.get("telegram", {}))
    except (FileNotFoundError, ValueError):
        pass
    return cfg


def save_config():
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print("Gagal menyimpan config:", e)


CONFIG = load_config()
SCALE = int(CONFIG["scale"])
SPRITE = GRID * SCALE

# DPI awareness
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

root = tk.Tk()
root.withdraw()


def work_area():
    r = wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0)
    return r.left, r.top, r.right, r.bottom


def build_grid_image(grid):
    h, w = len(grid), len(grid[0])
    img = tk.PhotoImage(width=w, height=h)
    rows = ["{" + " ".join((c if c else TRANSPARENT) for c in row) + "}" for row in grid]
    img.put(" ".join(rows), to=(0, 0))
    return img.zoom(SCALE)


_prop_cache = {}
OUTLINE = "#241b2b"   # warna garis tepi, senada dengan outline tubuh pet


def _add_outline(grid, color=OUTLINE):
    """Bungkus sprite dengan garis tepi 1px (8 arah) agar gayanya senada pet."""
    h, w = len(grid), len(grid[0])
    H, W = h + 2, w + 2
    big = [[None] * W for _ in range(H)]
    for y in range(h):
        for x in range(w):
            big[y + 1][x + 1] = grid[y][x]
    out = [row[:] for row in big]
    nb = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    for y in range(H):
        for x in range(W):
            if big[y][x] is not None:
                continue
            for dx, dy in nb:
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and big[ny][nx] is not None:
                    out[y][x] = color
                    break
    return out


def prop_image(kind, color=None):
    key = (kind, SCALE, color)
    if key in _prop_cache:
        return _prop_cache[key]
    rows, cmap = _PROPS[kind]
    grid = []
    for row in rows:
        line = []
        for ch in row:
            c = cmap.get(ch)            # None untuk spasi/transparan
            if c == "ACCENT":
                c = color or "#ffd166"
            line.append(c)
        grid.append(line)
    img = build_grid_image(_add_outline(grid))  # tambah outline -> gaya menyatu
    _prop_cache[key] = img
    return img


# =========================================================================
#  LLM (OpenAI-compatible /chat/completions)
# =========================================================================
def llm_chat(messages):
    cfg = CONFIG["llm"]
    base = normalize_url(cfg["base_url"]).rstrip("/")
    if not base:
        return False, "Endpoint LLM belum diatur (buka Pengaturan)."
    body = json.dumps({
        "model": cfg["model"],
        "messages": messages,
        "temperature": cfg.get("temperature", 0.7),
        "max_tokens": cfg.get("max_tokens", 300),
        "stream": False,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if cfg.get("api_key"):
        headers["Authorization"] = "Bearer " + cfg["api_key"]

    # coba URL apa adanya; kalau gagal & belum ada '/v1', coba otomatis dengan '/v1'
    candidates = [base + "/chat/completions"]
    if not base.endswith("/v1"):
        candidates.append(base + "/v1/chat/completions")

    last_err = "Tidak bisa terhubung."
    for url in candidates:
        try:
            req = urlrequest.Request(url, data=body, headers=headers, method="POST")
            with urlrequest.urlopen(req, timeout=90) as resp:
                data = json.load(resp)
            return True, data["choices"][0]["message"]["content"].strip()
        except urlerror.HTTPError as e:
            last_err = "HTTP %s dari %s (cek model/URL)." % (e.code, url)
        except urlerror.URLError as e:
            last_err = "Tidak bisa terhubung ke %s (%s)." % (url, getattr(e, "reason", e))
        except (KeyError, ValueError):
            last_err = "Respons tidak dikenali (bukan format OpenAI-compatible?)."
        except Exception as e:
            last_err = "Error: %s" % e
    return False, last_err


# =========================================================================
#  Telegram bridge  (pet = otak bot Hermes; tanpa pip install)
#  Worker thread: getUpdates -> llm_chat -> sendMessage, lalu kirim event
#  ke main-thread lewat queue (drain) untuk ditampilkan jadi running text.
# =========================================================================
TG_API = "https://api.telegram.org/bot%s/%s"


def tg_call(token, method, params=None, timeout=35):
    url = TG_API % (token, method)
    data = urllib.parse.urlencode(params).encode() if params else None
    try:
        req = urlrequest.Request(url, data=data)
        with urlrequest.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urlerror.HTTPError as e:
        try:
            return json.load(e)
        except Exception:
            return {"ok": False, "description": "HTTP %s" % e.code}
    except Exception as e:
        return {"ok": False, "description": str(e)}


class TelegramBridge:
    instance = None

    def __init__(self, token):
        self.token = token
        self.offset = 0
        self.running = False
        self.thread = None
        self.events = []
        self.lock = threading.Lock()
        self.histories = {}
        self.bot_username = None
        self._last_status = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _push(self, ev):
        with self.lock:
            self.events.append(ev)

    def _status(self, text):
        # hindari spam: hanya kirim kalau status berubah
        if text == self._last_status:
            return
        self._last_status = text
        self._push({"type": "status", "text": text})

    def drain(self):
        with self.lock:
            evs, self.events = self.events, []
        return evs

    def _send(self, chat_id, text):
        tg_call(self.token, "sendMessage", {"chat_id": chat_id, "text": text}, timeout=20)

    def _loop(self):
        me = tg_call(self.token, "getMe", timeout=15)
        if not me.get("ok"):
            self._status("Token Telegram tidak valid: " + me.get("description", "?"))
            self.running = False
            return
        self.bot_username = me["result"].get("username")
        # Pastikan mode polling: hapus webhook jika ada (sumber konflik umum).
        tg_call(self.token, "deleteWebhook", {"drop_pending_updates": "false"}, timeout=15)
        self._status("Bot @%s aktif & mendengarkan" % self.bot_username)

        had_error = False
        while self.running:
            res = tg_call(self.token, "getUpdates",
                          {"offset": self.offset, "timeout": 25}, timeout=35)
            if not self.running:
                break
            if not res.get("ok"):
                desc = res.get("description", "error")
                if "Conflict" in desc or "409" in desc or "terminated by other" in desc:
                    self._status("Ada instance bot lain yang aktif - menunggu. "
                                 "Tutup agent/aplikasi pet lain untuk bot ini.")
                    time.sleep(8)
                else:
                    self._status("Telegram bermasalah: " + desc)
                    time.sleep(4)
                had_error = True
                continue
            if had_error:
                self._status("Tersambung lagi ke Telegram.")
                had_error = False
            for upd in res.get("result", []):
                self.offset = upd["update_id"] + 1
                msg = upd.get("message") or upd.get("edited_message")
                if not msg or not msg.get("text"):
                    continue
                text = msg["text"]
                chat_id = msg["chat"]["id"]
                who = msg.get("from", {}).get("first_name", "")
                if text.startswith("/start"):
                    self._send(chat_id, "Hai! 🐾 Ada yang bisa kubantu?")
                    continue
                hist = self.histories.setdefault(
                    chat_id, [{"role": "system", "content": CONFIG["llm"]["system_prompt"]}])
                hist.append({"role": "user", "content": text})
                ok, reply = llm_chat([hist[0]] + hist[1:][-11:])  # system + 11 pesan terakhir
                if ok:
                    hist.append({"role": "assistant", "content": reply})
                self._send(chat_id, reply if ok else ("⚠ " + reply))
                self._push({"type": "msg", "who": who, "q": text, "a": reply, "ok": ok})


_tg_lock_sock = None


def _acquire_tg_lock():
    """Pastikan hanya SATU proses pet yang menarik update Telegram (cegah konflik
    dari aplikasi yang tak sengaja dibuka dua kali). Socket auto-lepas saat keluar."""
    global _tg_lock_sock
    if _tg_lock_sock is not None:
        return True
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 49517))
        s.listen(1)
        _tg_lock_sock = s
        return True
    except OSError:
        s.close()
        return False


def apply_telegram():
    cfg = CONFIG["telegram"]
    b = TelegramBridge.instance
    if cfg.get("enabled") and cfg.get("bot_token"):
        if b and b.token == cfg["bot_token"] and b.running:
            return
        if not _acquire_tg_lock():
            if Pet.pets:
                Pet.pets[0].say("Telegram sudah dijalankan aplikasi pet lain")
            return
        if b:
            b.stop()
        TelegramBridge.instance = TelegramBridge(cfg["bot_token"])
        TelegramBridge.instance.start()
    elif b:
        b.stop()
        TelegramBridge.instance = None


def tg_pump():
    b = TelegramBridge.instance
    if b and Pet.pets:
        pet = Pet.pets[0]
        for ev in b.drain():
            if ev["type"] == "status":
                pet.say("[Telegram] " + ev["text"])
            else:
                who = ev.get("who") or "TG"
                pet.start_marquee("%s: %s" % (who, ev["a"]), loops=2)
    root.after(800, tg_pump)


# =========================================================================
#  Pet
# =========================================================================
class Pet:
    pets = []

    def __init__(self):
        Pet.pets.append(self)
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.wm_attributes("-transparentcolor", TRANSPARENT)
        self.win.config(bg=TRANSPARENT)
        self.label = tk.Label(self.win, bg=TRANSPARENT, bd=0, highlightthickness=0)
        self.label.pack()

        l, t, r, b = work_area()
        self.bounds = (l, r)
        self.floor = b - SPRITE
        self.x = float(random.randint(l, max(l, r - SPRITE)))
        self.y = float(self.floor)

        self.facing = random.choice((-1, 1))
        self.state = "idle"
        self.vy = 0.0
        self.vx = 0.0
        self.anim = 0
        self.timer = 0
        self.next_change = random.randint(15, 45)
        self.speed = 2

        self.bubble = self.bubble_label = None
        self.bubble_persist = False
        self.prop_win = self.prop_label = None
        self.prop_kind = None
        self.prop_imgref = None
        self.act = None              # nama aktivitas yang sedang berjalan
        self.sq_impulse = 0.0        # impuls squash & stretch (meluruh tiap tick)
        self._bf_pos = (0, 0)        # posisi kupu-kupu (untuk chase)
        self._bf_cx = 0.0
        self._bf_drift = 3
        self._pace_cx = 0.0          # titik tengah untuk gerak mondar-mandir

        # running text (teks berjalan untuk jawaban LLM)
        self.mq_win = self.mq_label = None
        self.mq_text = ""
        self.mq_pos = 0
        self.mq_loops = 0
        self.mq_active = False

        self.current_image = None
        self.llm_busy = False
        self._llm_result = None
        self.chat_win = None
        self.history = [{"role": "system", "content": CONFIG["llm"]["system_prompt"]}]

        self.new_look()
        self._bind()
        self.place()
        self.loop()

    # ----------------------- tampilan -----------------------------------
    def new_look(self, randomize=True):
        if randomize or not hasattr(self, "shape"):
            self.name, self.key, self.shape = pet_art.random_pet()
            self.palette = pet_art.PALETTES[self.key]
        self._img_cache = {}  # gambar dirender ulang sesuai pose + squash/stretch

    def _frame_kwargs(self):
        """Tentukan pose (argumen render) sesuai state & animasi saat ini."""
        a, st = self.anim, self.state
        kw = {"sparkle": self.shape.get("sparkle", False)}
        if st == "sleep":
            kw.update(bob=1, blink=True)
        elif st in ("jump", "fall", "parachute"):
            kw.update(leg=3, tail_up=True)
        elif st == "run":
            kw.update(leg=1 if a % 2 == 0 else 2, tail_up=True)
        elif st == "walk":
            if (a // 2) % 2 == 0:
                kw.update(bob=0, leg=1, tail_up=True)
            else:
                kw.update(bob=1, leg=2)
        elif st == "drag":
            kw.update(bob=1)
        elif st == "act":
            pose = ACT[self.act]["pose"]
            if pose == "tuck":
                kw.update(leg=3, tail_up=True)
            elif pose == "walk":
                if (a // 2) % 2 == 0:
                    kw.update(bob=0, leg=1, tail_up=True)
                else:
                    kw.update(bob=1, leg=2)
            else:
                kw.update(bob=(a // 4) % 2)
        elif st == "think":
            kw.update(bob=(a // 4) % 2)
        else:  # idle
            if a % 50 < 3:
                kw.update(blink=True)
            else:
                kw.update(bob=(a // 4) % 2)
        return kw

    def _deform(self):
        """Hitung faktor squash & stretch (sx, sy) untuk frame ini."""
        a, st = self.anim, self.state
        osc = 0.0
        if st == "idle":
            osc = 0.035 * math.sin(a * 0.11)              # napas halus
        elif st in ("walk", "run"):
            osc = 0.05 * math.sin(a * 0.6)                # pegas saat melangkah
        elif st == "jump":
            osc = 0.11 if self.vy < 0 else -0.06          # melar naik, mengkerut turun
        elif st == "parachute":
            osc = 0.05
        elif st == "act" and ACT[self.act]["motion"] == "hop":
            osc = 0.14 * math.sin(a * 0.5)
        total = self.sq_impulse + osc
        total = max(-0.30, min(0.18, total))
        # kuantisasi biar cache tidak meledak
        total = round(total / 0.03) * 0.03
        return (1 - 0.55 * total), (1 + total)

    def render_frame(self):
        kw = self._frame_kwargs()
        sx, sy = self._deform()
        face_right = self.facing >= 0
        key = (tuple(sorted(kw.items())), round(sx, 3), round(sy, 3), face_right)
        img = self._img_cache.get(key)
        if img is None:
            g = pet_art.render(self.shape, self.palette, sx=sx, sy=sy, **kw)
            if not face_right:
                g = pet_art.mirror(g)
            img = build_grid_image(g)
            if len(self._img_cache) > 256:   # batasi memori
                self._img_cache.clear()
            self._img_cache[key] = img
        self.current_image = img
        self.label.config(image=img)

    def place(self):
        self.win.geometry("%dx%d+%d+%d" % (SPRITE, SPRITE, int(self.x), int(self.y)))

    # ----------------------- loop perilaku ------------------------------
    def loop(self):
        try:
            self.tick()
        except tk.TclError:
            return
        self.win.after(TICK_MS, self.loop)

    def tick(self):
        self.anim += 1
        self.timer += 1
        self.sq_impulse *= 0.80          # impuls squash meluruh -> pegas balik
        l, r = self.bounds
        st = self.state

        if st == "idle":
            if self.timer >= self.next_change:
                self._choose_behavior()
        elif st in ("walk", "run"):
            self.x += self.speed * self.facing
            if self.x <= l:
                self.x = l; self.facing = 1
            elif self.x >= r - SPRITE:
                self.x = r - SPRITE; self.facing = -1
            if self.timer >= self.next_change:
                self._start_idle()
        elif st == "jump":
            self.vy += GRAVITY
            self.y += self.vy
            self.x += self.vx
            if self.x <= l:
                self.x = l; self.vx = abs(self.vx)
            elif self.x >= r - SPRITE:
                self.x = r - SPRITE; self.vx = -abs(self.vx)
            if self.y >= self.floor:
                self.y = self.floor; self.vy = self.vx = 0
                self.sq_impulse = -0.30          # mendarat -> squash
                self._start_idle()
        elif st == "fall":
            self.vy += GRAVITY
            self.y += self.vy
            if self.y >= self.floor:
                self.y = self.floor
                self.sq_impulse = min(-0.18, -0.04 * self.vy)  # makin cepat, makin squash
                self.vy = 0
                self._start_idle()
        elif st == "parachute":
            self.vy = min(self.vy + 0.35, 3.2)        # melayang turun pelan
            self.y += self.vy
            self.x += math.sin(self.anim * 0.18) * 1.6  # ayun pelan ke kiri-kanan
            self.x = min(max(self.x, l), r - SPRITE)
            self._place_prop("chute")
            if self.y >= self.floor:
                self.y = self.floor; self.vy = 0
                self.sq_impulse = -0.16          # mendarat lembut
                self.hide_prop()
                self._start_idle()
        elif st == "think":
            if (self.anim % 4) == 0:
                self._set_bubble(THINK_FRAMES[(self.anim // 4) % len(THINK_FRAMES)])
            if not self.llm_busy and self.timer >= self.next_change:
                self._start_idle()
        elif st == "sleep":
            if self.timer >= self.next_change:
                self._start_idle()
        elif st == "act":
            self._activity_step()

        self.render_frame()
        self.place()
        self._reposition_bubble()
        if self.mq_active:
            self._animate_marquee()

    def _choose_behavior(self):
        # ~60% berpindah tempat (biar lincah seperti dulu), ~40% aktivitas.
        if random.random() < 0.60:
            beh = random.choices(
                ["walk", "run", "jalan_santai", "zoomies", "lari_keliling",
                 "mondar_mandir", "jump", "skate"],
                weights=[26, 16, 12, 10, 8, 8, 8, 6])[0]
        else:
            beh = random.choices(
                ["think", "sleep"] + list(ACT.keys()),
                weights=[6, 4] + [3] * len(ACT))[0]
        if beh in ACT:
            self._start_act(beh)
        else:
            getattr(self, "_start_" + beh)()

    # ------ pemicu tiap gerakan ------
    def _start_idle(self):
        self._exit_activity()
        self.state = "idle"; self.timer = 0
        self.y = float(self.floor)  # pulihkan ke lantai (setelah hop/dance/jump)
        lo, hi = GAP_RANGES.get(CONFIG.get("activity_gap", "medium"), GAP_RANGES["medium"])
        self.next_change = random.randint(lo, hi)  # jeda antar aktivitas (dari Pengaturan)
        if random.random() < 0.15:
            self.say(random.choice(PHRASES["idle"]))

    def _start_walk(self):
        self._exit_activity()
        self.state = "walk"; self.timer = 0
        self.facing = random.choice((-1, 1))
        self.speed = random.choice((2, 3))
        self.next_change = random.randint(25, 70)

    def _start_run(self):
        self._exit_activity()
        self.state = "run"; self.timer = 0
        self.facing = random.choice((-1, 1))
        self.speed = random.choice((6, 7))
        self.next_change = random.randint(18, 40)

    def _start_jump(self):
        self._exit_activity()
        self.state = "jump"; self.timer = 0
        self.vy = -JUMP_V
        self.vx = self.facing * random.choice((2, 3))
        self.sq_impulse = 0.26          # melar ke atas saat melompat

    def _start_think(self):
        self._exit_activity()
        self.state = "think"; self.timer = 0
        self.next_change = random.randint(20, 40)
        self._set_bubble(THINK_FRAMES[0], persist=True)

    def _start_sleep(self):
        self._exit_activity()
        self.state = "sleep"; self.timer = 0
        self.next_change = random.randint(60, 140)
        self.say(random.choice(PHRASES["sleep"]))

    def _start_act(self, name):
        self._exit_activity()
        self.act = name
        d = ACT[name]
        self.state = "act"
        self.timer = 0
        self.facing = random.choice((-1, 1))
        self.next_change = random.randint(*d["dur"])
        m = d["motion"]
        if m in ("glide", "moonwalk"):
            self.speed = random.choice((4, 5))
        elif m in ("roll", "zoomies"):
            self.speed = random.choice((6, 7))
        else:
            self.speed = random.choice((2, 3))
        if m == "chase":
            self._bf_cx = float(self.x)
            self._bf_drift = random.choice((-3, 3))
        if m == "pace":
            self._pace_cx = float(self.x)
        if d.get("prop"):
            self.show_prop(d["prop"])
            self._place_prop(d["place"])
        self.say(random.choice(PHRASES.get(name, PHRASES["idle"])))

    def _activity_step(self):
        d = ACT[self.act]
        l, r = self.bounds
        a = self.anim
        m = d["motion"]
        if m in ("glide", "roll"):
            self.x += self.speed * self.facing
            if self.x <= l:
                self.x = l; self.facing = 1
            elif self.x >= r - SPRITE:
                self.x = r - SPRITE; self.facing = -1
        elif m == "moonwalk":
            self.x += self.speed * (-self.facing)  # bergerak mundur
            if self.x <= l:
                self.x = l; self.facing = -1
            elif self.x >= r - SPRITE:
                self.x = r - SPRITE; self.facing = 1
        elif m in ("wander", "zoomies"):
            self.x += self.speed * self.facing
            if self.x <= l:
                self.x = l; self.facing = 1
            elif self.x >= r - SPRITE:
                self.x = r - SPRITE; self.facing = -1
            if random.random() < (0.04 if m == "wander" else 0.10):
                self.facing *= -1
        elif m == "pace":
            self.x += self.speed * self.facing
            if self.x > self._pace_cx + SPRITE:
                self.facing = -1
            elif self.x < self._pace_cx - SPRITE:
                self.facing = 1
            self.x = min(max(self.x, l), r - SPRITE)
        elif m == "sway":
            self.x += math.sin(a * 0.3) * 1.5
            self.x = min(max(self.x, l), r - SPRITE)
        elif m == "shiver":
            self.x = min(max(self.x + random.choice((-1, 0, 1)), l), r - SPRITE)
        elif m == "spin":
            if a % 3 == 0:
                self.facing *= -1
        elif m == "dance":
            if a % 4 == 0:
                self.facing *= -1
            self.y = self.floor - abs(math.sin(a * 0.6)) * SPRITE * 0.12
        elif m == "hop":
            self.y = self.floor - abs(math.sin(a * 0.5)) * SPRITE * 0.28
        elif m == "chase":
            self._bf_cx += self._bf_drift
            if self._bf_cx <= l:
                self._bf_cx = l; self._bf_drift = abs(self._bf_drift)
            elif self._bf_cx >= r - SPRITE:
                self._bf_cx = r - SPRITE; self._bf_drift = -abs(self._bf_drift)
            bx = self._bf_cx + math.sin(a * 0.18) * SPRITE * 1.2
            by = self.y + SPRITE * 0.05 + math.sin(a * 0.33) * SPRITE * 0.25
            self._bf_pos = (bx, by)
            target = bx - SPRITE * 0.4
            if target > self.x + 3:
                self.x = min(self.x + 3, r - SPRITE); self.facing = 1
            elif target < self.x - 3:
                self.x = max(self.x - 3, l); self.facing = -1
        # "still" tidak bergerak

        if d.get("prop"):
            self._place_prop(d["place"])
        if self.timer % 22 == 0:
            self.say(random.choice(PHRASES.get(self.act, PHRASES["idle"])))
        if self.timer >= self.next_change:
            self._start_idle()

    def _exit_activity(self):
        self.act = None
        self.hide_prop()
        if self.bubble_persist:
            self._kill_bubble()

    # ----------------------- prop overlay (sprite pixel-art) ------------
    def show_prop(self, kind):
        self.hide_prop()
        self.prop_kind = kind
        w = tk.Toplevel(root)
        w.overrideredirect(True)
        w.wm_attributes("-topmost", True)
        w.wm_attributes("-transparentcolor", TRANSPARENT)
        w.config(bg=TRANSPARENT)
        self.prop_label = tk.Label(w, bg=TRANSPARENT, bd=0, highlightthickness=0)
        self.prop_label.pack()
        self.prop_win = w

    def _place_prop(self, place):
        if not self.prop_win or not place:
            return
        a = self.anim
        img = prop_image(self.prop_kind, self.palette["accent"])
        self.prop_label.config(image=img)
        self.prop_imgref = img
        pw, ph = img.width(), img.height()
        fr = self.facing >= 0
        if place == "front_feet":
            x = self.x + SPRITE * 0.66 if fr else self.x + SPRITE * 0.34 - pw
            y = self.y + SPRITE - ph - SPRITE * 0.06
        elif place == "bounce":
            bounce = int(abs(math.sin(a * 0.45)) * SPRITE * 0.5)
            x = self.x + SPRITE * 0.70 if fr else self.x + SPRITE * 0.30 - pw
            y = self.y + SPRITE - ph - bounce
        elif place == "float_up":
            rise = int((a * 2) % (SPRITE * 0.7))
            x = self.x + SPRITE * 0.70 if fr else self.x + SPRITE * 0.30 - pw
            y = self.y + SPRITE * 0.10 - rise
        elif place == "under":
            x = self.x + SPRITE * 0.5 - pw / 2
            y = self.y + SPRITE - ph + SPRITE * 0.02
        elif place == "above":
            x = self.x + SPRITE * 0.5 - pw / 2
            y = self.y - ph + SPRITE * 0.12
        elif place == "high":
            sway = int(math.sin(a * 0.12) * SPRITE * 0.3)
            x = self.x + SPRITE * 0.5 - pw / 2 + sway
            y = self.y - ph - SPRITE * 0.15
        elif place == "flit":
            x, y = self._bf_pos
        elif place == "chute":
            x = self.x + SPRITE * 0.5 - pw / 2
            y = self.y - ph + SPRITE * 0.22   # kanopi di atas, tali menyentuh kepala pet
        else:
            x, y = self.x, self.y
        try:
            self.prop_win.geometry("+%d+%d" % (int(x), int(y)))
        except tk.TclError:
            self.prop_win = self.prop_label = None

    def hide_prop(self):
        if self.prop_win:
            try:
                self.prop_win.destroy()
            except tk.TclError:
                pass
        self.prop_win = self.prop_label = None
        self.prop_kind = None

    # ----------------------- interaksi mouse ----------------------------
    def _bind(self):
        self.label.bind("<Button-1>", self._on_press)
        self.label.bind("<B1-Motion>", self._on_drag)
        self.label.bind("<ButtonRelease-1>", self._on_release)
        self.label.bind("<Double-Button-1>", self._on_double)
        self.label.bind("<Button-3>", self._on_menu)

    def _on_press(self, e):
        self._exit_activity()
        self.stop_marquee()
        self._dx = e.x_root - self.x
        self._dy = e.y_root - self.y
        self.state = "drag"; self.vy = 0
        self._kill_bubble()

    def _on_drag(self, e):
        self.x = e.x_root - self._dx
        self.y = e.y_root - self._dy
        self.place()

    def _on_release(self, e):
        if self.state == "drag":
            if (self.floor - self.y) > SPRITE * 1.2:   # dijatuhkan dari tinggi -> parasut
                self._start_parachute()
            else:
                self.state = "fall"; self.vy = 0

    def _start_parachute(self):
        self._exit_activity()
        self.state = "parachute"
        self.vy = 0.5
        self.show_prop("parachute")
        self._place_prop("chute")
        self.say(random.choice(["Wheee~", "Meluncur pelan~", "Parasut terbuka!", "Aman mendarat~"]))

    def _on_double(self, e):
        self.open_chat()

    def _on_menu(self, e):
        m = tk.Menu(root, tearoff=0)
        m.add_command(label="💬  Ngobrol dengan %s" % self.name, command=self.open_chat)
        m.add_separator()
        size_menu = tk.Menu(m, tearoff=0)
        for label, val in SCALE_PRESETS.items():
            size_menu.add_radiobutton(
                label="%s (%dpx)" % (label, GRID * val), value=val,
                variable=_scale_var, command=lambda v=val: apply_scale(v))
        m.add_cascade(label="📏  Ukuran pet", menu=size_menu)
        m.add_command(label="🎲  Ganti tampilan",
                      command=lambda: (self.new_look(True), self.render_frame()))
        m.add_command(label="🎬  Aksi acak (%d gerakan)" % len(ACT),
                      command=lambda: self._start_act(random.choice(list(ACT.keys()))))
        lbl = "☀  Bangunkan" if self.state == "sleep" else "💤  Tidurkan"
        m.add_command(label=lbl, command=self.toggle_sleep)
        m.add_separator()
        m.add_command(label="➕  Tambah pet", command=add_pet)
        m.add_command(label="⚙  Pengaturan...", command=open_settings)
        tg_on = bool(TelegramBridge.instance and TelegramBridge.instance.running)
        m.add_command(label=("📡  Telegram: ON (matikan)" if tg_on else "📡  Telegram: OFF (nyalakan)"),
                      command=toggle_telegram)
        m.add_separator()
        m.add_command(label="🗑  Hapus pet ini", command=self.remove)
        m.add_command(label="🚪  Keluar semua", command=quit_all)
        m.tk_popup(e.x_root, e.y_root)

    def toggle_sleep(self):
        if self.state == "sleep":
            self._start_idle()
        else:
            self._start_sleep()

    # ----------------------- balon teks ---------------------------------
    def _ensure_bubble(self):
        if self.bubble:
            return
        b = tk.Toplevel(root)
        b.overrideredirect(True)
        b.wm_attributes("-topmost", True)
        b.config(bg="#1c2130", highlightbackground="#7c8cff", highlightthickness=1)
        lbl = tk.Label(b, text="", bg="#1c2130", fg="#e7ecf5", justify="left",
                       font=("Segoe UI", 10), padx=8, pady=4, wraplength=240)
        lbl.pack()
        self.bubble, self.bubble_label = b, lbl

    def _set_bubble(self, text, persist=True):
        self._ensure_bubble()
        self.bubble_persist = persist
        self.bubble_label.config(text=text)
        self._reposition_bubble()

    def say(self, text):
        if self.mq_active:  # jangan ganggu teks berjalan
            return
        self._set_bubble(text, persist=False)
        self.win.after(2400, lambda: None if self.bubble_persist else self._kill_bubble())

    def _reposition_bubble(self):
        if not self.bubble:
            return
        try:
            self.bubble.update_idletasks()
            bw = self.bubble.winfo_width()
            bx = int(self.x + SPRITE / 2 - bw / 2)
            by = int(self.y - self.bubble.winfo_height() - 6)
            self.bubble.geometry("+%d+%d" % (bx, by))
        except tk.TclError:
            self.bubble = self.bubble_label = None

    def _kill_bubble(self):
        if self.bubble:
            try:
                self.bubble.destroy()
            except tk.TclError:
                pass
        self.bubble = self.bubble_label = None
        self.bubble_persist = False

    # ----------------------- running text (marquee) ---------------------
    MQ_CHARS = 22  # lebar jendela teks berjalan (karakter)

    def start_marquee(self, text, loops=2):
        text = " ".join(text.split())  # rapikan spasi/baris
        self._kill_bubble()
        if not self.mq_win:
            w = tk.Toplevel(root)
            w.overrideredirect(True)
            w.wm_attributes("-topmost", True)
            w.config(bg="#11141d", highlightbackground="#5fd6a4", highlightthickness=1)
            self.mq_label = tk.Label(w, text="", bg="#11141d", fg="#5fd6a4",
                                     font=("Consolas", 11), anchor="w", width=self.MQ_CHARS,
                                     padx=8, pady=4)
            self.mq_label.pack()
            self.mq_win = w
        pad = " " * self.MQ_CHARS
        self.mq_text = pad + text + pad
        self.mq_pos = 0
        self.mq_loops = 0
        self.mq_max_loops = loops
        self.mq_active = True
        self._animate_marquee()

    def _animate_marquee(self):
        if not self.mq_active or not self.mq_win:
            return
        span = max(1, len(self.mq_text) - self.MQ_CHARS)
        view = self.mq_text[self.mq_pos:self.mq_pos + self.MQ_CHARS]
        try:
            self.mq_label.config(text=view)
            self.mq_win.update_idletasks()
            mw = self.mq_win.winfo_width()
            bx = int(self.x + SPRITE / 2 - mw / 2)
            by = int(self.y - self.mq_win.winfo_height() - 6)
            self.mq_win.geometry("+%d+%d" % (bx, by))
        except tk.TclError:
            self.mq_win = self.mq_label = None
            self.mq_active = False
            return
        self.mq_pos += 1
        if self.mq_pos >= span:
            self.mq_pos = 0
            self.mq_loops += 1
            if self.mq_loops >= self.mq_max_loops:
                self.stop_marquee()

    def stop_marquee(self):
        self.mq_active = False
        if self.mq_win:
            try:
                self.mq_win.destroy()
            except tk.TclError:
                pass
        self.mq_win = self.mq_label = None

    # ----------------------- chat / LLM ---------------------------------
    def open_chat(self):
        if self.chat_win and tk.Toplevel.winfo_exists(self.chat_win):
            self.chat_win.deiconify(); self.chat_win.lift(); self.entry.focus_set()
            return
        w = tk.Toplevel(root)
        self.chat_win = w
        w.title("💬 %s" % self.name)
        w.configure(bg="#11141d")
        w.geometry("380x460")
        w.minsize(320, 320)
        w.attributes("-topmost", True)

        # --- header (atas) ---
        tk.Label(w, text="Ngobrol dengan %s" % self.name, bg="#11141d", fg="#e7ecf5",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(w, text="→ %s · %s" % (normalize_url(CONFIG["llm"]["base_url"]), CONFIG["llm"]["model"]),
                 bg="#11141d", fg="#8c97b0", font=("Segoe UI", 8)).pack(anchor="w", padx=10)

        # --- kolom input (BAWAH) dipasang DULU supaya tidak pernah terdorong keluar ---
        bar = tk.Frame(w, bg="#11141d")
        bar.pack(side="bottom", fill="x", padx=10, pady=10)
        self.send_btn = tk.Button(bar, text="Kirim", bg="#7c8cff", fg="#0c0e14", bd=0,
                                  font=("Segoe UI", 10, "bold"), padx=14, command=self._send_chat)
        self.send_btn.pack(side="right")
        self.entry = tk.Entry(bar, bg="#1c2130", fg="#e7ecf5", bd=0,
                              insertbackground="#e7ecf5", font=("Segoe UI", 10))
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self._send_chat())

        # --- area log (mengisi sisa ruang di tengah) ---
        self.log = tk.Text(w, bg="#0c0e14", fg="#e7ecf5", bd=0, wrap="word",
                           font=("Segoe UI", 10), padx=8, pady=8, height=8,
                           insertbackground="#e7ecf5")
        self.log.pack(side="top", fill="both", expand=True, padx=10, pady=(8, 0))
        self.log.tag_config("me", foreground="#7c8cff")
        self.log.tag_config("pet", foreground="#5fd6a4")
        self.log.tag_config("err", foreground="#ff8f8f")
        self.log.config(state="disabled")

        self._log_line("pet", "%s: Hai! Tanya apa saja ya 🐾" % self.name)
        w.lift()
        w.after(50, lambda: (w.focus_force(), self.entry.focus_set()))

    def _log_line(self, tag, text):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def _send_chat(self):
        if self.llm_busy:
            return
        msg = self.entry.get().strip()
        if not msg:
            return
        self.entry.delete(0, "end")
        self._log_line("me", "Kamu: " + msg)
        self.history.append({"role": "user", "content": msg})

        self.llm_busy = True
        self.send_btn.config(state="disabled", text="...")
        self._start_think()
        self._set_bubble(THINK_FRAMES[0], persist=True)

        msgs = list(self.history)
        self._llm_result = None
        threading.Thread(target=self._llm_worker, args=(msgs,), daemon=True).start()
        self.win.after(150, self._poll_llm)

    def _llm_worker(self, msgs):
        # Worker TIDAK memanggil Tk; hasil diambil main-thread via _poll_llm.
        self._llm_result = llm_chat(msgs)

    def _poll_llm(self):
        if self._llm_result is None:
            try:
                self.win.after(150, self._poll_llm)
            except tk.TclError:
                pass
            return
        ok, text = self._llm_result
        self._llm_result = None
        self._on_llm_reply(ok, text)

    def _on_llm_reply(self, ok, text):
        self.llm_busy = False
        try:
            self.send_btn.config(state="normal", text="Kirim")
        except (tk.TclError, AttributeError):
            pass
        self._start_idle()
        if ok:
            self.history.append({"role": "assistant", "content": text})
            self._safe_log("pet", "%s: %s" % (self.name, text))
            self._kill_bubble()
            # jawaban tampil sebagai TEKS BERJALAN di atas pet
            self.start_marquee(text, loops=2)
        else:
            self._safe_log("err", "⚠ " + text)
            self._kill_bubble()
            self.say("⚠ gagal terhubung")

    def _safe_log(self, tag, text):
        if self.chat_win and tk.Toplevel.winfo_exists(self.chat_win):
            self._log_line(tag, text)

    # ----------------------- hapus / keluar -----------------------------
    def remove(self):
        self.hide_prop()
        self.stop_marquee()
        self._kill_bubble()
        for w in (self.chat_win, self.win):
            try:
                if w:
                    w.destroy()
            except tk.TclError:
                pass
        if self in Pet.pets:
            Pet.pets.remove(self)
        if not Pet.pets:
            quit_all()


# =========================================================================
#  fungsi global: scale, settings, tambah pet, keluar
# =========================================================================
def apply_scale(n):
    global SCALE, SPRITE
    SCALE = int(n)
    SPRITE = GRID * SCALE
    CONFIG["scale"] = SCALE
    _scale_var.set(SCALE)
    save_config()
    l, t, r, b = work_area()
    for p in Pet.pets:
        p.bounds = (l, r)
        p.floor = b - SPRITE
        p.x = min(max(p.x, l), max(l, r - SPRITE))
        p.y = min(p.y, p.floor)
        p.new_look(randomize=False)
        p.render_frame()
        p.place()


def open_settings():
    w = tk.Toplevel(root)
    w.title("⚙ Pengaturan PetDex")
    w.configure(bg="#11141d")
    w.geometry("420x500")
    w.attributes("-topmost", True)
    pad = {"padx": 14, "pady": 4}

    def header(txt):
        tk.Label(w, text=txt, bg="#11141d", fg="#7c8cff",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 2))

    def field(label, value, show=None):
        tk.Label(w, text=label, bg="#11141d", fg="#e7ecf5",
                 font=("Segoe UI", 9)).pack(anchor="w", **pad)
        var = tk.StringVar(value=value)
        tk.Entry(w, textvariable=var, bg="#1c2130", fg="#e7ecf5", bd=0,
                 insertbackground="#e7ecf5", show=show,
                 font=("Segoe UI", 10)).pack(fill="x", padx=14, ipady=5)
        return var

    header("Ukuran pet")
    scale_var = tk.IntVar(value=SCALE)
    sframe = tk.Frame(w, bg="#11141d"); sframe.pack(fill="x", padx=14)
    tk.Scale(sframe, from_=3, to=10, orient="horizontal", variable=scale_var,
             bg="#11141d", fg="#e7ecf5", troughcolor="#1c2130", highlightthickness=0,
             length=260).pack(side="left")
    tk.Label(sframe, text="(px = nilai × 24)", bg="#11141d", fg="#8c97b0",
             font=("Segoe UI", 8)).pack(side="left", padx=8)

    header("Jeda antar aktivitas")
    gap_var = tk.StringVar(value=CONFIG.get("activity_gap", "medium"))
    gframe = tk.Frame(w, bg="#11141d"); gframe.pack(fill="x", padx=12)
    for val, lbl in (("singkat", "Singkat"), ("medium", "Medium"), ("lama", "Lama")):
        tk.Radiobutton(gframe, text=lbl, value=val, variable=gap_var,
                       bg="#11141d", fg="#e7ecf5", selectcolor="#1c2130",
                       activebackground="#11141d", activeforeground="#e7ecf5",
                       font=("Segoe UI", 9)).pack(side="left", padx=(0, 12))

    header("Koneksi LLM (OpenAI-compatible)")
    url_var = field("Base URL (mis. http://localhost:1234/v1)", CONFIG["llm"]["base_url"])
    model_var = field("Model", CONFIG["llm"]["model"])
    key_var = field("API Key (kosongkan jika lokal)", CONFIG["llm"]["api_key"], show="•")

    tk.Label(w, text="System prompt", bg="#11141d", fg="#e7ecf5",
             font=("Segoe UI", 9)).pack(anchor="w", **pad)
    sys_text = tk.Text(w, height=3, bg="#1c2130", fg="#e7ecf5", bd=0, wrap="word",
                       insertbackground="#e7ecf5", font=("Segoe UI", 9), padx=6, pady=4)
    sys_text.pack(fill="x", padx=14)
    sys_text.insert("1.0", CONFIG["llm"]["system_prompt"])

    header("Jembatan Telegram (pet jadi otak bot)")
    tg_token_var = field("Bot token", CONFIG["telegram"]["bot_token"], show="•")
    tg_enabled_var = tk.BooleanVar(value=CONFIG["telegram"]["enabled"])
    tk.Checkbutton(w, text="Aktifkan jembatan Telegram (bot auto-jawab pakai Hermes)",
                   variable=tg_enabled_var, bg="#11141d", fg="#e7ecf5",
                   selectcolor="#1c2130", activebackground="#11141d",
                   activeforeground="#e7ecf5", font=("Segoe UI", 9)).pack(anchor="w", padx=12)

    status = tk.Label(w, text="Tip: setelan otomatis tersimpan saat jendela ditutup.",
                      bg="#11141d", fg="#8c97b0", font=("Segoe UI", 9), wraplength=390, justify="left")
    status.pack(anchor="w", padx=14, pady=(8, 0))

    def collect():
        CONFIG["activity_gap"] = gap_var.get()
        CONFIG["llm"]["base_url"] = normalize_url(url_var.get())
        CONFIG["llm"]["model"] = model_var.get().strip()
        CONFIG["llm"]["api_key"] = key_var.get().strip()
        CONFIG["llm"]["system_prompt"] = sys_text.get("1.0", "end").strip()
        CONFIG["telegram"]["bot_token"] = tg_token_var.get().strip()
        CONFIG["telegram"]["enabled"] = bool(tg_enabled_var.get())
        for p in Pet.pets:
            p.history[0]["content"] = CONFIG["llm"]["system_prompt"]

    def persist():
        collect()
        save_config()
        apply_scale(scale_var.get())
        apply_telegram()

    def do_test():
        persist()
        status.config(text="Menguji koneksi...", fg="#8c97b0")
        w.update_idletasks()
        holder = {}

        def worker():
            holder["res"] = llm_chat([{"role": "user", "content": "ping"}])

        def poll():
            if "res" not in holder:
                w.after(150, poll); return
            ok, text = holder["res"]
            status.config(text=("✓ Terhubung!" if ok else "✗ " + text),
                          fg=("#5fd6a4" if ok else "#ff8f8f"))
        threading.Thread(target=worker, daemon=True).start()
        w.after(150, poll)

    def do_save():
        persist()
        status.config(text="✓ Tersimpan.", fg="#5fd6a4")
        w.after(600, w.destroy)

    def on_close():
        persist()
        w.destroy()

    w.protocol("WM_DELETE_WINDOW", on_close)

    def do_test_tg():
        token = tg_token_var.get().strip()
        if not token:
            status.config(text="Isi bot token dulu.", fg="#ff8f8f"); return
        status.config(text="Menguji token Telegram...", fg="#8c97b0")
        w.update_idletasks()
        holder = {}

        def worker():
            holder["res"] = tg_call(token, "getMe", timeout=15)

        def poll():
            if "res" not in holder:
                w.after(150, poll); return
            r = holder["res"]
            if r.get("ok"):
                status.config(text="✓ Token valid: bot @%s" % r["result"].get("username"), fg="#5fd6a4")
            else:
                status.config(text="✗ " + r.get("description", "token invalid"), fg="#ff8f8f")
        threading.Thread(target=worker, daemon=True).start()
        w.after(150, poll)

    btns = tk.Frame(w, bg="#11141d"); btns.pack(fill="x", padx=14, pady=14)
    tk.Button(btns, text="Tes LLM", bg="#1c2130", fg="#e7ecf5", bd=0,
              font=("Segoe UI", 10), padx=12, pady=6, command=do_test).pack(side="left")
    tk.Button(btns, text="Tes Telegram", bg="#1c2130", fg="#e7ecf5", bd=0,
              font=("Segoe UI", 10), padx=12, pady=6, command=do_test_tg).pack(side="left", padx=(8, 0))
    tk.Button(btns, text="Simpan", bg="#7c8cff", fg="#0c0e14", bd=0,
              font=("Segoe UI", 10, "bold"), padx=18, pady=6, command=do_save).pack(side="right")


def toggle_telegram():
    on = bool(TelegramBridge.instance and TelegramBridge.instance.running)
    if on:
        CONFIG["telegram"]["enabled"] = False
    else:
        if not CONFIG["telegram"].get("bot_token"):
            if Pet.pets:
                Pet.pets[0].say("Isi bot token di ⚙ Pengaturan dulu ya")
            return
        CONFIG["telegram"]["enabled"] = True
    save_config()
    apply_telegram()
    if Pet.pets:
        Pet.pets[0].say("📡 Telegram " + ("dimatikan" if on else "dinyalakan"))


def add_pet():
    Pet()


def quit_all():
    if TelegramBridge.instance:
        TelegramBridge.instance.stop()
    for p in list(Pet.pets):
        try:
            p.hide_prop()
            p.stop_marquee()
            p.win.destroy()
        except tk.TclError:
            pass
    root.destroy()


_scale_var = tk.IntVar(value=SCALE)


if __name__ == "__main__":
    Pet()
    apply_telegram()  # nyalakan jembatan Telegram bila diaktifkan di config
    tg_pump()         # loop penampil event Telegram -> running text
    root.mainloop()
