#!/usr/bin/env python3
"""
Validate firmware files and mapping consistency
"""

import json
import os
from pathlib import Path
from urllib.parse import urlparse

def main():
    print("=== Firmware Validation ===")
    
    # 1. Prüfe ob Mapping-Datei existiert und gültig ist
    mapping_file = "data/device-firmware-mapping.json"
    if not os.path.exists(mapping_file):
        print(f"ERROR: {mapping_file} nicht gefunden")
        return False
    
    try:
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Ungültiges JSON in {mapping_file}: {e}")
        return False
    
    print(f"✓ Mapping JSON gültig ({len(mapping)} Geräte)")
    
    # 2. Validiere Firmware-URLs und lokale Dateien
    errors = []
    warnings = []
    total_versions = 0
    
    for device, versions in mapping.items():
        print(f"\nValidating {device}:")
        total_versions += len(versions)
        
        for version_info in versions:
            version_id = version_info.get("id", "unknown")
            bin_urls = version_info.get("bin_urls", {})
            
            if not bin_urls:
                warnings.append(f"{device} {version_id}: Keine bin_urls")
                continue
            
            print(f"  Version {version_id}: {len(bin_urls)} Dateien")
            
            for url_type, url in bin_urls.items():
                # Parse URL um lokalen Pfad zu extrahieren
                parsed = urlparse(url)
                local_path = parsed.path
                
                # Entferne '/backend' prefix
                if local_path.startswith('/backend/'):
                    local_path = local_path[9:]
                
                full_local_path = Path(local_path)
                
                if not full_local_path.exists():
                    errors.append(f"{device} {version_id} {url_type}: Datei nicht gefunden: {full_local_path}")
                else:
                    file_size = full_local_path.stat().st_size
                    if file_size == 0:
                        errors.append(f"{device} {version_id} {url_type}: Datei ist leer: {full_local_path}")
                    elif file_size < 1000:  # < 1KB ist verdächtig für Firmware
                        warnings.append(f"{device} {version_id} {url_type}: Datei sehr klein ({file_size} bytes): {full_local_path}")
                    else:
                        print(f"    ✓ {url_type}: {file_size:,} bytes")
    
    # 3. Prüfe auf verwaiste Firmware-Dateien
    print(f"\n=== Checking for orphaned files ===")
    firmware_dir = Path("firmware")
    if firmware_dir.exists():
        all_mapped_files = set()
        
        # Sammle alle in Mapping referenzierten Dateien
        for device, versions in mapping.items():
            for version_info in versions:
                for url in version_info.get("bin_urls", {}).values():
                    parsed = urlparse(url)
                    local_path = parsed.path
                    if local_path.startswith('/backend/'):
                        local_path = local_path[9:]
                    all_mapped_files.add(local_path)
        
        # Finde alle tatsächlichen Firmware-Dateien
        all_actual_files = set()
        for file_path in firmware_dir.rglob("*.bin"):
            rel_path = str(file_path)
            all_actual_files.add(rel_path)
        
        for file_path in firmware_dir.rglob("*.uf2"):
            rel_path = str(file_path)
            all_actual_files.add(rel_path)
        
        orphaned_files = all_actual_files - all_mapped_files
        if orphaned_files:
            print(f"Found {len(orphaned_files)} orphaned files:")
            for f in sorted(orphaned_files):
                print(f"  {f}")
        else:
            print("✓ No orphaned files")
    
    # 4. Zusammenfassung
    print(f"\n=== Validation Summary ===")
    print(f"Devices: {len(mapping)}")
    print(f"Total versions: {total_versions}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    if errors:
        print(f"\n❌ ERRORS:")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors:
        print(f"\n✅ Validation passed!")
        return True
    else:
        print(f"\n❌ Validation failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
