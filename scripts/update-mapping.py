#!/usr/bin/env python3
"""
Update device-firmware-mapping.json with new firmware version
"""

import json
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def load_mapping(file_path: str) -> Dict[str, List[Dict]]:
    """Load existing mapping or create empty one"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_mapping(file_path: str, mapping: Dict[str, List[Dict]]) -> None:
    """Save mapping to file with pretty formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

def get_board_to_hardware_mapping() -> Dict[str, str]:
    """Mapping from PlatformIO board names to hardware slugs"""
    return {
        "heltec-v3": "HELTEC_V3",
        "heltec-wireless-tracker-V1-0": "HELTEC_TRACKER",
        "tbeam": "TBEAM",
        "tlora-v2": "TLORA_V2",
        "tlora-v1": "TLORA_V1",
        "tlora-v1_3": "TLORA_V1_3",
        "techo": "TECHO"
    }

def get_hardware_display_names() -> Dict[str, str]:
    """Display names for hardware"""
    return {
        "HELTEC_V3": "Heltec V3",
        "HELTEC_TRACKER": "Heltec Wireless Tracker V1.0",
        "TBEAM": "TTGO T-Beam", 
        "TLORA_V2": "TTGO LoRa V2",
        "TLORA_V1": "TTGO LoRa V1",
        "TLORA_V1_3": "TTGO LoRa V1.3",
        "TECHO": "T-Echo"
    }

def create_firmware_entry(
    version: str,
    short_version: str,
    build_date: str,
    release_url: str,
    board: str,
    hw_slug: str,
    display_name: str
) -> Dict[str, Any]:
    """Create a firmware entry for the mapping"""
    
    base_url = "https://flasher.schwarzes-seelenreich.de/backend"
    firmware_path = f"firmware/{board}/{version}"
    
    # HIER: Custom Firmware Name
    firmware_name = "Mesh Hessen Firmware" 
    
    entry = {
        "id": version,
        "title": f"{firmware_name} für {display_name}",  
        "page_url": release_url,
        "created_at": build_date,
        "bin_urls": {}
    }
    
    # Verschiedene Firmware-Typen hinzufügen wenn sie existieren
    firmware_types = {
        "factory": f"firmware-{board}-{version}-factory.bin",
        "update": f"firmware-{board}-{version}-update.bin", 
        "ota": f"firmware-{board}-{version}-ota.bin"
    }
    
    for fw_type, filename in firmware_types.items():
        file_path = Path(f"firmware/{board}/{version}/{filename}")
        if file_path.exists():
            entry["bin_urls"][fw_type] = f"{base_url}/{firmware_path}/{filename}"
    
    # Fallback: Wenn nur eine .bin Datei existiert
    if not entry["bin_urls"]:
        generic_bin = Path(f"firmware/{board}/{version}/firmware-{board}-{version}.bin")
        if generic_bin.exists():
            entry["bin_urls"]["factory"] = f"{base_url}/{firmware_path}/firmware-{board}-{version}.bin"
            entry["bin_urls"]["update"] = f"{base_url}/{firmware_path}/firmware-{board}-{version}.bin"
    
    # Zusätzliche Dateitypen (UF2, etc.)
    for ext in ["uf2", "hex"]:
        ext_file = Path(f"firmware/{board}/{version}/firmware-{board}-{version}.{ext}")
        if ext_file.exists():
            entry["bin_urls"][ext] = f"{base_url}/{firmware_path}/firmware-{board}-{version}.{ext}"
    
    return entry

def main():
    parser = argparse.ArgumentParser(description='Update firmware mapping')
    parser.add_argument('--version', required=True, help='Full version string')
    parser.add_argument('--short-version', required=True, help='Short version')
    parser.add_argument('--build-date', required=True, help='Build date (ISO format)')
    parser.add_argument('--boards', required=True, help='Space-separated board names')
    parser.add_argument('--release-url', required=True, help='Release URL')
    parser.add_argument('--mapping-file', default='data/device-firmware-mapping.json')
    parser.add_argument('--max-versions', type=int, default=10, help='Max versions per device')
    
    args = parser.parse_args()
    
    print(f"Updating firmware mapping for version: {args.version}")
    
    # Lade bestehendes Mapping
    mapping = load_mapping(args.mapping_file)
    board_mapping = get_board_to_hardware_mapping()
    display_names = get_hardware_display_names()
    
    boards = args.boards.strip().split()
    updated_devices = []
    
    for board in boards:
        if not board:  # Skip empty strings
            continue
            
        hw_slug = board_mapping.get(board, board.upper())
        display_name = display_names.get(hw_slug, hw_slug)
        
        print(f"Processing board: {board} -> {hw_slug} ({display_name})")
        
        # Hardware-Slug im Mapping anlegen falls nicht vorhanden
        if hw_slug not in mapping:
            mapping[hw_slug] = []
        
        # Prüfen ob Version bereits existiert
        existing_versions = [fw["id"] for fw in mapping[hw_slug]]
        if args.version in existing_versions:
            print(f"  Version {args.version} bereits vorhanden für {hw_slug}")
            continue
        
        # Neue Firmware-Entry erstellen
        firmware_entry = create_firmware_entry(
            args.version,
            args.short_version, 
            args.build_date,
            args.release_url,
            board,
            board,  # Verwende board name für Pfade
            display_name
        )
        
        # Prüfen ob mindestens eine bin_url vorhanden ist
        if not firmware_entry["bin_urls"]:
            print(f"  WARNUNG: Keine Firmware-Dateien für {board} gefunden")
            continue
        
        # Am Anfang der Liste einfügen (neueste Version zuerst)
        mapping[hw_slug].insert(0, firmware_entry)
        
        # Auf maximale Anzahl Versionen beschränken
        mapping[hw_slug] = mapping[hw_slug][:args.max_versions]
        
        updated_devices.append(hw_slug)
        print(f"  ✓ {hw_slug}: {len(firmware_entry['bin_urls'])} Dateien hinzugefügt")
    
    if updated_devices:
        # Mapping speichern
        save_mapping(args.mapping_file, mapping)
        print(f"\n✓ Mapping aktualisiert für: {', '.join(updated_devices)}")
        
        # Summary ausgeben
        print(f"\n=== Mapping Summary ===")
        for device in sorted(mapping.keys()):
            versions = len(mapping[device])
            latest = mapping[device][0]["id"] if versions > 0 else "none"
            print(f"  {device}: {versions} Versionen (latest: {latest})")
    else:
        print("\n! Keine Geräte aktualisiert")

if __name__ == "__main__":
    main()
