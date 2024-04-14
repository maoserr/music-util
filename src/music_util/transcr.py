import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from multiprocessing import Process, Queue

import librosa
import pandas as pd


def get_notes(notes: pd.DataFrame, hop_duration=10) -> pd.DataFrame:
    notes['note'] = librosa.hz_to_note(notes['pitch'])
    notes['chg'] = notes.note.ne(notes.note.shift())
    notes['note_num'] = notes['chg'].cumsum()

    notes_uniq = notes.groupby('note_num').agg({
        'pitch': 'mean',
        'confidence': 'mean',
        'note': 'first',
        'chg': 'count'
    })
    notes_uniq['not_rest'] = notes_uniq.confidence.gt(0.6)
    notes_uniq['duration_ms'] = notes_uniq['chg'] * hop_duration
    return notes_uniq


def smooth_notes(notes: pd.DataFrame, min_length: float) -> pd.DataFrame:
    notes['rollup'] = False
    notes.loc[notes['duration_ms'] < min_length, 'rollup'] = True

    # get groups of notes to roll up
    nusg = notes.groupby(notes['rollup'].ne(notes['rollup'].shift()).cumsum()).agg({
        'pitch': 'mean',
        'confidence': 'mean',
        'note': 'first',
        'chg': 'sum',
        'not_rest': 'first',
        'duration_ms': 'sum',
        'rollup': 'first'
    })

    # Roll up to next note
    nugr = nusg.groupby(nusg['rollup'].eq(True).cumsum()).agg({
        'pitch': 'last',
        'confidence': 'last',
        'note': 'last',
        'chg': 'sum',
        'not_rest': 'last',
        'duration_ms': 'sum',
    })

    # Remove note name from rests
    nugr.loc[~nugr['not_rest'], 'note'] = ''

    # Combine same notes
    nuc = nugr.groupby(nugr['note'].ne(nugr['note'].shift()).cumsum()).agg({
        'pitch': 'first',
        'confidence': 'mean',
        'note': 'first',
        'chg': 'sum',
        'not_rest': 'first',
        'duration_ms': 'sum'
    })
    return nuc


def gen_sheet(note_cnts: pd.DataFrame,
              beat_len_ms: float,
              min_note: int,
              outfile: str,
              inbase: str):
    import numpy as np
    note_cnts['num_beats'] = note_cnts['duration_ms'] / beat_len_ms

    valid_notes = pd.Series([-np.inf, 1 / 16, 1 / 4, 1 / 2, 1, 2, 4, 8])
    labels = ['32', '16', '8', '4', '2', '1', '1/2']
    note_cnts['note_cat'] = pd.cut(note_cnts['num_beats'],
                                   valid_notes,
                                   labels=labels).fillna('2W')
    notations = []
    for _, r in note_cnts.iterrows():
        if r["not_rest"]:
            linote = r["note"][0].lower()
            octa = r["note"][-1]
            curr_not = linote
            if len(r["note"]) == 3:
                curr_not += 'is'
            if octa == '4':
                curr_not += "'"
            if r["note_cat"] == '1/2':
                notations.append(curr_not + "1")
                notations.append(curr_not + "1")
            else:
                notations.append(curr_not + r["note_cat"] )
        else:
            if r["note_cat"]  == '1/2':
                notations.append('r1')
                notations.append('r1')
            else:
                notations.append('r'+r["note_cat"] )
    with open(os.path.join(outfile, f"{inbase}_input.li"),"w") as f:
        f.write("{\n")
        f.write(" ".join(notations))
        f.write("\n}\n")

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
        os.makedirs(args[1], exist_ok=True)
        for file in infiles:
            fbase = os.path.splitext(os.path.basename(file))[0] + "0"
            while os.path.exists(os.path.join(args[1], f"{fbase}_notes.csv")):
                fbase = fbase[:-1] + str(int(fbase[-1]) + 1)
            audio_rosa, sr = librosa.load(file, sr=16000, mono=True)
            print("Getting tempo...")
            tempo, _ = librosa.beat.beat_track(y=audio_rosa, sr=sr)
            if audio_rosa.dtype == np.int16:
                audio_rosa = audio_rosa.astype(np.float32) / np.iinfo(np.int16).max

            print("Predicting pitch...")
            audio = torch.tensor(np.copy(audio_rosa.transpose()))[None]
            pitch, confidence = torchcrepe.predict(audio, sr, hop_length=160, return_periodicity=True, model="tiny")
            notes = pd.DataFrame({"pitch": pitch.numpy().squeeze(), "confidence": confidence.numpy().squeeze()})

            print("Processing notes...")
            note_cnts = get_notes(notes)

            beat_len_ms = (60 * 1000) / tempo
            min_note = 32  # 32nd note
            min_note_len = beat_len_ms / min_note
            note_smooth = smooth_notes(note_cnts, min_note_len)

            note_smooth.to_csv(os.path.join(args[1], f"{fbase}_notes.csv"))

            print("Sheet music...")
            gen_sheet(note_smooth, beat_len_ms, min_note, args[1], fbase)
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
