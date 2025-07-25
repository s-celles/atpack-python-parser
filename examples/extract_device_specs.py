#!/usr/bin/env python3
"""
Example: Extract device specifications from AtPack files

This example demonstrates how to extract comprehensive device specifications
including f_cpu, maximum_ram_size, maximum_size, Eeprom, EepromSize, Config, ConfigSize,
and GPR (General Purpose Register) information from PIC AtPack files.
"""

import sys
import json
import csv
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atpack_parser import AtPackParser, extract_device_specs_from_atpack, extract_all_device_specs_from_atpack


def extract_single_device_specs():
    """Extract specifications for a single device."""
    print("🔧 Extracting specifications for a single PIC device")
    print("=" * 60)
    
    # Path to PIC AtPack
    atpack_path = Path(__file__).parent.parent / "atpacks" / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
    
    if not atpack_path.exists():
        print(f"❌ AtPack file not found: {atpack_path}")
        return
    
    try:
        # Initialize parser
        parser = AtPackParser(str(atpack_path))
        print(f"✅ Loaded AtPack from: {atpack_path.name}")
        print(f"🏷️  Device family: {parser.device_family}")
        
        # Extract specs for a specific device
        device_name = "PIC16F877A"
        print(f"\n📋 Extracting specifications for {device_name}...")
        
        specs = parser.get_device_specs(device_name)
        
        print(f"\n📊 Device Specifications for {specs.device_name}:")
        print(f"   💻 Architecture: {specs.architecture}")
        print(f"   📦 Series: {specs.series}")
        print(f"   ⏰ CPU Frequency: {specs.f_cpu}")
        print(f"   💾 Program Memory (Flash): {specs.maximum_size} words")
        print(f"   🧠 Total RAM: {specs.maximum_ram_size} bytes")
        print(f"   💡 GPR Total: {specs.gpr_total_size} bytes")
        
        if specs.eeprom_size > 0:
            print(f"   💽 EEPROM: {specs.eeprom_size} bytes @ {specs.eeprom_addr}")
        else:
            print(f"   💽 EEPROM: Not available")
        
        if specs.config_size > 0:
            print(f"   ⚙️  Config Memory: {specs.config_size} bytes @ {specs.config_addr}")
        else:
            print(f"   ⚙️  Config Memory: Not available")
        
        print(f"\n🏦 GPR Memory Banks ({len(specs.gpr_sectors)} sectors):")
        for sector in specs.gpr_sectors:
            print(f"   - {sector.name}: 0x{sector.start_addr:04X}-0x{sector.end_addr:04X} ({sector.size} bytes) [Bank {sector.bank}]")
        
    except Exception as e:
        print(f"❌ Error extracting specifications: {e}")


