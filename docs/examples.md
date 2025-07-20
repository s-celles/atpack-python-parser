# Examples

This page provides practical examples of using AtPack Parser for common tasks.

## Basic Examples

### Simple Device Information

#### ATMEL Example
```python
from atpack_parser import AtPackParser

# Parse a Microchip PIC AtPack file
parser = AtPackParser("Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
device = parser.get_device("PIC16F877")

print(f"""
PIC Device Information:
- Name: {device.name}
- Family: {device.family}  
- Architecture: {device.architecture}
- Series: {device.series}
- Memory segments: {len(device.memory_segments)}
- Modules: {len(device.modules)} peripherals
""")
```

### ATMEL Device Example

```python
from atpack_parser import AtPackParser

# Parse an ATMEL AtPack file
parser = AtPackParser("Atmel.ATmega_DFP.2.2.509.atpack")
device = parser.get_device("ATmega16")

print(f"""
ATMEL Device Information:
- Name: {device.name}
- Family: {device.family}  
- Architecture: {device.architecture}
- Series: {device.series}
- Flash: {len([m for m in device.memory_segments if 'FLASH' in m.name.upper()])} segments
- Modules: {len(device.modules)} peripherals
""")
```

#### PIC Example  
```python
from atpack_parser import AtPackParser

# Parse a Microchip PIC AtPack file
parser = AtPackParser("Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
device = parser.get_device("PIC16F877A")

print(f"""
PIC Device Information:
- Name: {device.name}
- Family: {device.family}
- Architecture: {device.architecture}
- Series: {device.series}
- Memory Segments: {len(device.memory_segments)}
- Config Words: {len(device.config_words)}
- Detected Peripherals: {', '.join(device.detected_peripherals[:5])}
""")
```

### List All Devices

#### ATMEL Example
```python
from atpack_parser import AtPackParser

parser = AtPackParser("Atmel.ATmega_DFP.2.2.509.atpack")
devices = parser.get_devices()

print(f"Found {len(devices)} ATMEL devices:")
for device_name in sorted(devices)[:10]:  # Show first 10
    try:
        device = parser.get_device(device_name)
        modules = len(device.modules)
        memory_segs = len(device.memory_segments)
        print(f"  {device_name:<15} - Modules: {modules:>2}, Memory: {memory_segs}")
    except Exception as e:
        print(f"  {device_name:<15} - Error: {e}")
```

#### PIC Example
```python
from atpack_parser import AtPackParser

parser = AtPackParser("Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
devices = parser.get_devices()

print(f"Found {len(devices)} PIC devices:")
for device_name in sorted(devices)[:10]:  # Show first 10
    try:
        device = parser.get_device(device_name)
        config_words = len(device.config_words)
        peripherals = len(device.detected_peripherals)
        print(f"  {device_name:<15} - Config: {config_words:>2}, Peripherals: {peripherals:>2}")
    except Exception as e:
        print(f"  {device_name:<15} - Error: {e}")
```

### Memory Layout Analysis

#### ATMEL Example
```python
from atpack_parser import AtPackParser

parser = AtPackParser("Atmel.ATmega_DFP.2.2.509.atpack")
device = parser.get_device("ATmega16")

print("ATMEL Memory Layout:")
print("-" * 50)
for segment in device.memory_segments:
    start = segment.start
    end = start + segment.size - 1
    print(f"{segment.name:<12} 0x{start:04X} - 0x{end:04X} ({segment.size:>5} bytes)")
```

#### PIC Example
```python
from atpack_parser import AtPackParser

parser = AtPackParser("Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
device = parser.get_device("PIC16F877A")

print("PIC Memory Layout:")
print("-" * 50)
for segment in device.memory_segments:
    start = segment.start
    size = segment.size
    access_type = getattr(segment, 'access', 'Unknown')
    print(f"{segment.name:<15} 0x{start:04X} ({size:>6} bytes) - {access_type}")
```

## Advanced Examples

### Register Analysis Tool

