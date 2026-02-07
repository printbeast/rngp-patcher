# RNGP Game Patcher - Complete Setup Guide

## 📦 What You Get

This patcher system creates a **standalone Windows executable** that:
- ✅ Requires **NO installation** by players
- ✅ Has a **professional GUI** with your RNGP logo
- ✅ Downloads files from your **Wasabi S3 bucket**
- ✅ Verifies file integrity with **MD5 checksums**
- ✅ Shows **progress bar** and detailed logs
- ✅ Remembers the **game directory** between sessions
- ✅ Works on **any Windows PC** without Python

---

## 🚀 Quick Start (For Server Admins)

### Step 1: Setup Your Wasabi S3 Bucket

1. **Create a Wasabi Account** (if you don't have one)
   - Go to https://wasabi.com
   - Sign up for an account

2. **Create a Bucket**
   - Log into Wasabi Console
   - Create a new bucket (e.g., "rngp-patches")
   - Make it **publicly readable** (Settings → Permissions → Public Access)

3. **Upload Your Files**
   - Create a folder structure in your bucket:
     ```
     rngp-patches/
     ├── patch_manifest.json
     └── patches/
         ├── eqgame.exe
         ├── dbg.txt
         ├── UI/
         │   └── custom_ui.xml
         └── resources/
             └── items.txt
     ```

4. **Get Your Bucket URL**
   - Example: `https://s3.wasabisys.com/rngp-patches`
   - Or: `https://s3.us-east-1.wasabisys.com/rngp-patches`

### Step 2: Configure the Patcher

1. **Edit `rngp_patcher.py`** - Find the `WASABI_CONFIG` section (lines 30-36):

```python
WASABI_CONFIG = {
    "bucket_name": "rngp-patches",  # ← Your bucket name
    "region": "us-east-1",  # ← Your Wasabi region
    "endpoint": "s3.wasabisys.com",  # ← Your endpoint
    "base_url": "https://s3.wasabisys.com/rngp-patches",  # ← Full URL to your bucket
    "manifest_file": "patch_manifest.json"  # ← Manifest file name
}
```

2. **Create Your Manifest File** (`patch_manifest.json`):

```json
{
  "version": "1.0.0",
  "patch_date": "2024-02-07",
  "description": "RNGP Server Patch",
  "files": [
    {
      "path": "eqgame.exe",
      "url": "patches/eqgame.exe",
      "size": 5242880,
      "md5": "actual-md5-hash-here",
      "description": "Main game executable"
    },
    {
      "path": "dbg.txt",
      "url": "patches/dbg.txt",
      "size": 1024,
      "md5": "actual-md5-hash-here",
      "description": "Server configuration"
    }
  ],
  "notes": [
    "New random loot items added",
    "Oracle of Rebirth prestige system"
  ]
}
```

**Important**: 
- `path` = Where the file goes in the player's game folder
- `url` = Where the file is in your S3 bucket (relative to base_url)
- `md5` = The MD5 hash of the file (for verification)

### Step 3: Build the Executable

1. **Install Python** (if not installed)
   - Download from https://python.org
   - ✅ Check "Add Python to PATH" during installation

2. **Place Files in a Folder**
   ```
   patcher_project/
   ├── rngp_patcher.py
   ├── rngp_patcher.spec
   ├── build_patcher.bat
   ├── convert_logo.py
   ├── requirements.txt
   └── RNGP_Logo.png  ← Your logo (included)
   ```

3. **Run the Build Script**
   - Double-click `build_patcher.bat`
   - Wait 2-5 minutes for it to complete
   - You'll get: `RNGP_Patcher.exe`

4. **Test the Patcher**
   - Run `RNGP_Patcher.exe`
   - Select a test game directory
   - Click "Check for Updates"
   - Click "Start Patching"

5. **Distribute to Players**
   - Just give them `RNGP_Patcher.exe`
   - They don't need Python or anything else!

---

## 📋 Manifest File Guide

### How to Create the Manifest

The manifest file tells the patcher what files to download. You need to:

1. **List all files** you want to patch
2. **Calculate MD5 hashes** for each file
3. **Upload manifest** to your S3 bucket root

### Calculate MD5 Hashes

**Windows PowerShell:**
```powershell
Get-FileHash -Algorithm MD5 "eqgame.exe" | Select-Object -ExpandProperty Hash
```

**Windows Command Prompt:**
```cmd
certutil -hashfile eqgame.exe MD5
```

**Python Script** (if you prefer):
```python
import hashlib

def get_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

print(get_md5("eqgame.exe"))
```

### Manifest Structure Explained

```json
{
  "version": "1.0.0",           // Your patch version
  "patch_date": "2024-02-07",   // When you created this patch
  "description": "Description",  // What's in this patch
  
  "files": [
    {
      "path": "eqgame.exe",      // WHERE it goes (player's folder)
      "url": "patches/eqgame.exe", // WHERE it comes FROM (your S3 bucket)
      "size": 5242880,           // File size in bytes
      "md5": "hash",             // MD5 checksum for verification
      "description": "What is this file"
    }
  ],
  
  "notes": [
    "Patch note 1",
    "Patch note 2"
  ]
}
```

### Example: Complete Manifest

```json
{
  "version": "1.2.3",
  "patch_date": "2024-02-07",
  "description": "RNGP February Update - Random Loot v2",
  "files": [
    {
      "path": "eqgame.exe",
      "url": "patches/v1.2.3/eqgame.exe",
      "size": 8388608,
      "md5": "5d41402abc4b2a76b9719d911017c592",
      "description": "Updated game client"
    },
    {
      "path": "dbg.txt",
      "url": "patches/v1.2.3/dbg.txt",
      "size": 256,
      "md5": "098f6bcd4621d373cade4e832627b4f6",
      "description": "Server connection settings"
    },
    {
      "path": "UI/EQUI.xml",
      "url": "patches/v1.2.3/UI/EQUI.xml",
      "size": 4096,
      "md5": "7d793037a0760186574b0282f2f435e7",
      "description": "Custom UI framework"
    },
    {
      "path": "resources/spells_us.txt",
      "url": "patches/v1.2.3/resources/spells_us.txt",
      "size": 524288,
      "md5": "d41d8cd98f00b204e9800998ecf8427e",
      "description": "Spell data"
    }
  ],
  "notes": [
    "✨ Added 150+ new random loot items",
    "🔄 Oracle of Rebirth prestige system",
    "🐛 Fixed loot table bugs",
    "⚡ Performance improvements"
  ]
}
```

---

## 🔧 Wasabi S3 Setup Details

### Make Your Bucket Public

1. Go to Wasabi Console → Buckets
2. Click your bucket → Settings
3. Go to **Permissions** tab
4. Enable **"Allow public access"**
5. Click **"Save"**

### Set Bucket Policy (Optional but Recommended)

Add this policy to allow public read access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::rngp-patches/*"
    }
  ]
}
```

Replace `rngp-patches` with your actual bucket name.

### Test Your Setup

Try accessing your manifest directly in a browser:
```
https://s3.wasabisys.com/your-bucket-name/patch_manifest.json
```

If you see the JSON file, it's working! 🎉

---

## 🎯 How It Works

### Player Experience

1. **Download** `RNGP_Patcher.exe` from your website
2. **Run** the executable (no installation needed)
3. **Click Browse** and select their EverQuest folder
4. **Click "Check for Updates"** - sees what needs updating
5. **Click "Start Patching"** - downloads and installs files
6. **Done!** Game is patched and ready

### Behind the Scenes

1. Patcher connects to your Wasabi S3 bucket
2. Downloads `patch_manifest.json`
3. Compares local files with manifest (using MD5 hashes)
4. Downloads only files that are missing or outdated
5. Verifies each download with MD5 checksum
6. Shows progress and logs everything

---

## 📝 Updating Your Patches

When you want to release a new patch:

1. **Upload new/changed files** to your S3 bucket
2. **Calculate MD5 hashes** for the new files
3. **Update `patch_manifest.json`** with new file entries
4. **Upload the new manifest** to your S3 bucket
5. **Players run the patcher** - it automatically detects changes!

You don't need to rebuild the executable unless you change the patcher code itself.

---

## 🔍 Troubleshooting

### "Connection Error" when checking updates

**Problem**: Can't connect to Wasabi S3
**Solutions**:
- ✅ Verify your bucket URL is correct
- ✅ Check bucket is set to public access
- ✅ Make sure manifest file exists in bucket root
- ✅ Test URL in browser: `https://s3.wasabisys.com/your-bucket/patch_manifest.json`

### "Hash mismatch" warnings

**Problem**: Downloaded file doesn't match expected MD5
**Solutions**:
- ✅ Recalculate MD5 hash for the file
- ✅ Re-upload the file to S3
- ✅ Update manifest with correct hash
- ✅ Clear browser/CDN cache if using CloudFlare

### Files not updating

**Problem**: Patcher says "up to date" but files are wrong
**Solutions**:
- ✅ Check MD5 hash in manifest matches actual file
- ✅ Verify `path` in manifest matches actual file location
- ✅ Delete the file locally and re-patch to force download

### Build errors

**Problem**: `build_patcher.bat` fails
**Solutions**:
- ✅ Make sure Python is installed and in PATH
- ✅ Run: `python -m pip install --upgrade pip`
- ✅ Run: `python -m pip install -r requirements.txt`
- ✅ Check that `RNGP_Logo.png` exists in the folder

---

## 🎨 Customization

### Change the UI Colors

Edit `rngp_patcher.py` and modify these values:

```python
# Header background color
header_frame = tk.Frame(self.root, bg="#1a1a2e", height=200)

# Button colors
browse_btn = tk.Button(..., bg="#4CAF50", fg="white")  # Green
check_btn = tk.Button(..., bg="#2196F3", fg="white")   # Blue
patch_btn = tk.Button(..., bg="#FF9800", fg="white")   # Orange
exit_btn = tk.Button(..., bg="#f44336", fg="white")    # Red
```

### Change the Window Title

```python
self.root.title("Your Custom Title Here")
```

### Change the Footer Text

```python
footer = tk.Label(
    content_frame,
    text="Your custom text | yourwebsite.com",
    ...
)
```

### Add More Information

Add labels, text boxes, or links anywhere in the `create_ui()` method.

---

## 📊 Advanced Features

### Add Pre-Patch Backup

Add this to `_patch_thread()` before downloading:

```python
# Backup existing files before patching
backup_dir = Path(self.game_path.get()) / "backup"
backup_dir.mkdir(exist_ok=True)

for file_info in files_to_update:
    local_path = Path(self.game_path.get()) / file_info['path']
    if local_path.exists():
        backup_path = backup_dir / file_info['path']
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, backup_path)
```

### Add Download Speed Display

Track download speed and show it to users (requires modification to download function).

### Add Change Log Display

Parse the `notes` from manifest and display them in a popup or separate window.

---

## 📦 File Structure

```
Your Final Distribution:
├── RNGP_Patcher.exe  ← This is what players download
└── (That's it!)

Your Development Folder:
├── rngp_patcher.py          ← Main patcher code
├── rngp_patcher.spec        ← PyInstaller build config
├── build_patcher.bat        ← Build script
├── convert_logo.py          ← Logo converter
├── requirements.txt         ← Python dependencies
├── RNGP_Logo.png           ← Your logo (UI)
├── RNGP_Logo.ico           ← Your logo (icon) - generated
└── patch_manifest.json     ← Example manifest

Your Wasabi S3 Bucket:
rngp-patches/
├── patch_manifest.json      ← Patcher downloads this first
└── patches/
    ├── eqgame.exe
    ├── dbg.txt
    ├── UI/
    │   └── custom_ui.xml
    └── resources/
        └── items.txt
```

---

## 🎓 Best Practices

### For Patch Management

1. **Version your patches** - Use folders like `patches/v1.0/`, `patches/v1.1/`
2. **Keep old versions** - Don't delete old patches in case players need to rollback
3. **Test before releasing** - Always test the patcher with a clean game install
4. **Announce patches** - Let players know on Discord/forums when new patches are available
5. **Monitor downloads** - Check Wasabi S3 stats to see if patches are being downloaded

### For Security

1. **Use HTTPS** - Always use `https://` in your base URL (Wasabi provides this)
2. **Verify hashes** - The patcher already does this, don't skip it
3. **Don't include secrets** - Never put passwords/keys in the manifest or patcher
4. **Test malware** - Run the patcher through VirusTotal before distributing

### For Performance

1. **Compress large files** - Use ZIP for large files, extract after download
2. **CDN (optional)** - Use CloudFlare in front of Wasabi for faster downloads
3. **Partial updates** - Only include files that actually changed

---

## 💡 Tips & Tricks

### Faster Builds

After first build, you can use:
```bash
python -m PyInstaller rngp_patcher.spec
```

Instead of running the full `build_patcher.bat` every time.

### Testing Without Building

Just run the Python script directly:
```bash
python rngp_patcher.py
```

This is faster for testing changes.

### Multi-Region Support

If you have players in different regions, you can:
1. Create multiple S3 buckets (US, EU, Asia)
2. Add region selection dropdown in patcher
3. Change `WASABI_CONFIG['base_url']` based on selection

---

## ❓ FAQ

**Q: Do players need Python installed?**
A: No! The executable includes everything needed.

**Q: Does it work on Windows 7/8/10/11?**
A: Yes, works on all modern Windows versions.

**Q: Can I use Amazon S3 instead of Wasabi?**
A: Yes, just change the endpoint URL. Amazon S3 works the same way.

**Q: How much does Wasabi cost?**
A: ~$6/TB/month storage, no egress fees. Very affordable for game hosting.

**Q: Can I add a progress bar for individual files?**
A: Yes, but requires modifying the download code to track bytes downloaded.

**Q: Will antivirus flag the patcher?**
A: Possibly, as with any unsigned executable. You can code-sign it to prevent this.

**Q: Can I auto-update the patcher itself?**
A: Yes, but requires additional code to download and replace the executable.

---

## 📞 Support

If you need help:
1. Check the error log in the patcher (status window)
2. Review this documentation
3. Test your Wasabi bucket URL in a browser
4. Verify your manifest JSON is valid (use jsonlint.com)

---

## 🎉 You're Done!

You now have a professional, standalone game patcher! Your players will love how easy it is to stay updated.

**Next Steps:**
1. Build your patcher executable
2. Upload your game files to Wasabi
3. Create your manifest
4. Test everything
5. Distribute to players!

Good luck with RNGP! 🎮✨
