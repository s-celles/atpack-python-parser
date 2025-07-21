"""Tests for hierarchical memory layout functionality."""

import pytest
from src.atpack_parser import AtPackParser


def test_hierarchical_memory_pic():
    """Test hierarchical memory layout for PIC device."""
    parser = AtPackParser("./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
    
    # Test hierarchical memory spaces
    memory_spaces = parser.get_device_memory_hierarchical("PIC16F877")
    
    assert len(memory_spaces) >= 2  # Should have at least ProgramSpace and DataSpace
    
    # Check ProgramSpace
    program_space = next((s for s in memory_spaces if s.name == "ProgramSpace"), None)
    assert program_space is not None
    assert program_space.space_type == "ProgramSpace"
    assert len(program_space.segments) > 0
    
    # Check that program space contains PROG segments
    prog_segments = [s for s in program_space.segments if s.name.startswith("PROG")]
    assert len(prog_segments) >= 1
    
    # Verify hierarchy information
    for segment in program_space.segments:
        assert segment.parent_name == "ProgramSpace"
        assert segment.level == 1

    # Check DataSpace
    data_space = next((s for s in memory_spaces if s.name == "DataSpace"), None)
    assert data_space is not None
    assert data_space.space_type == "DataSpace"
    assert len(data_space.segments) > 0
    
    # Check that data space contains SFR bank segments
    sfr_segments = [s for s in data_space.segments if s.name.startswith("SFR_BANK")]
    assert len(sfr_segments) >= 1
    
    # Verify hierarchy information
    for segment in data_space.segments:
        assert segment.parent_name == "DataSpace"
        assert segment.level == 1


def test_hierarchical_memory_atmel():
    """Test hierarchical memory layout for ATMEL device."""
    parser = AtPackParser("./atpacks/Atmel.ATmega_DFP.2.2.509.atpack")
    
    # Test hierarchical memory spaces
    memory_spaces = parser.get_device_memory_hierarchical("ATmega16")
    
    assert len(memory_spaces) > 0
    
    # Check that we have common address spaces
    space_names = [s.name for s in memory_spaces]
    assert "prog" in space_names
    assert "data" in space_names
    
    # Check prog address space
    prog_space = next((s for s in memory_spaces if s.name == "prog"), None)
    assert prog_space is not None
    assert prog_space.space_type == "address-space"
    assert len(prog_space.segments) > 0
    
    # Check for FLASH segment
    flash_segments = [s for s in prog_space.segments if s.name == "FLASH"]
    assert len(flash_segments) == 1
    
    # Verify hierarchy information
    for segment in prog_space.segments:
        assert segment.parent_name == "prog"
        assert segment.level == 1

    # Check data address space
    data_space = next((s for s in memory_spaces if s.name == "data"), None)
    assert data_space is not None
    assert len(data_space.segments) > 0
    
    # Check for typical data segments
    data_segment_names = [s.name for s in data_space.segments]
    assert "IRAM" in data_segment_names


def test_flat_vs_hierarchical_consistency():
    """Test that flat and hierarchical memory views are consistent."""
    parser = AtPackParser("./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
    
    # Get flat memory layout
    flat_memory = parser.get_device_memory("PIC16F877")
    flat_segments = {seg.name for seg in flat_memory}
    
    # Get hierarchical memory layout
    hierarchical_memory = parser.get_device_memory_hierarchical("PIC16F877")
    hierarchical_segments = set()
    for space in hierarchical_memory:
        for segment in space.segments:
            hierarchical_segments.add(segment.name)
    
    # Both should contain the same segments (names might differ slightly due to parsing differences)
    # At minimum, check that major segments are present in both
    assert len(flat_segments.intersection(hierarchical_segments)) > 0


def test_memory_hierarchy_levels():
    """Test that memory hierarchy levels are correctly assigned."""
    parser = AtPackParser("./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
    
    memory_spaces = parser.get_device_memory_hierarchical("PIC16F877")
    
    for space in memory_spaces:
        for segment in space.segments:
            # All segments should be level 1 (children of memory spaces)
            assert segment.level == 1
            # All segments should have a parent name
            assert segment.parent_name is not None


def test_memory_segments_ordered_ascending():
    """Test that memory segments are ordered by ascending address."""
    parser = AtPackParser("./atpacks/Microchip.PIC16Fxxx_DFP.1.7.162.atpack")
    
    # Test hierarchical memory
    memory_spaces = parser.get_device_memory_hierarchical("PIC16F877")
    
    for space in memory_spaces:
        if len(space.segments) > 1:
            prev_start = -1
            for segment in space.segments:
                assert segment.start >= prev_start, f"Segments not ordered in {space.name}: {segment.name} at {segment.start:x} comes after {prev_start:x}"
                prev_start = segment.start
    
    # Test flat memory
    flat_memory = parser.get_device_memory("PIC16F877")
    if len(flat_memory) > 1:
        prev_start = -1
        for segment in flat_memory:
            assert segment.start >= prev_start, f"Flat segments not ordered: {segment.name} at {segment.start:x} comes after {prev_start:x}"
            prev_start = segment.start