#### ATMEL Register Analysis
```python
from atpack_parser import AtPackParser
from collections import defaultdict

def analyze_atmel_registers(atpack_file, device_name):
    parser = AtPackParser(atpack_file)
    device = parser.get_device(device_name)
    
    print(f"ATMEL Register Analysis for {device_name}")
    print("=" * 60)
    
    for module in device.modules:
        print(f"\nModule: {module.name}")
        for reg_group in module.register_groups:
            if reg_group.registers:
                print(f"  Group: {reg_group.name} ({len(reg_group.registers)} registers)")
                for reg in reg_group.registers[:3]:  # Show first 3
                    print(f"    0x{reg.offset:04X} {reg.name:<12} ({reg.size}B)")
                    if reg.bitfields:
                        bf_names = [bf.name for bf in reg.bitfields[:3]]
                        print(f"         Bits: {', '.join(bf_names)}")

# Usage
analyze_atmel_registers("Atmel.ATmega_DFP.2.2.509.atpack", "ATmega16")
```

#### PIC Register Analysis  
```python
from atpack_parser import AtPackParser

def analyze_pic_registers(atpack_file, device_name):
    parser = AtPackParser(atpack_file)
    device = parser.get_device(device_name)
    
    print(f"PIC Register Analysis for {device_name}")
    print("=" * 60)
    
    # Group by detected peripherals
    peripherals = device.detected_peripherals
    print(f"Detected Peripherals: {', '.join(peripherals)}")
    
    # Show config words
    if device.config_words:
        print(f"\nConfiguration Words ({len(device.config_words)}):")
        for config in device.config_words[:3]:  # Show first 3
            print(f"  {config.name:<15} @ 0x{config.address:04X}")
            print(f"    Default: 0x{config.default_value:04X}, Mask: 0x{config.mask:04X}")
            if config.bitfields:
                for bf in config.bitfields[:3]:
                    print(f"      {bf.name}: bits {bf.bit_offset}-{bf.bit_offset+bf.bit_width-1}")

# Usage  
analyze_pic_registers("Microchip.PIC16Fxxx_DFP.1.7.162.atpack", "PIC16F877A")
```

### Device Comparison Tool

#### Compare ATMEL Devices
```python
from atpack_parser import AtPackParser

def compare_atmel_devices(atpack_file, device_names):
    parser = AtPackParser(atpack_file)
    
    comparison = {}
    for name in device_names:
        try:
            device = parser.get_device(name)
            comparison[name] = {
                "modules": len(device.modules),
                "memory_segments": len(device.memory_segments),
                "fuses": len(device.fuses),
                "interrupts": len(device.interrupts),
                "architecture": device.architecture,
                "series": device.series
            }
        except Exception as e:
            comparison[name] = {"error": str(e)}
    
    # Display comparison
    print("ATMEL Device Comparison")
    print("=" * 80)
    print(f"{'Device':<12} {'Modules':<8} {'Memory':<8} {'Fuses':<8} {'IRQs':<6} {'Architecture'}")
    print("-" * 80)
    
    for name, specs in comparison.items():
        if "error" in specs:
            print(f"{name:<12} Error: {specs['error']}")
        else:
            print(f"{name:<12} {specs['modules']:>6} {specs['memory_segments']:>8} "
                  f"{specs['fuses']:>6} {specs['interrupts']:>6} {specs['architecture']}")
    
    return comparison

# Compare ATmega devices
devices_to_compare = ["ATmega8", "ATmega16", "ATmega32", "ATmega64"]
comparison = compare_atmel_devices("Atmel.ATmega_DFP.2.2.509.atpack", devices_to_compare)
```