def extract_all_device_specs():
    """Extract specifications for all devices in an AtPack."""
    print("\n\n🔧 Extracting specifications for all PIC devices")
    print("=" * 60)
    
    # Path to PIC AtPack
    atpack_path = Path(__file__).parent.parent / "atpacks" / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
    
    if not atpack_path.exists():
        print(f"❌ AtPack file not found: {atpack_path}")
        return
    
    try:
        # Initialize parser
        parser = AtPackParser(str(atpack_path))
        print(f"✅ Loaded AtPack from: {atpack_path.name}")
        
        # Extract specs for all devices
        print("📋 Extracting specifications for all devices...")
        all_specs = parser.get_all_device_specs()
        
        print(f"\n📊 Extracted specifications for {len(all_specs)} devices")
        
        # Show summary for first 10 devices
        print("\n📝 Summary of first 10 devices:")
        for i, specs in enumerate(all_specs[:10]):
            eeprom_info = f"{specs.eeprom_size}B" if specs.eeprom_size > 0 else "None"
            print(f"   {i+1:2d}. {specs.device_name:<12} - Flash: {specs.maximum_size:4d}W, RAM: {specs.maximum_ram_size:3d}B, EEPROM: {eeprom_info}")
        
        if len(all_specs) > 10:
            print(f"   ... and {len(all_specs) - 10} more devices")
        
        # Export to JSON
        output_json = Path("pic_device_specs.json")
        specs_data = [spec.model_dump() for spec in all_specs]
        with open(output_json, 'w') as f:
            json.dump(specs_data, f, indent=2)
        print(f"\n💾 Exported specifications to {output_json}")
        
        # Export to CSV
        output_csv = Path("pic_device_specs.csv")
        if all_specs:
            fieldnames = [
                'device_name', 'f_cpu', 'maximum_ram_size', 'maximum_size',
                'eeprom_addr', 'eeprom_size', 'config_addr', 'config_size',
                'gpr_total_size', 'architecture', 'series'
            ]
            
            with open(output_csv, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for spec in all_specs:
                    row = {
                        'device_name': spec.device_name,
                        'f_cpu': spec.f_cpu,
                        'maximum_ram_size': spec.maximum_ram_size,
                        'maximum_size': spec.maximum_size,
                        'eeprom_addr': spec.eeprom_addr,
                        'eeprom_size': spec.eeprom_size,
                        'config_addr': spec.config_addr,
                        'config_size': spec.config_size,
                        'gpr_total_size': spec.gpr_total_size,
                        'architecture': spec.architecture,
                        'series': spec.series,
                    }
                    writer.writerow(row)
            
            print(f"💾 Exported specifications to {output_csv}")
        
        # Show devices with EEPROM
        eeprom_devices = [spec for spec in all_specs if spec.eeprom_size > 0]
        print(f"\n💽 Devices with EEPROM ({len(eeprom_devices)} total):")
        for spec in eeprom_devices[:5]:  # Show first 5
            print(f"   - {spec.device_name}: {spec.eeprom_size} bytes @ {spec.eeprom_addr}")
        if len(eeprom_devices) > 5:
            print(f"   ... and {len(eeprom_devices) - 5} more devices with EEPROM")
        
        # Show GPR distribution
        print(f"\n🏦 GPR Memory Distribution:")
        gpr_sizes = {}
        for spec in all_specs:
            gpr_size = spec.gpr_total_size
            if gpr_size not in gpr_sizes:
                gpr_sizes[gpr_size] = []
            gpr_sizes[gpr_size].append(spec.device_name)
        
        for size in sorted(gpr_sizes.keys()):
            devices = gpr_sizes[size]
            print(f"   {size:3d} bytes: {len(devices)} devices (e.g., {devices[0]})")
        
    except Exception as e:
        print(f"❌ Error extracting specifications: {e}")


def demonstrate_gpr_details():
    """Demonstrate detailed GPR information extraction."""
    print("\n\n🏦 Detailed GPR (General Purpose Register) Information")
    print("=" * 60)
    
    # Path to PIC AtPack
    atpack_path = Path(__file__).parent.parent / "atpacks" / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
    
    if not atpack_path.exists():
        print(f"❌ AtPack file not found: {atpack_path}")
        return
    
    try:
        parser = AtPackParser(str(atpack_path))
        
        # Analyze GPR for different device types
        test_devices = ["PIC16F84A", "PIC16F877A", "PIC16F628A"]
        
        for device_name in test_devices:
            try:
                print(f"\n📋 GPR Analysis for {device_name}:")
                specs = parser.get_device_specs(device_name)
                
                print(f"   Total GPR: {specs.gpr_total_size} bytes across {len(specs.gpr_sectors)} banks")
                
                for sector in specs.gpr_sectors:
                    addr_range = f"0x{sector.start_addr:04X}-0x{sector.end_addr:04X}"
                    print(f"   🏛️  {sector.name}: {addr_range} ({sector.size} bytes)")
                
            except Exception as e:
                print(f"   ❌ Failed to analyze {device_name}: {e}")
    
    except Exception as e:
        print(f"❌ Error in GPR analysis: {e}")


def main():
    """Main function."""
    print("🚀 PIC Device Specifications Extraction Demo")
    print("=" * 60)
    
    # Extract specs for single device
    extract_single_device_specs()
    
    # Extract specs for all devices
    extract_all_device_specs()
    
    # Demonstrate GPR details
    demonstrate_gpr_details()
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main()
