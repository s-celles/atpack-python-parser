#!/usr/bin/env python3
"""
Download AtPack files for CI testing.

This script downloads the AtPack files required for integration tests.
It's designed to be used in CI environments to set up test dependencies.
"""

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import time


# AtPack file definitions with download URLs and checksums
ATPACK_FILES = {
    "Atmel.ATmega_DFP.2.2.509.atpack": {
        "url": "http://packs.download.atmel.com/Atmel.ATmega_DFP.2.2.509.atpack",
        "sha256": "242a4aa941cce60f1cd6123e170035687373bf9b29c7d64af4dce1fe2fa401b4",  # Will be calculated on first download
        "description": "ATMEL ATmega Device Family Pack",
        "required_for": ["tests/integration/test_atmel_atmega.py"]
    },
    "Microchip.PIC16Fxxx_DFP.1.7.162.atpack": {
        "url": "https://packs.download.microchip.com/Microchip.PIC16Fxxx_DFP.1.7.162.atpack",
        "sha256": "f4e4cc7765be381ef08a7013caba848d84d02964dd7a2f9632824aa17f1c9d84",  # Will be calculated on first download
        "description": "Microchip PIC16F Device Family Pack",
        "required_for": [
            "tests/integration/test_microchip_pic16fxxx.py",
            "tests/test_hierarchical_memory.py"
        ]
    },
    "Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpack": {
        "url": "https://packs.download.microchip.com/Microchip.PIC24F-KA-KL-KM_DFP.1.5.253.atpack",
        "sha256": None,  # Will be calculated on first download
        "description": "Microchip PIC24F-KA-KL-KM Device Family Pack",
        "required_for": ["tests/integration/test_microchip_pic24f-ka-kl-km.py"]
    }
}