#### Compare PIC Devices
```python
from atpack_parser import AtPackParser

def compare_pic_devices(atpack_file, device_names):
    parser = AtPackParser(atpack_file)
    
    comparison = {}
    for name in device_names:
        try:
            device = parser.get_device(name)
            comparison[name] = {
                "config_words": len(device.config_words),
                "memory_segments": len(device.memory_segments),
                "peripherals": len(device.detected_peripherals),
                "signatures": len(device.signatures),
                "architecture": device.architecture,
                "power_specs": "Yes" if device.power_specs else "No"
            }
        except Exception as e:
            comparison[name] = {"error": str(e)}
    
    # Display comparison  
    print("PIC Device Comparison")
    print("=" * 85)
    print(f"{'Device':<15} {'Config':<8} {'Memory':<8} {'Periph':<8} {'Sigs':<6} {'Power'}")
    print("-" * 85)
    
    for name, specs in comparison.items():
        if "error" in specs:
            print(f"{name:<15} Error: {specs['error']}")
        else:
            print(f"{name:<15} {specs['config_words']:>6} {specs['memory_segments']:>8} "
                  f"{specs['peripherals']:>7} {specs['signatures']:>5} {specs['power_specs']}")
    
    return comparison

# Compare PIC16F devices
devices_to_compare = ["PIC16F84A", "PIC16F628A", "PIC16F877A", "PIC16F887"]
comparison = compare_pic_devices("Microchip.PIC16Fxxx_DFP.1.7.162.atpack", devices_to_compare)
```

### PlatformIO Board Generator

#### ATMEL Board Generator
```python
from atpack_parser import AtPackParser
import json
from pathlib import Path

def generate_atmel_platformio_boards(atpack_file, output_dir="atmel_boards"):
    parser = AtPackParser(atpack_file)
    devices = parser.get_devices()
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for device_name in devices[:5]:  # Process first 5 devices
        try:
            device = parser.get_device(device_name)
            
            # Generate ATMEL board JSON
            board_config = {
                "build": {
                    "mcu": device.name.lower(),
                    "core": "arduino",
                    "variant": "standard"
                },
                "frameworks": ["arduino"],
                "name": f"ATMEL {device.name}",
                "upload": {
                    "protocol": "avrisp",
                    "speed": 19200
                },
                "vendor": "Atmel",
                "debug": {
                    "tools": {
                        "avr-stub": {
                            "server": {
                                "executable": "bin/avarice"
                            }
                        }
                    }
                }
            }
            
            # Add memory info if available
            flash_segments = [m for m in device.memory_segments if 'FLASH' in m.name.upper()]
            if flash_segments:
                board_config["upload"]["maximum_size"] = flash_segments[0].size
            
            # Write board file
            board_file = output_path / f"atmel_{device.name.lower()}.json"
            with open(board_file, "w") as f:
                json.dump(board_config, f, indent=2)
            
            print(f"Generated ATMEL board: {board_file}")
            
        except Exception as e:
            print(f"Error processing {device_name}: {e}")

# Generate ATMEL boards
generate_atmel_platformio_boards("Atmel.ATmega_DFP.2.2.509.atpack")
```

#### PIC Board Generator
```python
from atpack_parser import AtPackParser
import json
from pathlib import Path

def generate_pic_platformio_boards(atpack_file, output_dir="pic_boards"):
    parser = AtPackParser(atpack_file)
    devices = parser.get_devices()
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for device_name in devices[:5]:  # Process first 5 devices
        try:
            device = parser.get_device(device_name)
            
            # Generate PIC board JSON
            board_config = {
                "build": {
                    "mcu": device.name.lower(),
                    "core": "pic",
                    "variant": "standard"
                },
                "frameworks": ["pic"],
                "name": f"Microchip {device.name}",
                "upload": {
                    "protocol": "pickit2",
                    "require_upload_port": True
                },
                "vendor": "Microchip",
                "debug": {
                    "tools": {
                        "pickit2": {
                            "server": {
                                "executable": "bin/pk2cmd"
                            }
                        }
                    }
                }
            }
            
            # Add power specifications if available
            if device.power_specs:
                board_config["power"] = {
                    "vdd_min": device.power_specs.vdd_min,
                    "vdd_max": device.power_specs.vdd_max,
                    "vpp_default": device.power_specs.vpp_default
                }
            
            # Add memory info
            flash_segments = [m for m in device.memory_segments if 'FLASH' in m.name.upper() or 'PROGRAM' in m.name.upper()]
            if flash_segments:
                board_config["upload"]["maximum_size"] = flash_segments[0].size
            
            # Add peripheral info
            if device.detected_peripherals:
                board_config["peripherals"] = device.detected_peripherals[:10]
            
            # Write board file
            board_file = output_path / f"pic_{device.name.lower()}.json"
            with open(board_file, "w") as f:
                json.dump(board_config, f, indent=2)
            
            print(f"Generated PIC board: {board_file}")
            
        except Exception as e:
            print(f"Error processing {device_name}: {e}")

# Generate PIC boards
generate_pic_platformio_boards("Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
```

