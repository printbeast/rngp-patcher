"""
RNGP Game Patcher - Standalone Windows Application
Version: 1.0.0
Author: RNGP Development Team

This patcher connects to Wasabi S3 bucket to download and install game files.
No installation required - just run the executable!
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
import hashlib
import threading
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
import configparser

# GitHub Configuration
# IMPORTANT: Update these values with your GitHub repository details
# For local development, we'll use the local manifest file
GITHUB_CONFIG = {
    "repo_owner": "printbeast",             # Your GitHub username
    "repo_name": "rngp-patcher",            # Your repository name
    "manifest_url": "patch_manifest.json"   # Local manifest file for development
    # The manifest will contain direct download URLs to your GitHub Releases
}

class RNGPPatcher:
    def __init__(self, root):
        self.root = root
        self.root.title("RNGP - A Random Loot Progression Server - Game Patcher")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Set icon (will be embedded in exe)
        try:
            self.root.iconbitmap("RNGP_Logo.ico")
        except:
            pass
        
        # Variables
        self.game_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready to patch")
        self.progress_value = tk.DoubleVar(value=0)
        self.is_patching = False
        
        # Load saved settings
        self.config_file = "patcher_config.ini"
        self.load_config()
        
        # Build UI
        self.create_ui()
        
    def create_ui(self):
        """Create the main user interface"""
        
        # ===== Header Frame with Logo =====
        header_frame = tk.Frame(self.root, bg="#1a1a2e", height=200)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Load and display logo
        try:
            from PIL import Image, ImageTk
            logo_path = self.resource_path("RNGP_Logo.png")
            logo_image = Image.open(logo_path)
            # Resize to fit header
            logo_image = logo_image.resize((650, 180), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(header_frame, image=self.logo_photo, bg="#1a1a2e")
            logo_label.pack(pady=10)
        except Exception as e:
            # Fallback if logo can't be loaded
            title_label = tk.Label(
                header_frame, 
                text="RNGP\nA Random Loot Progression Server",
                font=("Arial", 24, "bold"),
                fg="#FFD700",
                bg="#1a1a2e"
            )
            title_label.pack(expand=True)
        
        # ===== Main Content Frame =====
        content_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Game Directory Selection
        dir_frame = tk.LabelFrame(content_frame, text="Game Directory", font=("Arial", 10, "bold"), padx=10, pady=10)
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        path_entry = tk.Entry(dir_frame, textvariable=self.game_path, font=("Arial", 9), state="readonly")
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(
            dir_frame,
            text="Browse",
            command=self.browse_directory,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            padx=15,
            cursor="hand2"
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Status Frame
        status_frame = tk.LabelFrame(content_frame, text="Status", font=("Arial", 10, "bold"), padx=10, pady=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Status text area (scrollable)
        self.status_display = tk.Text(
            status_frame,
            height=12,
            font=("Consolas", 9),
            bg="#ffffff",
            fg="#000000",
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.status_display.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar for status
        scrollbar = tk.Scrollbar(status_frame, command=self.status_display.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_display.config(yscrollcommand=scrollbar.set)
        
        # Progress Bar
        progress_frame = tk.Frame(content_frame, bg="#f0f0f0")
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_value,
            maximum=100,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Buttons Frame
        button_frame = tk.Frame(content_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X)
        
        # Check for Updates Button
        check_btn = tk.Button(
            button_frame,
            text="Check for Updates",
            command=self.check_updates,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        check_btn.pack(side=tk.LEFT, padx=5)
        
        # Patch Button
        self.patch_btn = tk.Button(
            button_frame,
            text="Start Patching",
            command=self.start_patching,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=30,
            pady=8,
            cursor="hand2"
        )
        self.patch_btn.pack(side=tk.LEFT, expand=True, padx=5)
        
        # Exit Button
        exit_btn = tk.Button(
            button_frame,
            text="Exit",
            command=self.exit_patcher,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        exit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Footer
        footer = tk.Label(
            content_frame,
            text="RNGP Patcher v1.0.0 | Visit us at rngp.example.com",
            font=("Arial", 8),
            fg="#666666",
            bg="#f0f0f0"
        )
        footer.pack(side=tk.BOTTOM, pady=(10, 0))
        
    def resource_path(self, relative_path):
        """Get absolute path to resource - works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def load_config(self):
        """Load saved configuration"""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file)
                if 'Settings' in config:
                    saved_path = config['Settings'].get('game_path', '')
                    if saved_path and os.path.exists(saved_path):
                        self.game_path.set(saved_path)
            except Exception as e:
                self.log_message(f"Could not load config: {e}", "WARNING")
    
    def save_config(self):
        """Save configuration"""
        config = configparser.ConfigParser()
        config['Settings'] = {
            'game_path': self.game_path.get()
        }
        try:
            with open(self.config_file, 'w') as f:
                config.write(f)
        except Exception as e:
            self.log_message(f"Could not save config: {e}", "WARNING")
    
    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(
            title="Select EverQuest Game Directory",
            initialdir=self.game_path.get() or "C:\\"
        )
        if directory:
            self.game_path.set(directory)
            self.save_config()
            self.log_message(f"Game directory set to: {directory}")
    
    def log_message(self, message, level="INFO"):
        """Add message to status display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}\n"
        
        self.status_display.config(state=tk.NORMAL)
        self.status_display.insert(tk.END, formatted_message)
        
        # Color coding
        if level == "ERROR":
            self.status_display.tag_add("error", "end-2l", "end-1l")
            self.status_display.tag_config("error", foreground="red")
        elif level == "SUCCESS":
            self.status_display.tag_add("success", "end-2l", "end-1l")
            self.status_display.tag_config("success", foreground="green")
        elif level == "WARNING":
            self.status_display.tag_add("warning", "end-2l", "end-1l")
            self.status_display.tag_config("warning", foreground="orange")
        
        self.status_display.see(tk.END)
        self.status_display.config(state=tk.DISABLED)
        self.root.update()
    
    def check_updates(self):
        """Check for available updates"""
        if not self.game_path.get():
            messagebox.showwarning("No Directory", "Please select your game directory first.")
            return
        
        self.log_message("Checking for updates...")
        
        # Run check in thread to avoid freezing UI
        thread = threading.Thread(target=self._check_updates_thread)
        thread.daemon = True
        thread.start()
    
    def _check_updates_thread(self):
        """Thread worker for checking updates"""
        try:
            # Check for old files that will be deleted
            files_to_delete = [
                "arena.eqg", "arena2.eqg", "arena2.zon", "arena2_EnvironmentEmitters.txt",
                "arena2_chr.txt", "arena_EnvironmentEmitters.txt", "highpasshold.eqg",
                "highpasshold.zon", "highpasshold_EnvironmentEmitters.txt", "lavastorm.emt",
                "lavastorm.eqg", "lavastorm.mp3", "lavastorm_EnvironmentEmitters.txt",
                "lavastorm_chr.txt", "nektulos.eqg", "nektulos_EnvironmentEmitters.txt",
                "nro_assets.txt", "fieldofbone_environmentemitters.txt"
            ]
            
            game_path = Path(self.game_path.get())
            found_old_files = [f for f in files_to_delete if (game_path / f).exists()]
            
            if found_old_files:
                self.log_message(f"Found {len(found_old_files)} old files that will be deleted during patching", "WARNING")
            
            # Download manifest file from GitHub
            self.log_message(f"Fetching manifest...")
            
            manifest_url = GITHUB_CONFIG['manifest_url']
            
            # Check if manifest is local file or remote URL
            if manifest_url == "patch_manifest.json":
                # Load local manifest file
                try:
                    with open(manifest_url, 'r') as f:
                        manifest_data = f.read()
                    manifest = json.loads(manifest_data)
                except Exception as e:
                    self.log_message(f"Failed to load local manifest: {e}", "ERROR")
                    messagebox.showerror("Error", f"Could not load local manifest:\n{e}")
                    return
            else:
                # Load from remote URL
                with urllib.request.urlopen(manifest_url, timeout=10) as response:
                    manifest_data = response.read().decode()
                manifest = json.loads(manifest_data)
            
            # Get list of files that need updating
            files_to_update = self._compare_files(manifest)
            
            if not files_to_update and not found_old_files:
                self.log_message("Your game is up to date!", "SUCCESS")
                messagebox.showinfo("Up to Date", "Your game files are already up to date!")
            else:
                message_parts = []
                
                if found_old_files:
                    message_parts.append(f"{len(found_old_files)} old files will be deleted")
                
                if files_to_update:
                    total_size = sum(f['size'] for f in files_to_update)
                    size_mb = total_size / (1024 * 1024)
                    message_parts.append(f"{len(files_to_update)} files to update ({size_mb:.2f} MB)")
                    self.log_message(f"Found {len(files_to_update)} files to update ({size_mb:.2f} MB)", "SUCCESS")
                
                message = "\n".join(message_parts)
                message += "\n\nClick 'Start Patching' to begin."
                messagebox.showinfo("Updates Available", message)
                
        except urllib.error.HTTPError as e:
            self.log_message(f"HTTP Error: {e.code} - {e.reason}", "ERROR")
            if e.code == 404:
                messagebox.showerror("Error", "Patch manifest not found on GitHub.\n\nMake sure:\n1. Your repository exists\n2. patch_manifest.json is uploaded\n3. The URL in GITHUB_CONFIG is correct")
            else:
                messagebox.showerror("Error", f"Could not download manifest:\n{e.reason}")
        except urllib.error.URLError as e:
            self.log_message(f"Connection error: {e.reason}", "ERROR")
            messagebox.showerror("Connection Error", f"Could not connect to GitHub:\n{e.reason}\n\nCheck your internet connection.")
        except Exception as e:
            self.log_message(f"Error checking updates: {e}", "ERROR")
            messagebox.showerror("Error", f"An error occurred:\n{e}\n\nPlease check your connection and try again.")
    
    def _compare_files(self, manifest):
        """Compare local files with manifest"""
        files_to_update = []
        game_path = Path(self.game_path.get())
        
        for file_info in manifest.get('files', []):
            file_path = game_path / file_info['path']
            
            # Check if file exists
            if not file_path.exists():
                files_to_update.append(file_info)
                continue
            
            # Check file hash
            local_hash = self._calculate_md5(file_path)
            if local_hash != file_info.get('md5', ''):
                files_to_update.append(file_info)
        
        return files_to_update
    
    def _calculate_md5(self, file_path):
        """Calculate MD5 hash of a file"""
        md5_hash = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception:
            return ""
    
    def start_patching(self):
        """Start the patching process"""
        if not self.game_path.get():
            messagebox.showwarning("No Directory", "Please select your game directory first.")
            return
        
        if self.is_patching:
            messagebox.showinfo("Patching", "Patching is already in progress.")
            return
        
        # Confirm with user
        result = messagebox.askyesno(
            "Start Patching",
            "This will download and install game files.\nMake sure the game is closed.\n\nContinue?"
        )
        
        if not result:
            return
        
        self.is_patching = True
        self.patch_btn.config(state=tk.DISABLED, text="Patching...")
        self.log_message("Starting patch process...")
        
        # Run patching in thread
        thread = threading.Thread(target=self._patch_thread)
        thread.daemon = True
        thread.start()
    
    def _delete_old_files(self):
        """Delete specific old files before patching"""
        files_to_delete = [
            "arena.eqg",
            "arena2.eqg",
            "arena2.zon",
            "arena2_EnvironmentEmitters.txt",
            "arena2_chr.txt",
            "arena_EnvironmentEmitters.txt",
            "highpasshold.eqg",
            "highpasshold.zon",
            "highpasshold_EnvironmentEmitters.txt",
            "lavastorm.emt",
            "lavastorm.eqg",
            "lavastorm.mp3",
            "lavastorm_EnvironmentEmitters.txt",
            "lavastorm_chr.txt",
            "nektulos.eqg",
            "nektulos_EnvironmentEmitters.txt",
            "nro_assets.txt",
            "fieldofbone_environmentemitters.txt"
        ]
        
        game_path = Path(self.game_path.get())
        deleted_count = 0
        
        self.log_message("Checking for old files to delete...")
        
        for filename in files_to_delete:
            file_path = game_path / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                    self.log_message(f"Deleted: {filename}", "SUCCESS")
                    deleted_count += 1
                except Exception as e:
                    self.log_message(f"Failed to delete {filename}: {e}", "WARNING")
        
        if deleted_count > 0:
            self.log_message(f"Deleted {deleted_count} old files", "SUCCESS")
        else:
            self.log_message("No old files found to delete")
    
    def _patch_thread(self):
        """Thread worker for patching"""
        try:
            # Delete old files first
            self._delete_old_files()
            
            # Download manifest from GitHub
            self.log_message(f"Downloading manifest...")
            
            manifest_url = GITHUB_CONFIG['manifest_url']
            
            # Check if manifest is local file or remote URL
            if manifest_url == "patch_manifest.json":
                # Load local manifest file
                try:
                    with open(manifest_url, 'r') as f:
                        manifest_data = f.read()
                    manifest = json.loads(manifest_data)
                except Exception as e:
                    self.log_message(f"Failed to load local manifest: {e}", "ERROR")
                    messagebox.showerror("Error", f"Could not load local manifest:\n{e}")
                    self._patching_complete(False)
                    return
            else:
                # Load from remote URL
                with urllib.request.urlopen(manifest_url, timeout=10) as response:
                    manifest_data = response.read().decode()
                manifest = json.loads(manifest_data)
            
            # Get files to update
            files_to_update = self._compare_files(manifest)
            
            if not files_to_update:
                self.log_message("No files need updating!", "SUCCESS")
                self._patching_complete(True)
                return
            
            total_files = len(files_to_update)
            self.log_message(f"Downloading {total_files} files from GitHub...")
            
            # Download each file from GitHub
            for index, file_info in enumerate(files_to_update, 1):
                file_url = file_info['url']  # Direct GitHub URL
                local_path = Path(self.game_path.get()) / file_info['path']
                
                self.log_message(f"[{index}/{total_files}] Downloading: {file_info['path']}")
                
                # Create directory if needed
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download file from GitHub
                try:
                    urllib.request.urlretrieve(file_url, local_path)
                    
                    # Verify hash
                    if 'md5' in file_info:
                        local_hash = self._calculate_md5(local_path)
                        if local_hash != file_info['md5']:
                            self.log_message(f"Hash mismatch for {file_info['path']}", "WARNING")
                    
                except Exception as e:
                    self.log_message(f"Failed to download {file_info['path']}: {e}", "ERROR")
                    continue
                
                # Update progress
                progress = (index / total_files) * 100
                self.progress_value.set(progress)
                self.root.update()
            
            self.log_message("Patching completed successfully!", "SUCCESS")
            self._patching_complete(True)
            
        except Exception as e:
            self.log_message(f"Patching failed: {e}", "ERROR")
            messagebox.showerror("Patching Failed", f"An error occurred:\n{e}\n\nPlease try again or contact support.")
            self._patching_complete(False)
    
    def _patching_complete(self, success):
        """Handle patching completion"""
        self.is_patching = False
        self.patch_btn.config(state=tk.NORMAL, text="Start Patching")
        self.progress_value.set(100 if success else 0)
        
        if success:
            messagebox.showinfo("Success", "Patching completed successfully!\nYour game is now up to date.")
        else:
            messagebox.showerror("Failed", "Patching failed. Check the status log for details.")
    
    def exit_patcher(self):
        """Exit the application"""
        if self.is_patching:
            result = messagebox.askyesno(
                "Patching in Progress",
                "Patching is still in progress.\nAre you sure you want to exit?"
            )
            if not result:
                return
        
        self.root.quit()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = RNGPPatcher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
