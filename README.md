## Neue Boards hinzufügen - Kompletter Prozess

### Schritt 1: Firmware Action erweitern

```yaml
env:
  BOARDS: "heltec-v3 heltec-wireless-tracker-V1-0 tbeam tlora-v2"  # Neue Boards hinzufügen
```

### Schritt 2: Backend Python Script erweitern

**In `scripts/update-mapping.py`:**

```python
def get_board_to_hardware_mapping() -> Dict[str, str]:
    """Mapping from PlatformIO board names to hardware slugs"""
    return {
        "heltec-v3": "HELTEC_V3",
        "heltec-wireless-tracker-V1-0": "HELTEC_TRACKER",
        "tbeam": "TBEAM",                    # NEU
        "tlora-v2": "TLORA_V2",             # NEU
        "tlora-v1": "TLORA_V1",
        "tlora-v1_3": "TLORA_V1_3",
        "techo": "TECHO"
    }

def get_hardware_display_names() -> Dict[str, str]:
    """Display names for hardware"""
    return {
        "HELTEC_V3": "Heltec V3",
        "HELTEC_TRACKER": "Heltec Wireless Tracker V1.0",
        "TBEAM": "TTGO T-Beam",             # NEU
        "TLORA_V2": "TTGO LoRa V2",         # NEU
        "TBEAM": "TTGO T-Beam", 
        "TLORA_V2": "TTGO LoRa V2",
        "TLORA_V1": "TTGO LoRa V1",
        "TLORA_V1_3": "TTGO LoRa V1.3",
        "TECHO": "T-Echo"
    }
```

### Schritt 3: Backend Hardware-Liste erweitern
kopieren aus: https://api.meshtastic.org/resource/deviceHardware

**`data/custom-hardware-list.json`:**

```json
[
  {
    "hwModel": 2,
    "hwModelSlug": "TBEAM",
    "platformioTarget": "tbeam",
    "architecture": "esp32",
    "activelySupported": true,
    "supportLevel": 1,
    "displayName": "TTGO T-Beam",
    "tags": ["esp32", "GPS"],
    "images": [],
    "partitionScheme": "4MB"
  },
  {
    "hwModel": 1,
    "hwModelSlug": "TLORA_V2",
    "platformioTarget": "tlora-v2",
    "architecture": "esp32",
    "activelySupported": true,
    "supportLevel": 1,
    "displayName": "TTGO LoRa V2",
    "tags": ["esp32"],
    "images": [],
    "partitionScheme": "4MB"
  }
]
```

### Schritt 4: Frontend FirmwareStore erweitern

**In `FirmwareStore.ts`:**

```typescript
const DEVICE_SPECIFIC_FIRMWARE: Record<string, FirmwareResource[]> = {
  'TLORA_V2': [],
  'TBEAM': [],
  'HELTEC_V3': [],
  'HELTEC_TRACKER': []  // Stelle sicher, dass das hier steht!
}
```