### Configuration Analysis Tool

#### ATMEL Fuse Configuration
```python
from atpack_parser import AtPackParser

def analyze_atmel_fuses(atpack_file, device_name):
    parser = AtPackParser(atpack_file)
    device = parser.get_device(device_name)
    
    print(f"ATMEL Fuse Configuration for {device_name}")
    print("=" * 60)
    
    if device.fuses:
        for fuse in device.fuses:
            print(f"\nFuse: {fuse.name}")
            if hasattr(fuse, 'address'):
                print(f"  Address: 0x{fuse.address:04X}")
            if hasattr(fuse, 'default_value'):
                print(f"  Default: 0x{fuse.default_value:02X}")
            
            if hasattr(fuse, 'bitfields') and fuse.bitfields:
                print("  Bit Fields:")
                for field in fuse.bitfields[:5]:  # Show first 5
                    print(f"    {field.name}: {field.caption or 'No description'}")
    else:
        print("No fuse information available")

# Analyze ATMEL fuses
analyze_atmel_fuses("Atmel.ATmega_DFP.2.2.509.atpack", "ATmega16")
```

#### PIC Configuration Words
```python
from atpack_parser import AtPackParser

def analyze_pic_config(atpack_file, device_name):
    parser = AtPackParser(atpack_file)
    device = parser.get_device(device_name)
    
    print(f"PIC Configuration for {device_name}")
    print("=" * 60)
    
    if device.config_words:
        print(f"Configuration Words ({len(device.config_words)}):")
        for config in device.config_words:
            print(f"\n{config.name} @ 0x{config.address:04X}")
            print(f"  Default: 0x{config.default_value:04X}")
            print(f"  Mask: 0x{config.mask:04X}")
            
            if config.bitfields:
                print("  Bit Fields:")
                for field in config.bitfields[:5]:  # Show first 5
                    bit_end = field.bit_offset + field.bit_width - 1
                    if field.bit_width == 1:
                        bit_range = str(field.bit_offset)
                    else:
                        bit_range = f"{bit_end}:{field.bit_offset}"
                    print(f"    [{bit_range:>5}] {field.name}")
    
    # Show power specifications
    if device.power_specs:
        print(f"\nPower Specifications:")
        if device.power_specs.vdd_min:
            print(f"  VDD: {device.power_specs.vdd_min}V - {device.power_specs.vdd_max}V")
        if device.power_specs.vpp_default:
            print(f"  VPP: {device.power_specs.vpp_default}V")
    
    # Show detected peripherals
    if device.detected_peripherals:
        print(f"\nDetected Peripherals:")
        for peripheral in device.detected_peripherals:
            print(f"  - {peripheral}")

# Analyze PIC configuration
analyze_pic_config("Microchip.PIC16Fxxx_DFP.1.7.162.atpack", "PIC16F877A")
```

## Data Processing Examples

### Export to CSV

