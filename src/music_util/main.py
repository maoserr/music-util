import sys

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from multiprocessing import Queue


def main(argv: list):
    import sv_ttk
    import os
    from threading import Thread
    from music_util.voc_rem import VocalRemover
    from music_util.transcr import Transcript
    from music_util.utils import enqueue_output, StdoutRedirector

    if os.name == 'nt':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    q = Queue()

    root: tk.Tk = tk.Tk()
    tab_c = ttk.Notebook(root)

    # Vocal remover
    voc_remover = VocalRemover(tab_c, q, pady=10, padx=10)
    tab_c.add(voc_remover, text="Vocal Remover")
    tab_c.pack(expand=1, fill="both")

    trans = Transcript(tab_c, q, pady=10, padx=10)
    tab_c.add(trans, text="Transcription")
    tab_c.pack(expand=1, fill="both")

    # Log console
    ttk.Label(root, text="Log Console", anchor="w").pack(fill='both', padx=10, pady=(10, 0))
    log_win = ScrolledText(root, wrap="none", width=50, height=10)
    log_win.pack(expand=1, fill="both", padx=10, pady=10)

    t = Thread(target=enqueue_output, args=(q, log_win))
    t.daemon = True  # thread dies with the program
    t.start()

    # Main window
    sv_ttk.set_theme("dark")
    root.title("Musician Utilities")
    root.geometry("800x600")
    root.iconphoto(False, tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),
                                                          'icon.png')))
    sys.stdout = StdoutRedirector(log_win)
    sys.stderr = StdoutRedirector(log_win)
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv)
