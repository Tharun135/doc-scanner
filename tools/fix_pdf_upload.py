#!/usr/bin/env python3
"""
Quick fix script for PDF upload issues - helps identify and resolve file locks
"""

import os
import psutil
import sys

def check_pdf_processes():
    """Check for processes that might be locking PDF files"""
    
    print("🔍 Checking for processes that might lock PDF files...")
    print()
    
    pdf_related_processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower()
                
                # Check for PDF-related processes
                pdf_keywords = ['adobe', 'acrobat', 'reader', 'pdf', 'foxit', 'chrome', 'edge', 'firefox']
                
                if any(keyword in proc_name for keyword in pdf_keywords):
                    pdf_related_processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'exe': proc_info['exe']
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return
    
    if pdf_related_processes:
        print("📋 Found PDF-related processes:")
        for proc in pdf_related_processes[:10]:  # Limit to first 10
            print(f"   • {proc['name']} (PID: {proc['pid']})")
    else:
        print("✅ No obvious PDF-related processes found")
    
    print()
    
    # Check temp directory
    temp_dir = os.environ.get('TEMP', os.environ.get('TMP', '/tmp'))
    print(f"🗂️ Checking temp directory: {temp_dir}")
    
    try:
        temp_files = [f for f in os.listdir(temp_dir) if f.lower().endswith('.pdf') and f.startswith('tmp')]
        if temp_files:
            print(f"⚠️ Found {len(temp_files)} temporary PDF files:")
            for tf in temp_files[:5]:  # Show first 5
                full_path = os.path.join(temp_dir, tf)
                try:
                    size = os.path.getsize(full_path)
                    print(f"   • {tf} ({size} bytes)")
                except OSError:
                    print(f"   • {tf} (access error)")
        else:
            print("✅ No temporary PDF files found")
    except Exception as e:
        print(f"❌ Error checking temp directory: {e}")
    
    print()
    print("🛠️ Recommendations:")
    print("1. Close any PDF viewers/readers before uploading")
    print("2. If upload still fails, restart your browser")
    print("3. Try uploading one file at a time")
    print("4. For large PDFs, try with smaller files first")
    
    return len(pdf_related_processes)

def clear_temp_pdfs():
    """Attempt to clear old temporary PDF files"""
    
    print("🧹 Attempting to clear old temporary PDF files...")
    
    temp_dir = os.environ.get('TEMP', os.environ.get('TMP', '/tmp'))
    cleared = 0
    errors = 0
    
    try:
        for filename in os.listdir(temp_dir):
            if filename.lower().endswith('.pdf') and filename.startswith('tmp'):
                file_path = os.path.join(temp_dir, filename)
                try:
                    os.unlink(file_path)
                    cleared += 1
                except OSError:
                    errors += 1
    
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return 0, 0
    
    print(f"✅ Cleared {cleared} temp files, {errors} files could not be removed")
    return cleared, errors

if __name__ == "__main__":
    print("🔧 PDF Upload Issue Diagnostic Tool")
    print("=" * 50)
    print()
    
    pdf_procs = check_pdf_processes()
    print()
    
    cleared, errors = clear_temp_pdfs()
    print()
    
    if pdf_procs > 0:
        print("💡 Try closing PDF applications and uploading again")
    else:
        print("✅ System looks clear for PDF uploads")
    
    print()
    print("🚀 Ready to try uploading again!")