#### Export ATMEL Devices
```python
from atpack_parser import AtPackParser
import csv

def export_atmel_devices_to_csv(atpack_file, output_file="atmel_devices.csv"):
    parser = AtPackParser(atpack_file)
    devices = parser.get_devices()
    
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "family", "architecture", "series", "modules", 
                     "memory_segments", "fuses", "interrupts"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        processed = 0
        for device_name in devices:
            try:
                device = parser.get_device(device_name)
                writer.writerow({
                    "name": device.name,
                    "family": device.family.value,
                    "architecture": device.architecture or "Unknown",
                    "series": device.series or "Unknown",
                    "modules": len(device.modules),
                    "memory_segments": len(device.memory_segments),
                    "fuses": len(device.fuses),
                    "interrupts": len(device.interrupts)
                })
                processed += 1
            except Exception as e:
                print(f"Error processing {device_name}: {e}")
    
    print(f"Exported {processed} ATMEL devices to {output_file}")

export_atmel_devices_to_csv("Atmel.ATmega_DFP.2.2.509.atpack")
```

#### Export PIC Devices  
```python
from atpack_parser import AtPackParser
import csv

def export_pic_devices_to_csv(atpack_file, output_file="pic_devices.csv"):
    parser = AtPackParser(atpack_file)
    devices = parser.get_devices()
    
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "family", "architecture", "series", "config_words",
                     "memory_segments", "peripherals", "signatures", "power_specs"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        processed = 0
        for device_name in devices:
            try:
                device = parser.get_device(device_name)
                writer.writerow({
                    "name": device.name,
                    "family": device.family.value,
                    "architecture": device.architecture or "Unknown", 
                    "series": device.series or "Unknown",
                    "config_words": len(device.config_words),
                    "memory_segments": len(device.memory_segments),
                    "peripherals": len(device.detected_peripherals),
                    "signatures": len(device.signatures),
                    "power_specs": "Yes" if device.power_specs else "No"
                })
                processed += 1
            except Exception as e:
                print(f"Error processing {device_name}: {e}")
    
    print(f"Exported {processed} PIC devices to {output_file}")

export_pic_devices_to_csv("Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
```

### Generate Documentation

#### ATMEL Device Documentation
```python
from atpack_parser import AtPackParser

def generate_atmel_device_docs(atpack_file, device_name, output_file=None):
    parser = AtPackParser(atpack_file)
    device = parser.get_device(device_name)
    
    if not output_file:
        output_file = f"{device_name}_atmel_docs.md"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {device_name} - ATMEL Device Documentation\n\n")
        
        # Device info
        f.write("## Device Information\n\n")
        f.write(f"- **Family**: {device.family.value}\n")
        f.write(f"- **Architecture**: {device.architecture}\n")
        f.write(f"- **Series**: {device.series}\n")
        f.write(f"- **Modules**: {len(device.modules)}\n")
        f.write(f"- **Memory Segments**: {len(device.memory_segments)}\n")
        f.write(f"- **Fuses**: {len(device.fuses)}\n")
        f.write(f"- **Interrupts**: {len(device.interrupts)}\n\n")
        
        # Memory layout
        f.write("## Memory Layout\n\n")
        f.write("| Segment | Start Address | Size | Type |\n")
        f.write("|---------|---------------|------|---------|\n")
        for segment in device.memory_segments:
            segment_type = getattr(segment, 'type', 'Unknown')
            f.write(f"| {segment.name} | 0x{segment.start:04X} | "
                   f"{segment.size} bytes | {segment_type} |\n")
        f.write("\n")
        
        # Modules summary
        if device.modules:
            f.write("## Peripheral Modules\n\n")
            f.write("| Module | Register Groups | Total Registers |\n")
            f.write("|--------|-----------------|----------------|\n")
            for module in device.modules:
                total_regs = sum(len(rg.registers) for rg in module.register_groups)
                f.write(f"| {module.name} | {len(module.register_groups)} | {total_regs} |\n")
    
    print(f"Generated ATMEL documentation: {output_file}")

# Generate ATMEL docs
generate_atmel_device_docs("Atmel.ATmega_DFP.2.2.509.atpack", "ATmega16")
```

