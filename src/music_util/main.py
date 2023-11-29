import os
import sys
from collections import OrderedDict
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
from multiprocessing import Process, Queue

model_list = OrderedDict([
    ("HT Demucs (fine-tuned)", "htdemucs_ft"),
    ("HT Demucs", "htdemucs"),
    ("HT Demucs + Guitar & Piano", "htdemucs_6s"),
])

default_opts = {
    "HT Demucs (fine-tuned)": "--two-stems vocals --mp3",
}


class StdoutProcRedirect(object):
    def __init__(self, q: Queue):
        self.queue = q

    def write(self, string: str):
        self.queue.put(string)

    def flush(self):
        pass


def demucs_exec(args: list, q: Queue):
    from demucs import separate
    sys.stdout = StdoutProcRedirect(q)
    sys.stderr = StdoutProcRedirect(q)
    separate.main(args)
    print("Processing complete")


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

        # Output row
        ttk.Label(self, text="Output").grid(row=r, column=0)
        ttk.Entry(self, textvariable=self.outfile).grid(row=r, column=1, sticky="ew")
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


class Transcript(tk.Frame):
    def __init__(self, root: ttk.Notebook, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()

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
        ttk.Button(self, text="...", command=self.set_outfile).grid(row=r, column=2, sticky="new")

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
        pass


class StdoutRedirector(object):
    def __init__(self, text_widget: ScrolledText):
        self.text_space = text_widget

    def write(self, string: str):
        if "\r" in string:
            self.text_space.delete('end-1l', 'end')
            chunks = string.split("\r")
            string = chunks[len(chunks) - 1]
        self.text_space.insert('end', string)
        self.text_space.see('end')

    def flush(self):
        pass


def enqueue_output(queue: Queue, log_win: ScrolledText):
    while True:
        items = queue.get(True)
        if "\r" in items:
            log_win.delete('end-1l', 'end')
            log_win.insert('end', '\n')
            chunks = items.split("\r")
            string = chunks[len(chunks) - 1]
        else:
            string = items
        log_win.insert('end', string)
        log_win.see('end')


def main(argv: list):
    import sv_ttk
    import os
    from threading import Thread
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

    trans = Transcript(tab_c, pady=10, padx=10)
    tab_c.add(trans, text="Transcription")
    tab_c.pack(expand=1, fill="both")

    # Log console
    ttk.Label(root, text="Log Console", anchor="w").pack(fill='both', padx=10, pady=(10, 0))
    log_win = ScrolledText(root, width=50, height=10)
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
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv)
