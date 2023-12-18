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
        self.queue.put("> "+string)

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


if __name__ == '__main__':
    import torchcrepe
    file = r'C:\Users\maose\Desktop\out\htdemucs_ft\HD周深 - 大魚 [歌詞字幕][動畫電影大魚海棠印象曲][完整高清音質] Big Fish & Begonia Theme Song (Zhou Shen - Big Fish)\vocals.wav'
    audio, sr = torchcrepe.load.audio( file )

    # Here we'll use a 5 millisecond hop length
    hop_length = int(sr / 200.)

    # Provide a sensible frequency range for your domain (upper limit is 2006 Hz)
    # This would be a reasonable range for speech
    fmin = 50
    fmax = 550

    # Select a model capacity--one of "tiny" or "full"
    model = 'tiny'

    # Choose a device to use for inference
    device = 'cuda:0'

    # Pick a batch size that doesn't cause memory errors on your gpu
    batch_size = 2048

    # Compute pitch using first gpu
    pitch = torchcrepe.predict(audio,
                               sr,
                               hop_length,
                               fmin,
                               fmax,
                               model,
                               batch_size=batch_size,
                               device=device)
