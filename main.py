import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

COLOR_PAPER = (0xF4, 0xF6, 0xF8)
COLOR_INK = (0x10, 0x14, 0x18)
COLOR_SEA_BLUE = (0x14, 0x50, 0x8C)
COLOR_ORANGE = (0xC7, 0x5B, 0x12)
COLOR_GRAY = (0x5A, 0x5A, 0x5A)

FONT = {
    'A': ".###.\n#...#\n#...#\n#####\n#...#\n#...#\n#...#",
    'B': "####.\n#...#\n#...#\n####.\n#...#\n#...#\n####.",
    'C': ".####\n#....\n#....\n#....\n#....\n#....\n.####",
    'D': "####.\n#...#\n#...#\n#...#\n#...#\n#...#\n####.",
    'E': "#####\n#....\n#....\n####.\n#....\n#....\n#####",
    'F': "#####\n#....\n#....\n####.\n#....\n#....\n#....",
    'G': ".####\n#....\n#....\n#.###\n#...#\n#...#\n.####",
    'H': "#...#\n#...#\n#...#\n#####\n#...#\n#...#\n#...#",
    'I': "#####\n..#..\n..#..\n..#..\n..#..\n..#..\n#####",
    'J': "..###\n...#.\n...#.\n...#.\n#..#.\n#..#.\n.##..",
    'K': "#...#\n#..#.\n#.#..\n##...\n#.#..\n#..#.\n#...#",
    'L': "#....\n#....\n#....\n#....\n#....\n#....\n#####",
    'M': "#...#\n##.##\n#.#.#\n#...#\n#...#\n#...#\n#...#",
    'N': "#...#\n##..#\n#.#.#\n#..##\n#...#\n#...#\n#...#",
    'O': ".###.\n#...#\n#...#\n#...#\n#...#\n#...#\n.###.",
    'P': "####.\n#...#\n#...#\n####.\n#....\n#....\n#....",
    'Q': ".###.\n#...#\n#...#\n#...#\n#.#.#\n#..#.\n.##.#",
    'R': "####.\n#...#\n#...#\n####.\n#.#..\n#..#.\n#...#",
    'S': ".####\n#....\n#....\n.###.\n....#\n....#\n####.",
    'T': "#####\n..#..\n..#..\n..#..\n..#..\n..#..\n..#..",
    'U': "#...#\n#...#\n#...#\n#...#\n#...#\n#...#\n.###.",
    'V': "#...#\n#...#\n#...#\n#...#\n#...#\n.#.#.\n..#..",
    'W': "#...#\n#...#\n#...#\n#.#.#\n#.#.#\n##.##\n#...#",
    'X': "#...#\n#...#\n.#.#.\n..#..\n.#.#.\n#...#\n#...#",
    'Y': "#...#\n#...#\n.#.#.\n..#..\n..#..\n..#..\n..#..",
    'Z': "#####\n....#\n...#.\n..#..\n.#...\n#....\n#####",
    '0': ".###.\n#..##\n#.#.#\n#.#.#\n##..#\n#...#\n.###.",
    '1': "..#..\n.##..\n..#..\n..#..\n..#..\n..#..\n.###.",
    '2': ".###.\n#...#\n....#\n..##.\n.#...\n#....\n#####",
    '3': "####.\n....#\n....#\n.###.\n....#\n....#\n####.",
    '4': "#...#\n#...#\n#...#\n#####\n....#\n....#\n....#",
    '5': "#####\n#....\n####.\n....#\n....#\n#...#\n.###.",
    '6': ".###.\n#....\n####.\n#...#\n#...#\n#...#\n.###.",
    '7': "#####\n....#\n...#.\n..#..\n..#..\n..#..\n..#..",
    '8': ".###.\n#...#\n#...#\n.###.\n#...#\n#...#\n.###.",
    '9': ".###.\n#...#\n#...#\n.####\n....#\n....#\n.###.",
    '.': ".....\n.....\n.....\n.....\n.....\n.##..\n.##..",
    ',': ".....\n.....\n.....\n.....\n.##..\n..#..\n.#...",
    "'": ".##..\n.##..\n..#..\n.....\n.....\n.....\n.....",
    '-': ".....\n.....\n.....\n#####\n.....\n.....\n.....",
    ':': ".....\n.##..\n.##..\n.....\n.##..\n.##..\n.....",
    '/': "....#\n...#.\n..#..\n..#..\n.#...\n#....\n.....",
    '%': "##..#\n##.#.\n...#.\n..#..\n.#...\n.#.##\n#..##",
    '$': "..#..\n.####\n#.#..\n.###.\n..#.#\n####.\n..#..",
    '+': ".....\n..#..\n..#..\n#####\n..#..\n..#..\n.....",
    '(': "...#.\n..#..\n.#...\n.#...\n.#...\n..#..\n...#.",
    ')': ".#...\n..#..\n...#.\n...#.\n...#.\n..#..\n.#...",
    '!': "..#..\n..#..\n..#..\n..#..\n.....\n..#..\n..#..",
    '&': ".##..\n#..#.\n.##..\n#.#.#\n#..#.\n#...#\n.##.#",
    ' ': ".....\n.....\n.....\n.....\n.....\n.....\n.....",
}

