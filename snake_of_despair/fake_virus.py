"""
Fake virus prank - Shows a realistic Windows file deletion dialog as a joke.
This is purely cosmetic and doesn't actually delete anything!
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import random
import os


# Fake file paths that look scary but are completely made up
FAKE_FILES = [
    "C:\\Users\\{user}\\Documents\\passwords.txt",
    "C:\\Users\\{user}\\Desktop\\important_work.xlsx",
    "C:\\Users\\{user}\\Pictures\\family_photos\\vacation_2024.jpg",
    "C:\\Users\\{user}\\Documents\\tax_returns_2024.pdf",
    "C:\\Windows\\System32\\kernel32.dll",
    "C:\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data",
    "C:\\Users\\{user}\\Documents\\bank_statements.pdf",
    "C:\\Program Files\\Microsoft Office\\Office16\\WINWORD.EXE",
    "C:\\Users\\{user}\\Desktop\\crypto_wallet_backup.dat",
    "C:\\Users\\{user}\\Documents\\resume_final_FINAL_v3.docx",
    "C:\\Windows\\System32\\ntoskrnl.exe",
    "C:\\Users\\{user}\\Pictures\\Screenshots\\screenshot_private.png",
    "C:\\Users\\{user}\\Downloads\\totally_legal_movie.mp4",
    "C:\\Users\\{user}\\Documents\\diary_2024.txt",
    "C:\\Users\\{user}\\AppData\\Roaming\\Discord\\Local Storage\\leveldb",
    "C:\\Windows\\System32\\drivers\\etc\\hosts",
    "C:\\Users\\{user}\\Documents\\secret_plans.docx",
    "C:\\Program Files\\Steam\\steamapps\\common",
    "C:\\Users\\{user}\\.ssh\\id_rsa",
    "C:\\Users\\{user}\\Documents\\grandmas_recipes.pdf",
]


class FakeVirusWindow:
    """Creates a fake Windows file deletion dialog."""
    
    def __init__(self):
        self.root: tk.Tk | None = None
        self.running = False
        self.thread = None
        self.username = os.environ.get('USERNAME', 'User')
        
    def _create_window(self):
        """Create the fake deletion window."""
        self.root = tk.Tk()
        assert self.root is not None
        self.root.title("Deleting Files")
        self.root.geometry("450x180")
        self.root.resizable(False, False)
        
        # Make it look like a Windows dialog
        self.root.configure(bg='#f0f0f0')
        
        # Try to set Windows-like icon (folder icon)
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=15, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # Header with icon placeholder and title
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Folder icon (text representation)
        icon_label = tk.Label(header_frame, text="📁", font=('Segoe UI', 24), bg='#f0f0f0')
        icon_label.pack(side='left', padx=(0, 10))
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="Permanently Deleting Files...", 
            font=('Segoe UI', 11, 'bold'),
            bg='#f0f0f0',
            fg='#000000'
        )
        title_label.pack(side='left', anchor='w')
        
        # Current file label
        self.file_label = tk.Label(
            main_frame,
            text="Preparing...",
            font=('Segoe UI', 9),
            bg='#f0f0f0',
            fg='#444444',
            anchor='w',
            wraplength=400
        )
        self.file_label.pack(fill='x', pady=(5, 5))
        
        # Progress bar frame
        progress_frame = tk.Frame(main_frame, bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=(5, 10))
        
        # Style for progress bar (Windows green)
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "green.Horizontal.TProgressbar",
            troughcolor='#e0e0e0',
            background='#06b025',
            darkcolor='#06b025',
            lightcolor='#06b025',
            bordercolor='#bcbcbc'
        )
        
        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame,
            style="green.Horizontal.TProgressbar",
            orient='horizontal',
            length=420,
            mode='determinate'
        )
        self.progress.pack(fill='x')
        
        # Items remaining label
        self.items_label = tk.Label(
            main_frame,
            text="Items remaining: calculating...",
            font=('Segoe UI', 9),
            bg='#f0f0f0',
            fg='#666666',
            anchor='w'
        )
        self.items_label.pack(fill='x')
        
        # Bottom frame with cancel button
        bottom_frame = tk.Frame(main_frame, bg='#f0f0f0')
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        # Cancel button (doesn't actually do anything lol)
        cancel_btn = tk.Button(
            bottom_frame,
            text="Cancel",
            font=('Segoe UI', 9),
            width=10,
            command=self._fake_cancel,
            bg='#e1e1e1',
            activebackground='#c7c7c7',
            relief='solid',
            borderwidth=1
        )
        cancel_btn.pack(side='right')
        
        # Position window in bottom right (like Windows notifications)
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - 470
        y = screen_height - 250
        self.root.geometry(f"+{x}+{y}")
        
        # Prevent stealing focus from the game
        self.root.attributes('-topmost', True) # Keep it visible
        
        # Windows-specific: prevent focus steal
        try:
            # This combination is more aggressive in preventing focus.
            # -disabled makes it ignore mouse/keyboard events initially.
            # -toolwindow helps prevent it from getting focus or appearing in the taskbar.
            self.root.wm_attributes('-disabled', True)
            self.root.wm_attributes('-toolwindow', 1)
        except:
            pass
        
        # Re-enable the window after a short delay so it's not permanently disabled.
        # This happens after it has already been drawn, avoiding the focus grab.
        if self.root:
            self.root.after(100, lambda: self.root and self.root.wm_attributes('-disabled', False))
    
    def _fake_cancel(self):
        """Fake cancel button - shows error message."""
        if self.root is None:
            return
        # Show a fake error that it can't be cancelled
        error_win = tk.Toplevel(self.root) 
        error_win.title("Error")
        error_win.geometry("300x100")
        error_win.resizable(False, False)
        error_win.configure(bg='#f0f0f0')
        error_win.transient(self.root)
        error_win.grab_set()
        
        # Center on parent
        error_win.geometry(f"+{self.root.winfo_x() + 75}+{self.root.winfo_y() + 40}")
        
        frame = tk.Frame(error_win, bg='#f0f0f0', padx=15, pady=15)
        frame.pack(fill='both', expand=True)
        
        tk.Label(
            frame,
            text="⚠️ Access Denied\nOperation cannot be cancelled.",
            font=('Segoe UI', 9),
            bg='#f0f0f0',
            justify='left'
        ).pack(pady=(0, 10))
        
        tk.Button(
            frame,
            text="OK",
            width=8,
            command=error_win.destroy,
            font=('Segoe UI', 9)
        ).pack()
        
    def _run_deletion_animation(self):
        """Animate the fake file deletion."""
        files = FAKE_FILES.copy()
        random.shuffle(files)
        
        # Replace {user} with actual username
        files = [f.replace("{user}", self.username) for f in files]
        
        total_files = len(files)
        
        for i, filepath in enumerate(files):
            if not self.running:
                break
                
            if self.root is None:
                break

            # Update UI
            try:
                # Truncate long paths
                display_path = filepath
                if len(display_path) > 55:
                    display_path = "..." + display_path[-52:]
                
                self.file_label.config(text=f"Deleting: {display_path}")
                self.progress['value'] = (i / total_files) * 100
                self.items_label.config(text=f"Items remaining: {total_files - i} ({self._random_size()} remaining)")
                self.root.update() 
            except:
                break
            
            # Random delay to simulate file deletion
            time.sleep(random.uniform(0.3, 1.5))
        
        # Finished - show completion
        if self.running and self.root:
            try:
                self.file_label.config(text="Deletion complete!")
                self.progress['value'] = 100
                self.items_label.config(text="All files have been permanently deleted.")
                self.root.update() 
                time.sleep(3)
                self._close()
            except:
                pass
    
    def _random_size(self):
        """Generate random file size string."""
        size = random.randint(1, 999)
        unit = random.choice(['KB', 'MB', 'GB'])
        return f"{size} {unit}"
    
    def start(self):
        """Start the fake virus window in a separate thread."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._thread_main, daemon=True)
        self.thread.start()
    
    def _thread_main(self):
        """Main thread function."""
        try:
            self._create_window()
            
            # Start deletion animation in another thread
            anim_thread = threading.Thread(target=self._run_deletion_animation, daemon=True)
            anim_thread.start()
            
            # Run tkinter main loop
            if self.root:
                self.root.mainloop()
        except Exception as e:
            print(f"Fake virus window error: {e}")
        finally:
            self.running = False
    
    def _close(self):
        """Close the window."""
        self.running = False
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
    
    def stop(self):
        """Stop and close the fake virus window."""
        self._close()


def start_fake_virus():
    """Convenience function to start the fake virus window."""
    virus = FakeVirusWindow()
    virus.start()
    return virus


# Test if run directly
if __name__ == "__main__":
    print("Starting fake virus window...")
    virus = start_fake_virus()
    input("Press Enter to stop...")
    virus.stop()
