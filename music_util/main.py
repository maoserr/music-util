import sys
import tkinter as tk
from tkinter import ttk, filedialog
from multiprocessing import Process


def demucs_exec(args: list):
    from demucs import separate
    print(" ".join(args))
    separate.main(args)


class VocalRemover(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()

        self.filename = tk.StringVar(root, "")
        self.outfile = tk.StringVar(root, "")

        ttk.Label(self, text="MP3 File:").grid(column=0, row=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.filename, width=50).grid(column=1, row=0, padx=10, pady=10)
        ttk.Button(self, text="...", command=self.set_file).grid(column=2, row=0, padx=10, pady=10)
        ttk.Button(self, text="Run Remover", command=self.run_demucs).grid(column=2, row=2)
        ttk.Button(self, text="Set output", command=self.set_outfile).grid(column=0, row=1)
        ttk.Entry(self, textvariable=self.outfile, width=50).grid(column=1,row=1)

    def set_file(self):
        self.filename.set(tk.filedialog.askopenfilename(title='Select MP3',
                                                        initialdir='/',
                                                        filetypes=(("MP3", "*.mp3"),)))

    def set_outfile(self):
        self.outfile.set(tk.filedialog.asksaveasfilename(title='Select output location',
                                                         filetypes=(("Folder","*.*"),)))

    def run_demucs(self):
        p = Process(target=demucs_exec, args=(["--two-stems", "vocals", "--mp3", "-n", "htdemucs_ft"]
                                              + [self.filename.get()],))
        p.start()


def main(argv: list):
    import sv_ttk

    root = tk.Tk()
    tab_c = ttk.Notebook(root)
    voc_remover = VocalRemover(tab_c, pady=10, padx=10)
    tab_c.add(voc_remover, text="Vocal Remover")
    tab_c.pack(expand=1, fill="both")

    sv_ttk.set_theme("dark")
    root.title("Musician Utilities")
    root.iconphoto(False, tk.PhotoImage(file='icon.png'))
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv)
