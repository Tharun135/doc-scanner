#!/usr/bin/env python3
"""
Doc-Scanner Desktop Launcher
Double-click this file to start the application with a nice GUI.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import webbrowser
from pathlib import Path

class DocScannerLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Doc-Scanner Launcher")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # App process
        self.app_process = None
        self.is_running = False
        
        # Style configuration
        self.root.configure(bg='#2A3B5A')
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#2A3B5A')
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = tk.Label(
            header_frame, 
            text="🤖 Doc-Scanner", 
            font=("Arial", 24, "bold"),
            fg='#FFD700',
            bg='#2A3B5A'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="AI-Powered Document Review Assistant",
            font=("Arial", 12),
            fg='#CCCCCC',
            bg='#2A3B5A'
        )
        subtitle_label.pack()
        
        # Status
        status_frame = tk.Frame(self.root, bg='#2A3B5A')
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="● Ready to start",
            font=("Arial", 11),
            fg='#28a745',
            bg='#2A3B5A'
        )
        self.status_label.pack()
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='#2A3B5A')
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        self.start_button = tk.Button(
            button_frame,
            text="🚀 Start Doc-Scanner",
            command=self.start_app,
            font=("Arial", 12, "bold"),
            bg='#007bff',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="🛑 Stop Server",
            command=self.stop_app,
            font=("Arial", 12),
            bg='#dc3545',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.browser_button = tk.Button(
            button_frame,
            text="🌐 Open Browser",
            command=self.open_browser,
            font=("Arial", 12),
            bg='#28a745',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.browser_button.pack(side=tk.LEFT, padx=5)
        
        # Log output
        log_frame = tk.Frame(self.root, bg='#2A3B5A')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        log_label = tk.Label(
            log_frame,
            text="Application Log:",
            font=("Arial", 11, "bold"),
            fg='#CCCCCC',
            bg='#2A3B5A'
        )
        log_label.pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            bg='#1a1a1a',
            fg='#00ff00',
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Info footer
        info_frame = tk.Frame(self.root, bg='#2A3B5A')
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        info_label = tk.Label(
            info_frame,
            text="💡 The app will be available at http://localhost:5000 when started",
            font=("Arial", 9),
            fg='#888888',
            bg='#2A3B5A'
        )
        info_label.pack()
        
    def log_message(self, message):
        """Add message to log window."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def start_app(self):
        """Start the Doc-Scanner application."""
        if self.is_running:
            return
            
        try:
            self.log_message("🚀 Starting Doc-Scanner...")
            self.status_label.config(text="● Starting...", fg='#ffc107')
            
            # Check if run.py exists
            if not os.path.exists('run.py'):
                raise FileNotFoundError("run.py not found. Make sure you're in the correct directory.")
                
            # Start the Flask app
            self.app_process = subprocess.Popen(
                [sys.executable, 'run.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.browser_button.config(state=tk.NORMAL)
            
            self.status_label.config(text="● Running on http://localhost:5000", fg='#28a745')
            self.log_message("✅ Doc-Scanner started successfully!")
            self.log_message("📱 Server running on http://localhost:5000")
            self.log_message("🔍 Upload documents to analyze writing quality")
            
            # Start monitoring thread
            threading.Thread(target=self.monitor_app, daemon=True).start()
            
        except Exception as e:
            self.log_message(f"❌ Error starting app: {str(e)}")
            self.status_label.config(text="● Error", fg='#dc3545')
            messagebox.showerror("Error", f"Failed to start application:\n{str(e)}")
            
    def stop_app(self):
        """Stop the Doc-Scanner application."""
        if not self.is_running or not self.app_process:
            return
            
        try:
            self.log_message("🛑 Stopping Doc-Scanner...")
            self.app_process.terminate()
            self.app_process.wait(timeout=5)
            
        except subprocess.TimeoutExpired:
            self.log_message("⚠️ Force killing application...")
            self.app_process.kill()
            
        finally:
            self.is_running = False
            self.app_process = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.browser_button.config(state=tk.DISABLED)
            self.status_label.config(text="● Stopped", fg='#6c757d')
            self.log_message("✅ Doc-Scanner stopped")
            
    def open_browser(self):
        """Open the application in web browser."""
        if self.is_running:
            webbrowser.open('http://localhost:5000')
            self.log_message("🌐 Opening browser...")
        else:
            messagebox.showwarning("Warning", "Please start the application first.")
            
    def monitor_app(self):
        """Monitor the application process."""
        while self.is_running and self.app_process:
            if self.app_process.poll() is not None:
                # Process has ended
                self.log_message("⚠️ Application process ended unexpectedly")
                self.stop_app()
                break
                
            # Read any output
            try:
                output = self.app_process.stdout.readline()
                if output:
                    self.log_message(f"📝 {output.strip()}")
            except:
                pass
                
            threading.Event().wait(1)  # Check every second
            
    def on_closing(self):
        """Handle window closing."""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Application is running. Stop and quit?"):
                self.stop_app()
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the launcher."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    # Change to the script's directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    launcher = DocScannerLauncher()
    launcher.run()
