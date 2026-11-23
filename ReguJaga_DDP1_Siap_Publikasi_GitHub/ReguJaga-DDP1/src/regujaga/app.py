"""Jalur masuk aplikasi Tkinter."""
from .ui import ReguJagaApp


def main() -> None:
    import tkinter as tk
    root = tk.Tk()
    ReguJagaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