#### PIC Device Documentation
```python  
from atpack_parser import AtPackParser

def generate_pic_device_docs(atpack_file, device_name, output_file=None):
    parser = AtPackParser(atpack_file)
    device = parser.get_device(device_name)
    
    if not output_file:
        output_file = f"{device_name}_pic_docs.md"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# {device_name} - PIC Device Documentation\n\n")
        
        # Device info
        f.write("## Device Information\n\n")
        f.write(f"- **Family**: {device.family.value}\n") 
        f.write(f"- **Architecture**: {device.architecture}\n")
        f.write(f"- **Series**: {device.series}\n")
        f.write(f"- **Configuration Words**: {len(device.config_words)}\n")
        f.write(f"- **Memory Segments**: {len(device.memory_segments)}\n")
        f.write(f"- **Detected Peripherals**: {len(device.detected_peripherals)}\n")
        f.write(f"- **Signatures**: {len(device.signatures)}\n\n")
        
        # Configuration words
        if device.config_words:
            f.write("## Configuration Words\n\n")
            f.write("| Name | Address | Default | Mask | Bitfields |\n")
            f.write("|------|---------|---------|------|-----------|\n")
            for config in device.config_words:
                f.write(f"| {config.name} | 0x{config.address:04X} | "
                       f"0x{config.default_value:04X} | 0x{config.mask:04X} | "
                       f"{len(config.bitfields)} |\n")
            f.write("\n")
        
        # Detected peripherals
        if device.detected_peripherals:
            f.write("## Detected Peripherals\n\n")
            for peripheral in device.detected_peripherals:
                f.write(f"- {peripheral}\n")
            f.write("\n")
        
        # Power specifications
        if device.power_specs:
            f.write("## Power Specifications\n\n")
            f.write("| Parameter | Min | Max | Default |\n")
            f.write("|-----------|-----|-----|---------|\n")
            if device.power_specs.vdd_min:
                f.write(f"| VDD | {device.power_specs.vdd_min}V | {device.power_specs.vdd_max}V | - |\n")
            if device.power_specs.vpp_default:
                f.write(f"| VPP | - | - | {device.power_specs.vpp_default}V |\n")
            f.write("\n")
    
    print(f"Generated PIC documentation: {output_file}")

# Generate PIC docs
generate_pic_device_docs("Microchip.PIC16Fxxx_DFP.1.7.162.atpack", "PIC16F877A")
```

## CLI Integration Examples

### Batch Processing Script

#### Process ATMEL AtPacks
```python
#!/usr/bin/env python3
import subprocess
import json
from pathlib import Path

def process_atmel_atpacks(directory):
    """Process all ATMEL AtPack files in a directory"""
    atpack_dir = Path(directory)
    results = {}
    
    for atpack_file in atpack_dir.glob("*ATmega*.atpack"):  # Focus on ATmega
        print(f"Processing ATMEL {atpack_file.name}...")
        
        try:
            # Get device list using CLI
            result = subprocess.run([
                "atpack", "devices", "list", str(atpack_file), "--format", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                devices = json.loads(result.stdout)
                results[atpack_file.name] = {
                    "device_count": len(devices),
                    "sample_devices": devices[:5],  # First 5 devices
                    "type": "ATMEL"
                }
            else:
                results[atpack_file.name] = {"error": result.stderr}
        except Exception as e:
            results[atpack_file.name] = {"error": str(e)}
    
    # Save results
    with open("atmel_batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Processed {len(results)} ATMEL AtPack files")
    return results

# Usage
results = process_atmel_atpacks("./atpacks")
```

#### Process PIC AtPacks
```python
#!/usr/bin/env python3
import subprocess
import json
from pathlib import Path

def process_pic_atpacks(directory):
    """Process all PIC AtPack files in a directory"""
    atpack_dir = Path(directory)
    results = {}
    
    for atpack_file in atpack_dir.glob("*PIC*.atpack"):  # Focus on PIC
        print(f"Processing PIC {atpack_file.name}...")
        
        try:
            # Get device list using CLI
            result = subprocess.run([
                "atpack", "devices", "list", str(atpack_file), "--format", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                devices = json.loads(result.stdout)
                results[atpack_file.name] = {
                    "device_count": len(devices),
                    "sample_devices": devices[:5],  # First 5 devices
                    "type": "PIC"
                }
                
                # Get detailed info for first device if available
                if devices:
                    first_device = devices[0]
                    device_result = subprocess.run([
                        "atpack", "devices", "info", first_device, str(atpack_file), "--format", "json"
                    ], capture_output=True, text=True)
                    
                    if device_result.returncode == 0:
                        device_info = json.loads(device_result.stdout)
                        results[atpack_file.name]["sample_device_info"] = device_info
            else:
                results[atpack_file.name] = {"error": result.stderr}
        except Exception as e:
            results[atpack_file.name] = {"error": str(e)}
    
    # Save results
    with open("pic_batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Processed {len(results)} PIC AtPack files")
    return results

# Usage
results = process_pic_atpacks("./atpacks")
```

