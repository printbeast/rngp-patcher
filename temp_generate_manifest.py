"""
RNGP Patcher - Manifest Generator
Automatically creates patch_manifest.json from a folder of files
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime


def calculate_md5(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error calculating MD5 for {filepath}: {e}")
        return ""


def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except Exception:
        return 0


def generate_manifest(source_folder, base_url_path="https://raw.githubusercontent.com/printbeast/rngp-patcher/master/patch_files", version="1.0.0"):
    """
    Generate a patch manifest from a folder of files
    
    Args:
        source_folder: Path to folder containing files to patch
        base_url_path: Base path for downloads (GitHub raw URL)
        version: Version number for this patch
    """

    source_path = Path(source_folder)

    if not source_path.exists():
        print(f"ERROR: Source folder does not exist: {source_folder}")
        return None

    print("=" * 60)
    print("RNGP Patcher - Manifest Generator")
    print("=" * 60)
    print(f"Source Folder: {source_path.absolute()}")
    print(f"Version: {version}")
    print(f"Base URL Path: {base_url_path}")
    print()

    # Collect all files recursively
    files = []
    file_count = 0
    total_size = 0

    print("Scanning files...")
    for root, dirs, filenames in os.walk(source_path):
        for filename in filenames:
            file_path = Path(root) / filename

            # Get relative path from source folder
            relative_path = file_path.relative_to(source_path)

            # Convert Windows paths to forward slashes for consistency
            relative_path_str = str(relative_path).replace("\\", "/")

            print(f"  Processing: {relative_path_str}...", end=" ")

            # Calculate MD5
            md5_hash = calculate_md5(file_path)
            file_size = get_file_size(file_path)

            if md5_hash and file_size > 0:
                # Build GitHub URL path
                github_url = f"{base_url_path}/{relative_path_str}"

                file_entry = {
                    "path": relative_path_str,
                    "url": github_url,
                    "size": file_size,
                    "md5": md5_hash,
                    "description": f"{filename}"
                }

                files.append(file_entry)
                file_count += 1
                total_size += file_size

                print(f"OK (MD5: {md5_hash[:8]}...)")
            else:
                print("SKIPPED (error)")

    # Create manifest
    manifest = {
        "version": version,
        "patch_date": datetime.now().strftime("%Y-%m-%d"),
        "description": f"RNGP Server Patch v{version}",
        "files": files,
        "notes": [
            "This patch was automatically generated",
            f"Contains {file_count} files",
            f"Total size: {total_size / (1024*1024):.2f} MB"
        ]
    }

    # Save manifest
    manifest_path = "patch_manifest.json"
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        print()
        print("=" * 60)
        print("MANIFEST GENERATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Files: {file_count}")
        print(f"Total Size: {total_size / (1024*1024):.2f} MB")
        print(f"Output: {manifest_path}")
        print()
        print("Next steps:")
        print("1. Review the generated patch_manifest.json")
        print("2. Upload all files to your Wasabi S3 bucket")
        print("3. Upload patch_manifest.json to bucket root")
        print("4. Test the patcher!")
        print()

        return manifest

    except Exception as e:
        print(f"ERROR: Could not save manifest: {e}")
        return None

def main():
    """Main entry point"""
    print()
    print("RNGP Patcher - Manifest Generator v1.0")
    print("=" * 40)
    print()

    # Get user input
    print("This tool will scan a folder and generate patch_manifest.json")
    print()

    source_folder = "patch_files"

    if not source_folder:
        print("ERROR: No folder specified")
        input("\nPress Enter to exit...")
        return

    print()
    version = "1.0.0"

    print()
    base_url = "https://raw.githubusercontent.com/printbeast/rngp-patcher/master/patch_files"

    print()
    print("Generating manifest...")
    print()

    manifest = generate_manifest(source_folder, base_url, version)

    if manifest:
        print("Done!")
    else:
        print("Failed to generate manifest")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
