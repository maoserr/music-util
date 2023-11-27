import sys
import tkinter
from tkinter import ttk, Frame, PhotoImage
from tkinter import filedialog as fd
from multiprocessing import Process


def demucs_exec(args: list):
    from demucs import separate
    print(" ".join(args))
    separate.main(args)


class MainApplication(Frame):
    filename = ""

    def __init__(self, root, *args, **kwargs):
        Frame.__init__(self, root, *args, **kwargs)
        self.grid()

        ttk.Label(self, text="MP3 File:").grid(column=0, row=0, padx=10, pady=10)
        ttk.Entry(self).grid(column=1, row=0, padx=10, pady=10)
        ttk.Button(self, text="...", command=self.set_file).grid(column=2, row=0)
        ttk.Button(self, text="Run Demucs", command=self.run_demucs).grid(column=3, row=0)

    def set_file(self):
        self.filename = fd.askopenfilename(title='Select MP3',
                                           initialdir='/',
                                           filetypes=(("MP3", "*.mp3"),))

    def run_demucs(self):
        p = Process(target=demucs_exec, args=(["--two-stems", "vocals", "--mp3", "-n", "htdemucs_ft"]
                                              + [self.filename],))
        p.start()


def main(argv: list):
    import sv_ttk

    root = tkinter.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)

    sv_ttk.set_theme("dark")
    root.title("Musician Utilities")
    root.geometry("600x400")
    root.iconphoto(False, PhotoImage(file='icon.png'))
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv)
