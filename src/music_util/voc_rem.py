import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from collections import OrderedDict
from multiprocessing import Process, Queue

model_list = OrderedDict([
    ("HT Demucs (fine-tuned)", "htdemucs_ft"),
    ("HT Demucs", "htdemucs"),
    ("HT Demucs + Guitar & Piano", "htdemucs_6s"),
])

default_opts = {
    "HT Demucs (fine-tuned)": "--two-stems vocals --mp3",
}


def demucs_exec(args: list, q: Queue):
    from music_util.utils import StdoutProcRedirect
    sys.stdout = StdoutProcRedirect(q)
    sys.stderr = StdoutProcRedirect(q)

    try:
        from demucs import separate
        separate.main(args)
        print("Processing complete")
    except:
        import traceback
        traceback.print_exc()


class VocalRemover(tk.Frame):
    def __init__(self, root: ttk.Notebook, q: Queue, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()
        self.q = q

        default_model = list(model_list.keys())[0]

        self.outfile = tk.StringVar(root, os.path.join(os.getcwd(), "out"))
        self.model = tk.StringVar(root, list(model_list.keys())[0])
        self.adv_opt = tk.StringVar(root, default_opts.get(default_model, ""))
        r = 0

        # Input row
        ttk.Label(self, text="Inputs").grid(row=r, column=0, sticky="n")
        self.inp_list = ttk.Treeview(self, columns=('file',), show='headings')
        self.inp_list.column('file')
        self.inp_list.heading('file', text="MP3 Input Files")
        self.inp_list.grid(row=r, column=1, sticky="nsew")
        ttk.Button(self, text="+", command=self.set_file).grid(row=r, column=2, sticky="new")
        r = r + 1

        # Output row
        ttk.Label(self, text="Output").grid(row=r, column=0)
        ttk.Entry(self, textvariable=self.outfile).grid(row=r, column=1, sticky="ew")
        ttk.Button(self, text="...", command=self.set_outfile).grid(row=r, column=2, sticky="new")
        r = r + 1

        # Model selection row
        ttk.Label(self, text="Model").grid(row=r, column=0)
        ttk.Combobox(self, textvariable=self.model, state="readonly",
                     values=list(model_list.keys())).grid(row=r, column=1, sticky="we")
        r = r + 1

        # Run row
        ttk.Label(self, text="Advanced").grid(row=r, column=0)
        ttk.Entry(self, textvariable=self.adv_opt).grid(row=r, column=1, sticky="ew")
        ttk.Button(self, text="Run", command=self.run_demucs).grid(row=r, column=2, sticky="e")
        r = r + 1

        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(1, weight=4)
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def set_file(self):
        files = tk.filedialog.askopenfilenames(title='Select MP3',
                                               initialdir='/',
                                               filetypes=(("MP3", "*.mp3"), ("All files", "*.*")))
        for i in files:
            self.inp_list.insert('', tk.END, values=(i,))

    def set_outfile(self):
        self.outfile.set(tk.filedialog.asksaveasfilename(title='Select output location',
                                                         filetypes=(("Folder", "*.*"),)))

    def run_demucs(self):
        in_files = [self.inp_list.item(i)['values'][0] for i in self.inp_list.get_children()]
        mod = model_list[self.model.get()]
        args = self.adv_opt.get().split()
        out = self.outfile.get()
        print("Starting demucs...")
        all_args = ["-n", mod, "--out", out] + args + in_files
        print("All args: " + " ".join(all_args))
        p = Process(target=demucs_exec, args=(all_args, self.q))
        p.start()
