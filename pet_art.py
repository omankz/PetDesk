"""
PetDex Desktop - Pixel art renderer (tanpa dependency apa pun).
Menghasilkan "grid" warna (list 2D) untuk satu pet, lalu dipakai oleh
desktop_pet.py untuk dibuat jadi gambar di layar.
"""
import math
import random

GRID = 24  # jumlah sel per sisi sprite


# ----------------------------- palet warna -------------------------------
PALETTES = {
    "rose":   {"main": "#f76d8e", "shade": "#c84e6e", "belly": "#ffd0db", "accent": "#ffe08a", "eye": "#3a2230"},
    "mint":   {"main": "#5fd6a4", "shade": "#3fa57c", "belly": "#d6fbe9", "accent": "#ffd166", "eye": "#1f3a30"},
    "sky":    {"main": "#5aa9f7", "shade": "#3a7fd0", "belly": "#d6ecff", "accent": "#ffb454", "eye": "#22324a"},
    "lilac":  {"main": "#b48cf0", "shade": "#8a63cc", "belly": "#ecdcff", "accent": "#9be7ff", "eye": "#322444"},
    "amber":  {"main": "#f7a64a", "shade": "#cc7d2c", "belly": "#ffe2bd", "accent": "#7fe3c0", "eye": "#3a2a14"},
    "cherry": {"main": "#e8554d", "shade": "#b73a36", "belly": "#ffd2c4", "accent": "#ffe066", "eye": "#3a1c1a"},
    "forest": {"main": "#4c9a5b", "shade": "#357043", "belly": "#d4f0cf", "accent": "#ffd166", "eye": "#1d2e1f"},
    "ocean":  {"main": "#2bb8c4", "shade": "#1c8a93", "belly": "#cdf3f6", "accent": "#ff9f6e", "eye": "#10363a"},
    "grape":  {"main": "#8a6cf0", "shade": "#5f44c4", "belly": "#e1d6ff", "accent": "#ffd166", "eye": "#241a40"},
    "sun":    {"main": "#ffcf4d", "shade": "#e0a92e", "belly": "#fff3c4", "accent": "#ff8a5c", "eye": "#3a2e10"},
    "coal":   {"main": "#3a4150", "shade": "#262b36", "belly": "#5a6478", "accent": "#7fe3c0", "eye": "#cdd6e6"},
    "candy":  {"main": "#ff8fc7", "shade": "#d96aa3", "belly": "#ffe0f1", "accent": "#9be7ff", "eye": "#3a2230"},
    "lime":   {"main": "#a8d84a", "shade": "#80a82e", "belly": "#ecf8c4", "accent": "#ff8a5c", "eye": "#2a330f"},
}
PALETTE_KEYS = list(PALETTES.keys())

NAME_A = ["Mochi", "Pixel", "Nimbus", "Biscuit", "Sprout", "Echo", "Pebble", "Maple",
          "Cinder", "Tofu", "Gizmo", "Waffle", "Glimmer", "Noodle", "Comet", "Pudding",
          "Ziggy", "Marble", "Fern", "Cocoa", "Twinkle", "Bumble", "Lumen", "Pippin"]
NAME_B = ["boo", "kin", "let", "ly", "zoo", "pop", "bun", "tail", "puff", "paw", "byte",
          "jelly", "spark", "muffin", "claw", "wing"]


def random_pet(rng=None):
    """Buat konfigurasi pet acak: (name, palette_key, shape)."""
    r = rng or random
    name = r.choice(NAME_A) + r.choice(NAME_B)
    key = r.choice(PALETTE_KEYS)
    shape = {
        "body":    r.randint(0, 2),     # 0 bulat, 1 jangkung, 2 lebar
        "ears":    r.randint(0, 3),     # 0 tanpa, 1 kucing, 2 kelinci, 3 bulat
        "eyes":    1 if r.random() < 0.4 else 0,
        "horn":    r.random() < 0.22,
        "antenna": r.random() < 0.18,
        "tail":    r.random() < 0.65,
        "spots":   r.random() < 0.4,
        "belly":   r.random() < 0.75,
        "cheeks":  r.random() < 0.7,
        "sparkle": r.random() < 0.18,
        "seed":    r.randint(1, 10_000_000),
    }
    return name, key, shape


