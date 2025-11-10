"""
SVG Icon Mapper für Materialien
Behandelt Spezialfälle beim Mapping von Material-Namen zu SVG Symbol-IDs
"""

# Mapping für Spezialfälle
SPECIAL_MAPPINGS = {
    2: "IronBar",  # Iron -> IronBar
    6: "CopperBar",  # Copper -> CopperBar
    12: "BasicRations",  # Rations -> BasicRations
    15: "BasicExosuit",  # Exosuit -> BasicExosuit
    17: "BasicTools",  # Tools -> BasicTools
    26: "BasicConstructionKit",  # Construction Kit -> BasicConstructionKit
    37: "Cow",  # Cows -> Cow
    55: "Motor",  # Electric Motor -> Motor
    57: "Gasoline",  # Ethanol -> Gasoline
    62: "CopperWiring",  # Copper Wire -> CopperWiring
    63: "Electronics",  # Consumer Electronics -> Electronics
    80: "Graphenium",  # Graphenium Wire -> Graphenium (verwendet das Graphenium Symbol)
    88: "Chicken",  # Chickens -> Chicken
    92: "BasicPrefabKit",  # Prefab Kit -> BasicPrefabKit
    93: "BasicAmenities",  # Amenities -> BasicAmenities
    98: "CompositeTruss",  # Truss -> CompositeTruss (oder ReinforcedTruss?)
    100: "AdvancedDrill",  # Titanium Carbide Drill -> AdvancedDrill
    104: "BasicHullPlate",  # Hull Plate -> BasicHullPlate
    109: "BasicFTLEmitter",  # Linear FTL Emitter -> BasicFTLEmitter
    110: "HydrogenFuelCell",  # Hydrogen Fuel -> HydrogenFuelCell
    114: "Starglass",  # Starglass Hull Plate -> Starglass (verwendet das Starglass Symbol)
    118: "BasicShipBridge",  # Shuttle Bridge -> BasicShipBridge
    134: "SuperiorFTLEmitter",  # Quantum FTL Emitter -> SuperiorFTLEmitter
    139: "BasicShipBridge",  # Hauler Bridge -> BasicShipBridge (gleich wie Shuttle Bridge)
    147: "AI",  # Artificial Intelligence -> AI
    152: "HyperCoil",  # Superconducting Coil -> HyperCoil
    160: "SuperiorFTLEmitter",  # Extra-dimensional FTL Emitter -> SuperiorFTLEmitter
    163: "Nanobots",  # Nanites -> Nanobots
    166: "T4ShipBridge",  # Freighter Bridge -> T4ShipBridge
    168: None,  # TEMP -> Kein Icon verfügbar
    169: "APU",  # Advanced Processing Unit -> APU
    171: "T4ShipElements",  # Starlifter Structural Elements -> T4ShipElements
    174: "FieldCooling",  # Field Cooling System -> FieldCooling
    175: "NutrientBlend",  # Bio-Nutrient Blend -> NutrientBlend
    176: "Pack_Medicine",  # Medicine Shipment -> Pack_Medicine
    177: "Pack_Food",  # Food Shipment -> Pack_Food
    178: "Pack_ShipParts",  # Ship Parts Shipment -> Pack_ShipParts
    179: "Pack_Defense",  # Defense systems pack -> Pack_Defense
    180: "Pack_Habitats",  # Habitats shipment -> Pack_Habitats
    181: "Pack_Scientific",  # Scientific Instruments Shipment -> Pack_Scientific
}

def get_svg_id_for_material(mat_id: int, mat_name: str) -> str:
    """
    Gibt die SVG Symbol-ID für ein Material zurück.

    Args:
        mat_id: Die Material-ID aus data.json
        mat_name: Der Material-Name aus data.json

    Returns:
        Die SVG Symbol-ID oder None wenn kein Icon verfügbar
    """
    # Prüfe zuerst ob es einen Spezialfall gibt
    if mat_id in SPECIAL_MAPPINGS:
        return SPECIAL_MAPPINGS[mat_id]

    # Standard: Leerzeichen entfernen
    return mat_name.replace(' ', '')


if __name__ == "__main__":
    # Test mit einigen Beispielen
    import json

    with open('data.json', 'r', encoding='utf-8') as f:
        daten = json.load(f)

    print("Test der Icon-Mappings:")
    print("=" * 80)

    test_ids = [2, 6, 12, 15, 17, 37, 55, 62, 63, 80, 88, 92, 93, 98, 100,
                104, 109, 110, 114, 118, 134, 139, 147, 152, 160, 163, 166,
                168, 169, 171, 174, 175, 176, 177, 178, 179, 180, 181]

    for mat_id in test_ids:
        material = next((m for m in daten['materials'] if m['id'] == mat_id), None)
        if material:
            svg_id = get_svg_id_for_material(mat_id, material['name'])
            print(f"{mat_id:<4} {material['name']:<35} -> {svg_id}")
