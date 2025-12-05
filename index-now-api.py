"""
IndexNow API Tool
========================

A GUI application to interact with the IndexNow API.
Allows users to publish URLs to the IndexNow API.

Author: ALI MARESH
License: MIT
"""

import os
import json
import threading
import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext, font
import webbrowser

# Configuration
INDEXNOW_ENDPOINT = "https://www.bing.com/indexnow"
DEFAULT_KEY_FILE = "indexnow_key.txt"

# Theme Colors (Dark Modern)
BG_COLOR = "#0f1115"
PANEL_COLOR = "#14151A"
ACCENT_COLOR = "#6C63FF"
TEXT_COLOR = "#E6EDF3"
MUTED_COLOR = "#97A0B3"
INPUT_BG_COLOR = "#0d0f14"
ERROR_COLOR = "#FF6B6B"
SUCCESS_COLOR = "#4CD97B"

class IndexNowApp:
    """
    A GUI application to send URLs to the IndexNow API (Bing/Yandex).
    """
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_fonts()
        self.create_widgets()

    def setup_window(self):
        """Configure the main window settings."""
        self.root.title("IndexNow API Tool")
        self.root.geometry("720x480")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

    def setup_fonts(self):
        """Initialize custom fonts."""
        self.h1_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.h2_font = font.Font(family="Segoe UI", size=10, weight="bold")
        self.body_font = font.Font(family="Segoe UI", size=10)
        self.mono_font = font.Font(family="Consolas", size=10)

    def create_widgets(self):
        """Create and place all UI elements."""
        # Header
        tk.Label(self.root, text="IndexNow API Tool", bg=BG_COLOR, fg=TEXT_COLOR, font=self.h1_font).place(x=20, y=20)
        tk.Label(self.root, text="Instantly submit URLs to Bing & Yandex for indexing.", bg=BG_COLOR, fg=MUTED_COLOR, font=self.body_font).place(x=20, y=55)

        # API Key Input
        tk.Label(self.root, text="IndexNow Key:", bg=BG_COLOR, fg=TEXT_COLOR, font=self.h2_font).place(x=20, y=95)
        self.key_var = tk.StringVar()
        if os.path.isfile(DEFAULT_KEY_FILE):
            try:
                with open(DEFAULT_KEY_FILE, "r", encoding="utf-8") as f:
                    self.key_var.set(f.read().strip())
            except Exception:
                pass # Fail silently if file cannot be read

        self.key_entry = self.create_entry(self.key_var, placeholder="Enter your IndexNow key")
        self.key_entry.place(x=20, y=120)

        # URL Input
        tk.Label(self.root, text="URL to Index:", bg=BG_COLOR, fg=TEXT_COLOR, font=self.h2_font).place(x=20, y=165)
        self.url_var = tk.StringVar()
        self.url_entry = self.create_entry(self.url_var, placeholder="https://example.com/page-to-index")
        self.url_entry.place(x=20, y=190)

        # Send Button
        self.send_btn = tk.Button(self.root, text="Submit URL", command=self.on_send, bg=ACCENT_COLOR, fg="white", 
                                  relief="flat", font=self.h2_font, padx=20, pady=8, cursor="hand2", activebackground="#5a52d5", activeforeground="white")
        self.send_btn.place(x=20, y=235)

        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, bg=BG_COLOR, fg=MUTED_COLOR, font=self.body_font)
        self.status_label.place(x=140, y=242)

        # Response Area
        tk.Label(self.root, text="API Response:", bg=BG_COLOR, fg=TEXT_COLOR, font=self.h2_font).place(x=20, y=290)
        self.output = scrolledtext.ScrolledText(self.root, width=84, height=8, bg=INPUT_BG_COLOR, fg=TEXT_COLOR, 
                                                insertbackground=TEXT_COLOR, relief="flat", font=self.mono_font, borderwidth=1)
        self.output.place(x=20, y=315)

        # Footer / Credits
        link = tk.Label(self.root, text="Open Source Project", bg=BG_COLOR, fg=ACCENT_COLOR, font=self.body_font, cursor="hand2")
        link.place(x=20, y=450)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/")) # Placeholder for actual repo

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.on_send())

    def create_entry(self, variable, placeholder=""):
        """Helper to create styled entry widgets."""
        entry = tk.Entry(self.root, textvariable=variable, width=78, bg=INPUT_BG_COLOR, fg=TEXT_COLOR, 
                         insertbackground=TEXT_COLOR, relief="flat", font=self.body_font, borderwidth=5)
        # Simple placeholder logic could be added here if needed, but keeping it simple for now
        return entry

    def set_status(self, text, color=None):
        """Update the status label safely."""
        self.status_var.set(text)
        self.status_label.config(fg=color if color else MUTED_COLOR)
        self.root.update_idletasks()

    def on_send(self):
        """Handle the send button click."""
        t = threading.Thread(target=self.send_indexnow, daemon=True)
        t.start()

    def send_indexnow(self):
        """Execute the API request in a background thread."""
        self.send_btn.config(state="disabled", bg=MUTED_COLOR)
        self.output.delete(1.0, tk.END)
        
        key = self.key_var.get().strip()
        url = self.url_var.get().strip()

        if not key:
            messagebox.showerror("Missing Information", "Please enter your IndexNow API Key.")
            self.set_status("Error: Missing API Key", ERROR_COLOR)
            self.send_btn.config(state="normal", bg=ACCENT_COLOR)
            return
        
        if not url or not url.startswith("http"):
            messagebox.showerror("Invalid URL", "Please enter a valid URL starting with http:// or https://")
            self.set_status("Error: Invalid URL", ERROR_COLOR)
            self.send_btn.config(state="normal", bg=ACCENT_COLOR)
            return

        # Extract host from URL
        try:
            host = url.split("/")[2]
        except IndexError:
             messagebox.showerror("Invalid URL", "Could not parse hostname from URL.")
             self.set_status("Error: Invalid URL format", ERROR_COLOR)
             self.send_btn.config(state="normal", bg=ACCENT_COLOR)
             return

        payload = {
            "host": host,
            "key": key,
            "urlList": [url]
        }

        try:
            self.set_status("Sending request...", TEXT_COLOR)
            response = requests.post(INDEXNOW_ENDPOINT, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
            
            # Format response
            try:
                response_data = response.json()
                pretty_response = json.dumps(response_data, indent=2)
            except json.JSONDecodeError:
                pretty_response = response.text

            self.output.insert(tk.END, f"Status Code: {response.status_code}\n\nResponse Body:\n{pretty_response}")
            
            if response.status_code == 200:
                self.set_status("Success: URL submitted!", SUCCESS_COLOR)
            elif response.status_code == 202:
                 self.set_status("Success: Request accepted!", SUCCESS_COLOR)
            else:
                self.set_status(f"Failed: HTTP {response.status_code}", ERROR_COLOR)

        except requests.RequestException as e:
            self.output.insert(tk.END, f"Connection Error:\n{str(e)}")
            self.set_status("Connection Error", ERROR_COLOR)
        except Exception as e:
            self.output.insert(tk.END, f"Unexpected Error:\n{str(e)}")
            self.set_status("Unexpected Error", ERROR_COLOR)
        finally:
            self.send_btn.config(state="normal", bg=ACCENT_COLOR)


if __name__ == "__main__":
    root = tk.Tk()
    app = IndexNowApp(root)
    root.mainloop()
