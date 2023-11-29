from tkinter.scrolledtext import ScrolledText
from multiprocessing import Queue


def _print(items: str, log_win: ScrolledText):
    log_win.delete('end-1c', 'end')
    if "\r" in items:
        log_win.delete('end-1l', 'end')
        log_win.insert('end', '\n')
        chunks = items.split("\r")
        string = chunks[len(chunks) - 1]
    else:
        string = items
    log_win.insert('end', string + "\n")
    log_win.see('end')


class StdoutProcRedirect(object):
    def __init__(self, q: Queue):
        self.queue = q

    def write(self, string: str):
        self.queue.put(string)

    def flush(self):
        pass


class StdoutRedirector(object):
    def __init__(self, text_widget: ScrolledText):
        self.text_space = text_widget

    def write(self, string: str):
        _print(string, self.text_space)

    def flush(self):
        pass


def enqueue_output(queue: Queue, log_win: ScrolledText):
    while True:
        items = queue.get(True)
        _print(items, log_win)
