import datetime
import queue
import logging
import signal
import time
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W


logger = logging.getLogger(__name__)


class Clock(threading.Thread):
    """Class to display the time every seconds
    Every 5 seconds, the time is displayed using the logging.ERROR level
    to show that different colors are associated to the log levels
    """

    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def run(self):
        logger.debug('Clock started')
        previous = -1
        line=0
        while not self._stop_event.is_set():
            now = datetime.datetime.now()

            if now.second % 5 == 0:
                level = logging.ERROR
            else:
                level = logging.INFO
            f = open("logCommits.txt", "r")
            logger.info(f.readlines()[line])
            line+=1
            time.sleep(0.2)

    def stop(self):
        self._stop_event.set()

class QueueHandler(logging.Handler):
    print("testt   ",logging.Handler.__dict__)
    """Class to send logging records to a queue
    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget
    """
    # Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    # (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
    # See https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

log_queue = queue.Queue()
queue_handler = QueueHandler(log_queue)
print("PRINTTTTT",queue_handler.log_queue.__dict__)
formatter = logging.Formatter('%(asctime)s: %(message)s')
queue_handler.setFormatter(formatter)
logger.addHandler(queue_handler)
# Start polling messages from the queue
tk.frame.after(100, poll_log_queue)

def display(self, record):
    msg = self.queue_handler.format(record)
    print(msg)
    self.scrolled_text.configure(state='normal')
    self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
    self.scrolled_text.configure(state='disabled')
    # Autoscroll to the bottom
    self.scrolled_text.yview(tk.END)

def poll_log_queue(self):
    print("checked")
    # Check every 100ms if there is a new message in the queue to display
    while True:
        try:
            record = self.log_queue.get(block=False)
        except queue.Empty:
            break
        else:
            self.display(record)
    self.frame.after(100, self.poll_log_queue)
class App:

    def __init__(self, root):
        self.root = root
        root.title('Logging Handler')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        # Create the panes and frames
        vertical_pane = ttk.PanedWindow(self.root, orient=VERTICAL)
        vertical_pane.grid(row=0, column=0, sticky="nsew")
        horizontal_pane = ttk.PanedWindow(vertical_pane, orient=HORIZONTAL)
        vertical_pane.add(horizontal_pane)
        console_frame = ttk.Labelframe(horizontal_pane, text="Console")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        horizontal_pane.add(console_frame, weight=1)
        # Initialize all frames
        self.console = ConsoleUi(console_frame)
        self.clock = Clock()
        self.clock.start()
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)
        signal.signal(signal.SIGINT, self.quit)

    def quit(self, *args):
        self.root.destroy()
def main():
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Tk()
    app = App(root)
    app.root.mainloop()


if __name__ == '__main__':
    main()