### Device Search Tool

#### Search ATMEL Devices
```python
import subprocess
import json
import re

def search_atmel_devices(pattern, atpack_directory):
    """Search for ATMEL devices matching a pattern across AtPacks"""
    from pathlib import Path
    
    atpack_dir = Path(atpack_directory)
    matches = []
    
    for atpack_file in atpack_dir.glob("*ATmega*.atpack"):
        try:
            # Get devices from this ATMEL AtPack
            result = subprocess.run([
                "atpack", "devices", "list", str(atpack_file), "--format", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                devices = json.loads(result.stdout)
                
                # Search for pattern
                regex = re.compile(pattern, re.IGNORECASE)
                for device in devices:
                    if regex.search(device):
                        matches.append({
                            "device": device,
                            "atpack": atpack_file.name,
                            "family": "ATMEL"
                        })
        except Exception as e:
            print(f"Error processing {atpack_file.name}: {e}")
    
    # Display results
    print(f"Found {len(matches)} ATMEL devices matching '{pattern}':")
    for match in sorted(matches, key=lambda m: m["device"]):
        print(f"  {match['device']:<20} in {match['atpack']}")
    
    return matches

# Search for all ATtiny devices in ATMEL packs
matches = search_atmel_devices(r"ATtiny\d+", "./atpacks")
```

#### Search PIC Devices
```python  
import subprocess
import json
import re

def search_pic_devices(pattern, atpack_directory):
    """Search for PIC devices matching a pattern across AtPacks"""
    from pathlib import Path
    
    atpack_dir = Path(atpack_directory)
    matches = []
    
    for atpack_file in atpack_dir.glob("*PIC*.atpack"):
        try:
            # Get devices from this PIC AtPack
            result = subprocess.run([
                "atpack", "devices", "list", str(atpack_file), "--format", "json"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                devices = json.loads(result.stdout)
                
                # Search for pattern
                regex = re.compile(pattern, re.IGNORECASE)
                for device in devices:
                    if regex.search(device):
                        # Get additional device info
                        device_result = subprocess.run([
                            "atpack", "devices", "info", device, str(atpack_file), "--format", "json"
                        ], capture_output=True, text=True, timeout=10)
                        
                        device_info = {"name": device}
                        if device_result.returncode == 0:
                            try:
                                parsed_info = json.loads(device_result.stdout)
                                device_info.update(parsed_info)
                            except:
                                pass
                        
                        matches.append({
                            "device": device,
                            "atpack": atpack_file.name,
                            "family": "PIC",
                            "info": device_info
                        })
        except Exception as e:
            print(f"Error processing {atpack_file.name}: {e}")
    
    # Display results
    print(f"Found {len(matches)} PIC devices matching '{pattern}':")
    for match in sorted(matches, key=lambda m: m["device"]):
        print(f"  {match['device']:<20} in {match['atpack']}")
    
    return matches

# Search for PIC16F87x series devices  
matches = search_pic_devices(r"PIC16F87\w+", "./atpacks")

# Search for all PIC18 devices
pic18_matches = search_pic_devices(r"PIC18F\d+", "./atpacks")
```

These examples demonstrate the versatility of AtPack Parser for both ATMEL and PIC devices, covering various tasks from device information extraction to complex data processing and integration with other tools. The examples now show the different data models and capabilities available for each device family.
