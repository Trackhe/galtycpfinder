import sys
import json
import math
from typing import Set
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QCheckBox,
                             QLineEdit, QTreeWidget, QTreeWidgetItem, QTextEdit,
                             QGroupBox, QGridLayout, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont
from icon_mapper import get_svg_id_for_material

# SVG zu PNG Konvertierung
try:
    from cairosvg import svg2png
    from PIL import Image
    from io import BytesIO
    import xml.etree.ElementTree as ET
    USE_CAIRO = True
except ImportError:
    USE_CAIRO = False
    print("CairoSVG/PIL nicht verfügbar - Icons werden nicht angezeigt")


class PlanetFinderPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 Planet Finder - Galactic Tycoons")
        self.setMinimumSize(1600, 900)

        # Daten laden
        with open('data.json', 'r', encoding='utf-8') as f:
            self.daten = json.load(f)

        # SVG Icons laden
        self.svg_root = None
        self.svg_ns = {'svg': 'http://www.w3.org/2000/svg'}
        self.icon_cache = {}

        try:
            tree = ET.parse('sprite-D4k0byZ2.svg')
            self.svg_root = tree.getroot()
        except Exception as e:
            print(f"Fehler beim Laden der SVG Datei: {e}")

        # Koordinaten
        self.EXCHANGE_X = 3301
        self.EXCHANGE_Y = 1409
        self.PX_TO_LY = self.daten['galaxyConfig']['pxToLY']

        # Verfügbare Materialien sammeln
        self.available_materials = self.get_available_materials()
        self.selected_materials: Set[int] = set()
        self.material_buttons = {}
        self.planeten_liste = []

        # UI erstellen
        self.init_ui()

    def get_available_materials(self) -> Set[int]:
        """Sammelt alle Material-IDs, die auf Planeten vorkommen."""
        material_ids = set()
        for system in self.daten.get('systems', []):
            planets = system.get('planets')
            if planets is None:
                continue
            for planet in planets:
                mats = planet.get('mats')
                if mats:
                    for mat in mats:
                        material_ids.add(mat['id'])
        return material_ids

    def load_icon(self, mat_id: int, mat_name: str, size: int = 24) -> QPixmap:
        """Lädt ein Icon für ein Material."""
        if not USE_CAIRO or not self.svg_root:
            return None

        cache_key = f"{mat_id}_{size}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]

        svg_id = get_svg_id_for_material(mat_id, mat_name)
        if svg_id is None:
            return None

        symbol = self.svg_root.find(f".//svg:symbol[@id='{svg_id}']", self.svg_ns)
        if symbol is None:
            return None

        try:
            viewBox = symbol.get('viewBox', '0 0 24 24')
            svg_str = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="{size}" height="{size}">
{ET.tostring(symbol, encoding='unicode').replace('symbol', 'g')}
</svg>'''

            png_data = svg2png(bytestring=svg_str.encode('utf-8'), output_width=size, output_height=size)
            img = Image.open(BytesIO(png_data))

            # Convert PIL Image to QPixmap
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(img_byte_arr.getvalue())

            self.icon_cache[cache_key] = pixmap
            return pixmap
        except Exception as e:
            print(f"Fehler beim Laden von Icon {svg_id}: {e}")
            return None

    def get_planet_svg_id(self, planet_type: int) -> str:
        """Mappt Planet-Typ-ID zu SVG-ID."""
        type_map = {
            1: "P_Exchange",
            2: "P_Desert",
            3: "P_Desert",
            4: "P_Rock",
            5: "P_WaterGrass",
            6: "P_WaterRock",
            7: "P_GasMix",
            8: "P_Lava",
            9: "P_GasYellow",
            10: "P_Ocean",
            11: "P_WaterSandFertile",
            12: "P_DesertRed",
            13: "P_AcidRock",
            14: "P_RockDark",
            15: "P_DesertOrange",
            16: "P_RockWhite",
            17: "P_Acid",
            18: "P_GasGreen",
            19: "P_GasBlue",
            20: "P_GasYellow"
        }
        return type_map.get(planet_type, f"P_Unknown_{planet_type}")

    def load_planet_icon(self, planet_type: int, size: int = 80) -> QPixmap:
        """Lädt ein Icon für einen Planeten-Typ."""
        if not USE_CAIRO or not self.svg_root:
            return None

        svg_id = self.get_planet_svg_id(planet_type)
        cache_key = f"planet_{svg_id}_{size}"

        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]

        symbol = self.svg_root.find(f".//svg:symbol[@id='{svg_id}']", self.svg_ns)
        if symbol is None:
            return None

        try:
            viewBox = symbol.get('viewBox', '0 0 24 24')
            svg_str = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="{size}" height="{size}">
{ET.tostring(symbol, encoding='unicode').replace('symbol', 'g')}
</svg>'''

            png_data = svg2png(bytestring=svg_str.encode('utf-8'), output_width=size, output_height=size)
            img = Image.open(BytesIO(png_data))

            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(img_byte_arr.getvalue())

            self.icon_cache[cache_key] = pixmap
            return pixmap
        except Exception as e:
            print(f"Fehler beim Laden von Planeten-Icon {svg_id}: {e}")
            return None

    def init_ui(self):
        """Erstellt die Benutzeroberfläche."""
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Titel
        title = QLabel("🌍 Planet Finder")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Filter Group
        filter_group = QGroupBox("🔍 Filter")
        filter_layout = QVBoxLayout()

        # Tier Checkboxes
        tier_layout = QHBoxLayout()
        tier_layout.addWidget(QLabel("Tiers:"))
        self.tier_checkboxes = []
        for i in range(1, 5):
            cb = QCheckBox(f"Tier {i}")
            cb.setChecked(True)
            self.tier_checkboxes.append(cb)
            tier_layout.addWidget(cb)
        tier_layout.addStretch()
        filter_layout.addLayout(tier_layout)

        # Max Distanz
        dist_layout = QHBoxLayout()
        dist_layout.addWidget(QLabel("Max Entfernung (LY):"))
        self.max_distanz_input = QLineEdit()
        self.max_distanz_input.setMaximumWidth(150)
        dist_layout.addWidget(self.max_distanz_input)
        dist_layout.addStretch()
        filter_layout.addLayout(dist_layout)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        # Materialien Group
        materials_group = QGroupBox(f"🔬 Materialien (verfügbar auf Planeten: {len(self.available_materials)})")
        materials_layout = QVBoxLayout()

        # Scroll Area für Materialien
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(250)

        scroll_content = QWidget()
        materials_grid = QGridLayout(scroll_content)

        # Material Buttons erstellen (6 Spalten)
        row = 0
        col = 0
        max_cols = 6

        for material in self.daten['materials']:
            mat_id = material['id']
            mat_name = material['name']

            if mat_id not in self.available_materials:
                continue

            # Icon laden
            icon = self.load_icon(mat_id, mat_name, size=24)

            # Button erstellen
            btn = QPushButton(f"  {mat_id}: {mat_name}")
            btn.setCheckable(True)
            btn.setMinimumHeight(50)  # HIER! PyQt6 hat setMinimumHeight()!
            btn.setMaximumHeight(50)

            if icon:
                btn.setIcon(QIcon(icon))
                btn.setIconSize(QSize(24, 24))

            btn.clicked.connect(lambda checked, mid=mat_id: self.toggle_material(mid))

            materials_grid.addWidget(btn, row, col)
            self.material_buttons[mat_id] = btn

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        scroll.setWidget(scroll_content)
        materials_layout.addWidget(scroll)

        # Buttons
        buttons_layout = QHBoxLayout()

        search_btn = QPushButton("🔍 Planeten suchen")
        search_btn.clicked.connect(self.search_planets)
        buttons_layout.addWidget(search_btn)

        clear_btn = QPushButton("🗑️ Materialien zurücksetzen")
        clear_btn.clicked.connect(self.clear_materials)
        buttons_layout.addWidget(clear_btn)

        buttons_layout.addStretch()
        materials_layout.addLayout(buttons_layout)

        materials_group.setLayout(materials_layout)
        main_layout.addWidget(materials_group)

        # Ergebnisse
        results_group = QGroupBox("📊 Ergebnisse")
        results_layout = QVBoxLayout()

        # TreeWidget für Planeten
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "ID", "System-ID", "Typ", "Fert", "X", "Y", "Size", "Tier", "Distanz", "LY"])
        self.tree.itemSelectionChanged.connect(self.on_planet_select)
        # Spaltenbreite auf Inhalt anpassen
        header = self.tree.header()
        header.setStretchLastSection(False)
        for i in range(11):
            header.setSectionResizeMode(i, header.ResizeMode.Stretch if i == 0 else header.ResizeMode.ResizeToContents)
        results_layout.addWidget(self.tree)

        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        # Planet Details
        details_group = QGroupBox("📦 Planet Details")
        details_main_layout = QHBoxLayout()

        # Planet Icon
        self.planet_icon_label = QLabel()
        self.planet_icon_label.setMinimumSize(80, 80)
        self.planet_icon_label.setMaximumSize(80, 80)
        self.planet_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        details_main_layout.addWidget(self.planet_icon_label)

        # Details Grid
        details_grid_widget = QWidget()
        self.details_grid = QGridLayout(details_grid_widget)
        self.details_grid.setSpacing(10)
        self.details_grid.setColumnStretch(0, 0)
        self.details_grid.setColumnStretch(1, 0)
        self.details_grid.setColumnStretch(2, 0)
        self.details_grid.setColumnStretch(3, 0)
        self.details_grid.setColumnStretch(4, 0)
        self.details_grid.setColumnStretch(5, 0)
        details_main_layout.addWidget(details_grid_widget)
        details_main_layout.addStretch()

        details_group.setLayout(details_main_layout)
        main_layout.addWidget(details_group)

        # Status Label
        self.status_label = QLabel("✓ Bereit")
        main_layout.addWidget(self.status_label)

        print(f"Verfügbare Materialien auf Planeten: {len(self.available_materials)} von {len(self.daten['materials'])}")

    def toggle_material(self, mat_id):
        """Material auswählen/abwählen."""
        if mat_id in self.selected_materials:
            self.selected_materials.remove(mat_id)
        else:
            self.selected_materials.add(mat_id)

    def clear_materials(self):
        """Alle Materialien abwählen."""
        self.selected_materials.clear()
        for btn in self.material_buttons.values():
            btn.setChecked(False)
        self.status_label.setText("✓ Materialauswahl zurückgesetzt")

    def search_planets(self):
        """Planeten suchen basierend auf Filtern."""
        self.tree.clear()
        self.planeten_liste = []

        # Tier Filter
        tier_filter = [i+1 for i, cb in enumerate(self.tier_checkboxes) if cb.isChecked()]

        if not tier_filter:
            self.status_label.setText("❌ Fehler: Mindestens ein Tier muss ausgewählt sein!")
            return

        # Material Filter
        material_filter = list(self.selected_materials)

        # Max Distanz
        max_distanz_ly = None
        if self.max_distanz_input.text().strip():
            try:
                max_distanz_ly = float(self.max_distanz_input.text().strip())
            except ValueError:
                self.status_label.setText("❌ Fehler: Ungültige Entfernung!")
                return

        # Planeten durchsuchen
        for system in self.daten.get('systems', []):
            planets = system.get('planets')
            if planets is None:
                continue

            for planet in planets:
                if planet['tier'] not in tier_filter:
                    continue

                # Material Filter
                if material_filter:
                    planet_mat_ids = [mat['id'] for mat in planet.get('mats', [])]
                    if not all(mat_id in planet_mat_ids for mat_id in material_filter):
                        continue

                # Distanz berechnen
                distanz = math.sqrt((planet['x'] - self.EXCHANGE_X)**2 + (planet['y'] - self.EXCHANGE_Y)**2)
                lichtjahre = distanz / self.PX_TO_LY

                # Max Distanz Filter
                if max_distanz_ly is not None and lichtjahre > max_distanz_ly:
                    continue

                planet['distanz'] = distanz
                planet['lichtjahre'] = lichtjahre
                self.planeten_liste.append(planet)

        # Sortieren
        self.planeten_liste.sort(key=lambda p: p['distanz'])

        # In Tree einfügen
        for planet in self.planeten_liste:
            item = QTreeWidgetItem([
                str(planet['name']),
                str(planet['id']),
                str(planet['sId']),
                str(planet['type']),
                str(planet['fert']),
                str(planet['x']),
                str(planet['y']),
                str(planet['size']),
                str(planet['tier']),
                f"{planet['distanz']:.2f}",
                f"{planet['lichtjahre']:.2f}"
            ])
            self.tree.addTopLevelItem(item)

        self.status_label.setText(f"✓ Gefundene Planeten: {len(self.planeten_liste)}")

    def on_planet_select(self):
        """Zeigt Details für ausgewählten Planeten."""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        planet_id = int(item.text(1))

        planet = next((p for p in self.planeten_liste if p['id'] == planet_id), None)
        if not planet:
            return

        # Planet Icon laden
        planet_icon = self.load_planet_icon(planet['type'], size=80)
        if planet_icon:
            self.planet_icon_label.setPixmap(planet_icon)
        else:
            self.planet_icon_label.setText(str(planet['type']))

        # Altes Grid leeren
        while self.details_grid.count():
            child = self.details_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Planetenname und ID als Titel
        title_layout = QHBoxLayout()
        title = QLabel(f"🌍 {planet['name']}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title_layout.addWidget(title)

        id_label = QLabel(f"(ID: {planet['id']})")
        id_label.setStyleSheet("color: gray; font-size: 12px;")
        title_layout.addWidget(id_label)
        title_layout.addStretch()

        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        self.details_grid.addWidget(title_widget, 0, 0, 1, 6)

        # Planet Informationen in Grid
        row = 1
        svg_id = self.get_planet_svg_id(planet['type'])
        info_labels = [
            ("📍 Koordinaten:", f"({planet['x']}, {planet['y']})"),
            ("📏 Entfernung:", f"{planet['lichtjahre']:.2f} LY ({planet['distanz']:.2f} px)"),
            ("⭐ Tier:", str(planet['tier'])),
            ("📊 Typ:", f"{svg_id} (ID: {planet['type']})"),
            ("🌱 Fruchtbarkeit:", str(planet['fert'])),
            ("📐 Größe:", str(planet['size']))
        ]

        for i, (label_text, value_text) in enumerate(info_labels):
            col = (i % 2) * 2
            if i % 2 == 0 and i > 0:
                row += 1

            label = QLabel(label_text)
            label_font = QFont()
            label_font.setBold(True)
            label.setFont(label_font)
            self.details_grid.addWidget(label, row, col)

            value = QLabel(value_text)
            self.details_grid.addWidget(value, row, col + 1)

        row += 1

        # Materialien Sektion
        mat_title = QLabel("🔬 Materialien:")
        mat_title_font = QFont()
        mat_title_font.setBold(True)
        mat_title.setFont(mat_title_font)
        self.details_grid.addWidget(mat_title, row, 0, 1, 6)
        row += 1

        if planet.get('mats'):
            mat_flow = QHBoxLayout()
            mat_flow.setSpacing(15)

            for mat in planet['mats']:
                mat_id = mat['id']
                abundance = mat['ab']
                mat_name = next((m['name'] for m in self.daten['materials'] if m['id'] == mat_id), 'Unbekannt')

                # Icon laden
                icon = self.load_icon(mat_id, mat_name, size=24)

                mat_item_layout = QHBoxLayout()
                mat_item_layout.setSpacing(5)

                icon_label = QLabel()
                if icon:
                    icon_label.setPixmap(icon)
                    icon_label.setFixedSize(24, 24)
                else:
                    icon_label.setText("•")
                mat_item_layout.addWidget(icon_label)

                info_layout = QVBoxLayout()
                info_layout.setSpacing(0)

                name_label = QLabel(f"{mat_name}")
                name_font = QFont()
                name_font.setBold(True)
                name_label.setFont(name_font)
                info_layout.addWidget(name_label)

                ab_label = QLabel(f"ID: {mat_id} • AB: {abundance}")
                ab_label.setStyleSheet("color: gray; font-size: 10px;")
                info_layout.addWidget(ab_label)

                mat_item_layout.addLayout(info_layout)

                mat_widget = QWidget()
                mat_widget.setLayout(mat_item_layout)
                mat_flow.addWidget(mat_widget)

            mat_flow.addStretch()

            mat_container = QWidget()
            mat_container.setLayout(mat_flow)
            self.details_grid.addWidget(mat_container, row, 0, 1, 6)
        else:
            no_mats = QLabel("Keine Materialien vorhanden")
            no_mats.setStyleSheet("color: gray; font-style: italic;")
            self.details_grid.addWidget(no_mats, row, 0, 1, 6)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlanetFinderPyQt()
    window.show()
    sys.exit(app.exec())
