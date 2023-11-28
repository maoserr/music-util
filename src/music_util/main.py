import sys
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
from multiprocessing import Process


def demucs_exec(args: list):
    from demucs import separate
    print(" ".join(args))
    separate.main(args)


class VocalRemover(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()

        self.outfile = tk.StringVar(root, "")

        ttk.Entry(self, textvariable=self.outfile, width=50).grid(column=1, row=1)
        ttk.Button(self, text="Set output", command=self.set_outfile).grid(column=0, row=1)

        self.inp_list = ttk.Treeview(self, columns=('file',), show='headings')
        self.inp_list.column('file', width=500)
        self.inp_list.heading('file', text="MP3 Input Files")
        self.inp_list.grid(column=0, row=3, columnspan=2)
        ttk.Button(self, text="+", command=self.set_file).grid(column=2, row=0)

        ttk.Button(self, text="Run Remover", command=self.run_demucs).grid(column=2, row=2)
        ScrolledText(self, width=50, height=20).grid(column=0, row=4, columnspan=2)

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
        # p = Process(target=demucs_exec, args=(["--two-stems", "vocals", "--mp3", "-n", "htdemucs_ft"]
        #                                       + in_files,))
        # p.start()


class transcription(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.grid()


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

    sv_ttk.set_theme("dark")
    root.title("Musician Utilities")
    root.iconphoto(False, tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),
                                                          'icon.png')))
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv)
