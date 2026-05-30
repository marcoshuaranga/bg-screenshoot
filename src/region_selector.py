"""Screen region selector for Screenshot Capture"""

import logging
import tkinter as tk

logger = logging.getLogger(__name__)


class RegionSelector:
    """Visual region selector overlay"""

    def __init__(self):
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None  # (x, y, width, height)

    def select_region(self) -> tuple[int, int, int, int] | None:
        """Show fullscreen overlay and let user select a region

        Returns:
            Tuple (x, y, width, height) or None if cancelled
        """
        self.region = None

        # Create fullscreen window
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)  # Semi-transparent
        self.root.attributes("-topmost", True)
        self.root.configure(cursor="crosshair")

        screen_width = self.root.winfo_screenwidth()

        # Create canvas
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)

        # Instructions
        self.canvas.create_text(
            screen_width // 2,
            30,
            text="Click and drag to select region | ESC to cancel | Enter to capture full screen",
            fill="white",
            font=("Arial", 14, "bold"),
        )

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Escape>", lambda e: self._cancel())
        self.root.bind("<Return>", lambda e: self._select_fullscreen())

        self.root.mainloop()

        return self.region

    def _on_press(self, event):
        """Mouse button pressed - start selection"""
        self.start_x = event.x
        self.start_y = event.y

        # Create rectangle
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="red",
            width=2,
            fill="red",
            stipple="gray50",  # Checkered pattern
        )

    def _on_drag(self, event):
        """Mouse dragged - update selection rectangle"""
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def _on_release(self, event):
        """Mouse released - finalize selection"""
        if self.rect:
            # Calculate region
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)

            width = x2 - x1
            height = y2 - y1

            # Validate minimum size
            if width < 10 or height < 10:
                logger.warning("Region too small, cancelled")
                self._cancel()
                return

            self.region = (x1, y1, width, height)
            logger.info(f"Region selected: {self.region}")
            self.root.destroy()

    def _cancel(self):
        """Cancel selection"""
        self.region = None
        logger.info("Region selection cancelled")
        self.root.destroy()

    def _select_fullscreen(self):
        """Select full screen (no region)"""
        self.region = None  # None means fullscreen
        logger.info("Full screen selected")
        self.root.destroy()


def test_region_selector():
    """Test the region selector"""
    selector = RegionSelector()
    region = selector.select_region()

    if region:
        print(f"Selected region: x={region[0]}, y={region[1]}, w={region[2]}, h={region[3]}")
    else:
        print("Full screen or cancelled")


if __name__ == "__main__":
    test_region_selector()
