import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from collections import OrderedDict
from multiprocessing import Process, Queue


def crepe_exe(args: list, q: Queue):
    from music_util.utils import StdoutProcRedirect
    sys.stdout = StdoutProcRedirect(q)
    sys.stderr = StdoutProcRedirect(q)

    import crepe
    import librosa
    import pandas as pd
    audio, sr = librosa.load(args[0])
    time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True)
    pd.DataFrame({'time':time,"freq":frequency,"confident":confidence}).to_csv(args[1])
    print("Processing complete")


class Transcript(tk.Frame):
    def __init__(self, root: ttk.Notebook, q: Queue, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()
        self.q = q

        self.outfile = tk.StringVar(root, os.path.join(os.getcwd(), "out"))
        self.inpfile = tk.StringVar(root, "")
        r = 0

        # Output row
        ttk.Label(self, text="Output").grid(row=r, column=0)
        ttk.Entry(self, textvariable=self.outfile).grid(row=r, column=1, sticky="ew")
        ttk.Button(self, text="...", command=self.set_outfile).grid(row=r, column=2, sticky="new")

        r = r + 1
        # Input row
        ttk.Label(self, text="Input").grid(row=r, column=0)
        ttk.Entry(self, textvariable=self.inpfile).grid(row=r, column=1, sticky="ew")
        ttk.Button(self, text="...", command=self.set_infile).grid(row=r, column=2, sticky="new")

        r = r + 1
        # Run row
        ttk.Button(self, text="Run", command=self.run_transcipt).grid(row=r, column=2, sticky="e")

        self.grid_columnconfigure(1, weight=4)
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def set_outfile(self):
        self.outfile.set(tk.filedialog.asksaveasfilename(title='Select output location',
                                                         filetypes=(("Folder", "*.*"),)))

    def set_infile(self):
        self.inpfile.set(tk.filedialog.askopenfilename(title='Select MP3',
                                                       initialdir='/',
                                                       filetypes=(("MP3", "*.mp3"), ("All files", "*.*")))
                         )

    def run_transcipt(self):
        infile = self.inpfile.get()
        outfile = self.outfile.get()
        print("Starting crepes...")
        all_args = [infile, outfile]
        p = Process(target=crepe_exe, args=(all_args, self.q))
        p.start()