# ----------------------------- util warna --------------------------------
def _hex_to_rgb(h):
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


def _rgb_to_hex(r, g, b):
    return "#%02x%02x%02x" % (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))


def _lighten(h, f):
    r, g, b = _hex_to_rgb(h)
    return _rgb_to_hex(r + (255 - r) * f, g + (255 - g) * f, b + (255 - b) * f)


def _r(v):
    """round ala JS (0.5 -> 1)."""
    return math.floor(v + 0.5)


# ----------------------------- renderer ----------------------------------
def render(shape, palette, *, bob=0, blink=False, leg=0, tail_up=False, sparkle=False,
           sx=1.0, sy=1.0):
    """Kembalikan grid GRID x GRID berisi string hex warna atau None (transparan).

    sx/sy = faktor squash & stretch (lebar/tinggi). Kaki tetap menempel di lantai:
    sy>1 = memanjang ke atas, sy<1 = memipih; sx melebar/menyempit."""
    g = [[None] * GRID for _ in range(GRID)]
    P = palette
    S = shape

    def px(x, y, color):
        if 0 <= x < GRID and 0 <= y < GRID:
            g[int(y)][int(x)] = color

    cx = GRID / 2
    if S["body"] == 0:
        bw, bh, cy = 8.5, 8.0, 14.0
    elif S["body"] == 1:
        bw, bh, cy = 7.0, 9.5, 13.5
    else:
        bw, bh, cy = 9.5, 7.0, 15.0
    cy += bob

    # squash & stretch dengan jangkar di garis kaki (foot line tetap)
    if sx != 1.0 or sy != 1.0:
        foot = cy + bh
        bw *= sx
        bh *= sy
        cy = foot - bh

    def in_ell(x, y, ecx, ecy, rx, ry):
        return ((x + 0.5 - ecx) ** 2) / (rx * rx) + ((y + 0.5 - ecy) ** 2) / (ry * ry) <= 1

    ear_y = cy - bh + 1

    # ---- telinga (di belakang badan) ----
    if S["ears"] == 1:  # kucing
        for dx in (-1, 1):
            ex = _r(cx + dx * (bw * 0.55))
            px(ex - 1, ear_y - 2, P["shade"]); px(ex, ear_y - 2, P["shade"])
            px(ex - 1, ear_y - 1, P["main"]);  px(ex, ear_y - 1, P["main"])
            px(ex, ear_y, P["main"])
    elif S["ears"] == 2:  # kelinci
        for dx in (-1, 1):
            ex = _r(cx + dx * (bw * 0.35))
            for k in range(4):
                px(ex, ear_y - 4 + k, P["shade"] if k == 0 else P["main"])
            px(ex, ear_y - 3, P["belly"]); px(ex, ear_y - 2, P["belly"])
    elif S["ears"] == 3:  # bulat
        for dx in (-1, 1):
            ex = _r(cx + dx * (bw * 0.5))
            px(ex, ear_y - 1, P["main"]); px(ex - 1, ear_y - 1, P["main"])
            px(ex, ear_y - 2, P["shade"])

    # ---- tanduk / antena ----
    if S["horn"]:
        px(_r(cx), ear_y - 2, P["accent"]); px(_r(cx), ear_y - 3, P["accent"])
    if S["antenna"]:
        px(_r(cx), ear_y - 3, P["shade"]); px(_r(cx), ear_y - 4, P["accent"])

    # ---- badan (outline + isi + bayangan) ----
    for y in range(GRID):
        for x in range(GRID):
            if not in_ell(x, y, cx, cy, bw, bh):
                continue
            edge = (not in_ell(x - 1, y, cx, cy, bw, bh) or
                    not in_ell(x + 1, y, cx, cy, bw, bh) or
                    not in_ell(x, y - 1, cx, cy, bw, bh) or
                    not in_ell(x, y + 1, cx, cy, bw, bh))
            color = P["main"]
            if y > cy + bh * 0.25:
                color = P["shade"]
            if edge:
                color = P["eye"]
            px(x, y, color)

    # ---- perut ----
    if S["belly"]:
        byc = cy + bh * 0.35
        for y in range(GRID):
            for x in range(GRID):
                if in_ell(x, y, cx, byc, bw * 0.45, bh * 0.45):
                    px(x, y, P["belly"])

    # ---- bintik ----
    if S["spots"]:
        sr = random.Random(S["seed"] ^ 0x9E37)
        for _ in range(3):
            sx = _r(cx + (sr.random() - 0.5) * bw * 1.2)
            sy = _r(cy + (sr.random() - 0.2) * bh * 0.8)
            if in_ell(sx, sy, cx, cy, bw - 1, bh - 1):
                px(sx, sy, P["shade"]); px(sx + 1, sy, P["shade"])

    # ---- mata ----
    eye_y = _r(cy - bh * 0.15)
    eye_dx = max(1, _r(bw * 0.32))
    l_eye = _r(cx - eye_dx)
    r_eye = _r(cx + eye_dx) - 1
    if blink:
        for ex in (l_eye, r_eye):
            px(ex - 1, eye_y, P["eye"]); px(ex, eye_y, P["eye"])
    elif S["eyes"] == 1:  # mata besar
        for ex in (l_eye, r_eye):
            px(ex, eye_y - 1, "#ffffff")
            px(ex, eye_y, P["eye"]); px(ex, eye_y + 1, P["eye"])
    else:  # mata titik
        for ex in (l_eye, r_eye):
            px(ex, eye_y, P["eye"])
            px(ex, eye_y - 1, "#ffffff")

    # ---- pipi ----
    if S["cheeks"] and not blink:
        blush = _lighten(P["accent"], 0.15)
        px(l_eye - 1, eye_y + 1, blush)
        px(r_eye + 1, eye_y + 1, blush)

    # ---- mulut ----
    px(_r(cx), eye_y + 2, P["eye"])

    # ---- ekor ----
    if S["tail"]:
        tx = _r(cx + bw * 0.85)
        ty = _r(cy + bh * 0.3) + (-1 if tail_up else 1)
        px(tx, ty, P["shade"])
        px(tx + 1, ty - (1 if tail_up else 0), P["main"])
        px(tx + 1, ty + (0 if tail_up else 1), P["main"])

    # ---- kaki (animasi jalan) ----
    foot_y = _r(cy + bh) - 1
    lx = _r(cx - bw * 0.4)
    rx = _r(cx + bw * 0.4) - 1
    if leg == 0:        # berdiri
        px(lx, foot_y, P["shade"]); px(rx, foot_y, P["shade"])
    elif leg == 1:      # langkah A
        px(lx, foot_y, P["shade"]); px(rx, foot_y - 1, P["shade"])
    elif leg == 2:      # langkah B
        px(lx, foot_y - 1, P["shade"]); px(rx, foot_y, P["shade"])
    else:               # leg == 3: kedua kaki terangkat (loncat)
        px(lx, foot_y - 1, P["shade"]); px(rx, foot_y - 1, P["shade"])

    # ---- kilau ----
    if sparkle:
        c = P["accent"]
        px(3, 4, c); px(GRID - 4, 5, c); px(GRID - 5, GRID - 6, c)

    return g


def mirror(grid):
    """Balik grid secara horizontal (untuk menghadap kiri)."""
    return [row[::-1] for row in grid]