pixels = bytearray(bytes(COLOR_PAPER) * (WIDTH * HEIGHT))

def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    c_bytes = bytes(color)
    span_len = x1 - x0
    row_bytes = c_bytes * span_len
    for py in range(y0, y1):
        idx0 = (py * WIDTH + x0) * 3
        idx1 = idx0 + span_len * 3
        pixels[idx0:idx1] = row_bytes

def stroke_rect(x, y, w, h, thickness, color):
    fill_rect(x, y, w, thickness, color)
    fill_rect(x, y + h - thickness, w, thickness, color)
    fill_rect(x, y, thickness, h, color)
    fill_rect(x + w - thickness, y, thickness, h, color)

def wrap(s, maxchars):
    if isinstance(s, (list, tuple)):
        lines = []
        for item in s:
            lines.extend(wrap(item, maxchars))
        return lines
    if '\n' in s:
        return [line.strip() for line in s.split('\n') if line.strip()]
    if ' / ' in s:
        return [line.strip() for line in s.split(' / ') if line.strip()]
    words = s.split()
    lines = []
    cur = []
    cur_len = 0
    for w in words:
        if not cur:
            cur.append(w)
            cur_len = len(w)
        elif cur_len + 1 + len(w) <= maxchars:
            cur.append(w)
            cur_len += 1 + len(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
    if cur:
        lines.append(" ".join(cur))
    return lines

def text(x, y, s, scale, color, max_x=1024, spacing=None):
    if spacing is None:
        spacing = 1 * scale
        if max_x < 1024 and len(s) > 1:
            max_w = max_x - x
            glyph_w = len(s) * 5 * scale
            n_gaps = len(s) - 1
            if glyph_w + n_gaps * spacing > max_w:
                spacing = max(1, (max_w - glyph_w) // n_gaps)
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        lines = glyph.splitlines()
        for r, row in enumerate(lines):
            py = y + r * scale
            for c, bit in enumerate(row):
                if bit == '#':
                    px = cx + c * scale
                    if px + scale <= max_x:
                        fill_rect(px, py, scale, scale, color)
        cx += 5 * scale + spacing

def render():
    pixels[:] = bytes(COLOR_PAPER) * (WIDTH * HEIGHT)
    # 1. Pita atas
    header_text = "THE WORLD IN ONE DAY"
    char_adv_8 = 6 * 8
    hdr_w = (len(header_text) - 1) * char_adv_8 + 5 * 8
    hdr_x = (WIDTH - hdr_w) // 2
    text(hdr_x, 26, header_text, 8, COLOR_INK)

    # Garis tebal di bawah pita atas
    fill_rect(36, 88, 952, 4, COLOR_INK)

    # Tanggal pita atas
    date_text = "TUESDAY 17 NOVEMBER 2026"
    char_adv_6 = 6 * 6
    date_w = (len(date_text) - 1) * char_adv_6 + 5 * 6
    date_x = (WIDTH - date_w) // 2
    text(date_x, 100, date_text, 6, COLOR_SEA_BLUE)

    # 2. Panel UTAMA (kotak biru tipis)
    panel_x = 36
    panel_y = 152
    panel_w = 952
    panel_h = 196
    stroke_rect(panel_x, panel_y, panel_w, panel_h, 2, COLOR_SEA_BLUE)

    # Judul utama (scale 6, 2 baris)
    main_title = "RECORD DRONE STORM ROCKS CRIMEAN BRIDGE"
    title_lines = wrap(main_title, 20)
    for i, line in enumerate(title_lines):
        text(panel_x + 16, panel_y + 12 + i * 46, line, 6, COLOR_INK)

    # 3 baris ringkas (scale 3)
    summary_lines = [
        "ROAD SPAN FALLS INTO KERCH STRAIT - 2 KILLED",
        "RUSSIA SAYS 1,441 DRONES DOWNED IN ONE NIGHT",
        "RUSSIA POUNDS KYIV BRIDGES - POWER OUT IN 8 REGIONS"
    ]
    for i, line in enumerate(summary_lines):
        text(panel_x + 16, panel_y + 112 + i * 26, line, 3, COLOR_INK)

    # 3. Kisi 3 kolom x 4 baris kartu cerita
    cards = [
        ("MIDEAST", "US JETS HIT\nQESHM ISLAND", "REPLY TO IRAN\nDRONE ATTACKS"),
        ("MIDEAST", "IRAN DRONES\nHIT GULF BASES", "BAHRAIN, KUWAIT\nDEFENCES INTERCEPT"),
        ("MIDEAST", "TARA GAS CREW\nABANDON SHIP", "TANKER HIT AGAIN\nOFF OMAN COAST"),
        ("EUROPE", "FRANCE PUBLIC\nWORKERS STRIKE", "TURNOUT FALLS\nTO 146,000"),
        ("EUROPE", "IRAN PLOT\nFOILED", "5 HELD IN GREECE\nAND MACEDONIA"),
        ("EUROPE", "HUNGARY HALTS\nUKRAINE TRAINS", "AFTER DRONES HIT\nTHE WEST"),
        ("ASIA", "TRUMP IN\nMANILA", "XI-PUTIN SUMMIT\nSET THURSDAY"),
        ("MARKETS", "WALL STREET\nFALLS 4TH DAY", "S&P LOWEST\nSINCE JULY"),
        ("TECH", "NVIDIA BEATS\nAFTER BELL", "REVENUE $115.8BN\nGUIDE $130BN"),
        ("MARKETS", "EUROPE WORST\nSINCE MARCH", "STOXX 600\nDOWN 1.75%"),
        ("CLIMATE", "COP31 TALKS\nTURN TO MONEY", "ISLAND STATES\nPRESS FINANCE"),
        ("SCIENCE", "SHINE BRIGHT\nVOYAGER 1", "EVE OF 1ST\nLIGHT-DAY - NASA"),
    ]

    grid_y = 362
    grid_h = 600
    row_h = grid_h // 4
    col_w = panel_w // 3

    # Garis pemisah vertikal antar kolom kartu
    for c in range(1, 3):
        vx = panel_x + c * col_w - 4
        fill_rect(vx, grid_y, 1, grid_h, COLOR_GRAY)

    # Garis pemisah horizontal antar baris kartu
    for r in range(1, 4):
        hy = grid_y + r * row_h - 4
        fill_rect(panel_x, hy, panel_w, 1, COLOR_GRAY)

    for idx, (section, title, detail) in enumerate(cards):
        r = idx // 3
        c = idx % 3
        cx = panel_x + c * col_w
        cy = grid_y + r * row_h
        if c < 2:
            clip_right = panel_x + (c + 1) * col_w - 5
        else:
            clip_right = panel_x + panel_w - 4

        # Label seksi (scale 3, oranye)
        text(cx + 2, cy + 6, section, 3, COLOR_ORANGE, clip_right)

        # Judul (scale 4, hitam, maks 2 baris)
        lines = wrap(title, 13)
        for li, line in enumerate(lines[:2]):
            text(cx + 2, cy + 32 + li * 32, line, 4, COLOR_INK, clip_right)

        # Detail (scale 3, abu, maks 2 baris)
        dlines = wrap(detail, 18)
        for li, line in enumerate(dlines[:2]):
            text(cx + 2, cy + 98 + li * 24, line, 3, COLOR_GRAY, clip_right)

    # 4. Kaki gambar
    fill_rect(panel_x, 972, panel_w, 2, COLOR_INK)
    footer_text = "SOURCES: REUTERS, AP, NASA"
    footer_w = (len(footer_text) - 1) * (6 * 3) + 5 * 3
    footer_x = (WIDTH - footer_w) // 2
    text(footer_x, 984, footer_text, 3, COLOR_INK)

def write_png(filepath):
    raw = bytearray(HEIGHT * (WIDTH * 3 + 1))
    stride = WIDTH * 3
    for y in range(HEIGHT):
        offset_raw = y * (stride + 1)
        raw[offset_raw] = 0
        raw[offset_raw + 1 : offset_raw + 1 + stride] = pixels[y * stride : (y + 1) * stride]

    compressed = zlib.compress(raw, level=6)

    def chunk(tag, data):
        length = struct.pack('>I', len(data))
        crc = struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        return length + tag + data + crc

    ihdr_data = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    ihdr = chunk(b'IHDR', ihdr_data)
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')

    png_data = b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(png_data)

def main():
    render()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_path = os.path.join(out_dir, "entry.png")
    write_png(out_path)

if __name__ == "__main__":
    main()
