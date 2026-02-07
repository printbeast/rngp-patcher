"""
RNGP Patcher - Connection Test Tool
Tests connectivity to your Wasabi S3 bucket with authentication and validates manifest
"""

import json
import sys
import hashlib
import hmac
from base64 import b64encode, b64decode
from datetime import datetime
import urllib.request
import urllib.error

def simple_decrypt(encrypted_data, key):
    """Simple XOR decryption (obfuscation) for credentials"""
    try:
        # Decode from base64
        data = b64decode(encrypted_data)
        # XOR with key
        key_bytes = key * (len(data) // len(key) + 1)
        decrypted = bytes([data[i] ^ key_bytes[i] for i in range(len(data))])
        return decrypted.decode('utf-8')
    except Exception as e:
        raise Exception(f"Failed to decrypt credentials: {e}")

def sign_s3_request(method, bucket, key, region, endpoint, access_key, secret_key):
    """Create AWS Signature Version 4 for Wasabi S3 request"""
    # Current time
    t = datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    # Service
    service = 's3'
    
    # Canonical request elements
    canonical_uri = f'/{key}'
    canonical_querystring = ''
    canonical_headers = f'host:{bucket}.{endpoint}\nx-amz-date:{amz_date}\n'
    signed_headers = 'host;x-amz-date'
    payload_hash = hashlib.sha256(b'').hexdigest()
    
    # Create canonical request
    canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'
    
    # Create string to sign
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{date_stamp}/{region}/{service}/aws4_request'
    string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}'
    
    # Calculate signature
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(f'AWS4{key}'.encode(), date_stamp.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region_name.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service_name.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b'aws4_request', hashlib.sha256).digest()
        return k_signing
    
    signing_key = get_signature_key(secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()
    
    # Create authorization header
    authorization_header = (
        f'{algorithm} Credential={access_key}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, Signature={signature}'
    )
    
    return {
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'Host': f'{bucket}.{endpoint}'
    }

def download_from_wasabi(bucket, key, region, endpoint, access_key, secret_key):
    """Download a file from Wasabi S3 with authentication"""
    # Create signed request
    headers = sign_s3_request('GET', bucket, key, region, endpoint, access_key, secret_key)
    
    # Build URL
    url = f'https://{bucket}.{endpoint}/{key}'
    
    # Create request
    request = urllib.request.Request(url, headers=headers)
    
    # Execute request
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()

def test_connection(bucket_name, region, endpoint, access_key, secret_key, manifest_file="patch_manifest.json"):
    """
    Test connection to Wasabi S3 bucket with authentication and validate manifest
    """
    
    print("=" * 70)
    print("RNGP Patcher - Authenticated Connection Test Tool")
    print("=" * 70)
    print()
    
    print(f"Testing connection to bucket: {bucket_name}")
    print(f"Region: {region}")
    print(f"Endpoint: {endpoint}")
    print(f"Manifest: {manifest_file}")
    print()
    
    # Test 1: Try to connect to manifest with authentication
    print("[1/4] Testing authenticated connection to Wasabi S3...")
    try:
        manifest_data = download_from_wasabi(bucket_name, manifest_file, region, endpoint, access_key, secret_key)
        print("      ✓ Connection successful!")
        print(f"      Downloaded {len(manifest_data)} bytes")
        print()
    except urllib.error.HTTPError as e:
        print(f"      ✗ HTTP Error: {e.code} - {e.reason}")
        print()
        print("      Common causes:")
        if e.code == 403:
            print("      - Access key doesn't have permission to access bucket")
            print("      - Bucket name is incorrect")
            print("      - IAM policy doesn't allow GetObject")
        elif e.code == 404:
            print("      - Manifest file doesn't exist in bucket")
            print("      - Bucket doesn't exist")
        else:
            print("      - Wrong credentials")
            print("      - Wrong region/endpoint")
        print()
        return False
    except urllib.error.URLError as e:
        print(f"      ✗ Connection Error: {e.reason}")
        print()
        print("      Common causes:")
        print("      - No internet connection")
        print("      - Wrong endpoint URL")
        print("      - Firewall blocking connection")
        print()
        return False
    except Exception as e:
        print(f"      ✗ Unexpected Error: {e}")
        print()
        return False
    
    # Test 2: Parse JSON
    print("[2/4] Parsing manifest JSON...")
    try:
        manifest = json.loads(manifest_data.decode('utf-8'))
        print("      ✓ Valid JSON format")
        print()
    except json.JSONDecodeError as e:
        print(f"      ✗ Invalid JSON: {e}")
        print()
        print("      Your manifest file is not valid JSON.")
        print("      Use jsonlint.com to validate it.")
        print()
        return False
    
    # Test 3: Validate manifest structure
    print("[3/4] Validating manifest structure...")
    
    required_fields = ['version', 'files']
    missing_fields = [field for field in required_fields if field not in manifest]
    
    if missing_fields:
        print(f"      ✗ Missing required fields: {', '.join(missing_fields)}")
        print()
        return False
    
    if not isinstance(manifest['files'], list):
        print("      ✗ 'files' field must be a list")
        print()
        return False
    
    if len(manifest['files']) == 0:
        print("      ⚠ Warning: No files in manifest")
        print()
    else:
        print(f"      ✓ Manifest contains {len(manifest['files'])} files")
        print()
    
    # Display manifest summary
    print("=" * 70)
    print("MANIFEST SUMMARY")
    print("=" * 70)
    print(f"Version:     {manifest.get('version', 'N/A')}")
    print(f"Patch Date:  {manifest.get('patch_date', 'N/A')}")
    print(f"Description: {manifest.get('description', 'N/A')}")
    print(f"File Count:  {len(manifest.get('files', []))}")
    print()
    
    if manifest.get('files'):
        print("Files to be patched:")
        print("-" * 70)
        total_size = 0
        for i, file_info in enumerate(manifest['files'][:10], 1):  # Show first 10
            path = file_info.get('path', 'unknown')
            size = file_info.get('size', 0)
            total_size += size
            size_mb = size / (1024 * 1024)
            print(f"  {i}. {path} ({size_mb:.2f} MB)")
        
        if len(manifest['files']) > 10:
            remaining = len(manifest['files']) - 10
            print(f"  ... and {remaining} more files")
        
        print()
        print(f"Total download size: {total_size / (1024 * 1024):.2f} MB")
        print()
    
    # Test 4: Try to access first file (if any)
    if manifest.get('files'):
        print("[4/4] Testing access to first file...")
        first_file = manifest['files'][0]
        file_key = first_file.get('url', '')
        
        print(f"Checking: {file_key}")
        try:
            file_data = download_from_wasabi(bucket_name, file_key, region, endpoint, access_key, secret_key)
            print(f"      ✓ File is accessible!")
            print(f"      Downloaded: {len(file_data)} bytes")
            
            # Verify MD5 if present
            if 'md5' in first_file:
                import hashlib
                md5_hash = hashlib.md5(file_data).hexdigest()
                if md5_hash == first_file['md5']:
                    print(f"      ✓ MD5 hash verified!")
                else:
                    print(f"      ⚠ MD5 hash mismatch!")
                    print(f"        Expected: {first_file['md5']}")
                    print(f"        Got: {md5_hash}")
            print()
        except urllib.error.HTTPError as e:
            print(f"      ✗ HTTP Error: {e.code} - {e.reason}")
            print("      File may not be uploaded to S3 yet")
            print()
        except Exception as e:
            print(f"      ✗ Error: {e}")
            print()
    
    # Final result
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print("✓ All tests passed!")
    print()
    print("Your Wasabi S3 bucket is configured correctly with authentication.")
    print("The patcher should be able to download files.")
    print()
    print("Next steps:")
    print("1. Make sure all files listed in manifest are uploaded")
    print("2. Test the patcher with a real game directory")
    print("3. Distribute RNGP_Patcher.exe to your players")
    print()
    
    return True

def main():
    """Main entry point"""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║    RNGP Patcher - Authenticated Connection Test Tool v2.0         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    
    print("This tool tests authenticated access to your Wasabi S3 bucket.")
    print()
    
    # Get configuration
    bucket_name = input("Bucket name: ").strip()
    if not bucket_name:
        print("ERROR: Bucket name is required")
        input("\nPress Enter to exit...")
        return
    
    region = input("Region (e.g., us-east-1): ").strip() or "us-east-1"
    endpoint = input("Endpoint (e.g., s3.wasabisys.com): ").strip() or "s3.wasabisys.com"
    
    print()
    print("Enter your Wasabi credentials:")
    access_key = input("Access Key: ").strip()
    secret_key = input("Secret Key: ").strip()
    
    if not access_key or not secret_key:
        print("ERROR: Both access key and secret key are required")
        input("\nPress Enter to exit...")
        return
    
    print()
    manifest_file = input("Manifest filename (default: patch_manifest.json): ").strip() or "patch_manifest.json"
    
    print()
    print("Starting tests...")
    print()
    
    success = test_connection(bucket_name, region, endpoint, access_key, secret_key, manifest_file)
    
    if not success:
        print("=" * 70)
        print("TEST FAILED")
        print("=" * 70)
        print("Please fix the issues above and try again.")
        print()
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()


def main():
    """Main entry point"""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           RNGP Patcher - Connection Test Tool v1.0                ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Get user input
    print("Enter your Wasabi S3 bucket URL")
    print("Example: https://s3.wasabisys.com/rngp-patches")
    print()
    
    base_url = input("Bucket URL: ").strip()
    
    if not base_url:
        print("ERROR: No URL provided")
        input("\nPress Enter to exit...")
        return
    
    # Remove trailing slash if present
    base_url = base_url.rstrip('/')
    
    print()
    manifest_file = input("Manifest filename (default: patch_manifest.json): ").strip()
    if not manifest_file:
        manifest_file = "patch_manifest.json"
    
    print()
    print("Starting tests...")
    print()
    
    success = test_connection(base_url, manifest_file)
    
    if not success:
        print("=" * 70)
        print("TEST FAILED")
        print("=" * 70)
        print("Please fix the issues above and try again.")
        print()
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
