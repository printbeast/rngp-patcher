#!/usr/bin/env python3
"""
Logo conversion utility for RNGP Patcher
Converts PNG logo to ICO format for Windows executable icon
"""

import os
from PIL import Image

def convert_logo():
    """Convert PNG logo to ICO format"""
    try:
        # Check if PNG logo exists
        if not os.path.exists("RNGP_Logo.png"):
            print("Warning: RNGP_Logo.png not found. Will use PNG only.")
            return False
            
        # Convert to ICO
        img = Image.open("RNGP_Logo.png")
        
        # Save as ICO (multiple sizes for better compatibility)
        img.save("RNGP_Logo.ico", format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
        
        print("Logo converted to ICO format")
        return True
        
    except Exception as e:
        print(f"Warning: Could not convert logo to ICO: {e}")
        print("Will use PNG logo only")
        return False

if __name__ == "__main__":
    convert_logo()