#!/usr/bin/env python3
"""
Simple branch switcher for doc-scanner
Just run: python switch.py <branch-name>
"""
import subprocess
import sys
import os

def clean_workspace():
    """Clean problematic files before switching"""
    try:
        # Remove ChromaDB directory
        if os.path.exists("chroma_db"):
            subprocess.run(["rmdir", "/s", "/q", "chroma_db"], shell=True, check=False)
        
        # Remove cache directories  
        if os.path.exists("__pycache__"):
            subprocess.run(["rmdir", "/s", "/q", "__pycache__"], shell=True, check=False)
        
        # Clean git state
        subprocess.run(["git", "reset", "--hard"], check=False, capture_output=True)
        subprocess.run(["git", "clean", "-fd"], check=False, capture_output=True)
        
        print("✓ Workspace cleaned")
    except Exception as e:
        print(f"Warning: {e}")

def switch_branch(branch_name):
    """Switch to the specified branch"""
    try:
        result = subprocess.run(["git", "checkout", branch_name], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Successfully switched to: {branch_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to switch to {branch_name}: {e.stderr}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python switch.py <branch-name>")
        print("\nAvailable branches:")
        subprocess.run(["git", "branch", "-a"])
        return
    
    branch_name = sys.argv[1]
    print(f"Switching to: {branch_name}")
    
    clean_workspace()
    if switch_branch(branch_name):
        # Show current branch
        result = subprocess.run(["git", "branch", "--show-current"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Current branch: {result.stdout.strip()}")

if __name__ == "__main__":
    main()