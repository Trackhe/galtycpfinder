import tkinter as tk
from tkinter import ttk
import json
import xml.etree.ElementTree as ET
from io import BytesIO
from icon_mapper import get_svg_id_for_material

# Versuche verschiedene Methoden, SVG anzuzeigen
try:
    from cairosvg import svg2png
    from PIL import Image, ImageTk
    USE_CAIRO = True
    print("✓ CairoSVG und PIL verfügbar")
except ImportError:
    USE_CAIRO = False
    print("✗ CairoSVG oder PIL nicht verfügbar")

# JSON laden
with open('data.json', 'r', encoding='utf-8') as f:
    daten = json.load(f)

# SVG parsen
tree = ET.parse('sprite-D4k0byZ2.svg')
root = tree.getroot()
ns = {'svg': 'http://www.w3.org/2000/svg'}

# Alle SVG Symbole sammeln
all_svg_symbols = {}
for symbol in root.findall('.//svg:symbol', ns):
    symbol_id = symbol.get('id')
    if symbol_id:
        all_svg_symbols[symbol_id] = False  # False = noch nicht verwendet

print(f"Geladene SVG Symbole: {len(all_svg_symbols)}")
print(f"Materialien in data.json: {len(daten['materials'])}")

# Fenster erstellen
window = tk.Tk()
window.title("SVG Icon Test - Alle Materialien")
window.geometry("1400x800")

# Scrollbarer Frame
canvas = tk.Canvas(window)
scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Header
header = tk.Label(
    scrollable_frame,
    text="Material Icon Test mit Icon Mapping",
    font=('Helvetica', 14, 'bold'),
    pady=10
)
header.grid(row=0, column=0, columnspan=3, sticky='w', padx=10)

# Zeige ALLE Materialien mit ihren Icons
row = 1
found_count = 0
not_found_count = 0

for i, material in enumerate(daten['materials']):
    mat_id = material['id']
    mat_name = material['name']

    # Label mit Material-Info
    info_label = tk.Label(
        scrollable_frame,
        text=f"{mat_id:3d}: {mat_name}",
        font=('Courier', 9),
        anchor='w',
        width=40
    )
    info_label.grid(row=row, column=0, padx=10, pady=3, sticky='w')

    # SVG ID mit Mapping ermitteln
    svg_id = get_svg_id_for_material(mat_id, mat_name)

    if svg_id is None:
        # Kein Icon verfügbar (z.B. TEMP)
        not_found_count += 1
        status_label = tk.Label(
            scrollable_frame,
            text=f"⊘ Kein Icon verfügbar",
            fg="gray",
            font=('Courier', 8),
            anchor='w'
        )
        status_label.grid(row=row, column=1, columnspan=2, padx=5, pady=3, sticky='w')
    else:
        # Symbol suchen
        symbol = root.find(f".//svg:symbol[@id='{svg_id}']", ns)

        if symbol is not None:
            found_count += 1
            # Als verwendet markieren
            all_svg_symbols[svg_id] = True

            status_label = tk.Label(
                scrollable_frame,
                text=f"✓ {svg_id}",
                fg="green",
                font=('Courier', 8),
                width=35,
                anchor='w'
            )
            status_label.grid(row=row, column=1, padx=5, pady=3, sticky='w')

            # Versuche Icon zu laden
            if USE_CAIRO:
                try:
                    viewBox = symbol.get('viewBox', '0 0 24 24')

                    # Erstelle vollständige SVG
                    svg_str = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="32" height="32">
{ET.tostring(symbol, encoding='unicode').replace('symbol', 'g')}
</svg>'''

                    # Konvertiere zu PNG
                    png_data = svg2png(bytestring=svg_str.encode('utf-8'), output_width=32, output_height=32)
                    img = Image.open(BytesIO(png_data))
                    photo = ImageTk.PhotoImage(img)

                    # Zeige Icon
                    icon_label = tk.Label(scrollable_frame, image=photo, bg='white', relief='solid', borderwidth=1)
                    icon_label.image = photo  # Referenz behalten!
                    icon_label.grid(row=row, column=2, padx=10, pady=3)

                except Exception as e:
                    error_label = tk.Label(
                        scrollable_frame,
                        text=f"Fehler: {str(e)[:30]}",
                        fg="orange",
                        font=('Courier', 7)
                    )
                    error_label.grid(row=row, column=2, padx=10, pady=3)
        else:
            not_found_count += 1
            status_label = tk.Label(
                scrollable_frame,
                text=f"✗ Nicht gefunden: {svg_id}",
                fg="red",
                font=('Courier', 8),
                anchor='w'
            )
            status_label.grid(row=row, column=1, columnspan=2, padx=5, pady=3, sticky='w')

    row += 1

# Nicht zugeordnete SVG Symbole finden
unused_svgs = sorted([svg_id for svg_id, used in all_svg_symbols.items() if not used])

# Statistik
row += 1
separator = tk.Label(scrollable_frame, text="═" * 120, font=('Courier', 8), fg='blue')
separator.grid(row=row, column=0, columnspan=3, pady=10)

row += 1
stats_text = f"""Statistik:
  Gesamt Materialien:      {len(daten['materials'])}
  ✓ Icons gefunden:        {found_count}
  ✗ Icons nicht gefunden:  {not_found_count}

  SVG Symbole gesamt:      {len(all_svg_symbols)}
  Nicht zugeordnet:        {len(unused_svgs)}

  CairoSVG verfügbar:      {'Ja' if USE_CAIRO else 'Nein'}
"""
stats_label = tk.Label(
    scrollable_frame,
    text=stats_text,
    font=('Courier', 10),
    justify='left',
    anchor='w',
    fg='blue'
)
stats_label.grid(row=row, column=0, columnspan=3, padx=10, pady=10, sticky='w')

# Nicht zugeordnete SVG Symbole anzeigen
if unused_svgs:
    row += 1
    unused_header = tk.Label(
        scrollable_frame,
        text=f"Nicht zugeordnete SVG Symbole ({len(unused_svgs)}):",
        font=('Courier', 11, 'bold'),
        fg='orange',
        anchor='w'
    )
    unused_header.grid(row=row, column=0, columnspan=3, padx=10, pady=(20, 5), sticky='w')

    # Zeige Icons in einem Grid (4 Spalten)
    cols = 4
    start_row = row + 1

    for idx, svg_id in enumerate(unused_svgs):
        grid_row = start_row + (idx // cols)
        grid_col = idx % cols

        # Frame für jedes ungenutztes SVG
        unused_frame = tk.Frame(scrollable_frame, relief='ridge', borderwidth=1, padx=5, pady=5)
        unused_frame.grid(row=grid_row, column=grid_col, padx=5, pady=5, sticky='w')

        # SVG ID Label
        id_label = tk.Label(
            unused_frame,
            text=svg_id,
            font=('Courier', 8),
            fg='gray'
        )
        id_label.pack()

        # Versuche Icon zu laden und anzuzeigen
        if USE_CAIRO:
            symbol = root.find(f".//svg:symbol[@id='{svg_id}']", ns)
            if symbol is not None:
                try:
                    viewBox = symbol.get('viewBox', '0 0 24 24')
                    svg_str = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="24" height="24">
{ET.tostring(symbol, encoding='unicode').replace('symbol', 'g')}
</svg>'''
                    png_data = svg2png(bytestring=svg_str.encode('utf-8'), output_width=24, output_height=24)
                    img = Image.open(BytesIO(png_data))
                    photo = ImageTk.PhotoImage(img)

                    icon_label = tk.Label(unused_frame, image=photo, bg='white')
                    icon_label.image = photo
                    icon_label.pack()
                except:
                    pass

