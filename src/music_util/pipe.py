# https://stackoverflow.com/questions/24277488/in-python-how-to-capture-the-stdout-from-a-c-shared-library-to-a-variable

import ctypes
import os
import sys
import threading

print 'Start'

liba = ctypes.cdll.LoadLibrary('libtest.dylib')

# Create pipe and dup2() the write end of it on top of stdout, saving a copy
# of the old stdout
stdout_fileno = sys.stdout.fileno()
stdout_save = os.dup(stdout_fileno)
stdout_pipe = os.pipe()
os.dup2(stdout_pipe[1], stdout_fileno)
os.close(stdout_pipe[1])

captured_stdout = ''
def drain_pipe():
    global captured_stdout
    while True:
        data = os.read(stdout_pipe[0], 1024)
        if not data:
            break
        captured_stdout += data

t = threading.Thread(target=drain_pipe)
t.start()

liba.hello()  # Call into the shared library

# Close the write end of the pipe to unblock the reader thread and trigger it
# to exit
os.close(stdout_fileno)
t.join()

# Clean up the pipe and restore the original stdout
os.close(stdout_pipe[0])
os.dup2(stdout_save, stdout_fileno)
os.close(stdout_save)

print 'Captured stdout:\n%s' % captured_stdout
