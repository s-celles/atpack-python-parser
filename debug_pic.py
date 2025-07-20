#!/usr/bin/env python3

import zipfile
from pathlib import Path
from src.atpack_parser.pic_parser import PicParser

try:
    atpack_file = Path(__file__).parent / "atpacks" / "Microchip.PIC16Fxxx_DFP.1.7.162.atpack"
    pic_file = "edc/PIC16F876A.PIC"
    
    with zipfile.ZipFile(atpack_file, 'r') as zf:
        with zf.open(pic_file) as f:
            pic_content = f.read().decode('utf-8')

    pic_parser = PicParser(pic_content)

    # Test XPath queries directly
    print("Testing XPath queries:")

    # Check if we can find the device element
    device_elements = pic_parser.parser.xpath('//edc:PIC[@edc:name="PIC16F876A"]')
    print(f"Device elements found: {len(device_elements)}")

    if device_elements:
        device_element = device_elements[0]

        # Test memory parsing XPaths
        program_space = pic_parser.parser.xpath(".//edc:ProgramSpace", device_element)
        print(f"ProgramSpace elements: {len(program_space)}")

        data_space = pic_parser.parser.xpath(".//edc:DataSpace", device_element)
        print(f"DataSpace elements: {len(data_space)}")

        sfr_data_sectors = pic_parser.parser.xpath(
            ".//edc:SFRDataSector", device_element
        )
        print(f"SFRDataSector elements: {len(sfr_data_sectors)}")

        nmmr_places = pic_parser.parser.xpath(".//edc:NMMRPlace", device_element)
        print(f"NMMRPlace elements: {len(nmmr_places)}")

        # Check if local-name versions work
        program_space_ln = pic_parser.parser.xpath(
            './/*[local-name()="ProgramSpace"]', device_element
        )
        print(f"ProgramSpace elements (local-name): {len(program_space_ln)}")

        data_space_ln = pic_parser.parser.xpath(
            './/*[local-name()="DataSpace"]', device_element
        )
        print(f"DataSpace elements (local-name): {len(data_space_ln)}")

        # Test parsing methods directly
        print("\nTesting parsing methods:")

        # Debug memory segments parsing
        print("Debugging memory segments parsing:")
        program_space = pic_parser.parser.xpath(
            './/edc:ProgramSpace | .//*[local-name()="ProgramSpace"]', device_element
        )
        print(f"Found {len(program_space)} ProgramSpace elements")

        for ps in program_space:
            code_sectors = pic_parser.parser.xpath(
                './/edc:CodeSector | .//*[local-name()="CodeSector"]', ps
            )
            print(f"  Found {len(code_sectors)} CodeSector elements")
            for cs in code_sectors:
                # Debug attributes
                start_attr = pic_parser.parser.get_attr(cs, "beginaddr", "NOT_FOUND")
                end_attr = pic_parser.parser.get_attr(cs, "endaddr", "NOT_FOUND")
                name_attr = pic_parser.parser.get_attr(cs, "sectionname", "NOT_FOUND")
                print(
                    f"    Raw attrs: beginaddr={start_attr}, endaddr={end_attr}, sectionname={name_attr}"
                )

                start = pic_parser.parser.get_attr_hex(cs, "beginaddr", 0)
                end = pic_parser.parser.get_attr_hex(cs, "endaddr", 0)
                name = pic_parser.parser.get_attr(cs, "sectionname", "PROG")
                print(f"    {name}: 0x{start:04x} - 0x{end:04x}")

        data_space = pic_parser.parser.xpath(
            './/edc:DataSpace | .//*[local-name()="DataSpace"]', device_element
        )
        print(f"Found {len(data_space)} DataSpace elements")

        for ds in data_space:
            sfr_sectors = pic_parser.parser.xpath(
                './/edc:SFRDataSector | .//*[local-name()="SFRDataSector"]', ds
            )
            print(f"  Found {len(sfr_sectors)} SFRDataSector elements")
            for sfr in sfr_sectors:
                start = pic_parser.parser.get_attr_hex(sfr, "beginaddr", 0)
                end = pic_parser.parser.get_attr_hex(sfr, "endaddr", 0)
                bank = pic_parser.parser.get_attr(sfr, "bank", "0")
                print(f"    Bank {bank}: 0x{start:04x} - 0x{end:04x}")

        memory_segments = pic_parser._parse_memory_segments(device_element)
        print(f"Memory segments parsed: {len(memory_segments)}")
        for seg in memory_segments:
            print(
                f"  {seg.name}: 0x{seg.start:04x} - 0x{seg.start + seg.size:04x} ({seg.size} bytes)"
            )

        modules = pic_parser._parse_modules(device_element)
        print(f"Modules parsed: {len(modules)}")
        for mod in modules:
            print(f"  {mod.name}: {len(mod.register_groups)} register groups")

        # Test interrupt parsing
        print("\nTesting interrupt parsing:")
        interrupts = pic_parser._parse_interrupts(device_element)
        print(f"Interrupts parsed: {len(interrupts)}")
        for interrupt in interrupts:
            print(f"  {interrupt.name}: {interrupt.caption}")

        # Test metadata extraction
        print("\nTesting metadata extraction:")
        metadata = pic_parser._extract_metadata(device_element)
        print(f"Metadata: {metadata}")

        # Test device parsing
        print("\nFull device parsing:")
        device = pic_parser.parse_device("PIC16F876A")
        print(f"Device: {device.name}")
        print(f"Series: {device.series}")
        print(f"Interrupts: {len(device.interrupts)}")
        print(f"Signatures: {len(device.signatures)}")
        print(
            f"Metadata keys: {list(device.metadata.keys()) if device.metadata else 'None'}"
        )

except Exception as e:
    import traceback

    print(f"Error: {e}")
    traceback.print_exc()