# Alternative mirror URLs (in case primary fails)
MIRROR_URLS = {
    "https://packs.download.microchip.com/": [
        "https://ww1.microchip.com/downloads/aemDocuments/documents/DEV_TOOLS/ProductDocuments/DeviceSupport/",
        # Add more mirrors if available
    ]
}


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def download_file(url: str, output_path: Path, timeout: int = 30) -> bool:
    """
    Download a file from URL to output_path.
    
    Args:
        url: URL to download from
        output_path: Local path to save the file
        timeout: Request timeout in seconds
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        print(f"  Downloading from: {url}")
        
        # Create a request with headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = Request(url, headers=headers)
        
        with urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                with open(output_path, 'wb') as f:
                    # Download in chunks to handle large files
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                return True
            else:
                print(f"  ❌ HTTP {response.status}: {response.reason}")
                return False
                
    except HTTPError as e:
        print(f"  ❌ HTTP Error: {e}")
        return False
    except URLError as e:
        print(f"  ❌ URL Error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def try_download_with_mirrors(filename: str, info: Dict, output_path: Path) -> bool:
    """Try downloading from primary URL and mirrors."""
    urls_to_try = [info["url"]]
    
    # Add mirror URLs
    primary_base = info["url"].rsplit('/', 1)[0] + '/'
    if primary_base in MIRROR_URLS:
        for mirror_base in MIRROR_URLS[primary_base]:
            mirror_url = mirror_base + filename
            urls_to_try.append(mirror_url)
    
    for url in urls_to_try:
        print(f"  Trying: {url}")
        if download_file(url, output_path):
            return True
        time.sleep(1)  # Brief delay between attempts
    
    return False


def download_atpack_file(filename: str, info: Dict, atpacks_dir: Path, force: bool = False) -> bool:
    """Download a single AtPack file."""
    output_path = atpacks_dir / filename
    
    # Check if file already exists
    if output_path.exists() and not force:
        file_size = output_path.stat().st_size
        if file_size > 0:
            print(f"✅ {filename} already exists ({file_size:,} bytes)")
            return True
        else:
            print(f"⚠️  {filename} exists but is empty, re-downloading...")
            output_path.unlink()
    
    print(f"📥 Downloading {filename}")
    print(f"  Description: {info['description']}")
    
    # Try downloading
    if try_download_with_mirrors(filename, info, output_path):
        # Verify the download
        if output_path.exists() and output_path.stat().st_size > 0:
            file_size = output_path.stat().st_size
            print(f"  ✅ Download successful ({file_size:,} bytes)")
            
            # Calculate and display SHA256 if not provided
            if info["sha256"] is None:
                sha256 = calculate_sha256(output_path)
                print(f"  🔐 SHA256: {sha256}")
            else:
                # Verify checksum if provided
                actual_sha256 = calculate_sha256(output_path)
                if actual_sha256 == info["sha256"]:
                    print(f"  ✅ SHA256 checksum verified")
                else:
                    print(f"  ❌ SHA256 mismatch!")
                    print(f"     Expected: {info['sha256']}")
                    print(f"     Actual:   {actual_sha256}")
                    return False
            
            return True
        else:
            print(f"  ❌ Download failed or file is empty")
            return False
    else:
        print(f"  ❌ Failed to download from all available URLs")
        return False


def list_atpack_files():
    """List all available AtPack files and their info."""
    print("📋 Available AtPack files:")
    print()
    
    for filename, info in ATPACK_FILES.items():
        print(f"• {filename}")
        print(f"  Description: {info['description']}")
        print(f"  URL: {info['url']}")
        print(f"  Required for:")
        for test_file in info['required_for']:
            print(f"    - {test_file}")
        print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Download AtPack files for CI testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Download all AtPack files
  %(prog)s --list                   # List available files
  %(prog)s --file atmega            # Download only ATmega DFP
  %(prog)s --file pic16f pic24f     # Download PIC16F and PIC24F DFPs
  %(prog)s --force                  # Force re-download existing files
  %(prog)s --output ./custom-dir    # Download to custom directory
        """
    )
    
    parser.add_argument(
        "--list", 
        action="store_true",
        help="List available AtPack files and exit"
    )
    
    parser.add_argument(
        "--file", 
        nargs="+", 
        metavar="PATTERN",
        help="Download specific files (partial name matching)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output directory (default: atpacks/)"
    )
    
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force re-download existing files"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Download timeout in seconds (default: 60)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_atpack_files()
        return 0
    
    # Determine output directory
    if args.output:
        atpacks_dir = args.output
    else:
        # Default to atpacks/ directory relative to script location
        script_dir = Path(__file__).parent
        atpacks_dir = script_dir / "atpacks"
    
    # Create output directory if it doesn't exist
    atpacks_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {atpacks_dir.absolute()}")
    print()
    
    # Determine which files to download
    files_to_download = {}
    
    if args.file:
        # Filter files based on patterns
        for pattern in args.file:
            pattern_lower = pattern.lower()
            for filename, info in ATPACK_FILES.items():
                if pattern_lower in filename.lower():
                    files_to_download[filename] = info
        
        if not files_to_download:
            print(f"❌ No files found matching patterns: {', '.join(args.file)}")
            print("Use --list to see available files")
            return 1
    else:
        # Download all files
        files_to_download = ATPACK_FILES
    
    # Download files
    print(f"📥 Downloading {len(files_to_download)} AtPack file(s)...")
    print()
    
    successful_downloads = 0
    failed_downloads = []
    
    for filename, info in files_to_download.items():
        try:
            if download_atpack_file(filename, info, atpacks_dir, args.force):
                successful_downloads += 1
            else:
                failed_downloads.append(filename)
        except KeyboardInterrupt:
            print("\n⏹️  Download interrupted by user")
            return 1
        except Exception as e:
            print(f"❌ Unexpected error downloading {filename}: {e}")
            failed_downloads.append(filename)
        
        print()  # Add spacing between downloads
    
    # Summary
    print("=" * 50)
    print(f"📊 Download Summary:")
    print(f"  ✅ Successful: {successful_downloads}")
    print(f"  ❌ Failed: {len(failed_downloads)}")
    
    if failed_downloads:
        print(f"\nFailed downloads:")
        for filename in failed_downloads:
            print(f"  • {filename}")
        print(f"\nYou can retry failed downloads with:")
        print(f"  {sys.argv[0]} --file {' '.join(failed_downloads)} --force")
    
    return 0 if len(failed_downloads) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
