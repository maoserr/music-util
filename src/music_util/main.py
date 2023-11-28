import sys
from collections import OrderedDict
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
from multiprocessing import Process

model_list = OrderedDict([
    ("HT Demucs (fine-tuned)", "htdemucs_ft"),
    ("HT Demucs", "htdemucs"),
    ("HT Demucs + Guitar & Piano", "htdemucs_6s"),
])

default_opts = {
    "HT Demucs (fine-tuned)": "--two-stems vocals --mp3",
}


def demucs_exec(args: list):
    from demucs import separate
    print("hello")
    print("test")
    separate.main(args)


class VocalRemover(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()

        default_model = list(model_list.keys())[0]

        self.outfile = tk.StringVar(root, "")
        self.model = tk.StringVar(root, list(model_list.keys())[0])
        self.adv_opt = tk.StringVar(root, default_opts.get(default_model, ""))
        r = 0

        # Output row
        ttk.Label(self, text="Output").grid(row=r, column=0)
        ttk.Entry(self, textvariable=self.outfile, width=50).grid(row=r, column=1)
        ttk.Button(self, text="...", command=self.set_outfile).grid(row=r, column=2, sticky="new")

        r = r + 1
        # Input row
        ttk.Label(self, text="Inputs").grid(row=r, column=0, sticky="n")
        self.inp_list = ttk.Treeview(self, columns=('file',), show='headings')
        self.inp_list.column('file')
        self.inp_list.heading('file', text="MP3 Input Files")
        self.inp_list.grid(row=r, column=1, sticky="nsew")
        ttk.Button(self, text="+", command=self.set_file).grid(row=r, column=2, sticky="new")

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
        print("All args: "+" ".join(all_args))
        p = Process(target=demucs_exec, args=(all_args,))
        p.start()


class transcription(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()


class StdoutRedirector(object):
    def __init__(self, text_widget: ScrolledText):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')

    def flush(self):
        pass

def main(argv: list):
    import sv_ttk
    import os
    if os.name == 'nt':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    root = tk.Tk()
    tab_c = ttk.Notebook(root)
    voc_remover = VocalRemover(tab_c, pady=10, padx=10)
    tab_c.add(voc_remover, text="Vocal Remover")
    tab_c.pack(expand=1, fill="both")

    # Log console
    ttk.Label(root, text="Log Console", anchor="w").pack(fill='both', padx=10, pady=(10, 0))
    log_win = ScrolledText(root, width=50, height=10)
    log_win.pack(expand=1, fill="both", padx=10, pady=10)

    sv_ttk.set_theme("dark")
    root.title("Musician Utilities")
    root.iconphoto(False, tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),
                                                          'icon.png')))
    root.resizable(False, False)

    sys.stdout = StdoutRedirector(log_win)
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv)
