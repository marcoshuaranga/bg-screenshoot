"""Configuration dialog for Screenshot Capture"""

import contextlib
import logging
import tkinter as tk
from tkinter import messagebox, ttk

from config_manager import Config

logger = logging.getLogger(__name__)


class ConfigDialog:
    def __init__(self, config: Config, on_save_callback=None):
        self.config = config
        self.on_save_callback = on_save_callback
        self.window = None

    def show(self):
        """Show configuration dialog"""
        self.window = tk.Tk()
        self.window.title("⚙️ Screenshot Capture - Settings")
        self.window.geometry("500x400")
        self.window.resizable(False, False)

        # Create notebook (tabs)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Screenshot settings
        screenshot_frame = ttk.Frame(notebook)
        notebook.add(screenshot_frame, text="📸 Screenshot")
        self._create_screenshot_tab(screenshot_frame)

        # Tab 2: Google Drive settings
        drive_frame = ttk.Frame(notebook)
        notebook.add(drive_frame, text="☁️  Google Drive")
        self._create_drive_tab(drive_frame)

        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(button_frame, text="💾 Save", command=self._save).pack(side="right", padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=self.window.destroy).pack(side="right")

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"+{x}+{y}")

        self.window.mainloop()

    def _create_screenshot_tab(self, parent):
        """Create screenshot settings tab"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill="both", expand=True)

        # Interval
        ttk.Label(frame, text="⏰ Capture Interval:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        interval_frame = ttk.Frame(frame)
        interval_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        self.interval_var = tk.IntVar(value=self.config.interval)
        self.interval_slider = ttk.Scale(
            interval_frame,
            from_=10,
            to=3600,
            orient="horizontal",
            variable=self.interval_var,
            command=self._update_interval_label,
        )
        self.interval_slider.pack(fill="x", padx=(0, 10))

        self.interval_label = ttk.Label(interval_frame, text=self._format_interval(self.config.interval))
        self.interval_label.pack()

        # Quick presets
        ttk.Label(frame, text="Quick presets:", font=("Arial", 9)).grid(row=2, column=0, sticky="w", pady=(0, 5))

        preset_frame = ttk.Frame(frame)
        preset_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        presets = [("30s", 30), ("1min", 60), ("5min", 300), ("10min", 600), ("30min", 1800), ("1hr", 3600)]

        for text, value in presets:
            ttk.Button(preset_frame, text=text, width=8, command=lambda v=value: self._set_interval_preset(v)).pack(
                side="left", padx=2
            )

        # Prefix
        ttk.Label(frame, text="📝 Filename Prefix:", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky="w", pady=(0, 5)
        )

        self.prefix_var = tk.StringVar(value=self.config.prefix)
        ttk.Entry(frame, textvariable=self.prefix_var, width=40).grid(row=5, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(frame, text="Example: screenshot_20260527_170000.png", font=("Arial", 8), foreground="gray").grid(
            row=6, column=0, sticky="w"
        )

    def _create_drive_tab(self, parent):
        """Create Google Drive settings tab"""
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill="both", expand=True)

        # Enable/Disable
        self.gdrive_enabled_var = tk.BooleanVar(value=self.config.gdrive_enabled)
        ttk.Checkbutton(
            frame,
            text="☁️  Enable Google Drive Upload",
            variable=self.gdrive_enabled_var,
            command=self._toggle_gdrive_options,
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Folder name
        self.folder_frame = ttk.Frame(frame)
        self.folder_frame.grid(row=1, column=0, sticky="ew")

        ttk.Label(self.folder_frame, text="📁 Drive Folder Name:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )

        self.gdrive_folder_var = tk.StringVar(value=self.config.gdrive_folder)
        ttk.Entry(self.folder_frame, textvariable=self.gdrive_folder_var, width=40).grid(
            row=1, column=0, sticky="ew", pady=(0, 10)
        )

        ttk.Label(
            self.folder_frame,
            text="Folder will be created in your Google Drive root",
            font=("Arial", 8),
            foreground="gray",
        ).grid(row=2, column=0, sticky="w")

        # Info
        info_text = (
            "ℹ️  Note: You need to authenticate with Google Drive first.\n"
            "   If not configured, uploads will be disabled automatically."
        )
        ttk.Label(frame, text=info_text, font=("Arial", 9), foreground="blue").grid(
            row=2, column=0, sticky="w", pady=(20, 0)
        )

        self._toggle_gdrive_options()

    def _toggle_gdrive_options(self):
        """Enable/disable Google Drive options based on checkbox"""
        state = "normal" if self.gdrive_enabled_var.get() else "disabled"
        for child in self.folder_frame.winfo_children():
            with contextlib.suppress(Exception):
                child.configure(state=state)

    def _set_interval_preset(self, seconds):
        """Set interval from preset button and update label"""
        self.interval_var.set(seconds)
        self.interval_label.config(text=self._format_interval(seconds))

    def _update_interval_label(self, value):
        """Update interval label when slider moves"""
        seconds = int(float(value))
        self.interval_label.config(text=self._format_interval(seconds))

    def _format_interval(self, seconds):
        """Format interval in human-readable form"""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours} hour{'s' if hours > 1 else ''}"

    def _save(self):
        """Save configuration and close"""
        try:
            # Validate
            if not self.prefix_var.get().strip():
                messagebox.showerror("Error", "Filename prefix cannot be empty")
                return

            if self.gdrive_enabled_var.get() and not self.gdrive_folder_var.get().strip():
                messagebox.showerror("Error", "Google Drive folder name cannot be empty")
                return

            # Save to config
            self.config.interval = self.interval_var.get()
            self.config.prefix = self.prefix_var.get().strip()
            self.config.gdrive_enabled = self.gdrive_enabled_var.get()
            self.config.gdrive_folder = self.gdrive_folder_var.get().strip()
            self.config.save()

            logger.info("✅ Configuration saved")
            messagebox.showinfo("Success", "Configuration saved!\n\nRestart the app for changes to take effect.")

            if self.on_save_callback:
                self.on_save_callback()

            self.window.destroy()
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")


if __name__ == "__main__":
    # Test dialog
    config = Config()
    dialog = ConfigDialog(config)
    dialog.show()