# Planeten-Icons am Ende anzeigen
row = start_row + ((len(unused_svgs) + cols - 1) // cols) + 2

planet_header = tk.Label(
    scrollable_frame,
    text=f"\n═══════════════════════════════════════════════════════════════\nPLANETEN-ICONS\n═══════════════════════════════════════════════════════════════",
    font=('Courier', 11, 'bold'),
    fg='purple',
    anchor='w'
)
planet_header.grid(row=row, column=0, columnspan=3, padx=10, pady=(20, 5), sticky='w')

# Sammle alle Planeten-Typen aus data.json
planet_types = set()
for system in daten.get('systems', []):
    for planet in system.get('planets', []):
        if 'type' in planet:
            planet_types.add(planet['type'])

planet_types = sorted(planet_types)

row += 1
planet_info_label = tk.Label(
    scrollable_frame,
    text=f"Gefundene Planeten-Typen: {len(planet_types)}",
    font=('Courier', 10),
    fg='purple',
    anchor='w'
)
planet_info_label.grid(row=row, column=0, columnspan=3, padx=10, pady=5, sticky='w')

# Zeige Planeten-Icons in einem Grid (6 Spalten)
planet_cols = 6
start_row = row + 1
planet_found = 0
planet_not_found = 0

for idx, planet_type in enumerate(planet_types):
    grid_row = start_row + (idx // planet_cols)
    grid_col = idx % planet_cols

    # Frame für jeden Planeten-Typ
    planet_frame = tk.Frame(scrollable_frame, relief='ridge', borderwidth=1, padx=5, pady=5)
    planet_frame.grid(row=grid_row, column=grid_col, padx=5, pady=5, sticky='w')

    # Planet Type Label
    type_label = tk.Label(
        planet_frame,
        text=planet_type,
        font=('Courier', 8),
        fg='purple'
    )
    type_label.pack()

    # Versuche Planet-Icon zu laden
    svg_id = f"P_{planet_type}"
    if USE_CAIRO:
        symbol = root.find(f".//svg:symbol[@id='{svg_id}']", ns)
        if symbol is not None:
            planet_found += 1
            try:
                viewBox = symbol.get('viewBox', '0 0 24 24')
                svg_str = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="48" height="48">
{ET.tostring(symbol, encoding='unicode').replace('symbol', 'g')}
</svg>'''
                png_data = svg2png(bytestring=svg_str.encode('utf-8'), output_width=48, output_height=48)
                img = Image.open(BytesIO(png_data))
                photo = ImageTk.PhotoImage(img)

                icon_label = tk.Label(planet_frame, image=photo, bg='white')
                icon_label.image = photo
                icon_label.pack()

                status_label = tk.Label(planet_frame, text="✓", fg="green", font=('Arial', 10))
                status_label.pack()
            except:
                planet_not_found += 1
                no_icon_label = tk.Label(planet_frame, text="[Fehler]", fg="orange")
                no_icon_label.pack()
        else:
            planet_not_found += 1
            no_icon_label = tk.Label(planet_frame, text="✗", fg="red", font=('Arial', 10))
            no_icon_label.pack()

# Planeten-Statistik
planet_stats_row = start_row + ((len(planet_types) + planet_cols - 1) // planet_cols) + 1
planet_stats_label = tk.Label(
    scrollable_frame,
    text=f"\nPlaneten-Icons: {planet_found} gefunden, {planet_not_found} nicht gefunden",
    font=('Courier', 10),
    fg='purple',
    anchor='w'
)
planet_stats_label.grid(row=planet_stats_row, column=0, columnspan=3, padx=10, pady=10, sticky='w')

window.mainloop()
