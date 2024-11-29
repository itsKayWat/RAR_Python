import subprocess
import sys
import os

def install_requirements():
    print("Installing RAR_Python requirements...")
    
    requirements = [
        'pillow',           # Image handling
        'send2trash',       # Safe file deletion
        'rarfile',          # RAR file support
        'python-magic;platform_system!="Windows"',  # Mime type detection (non-Windows)
        'python-magic-bin;platform_system=="Windows"'  # Windows support
    ]
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
    except subprocess.CalledProcessError:
        print("Error: pip is not installed!")
        return False
    
    for req in requirements:
        try:
            print(f"Installing {req}...")
            subprocess.check_call([
                sys.executable,
                '-m',
                'pip',
                'install',
                '--upgrade',
                req
            ])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {req}: {e}")
            return False
    
    print("\nAll requirements installed successfully!")
    print("You can now run RAR_Python using: python RAR_Python.py")
    return True

if __name__ == "__main__":
    install_requirements()