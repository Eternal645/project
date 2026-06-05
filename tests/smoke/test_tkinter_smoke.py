import os
import tkinter as tk
import unittest


class TkinterSmokeTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("DISPLAY"), "DISPLAY is required for Tkinter smoke test")
    def test_tkinter_window_can_be_created_and_closed(self):
        root = tk.Tk()
        try:
            root.withdraw()
            root.title("Tkinter smoke test")
            root.update()
            self.assertEqual(root.title(), "Tkinter smoke test")
        finally:
            root.quit()
            root.destroy()


if __name__ == "__main__":
    unittest.main()
