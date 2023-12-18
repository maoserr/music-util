import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from multiprocessing import Process, Queue

import librosa
import pandas as pd


def get_notes(notes: pd.DataFrame, outfile: str, tempo: float, beats: list):
    beat_len_ms = (60 * 1000) / tempo
    min_note_len = beat_len_ms / 16

    notes['chg'] = notes.note.ne(notes.note.shift())
    notes['not_rest'] = notes.confidence.gt(0.6)
    notes['notes_chg'] = notes['chg'] & notes['not_rest']
    notes['notes_size'] = notes['notes_chg'].cumsum()

    notes_uniq = notes.groupby('notes_size').agg({
        'pitch': 'first',
        'confidence': 'first',
        'note': 'first',
        'chg': 'count',
        'not_rest': 'first',
        'notes_chg': 'first'
    })
    outdf = notes
    outdf.to_csv(outfile)


def crepe_exe(args: list, q: Queue):
    from music_util.utils import StdoutProcRedirect
    sys.stdout = StdoutProcRedirect(q)
    sys.stderr = StdoutProcRedirect(q)

    try:
        import torchcrepe
        import numpy as np
        import torch
        import os

        infiles = args[0]
        for file in infiles:
            audio_rosa, sr = librosa.load(file, sr=16000, mono=True)
            tempo, beats = librosa.beat.beat_track(y=audio_rosa, sr=sr)
            if audio_rosa.dtype == np.int16:
                audio_rosa = audio_rosa.astype(np.float32) / np.iinfo(np.int16).max

            audio = torch.tensor(np.copy(audio_rosa.transpose()))[None]
            pitch, confidence = torchcrepe.predict(audio, sr, return_periodicity=True, model="tiny")
            notes = pd.DataFrame({"pitch": pitch.numpy().squeeze(), "confidence": confidence.numpy().squeeze()})
            notes['note'] = librosa.hz_to_note(notes['pitch'])
            get_notes(notes, args[1], tempo, beats)
        print("Processing complete")
    except:
        import traceback
        traceback.print_exc()


class Transcript(tk.Frame):
    def __init__(self, root: ttk.Notebook, q: Queue, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()
        self.q = q

        self.outfile = tk.StringVar(root, os.path.join(os.getcwd(), "out"))
        self.inpfile = tk.StringVar(root, "")
        r = 0

        # Input row
        ttk.Label(self, text="Input").grid(row=r, column=0, sticky="n")
        self.inp_list = ttk.Treeview(self, columns=('file',), show='headings')
        self.inp_list.column('file')
        self.inp_list.heading('file', text="MP3 Input Files")
        self.inp_list.grid(row=r, column=1, sticky="nsew")
        ttk.Button(self, text="+", command=self.set_infile).grid(row=r, column=2, sticky="new")
        r = r + 1

        # Output row
        ttk.Label(self, text="Output").grid(row=r, column=0)
        ttk.Entry(self, textvariable=self.outfile).grid(row=r, column=1, sticky="ew")
        ttk.Button(self, text="...", command=self.set_outfile).grid(row=r, column=2, sticky="new")
        r = r + 1

        # Run row
        ttk.Button(self, text="Run", command=self.run_transcipt).grid(row=r, column=2, sticky="e")

        self.grid_columnconfigure(1, weight=4)
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def set_outfile(self):
        self.outfile.set(tk.filedialog.asksaveasfilename(title='Select output location',
                                                         filetypes=(("CSV file", "*.csv"),)))

    def set_infile(self):
        files = tk.filedialog.askopenfilenames(title='Select MP3',
                                               initialdir='/',
                                               filetypes=(("MP3", "*.mp3"), ("All files", "*.*")))
        for i in files:
            self.inp_list.insert('', tk.END, values=(i,))

    def run_transcipt(self):
        in_files = [self.inp_list.item(i)['values'][0] for i in self.inp_list.get_children()]
        outfile = self.outfile.get()
        print("Starting crepes...")
        all_args = [in_files, outfile]
        p = Process(target=crepe_exe, args=(all_args, self.q))
        p.start()
